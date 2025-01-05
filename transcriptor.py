import platform
import subprocess
import os
import whisper
import torch
import io
from google.oauth2 import service_account
from google.cloud import speech
from loguru import logger as log

extracting_process = -1

def extract_audio_from_video(video_file_path):
    """Ekstrakcja audio z wideo z wykorzystaniem `ffmpeg`"""
    global extracting_process

    system_name = platform.system()
    filename_and_path, ext = os.path.splitext(video_file_path)
    audio_ext = "mp3"

    # update_status("Ekstrakcja audio w toku...")
    log.info(f"Rozpoczęto ekstrakcję audio z video. ({system_name})\n"
             f"Scieżka do pliku video: {video_file_path}")
    if system_name == "Windows":
        try:
            # TODO(altGreG): Po testach, usunąć opcję -t z komendy (-t mówi jak długi kawałek nagrania przekonwertować)
            extracting_process = subprocess.call(["ffmpeg", "-y", "-i", video_file_path, "-t", "00:00:50.0", f"{filename_and_path}.{audio_ext}"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.STDOUT)
        except Exception as err:
            # update_status(f"Wystąpił problem w czasie ekstrakcji audio z video: {err}")
            log.error(f"Wystąpił problem w czasie ekstrakcji audio z video: {err}")
            return -1
    elif system_name == "Linux":
        try:
            extracting_process = subprocess.call(["ffmpeg", "-y", "-i", video_file_path, f"{filename_and_path}.{audio_ext}"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.STDOUT)
        except Exception as err:
            # update_status(f"Wystąpił problem w czasie ekstrakcji audio z video: {err}")
            log.error(f"Wystąpił problem w czasie ekstrakcji audio z video: {err}")
            return -1

    if extracting_process != 0:
        # update_status(f"Błąd w czasie ekstrakcji audio z wideo. Kod błędu: {extracting_process}")
        log.error(f"Błąd w czasie ekstrakcji audio z wideo (ffmpeg). Kod błędu: {extracting_process}")
        return -1
    else:
        # update_status("Sukces. Dokonano ekstrakcji audio z wideo.")
        log.success("Skutecznie dokonano ekstrakcji audio z wideo.\n"
                    f"Ścieżka do pliku audio: {filename_and_path}.{audio_ext}")
        return 0

def transcribe_with_whisper_offline(audio_file_path):
    """Transkrypcja audio offline z wykorzystaniem modelu Whisper od OpenAi"""


    # update_status("Przygotowanie do transkrypcji audio.")
    filename_and_path, ext = os.path.splitext(audio_file_path)
    filename = (filename_and_path.replace("\\", "/")).split("/")[-1]
    audio_file_path = audio_file_path.replace("\\", "/")
    log.debug(f"Filename: {filename}  |  Ext: {ext}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        torch.cuda.init()
    log.info(f"Urządzenie na którym zostanie wykonana transkrypcja: {device}")

    # tiny, base, small, medium, large, turbo
    model = whisper.load_model("medium").to(device)
    audio = whisper.load_audio(audio_file_path)

    # update_status("Transkrypcja audio w toku...")
    try:
        with torch.cuda.device(device):
            result = model.transcribe(audio=audio, language="pl", word_timestamps=True)

        # Proste formatowanie tekstu
        transcribed_text = text_formatting(result["text"])

        # update_status("Skutecznie dokonano transkrypcji audio.")
        log.success("Skutecznie dokonano transkrypcji audio.")

        print("Przetranskrybowany tekst:\n", transcribed_text)
    except Exception as err:
        # update_status(f"Wystąpił problem w czasie transkrypcji audio: {err}")
        log.error(f"Wystąpił problem w czasie transkrypcji audio: {err}")
        return filename, -1

    return filename, transcribed_text

# TODO(altGreG): Na razie program może obsłużyć pliki audio o długości do 1 minuty, do poprawy
def transcribe_with_gcloud(audio_file_path):
    """Transkrypcja audio z wykorzystaniem api do usługi Speech to Text na Google Cloud"""


    # update_status("Przygotowanie do transkrypcji audio.")
    filename_and_path, ext = os.path.splitext(audio_file_path)
    filename = (filename_and_path.replace("\\", "/")).split("/")[-1]
    audio_file_path = audio_file_path.replace("\\", "/")
    log.debug(f"Filename: {filename}  |  Ext: {ext}")

    # Utworzenie obiektu do autoryzacji dostępu do usług Google Cloud
    # Uwaga: Użytkownik sam musi pozyskać plik JSON do autoryzacji w Google Cloud API
    # update_status("Załadowanie pliku autoryzacyjnego do usług Google Cloud, konfiguracja.")
    client_file = './sa_gc.json'
    credentials = service_account.Credentials.from_service_account_file(client_file)
    client = speech.SpeechClient(credentials=credentials)

    with io.open(audio_file_path, mode="rb") as audio_file:
        content = audio_file.read()
        audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=44100,
        language_code="pl-pl",
        enable_automatic_punctuation=True,
    )

    # update_status("Transkrypcja audio w toku...")
    try:
        response = client.recognize(config=config, audio=audio)

        transcribed_text_before_formatting = ""
        for result in response.results:
            transcribed_text_before_formatting = result.alternatives[0].transcript

        # Proste formatowanie tekstu
        transcribed_text = text_formatting(transcribed_text_before_formatting)

        # update_status("Skutecznie dokonano transkrypcji audio.")
        log.success("Skutecznie dokonano transkrypcji audio.")

        print("Przetranskrybowany tekst:\n", transcribed_text)
    except Exception as err:
        # update_status(f"Wystąpił problem w czasie transkrypcji audio: {err}")
        log.error(f"Wystąpił problem w czasie transkrypcji audio: {err}")
        return filename, -1

    return filename, transcribed_text

def text_formatting(text):
    i = 0
    result = ""
    for word in text.split(" "):
        i += 1
        if i % 30 == 0:
            result += f"{word}\n"
        else:
            result += f"{word} "
    return result

def save_text_to_txt(filename, transcribed_text):
    """ Zapis przetranskrybowanego tekstu do pliku .txt"""


    # update_status("Przygotowanie do zapisu transkrypcji w pliku txt.")
    output_dir = (os.path.dirname(__file__) + "/txt").replace("\\", "/")
    os.makedirs(output_dir, exist_ok=True)  # Tworzenie folderu, jeśli nie istnieje

    txt_path = (output_dir + f"/{filename}.txt").replace("\\", "/")
    log.info(f"Miejsce zapisu pliku txt: {txt_path}" )

    # update_status("Zapis do pliku txt w toku...")
    try:
        with open(txt_path, 'w', encoding='utf-8') as file:
            file.write(transcribed_text, )
            # update_status("Dokonano zapisu tekstu do pliku txt")
    except Exception as err:
        # update_status(f"Wystąpił problem w czasie zapisu do pliku txt: {err}")
        log.error(f"Wystąpił problem w czasie zapisu do pliku txt: {err}")

# TODO(altGreG): Przeprowadzić testy
# Uwaga: Ścieżki i nazwy plików trzeba dostosować pod siebie w czasie testów na własnej maszynie
def audio_extraction_test():
    s = r"D:\Studia\InzynieriaOprogramowania\kreator-notatek-ze-spotkan\nagrania\test.mkv"
    extract_audio_from_video(s)

def audio_transcribe_whisper_test():
    return transcribe_with_whisper_offline(r"D:\Studia\InzynieriaOprogramowania\kreator-notatek-ze-spotkan\nagrania\test.mp3")

def audio_transcribe_gc_test():
    return transcribe_with_gcloud(r"D:\Studia\InzynieriaOprogramowania\kreator-notatek-ze-spotkan\nagrania\test.mp3")

# Uwaga: Wywołania funkcji testujących oprogramowanie

audio_extraction_test()
filename, transcribed_text = audio_transcribe_whisper_test()
# filename, transcribed_text = audio_transcribe_gc_test()

if transcribed_text != -1:
    save_text_to_txt(filename, transcribed_text)
else:
    log.critical("Nie udało się wykonać transkrypcji audio. Nie można zapisać transkrypcji do pliku txt.")