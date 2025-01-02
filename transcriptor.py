import platform
import subprocess
import os

import whisper
from whisper.utils import get_writer
import torch

import speech_recognition as sr

import io
from google.oauth2 import service_account
from google.cloud import speech

def extract_audio_from_video(video_file_path):
    """Ekstrakcja audio z wideo z wykorzystaniem `ffmpeg`"""

    # Sprawdzenie platformy, definicja zmiennej dla kodu z procesu ffmpeg
    system_name = platform.system()
    extracting_process = -1

    # Pozyskanie nazwy pliku wideo
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
            extracting_process = subprocess.call(["ffmpeg", "-y", "-i", video_file_path, "-t", "00:01:00.0", f"{filename_and_path}.{audio_ext}"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.STDOUT)
        except Exception as err:
            print("Wystąpił problem: ", err)
            return -1
    elif system_name == "Linux":
        try:
            extracting_process = subprocess.call(["ffmpeg", "-y", "-i", video_file_path, f"{filename}.{audio_ext}"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.STDOUT)
        except Exception as err:
            print("Wystąpił problem: ", err)
            return -1
    # Aktualizacja statusu aplikacji po ekstrakcji
    # print(extracting_process)
    if extracting_process != 0:
        # update_status("Błąd w czasie ekstrakcji audio z wideo.")
        print("Błąd w czasie ekstrakcji audio z wideo.")
    else:
        # update_status("Sukces. Dokonano ekstrakcji audio z wideo.")
        print("Skutecznie dokonano ekstrakcji audio z wideo.")

def transcribe_with_whisper_offline(audio_file_path):
    """Transkrypcja audio offline z wykorzystaniem modelu Whisper od OpenAi"""

    # Pozyskanie nazwy transkrybowanego pliku
    filename_and_path, ext = os.path.splitext(audio_file_path)
    filename = (filename_and_path.replace("\\", "/")).split("/")[-1]
    print("Filename: ", filename, "    Ext: ", ext)

    # Wybór jednostki obliczeniowej, procesor lub karta graficzna
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        torch.cuda.init()

    print(f"Urządzenie na którym zostanie wykonana transkrypcja: {device}")

    # Wybór modelu, do transkrypcji
    # tiny, base, small, medium, large, turbo
    model = whisper.load_model("medium").to(device)

    # przygotowanie ścieżki skąd pobieramy audio, załadowanie pliku audio
    audio_file_path = audio_file_path.replace("\\", "/")
    audio = whisper.load_audio(audio_file_path)

    # Transkrypcja audio, wyświetlenie rezultatu w konsoli
    with torch.cuda.device(device):
        # whisper.DecodingOptions(language="pl", fp16=False, task="transcribe")
        result = model.transcribe(audio=audio, word_timestamps=True)
    # print(result)

    # word_options = {
    #     "highlight_words": True,
    #     "max_line_count": 50,
    #     "max_line_width": 3
    # }
    #
    # srt_writer = get_writer("srt", "./")
    # srt_writer(result, audio, word_options)

    print(result["text"])

    return filename, result["text"]


def transcribe_with_gcloud(audio_file_path):
    # Utworzenie obiektu do autoryzacji dostępu do usług Google Cloud
    # Uwaga: Użytkownik sam musi pozyskać plik JSON do autoryzacji w Google Cloud API
    client_file = './sa_gc.json'
    credentials = service_account.Credentials.from_service_account_file(client_file)
    client = speech.SpeechClient(credentials=credentials)

    # Załadowanie pliku audio
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

    # Wyświetlenie rezultatu w konsoli
    response = client.recognize(config=config, audio=audio)
    for result in response.results:
        print(result.alternatives[0].transcript)

# Uwaga: Ścieżki i nazwy plików trzeba dostosować pod siebie w czasie testów na własnej maszynie
def audio_extraction_test():
    s = r"D:\Studia\InzynieriaOprogramowania\kreator-notatek-ze-spotkan\nagrania\test.mkv"
    extract_audio_from_video(s)

def audio_transcribe_whisper_test():
    return transcribe_with_whisper_offline(r"D:\Studia\InzynieriaOprogramowania\kreator-notatek-ze-spotkan\nagrania\test.mp3")

def audio_transcribe_gc_test():
    transcribe_with_gcloud(r"D:\Studia\InzynieriaOprogramowania\kreator-notatek-ze-spotkan\nagrania\test.mp3")

def transcribe_with_sr(audio_file_path):
    """Transkrypcja audio z wykorzystaniem biblioteki Speech Recognition i wybranego serwisu do transkrypcji"""

    # Stworzenie obiektu Speech Recognizera, załadowanie pliku audio
    r = sr.Recognizer()
    audio_file_path = audio_file_path.replace("\\", "/")
    audio_file = sr.AudioFile(audio_file_path)

    # Transkrypcja audio
    text = ""
    with audio_file as source:
        audio = r.record(source, duration=30)
        # TODO(altGreG): Pozyskać klucz API do wybranego serwisu. Wybrać serwis.
        # text = r.recognize_google_cloud(audio)
    print(text)

def save_text_to_txt(filename, transcribed_text):
    """ Zapis przetranskrybowanego tekstu do pliku .txt"""

    # Ścieżka do folderu z plikami txt
    output_dir = (os.path.dirname(__file__) + "/txt").replace("\\", "/")

    print(output_dir)

    # Tworzenie pliku na transkrypcje, jeśli nie istnieje
    os.makedirs(output_dir, exist_ok=True)  # Tworzenie folderu, jeśli nie istnieje

    # Utworzenie ścieżki pliku do zapisu
    txt_path = (output_dir + f"/{filename}.txt").replace("\\", "/")
    print("Miejsce zapisu pliku txt:", txt_path )

    # Zapis tekstu do pliku txt
    with open(txt_path, 'w', encoding='utf-8') as file:
        file.write(transcribed_text, )

# TODO(altGreG): Przetestować, czy funkcjonalności działają teź na innej maszynie niż komputer autora kodu.
# audio_extraction_test()
# filename, transcribed_text = audio_transcribe_whisper_test()
# save_text_to_txt(filename, transcribed_text)
# audio_transcribe_gc_test()