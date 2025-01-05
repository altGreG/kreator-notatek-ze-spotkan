import platform
import subprocess
import os
import whisper
import torch
import io
from google.oauth2 import service_account
from google.cloud import speech
from loguru import logger as log
from logger import log_status

extracting_process = -1

def extract_audio_from_video(video_file_path, update_status):
    """Ekstrakcja audio z wideo z wykorzystaniem `ffmpeg`"""
    global extracting_process

    system_name = platform.system()
    filename_and_path, ext = os.path.splitext(video_file_path)
    audio_ext = "mp3"

    log_status("Ekstrakcja audio w toku...", "info", update_status)
    log.debug(f"Scieżka do pliku video: {video_file_path}. System: {system_name}")
    if system_name == "Windows":
        try:
            # TODO(altGreG): Po testach, usunąć opcję -t z komendy (-t mówi jak długi kawałek nagrania przekonwertować)
            extracting_process = subprocess.call(["ffmpeg", "-y", "-i", video_file_path, "-t", "00:00:50.0", f"{filename_and_path}.{audio_ext}"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.STDOUT)
        except Exception as err:
            log_status(f"Wystąpił problem w czasie ekstrakcji audio z video: {err}", "error", update_status)
            return -1
    elif system_name == "Linux":
        try:
            extracting_process = subprocess.call(["ffmpeg", "-y", "-i", video_file_path, f"{filename_and_path}.{audio_ext}"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.STDOUT)
        except Exception as err:
            log_status(f"Wystąpił problem w czasie ekstrakcji audio z video: {err}", "error", update_status)
            return -1

    if extracting_process != 0:
        log_status(f"Błąd w czasie ekstrakcji audio z wideo (ffmpeg).\nKod błędu: {extracting_process}", "error", update_status)
        return -1
    else:
        log_status("Sukces. Dokonano ekstrakcji audio z wideo.", "success", update_status)
        log.debug(f"Ścieżka do pliku audio: {filename_and_path}.{audio_ext}")
        return 0

def transcribe_with_whisper_offline(audio_file_path, update_status):
    """Transkrypcja audio offline z wykorzystaniem modelu Whisper od OpenAi"""


    log_status("Przygotowanie do transkrypcji audio.", "info", update_status)
    filename_and_path, ext = os.path.splitext(audio_file_path)
    filename = (filename_and_path.replace("\\", "/")).split("/")[-1]
    audio_file_path = audio_file_path.replace("\\", "/")
    log.debug(f"Filename: {filename}  |  Ext: {ext}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        torch.cuda.init()
    log_status(f"Urządzenie na którym zostanie wykonana transkrypcja: {device}", "info", update_status)

    # tiny, base, small, medium, large, turbo
    model = whisper.load_model("medium").to(device)
    audio = whisper.load_audio(audio_file_path)

    log_status("Transkrypcja audio w toku...", "info", update_status)
    try:
        with torch.cuda.device(device):
            result = model.transcribe(audio=audio, language="pl", word_timestamps=True)

        # Proste formatowanie tekstu
        transcribed_text = text_formatting(result["text"])

        log_status("Skutecznie dokonano transkrypcji audio.", "success", update_status)
        print("Przetranskrybowany tekst:\n", transcribed_text)
    except Exception as err:
        log_status(f"Wystąpił problem w czasie transkrypcji audio: {err}", "error", update_status)
        return filename, -1

    return filename, transcribed_text

# TODO(altGreG): Na razie program może obsłużyć pliki audio o długości do 1 minuty, do poprawy
def transcribe_with_gcloud(audio_file_path, update_status):
    """Transkrypcja audio z wykorzystaniem api do usługi Speech to Text na Google Cloud"""


    log_status("Przygotowanie do transkrypcji audio.", "info", update_status)

    filename_and_path, ext = os.path.splitext(audio_file_path)
    filename = (filename_and_path.replace("\\", "/")).split("/")[-1]
    audio_file_path = audio_file_path.replace("\\", "/")

    log.debug(f"Filename: {filename}  |  Ext: {ext}")

    """
    Utworzenie obiektu do autoryzacji dostępu do usług Google Cloud
    Uwaga: Użytkownik sam musi pozyskać plik JSON do autoryzacji w Google Cloud API
    """
    log_status("Załadowanie pliku autoryzacyjnego do usług Google Cloud, konfiguracja.", "info", update_status)
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

    log_status("Transkrypcja audio w toku...", "info", update_status)
    try:
        response = client.recognize(config=config, audio=audio)

        transcribed_text_before_formatting = ""
        for result in response.results:
            transcribed_text_before_formatting = result.alternatives[0].transcript

        # Proste formatowanie tekstu
        transcribed_text = text_formatting(transcribed_text_before_formatting)

        log_status("Skutecznie dokonano transkrypcji audio.", "success", update_status)
        print("Przetranskrybowany tekst:\n", transcribed_text)
    except Exception as err:
        log_status(f"Wystąpił problem w czasie transkrypcji audio: {err}", "error", update_status)
        return filename, -1

    return filename, transcribed_text

def text_formatting(text):
    """ Formatowanie tekstu by każda linijka tekstu zajmowała maksymalnie 30 słów"""
    i = 0
    result = ""
    for word in text.split(" "):
        i += 1
        if i % 30 == 0:
            result += f"{word}\n"
        else:
            result += f"{word} "
    return result

def save_text_to_txt(filename, transcribed_text, update_status):
    """ Zapis przetranskrybowanego tekstu do pliku .txt"""


    log_status("Przygotowanie do zapisu transkrypcji w pliku txt.", "info", update_status)
    output_dir = (os.path.dirname(__file__) + "/txt").replace("\\", "/")
    os.makedirs(output_dir, exist_ok=True)  # Tworzenie folderu, jeśli nie istnieje

    txt_path = (output_dir + f"/{filename}.txt").replace("\\", "/")
    log.debug(f"Miejsce zapisu pliku txt: {txt_path}", "info", update_status )

    log_status("Zapis do pliku txt w toku...", "info", update_status)
    try:
        with open(txt_path, 'w', encoding='utf-8') as file:
            file.write(transcribed_text, )
            log_status("Dokonano zapisu tekstu do pliku txt", "success", update_status)
    except Exception as err:
        log_status(f"Wystąpił problem w czasie zapisu do pliku txt: {err}", "error", update_status)


# TODO(altGreG): Przeprowadzić testy


# Uwaga: Ścieżki i nazwy plików trzeba dostosować pod siebie w czasie testów na własnej maszynie
def audio_extraction_test():
    s = r"D:\Studia\InzynieriaOprogramowania\kreator-notatek-ze-spotkan\nagrania\test.mkv"
    update_status = "placeholder"
    extract_audio_from_video(s, update_status)

def audio_transcribe_whisper_test():
    s = r"D:\Studia\InzynieriaOprogramowania\kreator-notatek-ze-spotkan\nagrania\test.mp3"
    update_status = "placeholder"
    return transcribe_with_whisper_offline(s, update_status)

def audio_transcribe_gc_test():
    s = r"D:\Studia\InzynieriaOprogramowania\kreator-notatek-ze-spotkan\nagrania\test.mp3"
    update_status = "placeholder"
    return transcribe_with_gcloud(s, update_status)

# Uwaga: Wywołania funkcji testujących oprogramowanie
audio_extraction_test()
# filename, transcribed_text = audio_transcribe_whisper_test()
filename, transcribed_text = audio_transcribe_gc_test()

if transcribed_text != -1:
    update_status = "placeholder"
    save_text_to_txt(filename, transcribed_text, update_status)
else:
    log.critical("Nie udało się wykonać transkrypcji audio. Nie można zapisać transkrypcji do pliku txt.")