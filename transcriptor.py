import platform
import subprocess
import os

import whisper
import torch

import speech_recognition as sr

def extract_audio_from_video(video_file):
    """Ekstrakcja audio z wideo z wykorzystaniem `ffmpeg`"""
    # Sprawdzenie platformy, definicja zmiennej dla kodu z procesu ffmpeg
    system_name = platform.system()
    extracting_process = -1

    # Pozyskanie nazwy pliku wideo
    filename, ext = os.path.splitext(video_file)

    # Rozszerzenie dla pliku audio
    audio_ext = "wav"

    # Ekstracja ścieżki audio z pliku i zapis do mp3
    # update_status("Ekstrakcja audio w toku...")
    if system_name == "Windows":
        extracting_process = subprocess.call(["./software/ffmpeg", "-y", "-i", video_file, f"{filename}.{audio_ext}"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)
    elif system_name == "Linux":
        extracting_process = subprocess.call(["ffmpeg", "-y", "-i", video_file, f"{filename}.mp3"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)

    # Aktualizacja statusu aplikacji po ekstrakcji
    # print(extracting_process)
    if extracting_process != 0:
        # update_status("Błąd w czasie ekstrakcji audio z wideo.")
        print("Błąd w czasie ekstrakcji audio z wideo.")
    else:
        # update_status("Sukces. Dokonano ekstrakcji audio z wideo.")
        print("Skutecznie dokonano ekstrakcji audio z wideo.")

# s = "./nagrania/test.mkv"
# extract_audio_from_video(s)

def transcribe_with_whisper_offline(audio_file):
    # Wybór jednostki obliczeniowej, procesor lub karta graficzna
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Wybór modelu, do transkrypcji
    # tiny, base, small, medium, large, turbo
    model = whisper.load_model("tiny").to(device)

    # przygotowanie ścieżki skąd pobieramy audio, załadowanie pliku audio
    audio_path = os.path.join(os.path.dirname(__file__), f"nagrania/{audio_file}").replace("\\", "/")
    audio = whisper.load_audio(audio_path)
    # audio = whisper.pad_or_trim(audio)

    # Transkrypcja audio, wyświetlenie rezultatu w konsoli
    result = model.transcribe(audio=audio, language="pl")
    print(result["text"])

# transcribe_with_whisper_offline("test.mp3")

def transcribe_with_sr(audio_file):
    r = sr.Recognizer()

    audio_path = os.path.join(os.path.dirname(__file__), f"nagrania/{audio_file}").replace("\\", "/")
    audio_file = sr.AudioFile(audio_path)
    with audio_file as source:
        audio = r.record(source, duration=30)
        # TODO(altGreG): Get api key to selected transcribe service
        # text = r.recognize_google_cloud(audio)
    # print(text)

# transcribe_with_whisper_offline("test.wav")
# transcribe_with_sr("test.wav")
