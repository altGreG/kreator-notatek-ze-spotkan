import platform
import subprocess
import os
import whisper
import torch
import io
from google.oauth2 import service_account
from google.cloud import speech

def extract_audio_from_video(video_file_path):
    """Ekstrakcja audio z wideo z wykorzystaniem `ffmpeg`"""

    # Sprawdzenie platformy, definicja zmiennej dla kodu z procesu ffmpeg
    system_name = platform.system()
    extracting_process = -1

    # Wycięcie rozszerzenia z ścieżki pliku
    filename_and_path, ext = os.path.splitext(video_file_path)

    # Rozszerzenie dla pliku audio
    audio_ext = "mp3"

    # Ekstracja ścieżki audio z pliku i zapis do mp3
    # update_status("Ekstrakcja audio w toku...")
    # TODO(altGreG): Po testach, usunąć opcję -t z komendy
    print(f"Rozpoczęto ekstrakcję audio z video. ({system_name})")
    print(f"Scieżka do pliku video: {video_file_path}")
    if system_name == "Windows":
        try:
            extracting_process = subprocess.call(["ffmpeg", "-y", "-i", video_file_path, "-t", "00:00:50.0", f"{filename_and_path}.{audio_ext}"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.STDOUT)
        except Exception as err:
            # update_status(f"Wystąpił problem w czasie ekstrakcji: {err}")
            print("Wystąpił problem w czasie ekstrakcji:", err)
            return -1
    elif system_name == "Linux":
        try:
            extracting_process = subprocess.call(["ffmpeg", "-y", "-i", video_file_path, f"{filename_and_path}.{audio_ext}"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.STDOUT)
        except Exception as err:
            # update_status(f"Wystąpił problem w czasie ekstrakcji: {err}")
            print("Wystąpił problem w czasie ekstrakcji:", err)
            return -1
    # Aktualizacja statusu aplikacji po ekstrakcji
    if extracting_process != 0:
        # update_status(f"Błąd w czasie ekstrakcji audio z wideo. Kod błędu: {extracting_process}")
        print(f"Błąd w czasie ekstrakcji audio z wideo. Kod błędu: {extracting_process}")
    else:
        # update_status("Sukces. Dokonano ekstrakcji audio z wideo.")
        print("Skutecznie dokonano ekstrakcji audio z wideo.")
        print("Ścieżka do pliku audio:", f"{filename_and_path}.{audio_ext}")

def transcribe_with_whisper_offline(audio_file_path):
    """Transkrypcja audio offline z wykorzystaniem modelu Whisper od OpenAi"""

    # Przygotowanie pliku audio i środowiska do transkrypcji
    # update_status("Przygotowanie do transkrypcji audio.")
    filename_and_path, ext = os.path.splitext(audio_file_path)
    filename = (filename_and_path.replace("\\", "/")).split("/")[-1]
    print("Filename: ", filename, "| Ext: ", ext)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        torch.cuda.init()
    # update_status(f"Urządzenie na którym zostanie wykonana transkrypcja: {device}")
    print(f"Urządzenie na którym zostanie wykonana transkrypcja: {device}")

    # tiny, base, small, medium, large, turbo
    model = whisper.load_model("medium").to(device)

    # update_status(f"Wczytanie pliku audio: {filename}{ext}")
    audio_file_path = audio_file_path.replace("\\", "/")
    audio = whisper.load_audio(audio_file_path)

    # Transkrypcja audio, wyświetlenie rezultatu w konsoli
    # update_status("Transkrypcja audio w toku...")
    transcribed_text = ""
    try:
        with torch.cuda.device(device):
            result = model.transcribe(audio=audio, language="pl", word_timestamps=True)
        i = 1
        for word in result["text"].split(" "):
            i += 1
            if i%30 == 0:
                transcribed_text += f"{word}\n"
            else:
                transcribed_text += f"{word} "
            # update_status("Skutecznie dokonano transkrypcji audio.")
            print("Skutecznie dokonano transkrypcji audio.")
        print(transcribed_text)
    except Exception as err:
        # update_status(f"Wystąpił problem w czasie transkrypcji audio: {err}")
        print("Wystąpił problem w czasie transkrypcji audio:", err)

    return filename, transcribed_text

# TODO(altGreG): Na razie program może obsłużyć pliki audio o długości do 1 minuty, do poprawy
def transcribe_with_gcloud(audio_file_path):
    """Transkrypcja audio z wykorzystaniem api do usługi Speech to Text na Google Cloud"""

    # Przygotowanie do transkrypcji audio
    # update_status("Przygotowanie do transkrypcji audio.")
    filename_and_path, ext = os.path.splitext(audio_file_path)
    filename = (filename_and_path.replace("\\", "/")).split("/")[-1]
    print("Filename: ", filename, "| Ext: ", ext)

    # Utworzenie obiektu do autoryzacji dostępu do usług Google Cloud
    # Uwaga: Użytkownik sam musi pozyskać plik JSON do autoryzacji w Google Cloud API
    # update_status("Załadowanie pliku autoryzacyjnego do usług Google Cloud")
    client_file = './sa_gc.json'
    credentials = service_account.Credentials.from_service_account_file(client_file)
    client = speech.SpeechClient(credentials=credentials)

    # Załadowanie pliku audio
    # update_status("Przygotowanie pliku audio, konfiguracja.")
    audio_file_path = audio_file_path.replace("\\", "/")
    with io.open(audio_file_path, mode="rb") as audio_file:
        content = audio_file.read()
        audio = speech.RecognitionAudio(content=content)

    # Konfiguracja narzędzi do transkrypcji
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=44100,
        language_code="pl-pl",
        enable_automatic_punctuation=True,
    )

    # update_status("Transkrypcja audio w toku...")
    transcribed_text = ""
    try:
        response = client.recognize(config=config, audio=audio)

        transcribed_text_before_formatting = ""
        for result in response.results:
            transcribed_text_before_formatting = result.alternatives[0].transcript
            print(transcribed_text_before_formatting)

        i = 1
        for word in transcribed_text_before_formatting.split(" "):
            i += 1
            if i%30 == 0:
                transcribed_text += f"{word}\n"
            else:
                transcribed_text += f"{word} "
        # update_status("Skutecznie dokonano transkrypcji audio.")
        print("Skutecznie dokonano transkrypcji audio.")
        print(transcribed_text)
    except Exception as err:
        # update_status(f"Wystąpił problem w czasie transkrypcji audio: {err}")
        print("Wystąpił problem w czasie transkrypcji audio:", err)

    return filename, transcribed_text

def save_text_to_txt(filename, transcribed_text):
    """ Zapis przetranskrybowanego tekstu do pliku .txt"""

    # update_status("Przygotowanie do zapisu transkrypcji w pliku txt.")

    # Ścieżka do folderu z plikami txt
    output_dir = (os.path.dirname(__file__) + "/txt").replace("\\", "/")

    # Tworzenie pliku na transkrypcje, jeśli nie istnieje
    os.makedirs(output_dir, exist_ok=True)  # Tworzenie folderu, jeśli nie istnieje

    # Utworzenie ścieżki pliku do zapisu
    txt_path = (output_dir + f"/{filename}.txt").replace("\\", "/")
    print("Miejsce zapisu pliku txt:", txt_path )

    # Zapis tekstu do pliku txt
    # update_status("Zapis do pliku txt w toku...")
    try:
        with open(txt_path, 'w', encoding='utf-8') as file:
            file.write(transcribed_text, )
            # update_status("Dokonano zapisu tekstu do pliku txt")
    except Exception as err:
        # update_status(f"Wystąpił problem w czasie zapisu do pliku txt: {err}")
        print("Wystąpił problem w czasie zapisu do pliku txt:", err)

# Uwaga: Ścieżki i nazwy plików trzeba dostosować pod siebie w czasie testów na własnej maszynie
def audio_extraction_test():
    s = r"D:\Studia\InzynieriaOprogramowania\kreator-notatek-ze-spotkan\nagrania\test.mkv"
    extract_audio_from_video(s)

def audio_transcribe_whisper_test():
    return transcribe_with_whisper_offline(r"D:\Studia\InzynieriaOprogramowania\kreator-notatek-ze-spotkan\nagrania\test.mp3")

def audio_transcribe_gc_test():
    return transcribe_with_gcloud(r"D:\Studia\InzynieriaOprogramowania\kreator-notatek-ze-spotkan\nagrania\test.mp3")

# TODO(altGreG): Przetestować, czy funkcjonalności działają teź na innej maszynie niż komputer autora kodu.
# audio_extraction_test()
# filename, transcribed_text = audio_transcribe_whisper_test()
# filename, transcribed_text = audio_transcribe_gc_test()
# save_text_to_txt(filename, transcribed_text)
