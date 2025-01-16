# app/transcriptor.py

"""Narzędzia transkrypcji audio

Ten skrypt pozwala użytkownikowi na transkrypcję plików audio do plików tekstowych.

Skrypt wymaga aby w środowisku Pythona w którym uruchamiasz ten skrypt zostały
zainstalowane następujące zależności:

    - `openai-whisper`
    - `torch`
    - `torchvision`
    - `torchaudio`
    - `google-cloud-speech`
    - `protobuf`
    - `loguru`
    - setuptools-rust

Do poprawnego działania skryptu należy zaimportować następujące funkcje:

    - `log_status` z modułu app.loger

Ten plik może zostać zaimportowany również jako moduł i zawiera następujące funkcje:

    * extract_audio_from_video - ekstrakcja audio z video
    * transcribe_with_whisper_offline - transkrypcja audio z modelem Whisper na maszynie użytkownika
    * transcribe_with_gcloud - transkrypcja audio w chmurze Google Cloud i usługu Speech To Text
    * text_formatting - formatowanie tekstu, by linijka zawierała maksymalnie 30 słów
"""


import platform
import subprocess
import os
import whisper
import torch
import io
from google.oauth2 import service_account
from google.cloud import speech
from loguru import logger as log
from app.logger import log_status

extracting_process = -1

def extract_audio_from_video(video_file_path: str, update_status: any) -> str | None:
    """
    Ekstrakcja audio z wideo z wykorzystaniem `ffmpeg`

    Args:
        video_file_path: ścieżka do pliku z video
        update_status: metoda aplikacji gui (aktualizacja wiadomości statusu)

    Returns:
        ścieżka do pliku audio | None w razie błędu
    """
    global extracting_process

    system_name = platform.system()
    filename = ((video_file_path.replace("\\", "/")).split("/")[-1]).split(".")[0]
    output_dir = (video_file_path.replace("\\", "/")).rsplit("/", 1)[0] + "/audio"
    os.makedirs(output_dir, exist_ok=True)  # Tworzenie folderu, jeśli nie istnieje
    filename_and_path = output_dir + "/" + filename
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
            return None
    elif system_name == "Linux":
        try:
            extracting_process = subprocess.call(["ffmpeg", "-y", "-i", video_file_path, f"{filename_and_path}.{audio_ext}"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.STDOUT)
        except Exception as err:
            log_status(f"Wystąpił problem w czasie ekstrakcji audio z video: {err}", "error", update_status)
            return None

    if extracting_process != 0:
        log_status(f"Błąd w czasie ekstrakcji audio z wideo (ffmpeg).\nKod błędu: {extracting_process}", "error", update_status)
        return None
    else:
        log_status("Sukces. Dokonano ekstrakcji audio z wideo.", "success", update_status)
        log.debug(f"Ścieżka do pliku audio: {filename_and_path}.{audio_ext}")
        return f"{filename_and_path}.{audio_ext}"

def transcribe_with_whisper_offline(audio_file_path: str, update_status: any) -> tuple[str, str | None]:
    """
    Transkrypcja audio offline z wykorzystaniem modelu Whisper od OpenAI

    Args:
        audio_file_path: ścieżka do pliku z audio
        update_status: metoda aplikacji gui (aktualizacja wiadomości statusu)

    Returns:
        nazwa pliku audio, którego dotyczy transkrypcja i przetranskrybowany tekst | nazwa pliku i None w razie błędu
    """


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
    try:
        audio = whisper.load_audio(audio_file_path)
        log.debug("Wczytano plik audio do modelu.")
    except Exception as err:
        log_status(f"Błąd w czasie wczytywania pliku audio. Sprawdź poprawność ścieżki do pliku.")
        log.error(f"Błąd: \n {err}")
        return filename, None

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
        return filename, None

    return filename, transcribed_text

# TODO(altGreG): Na razie program może obsłużyć pliki audio o długości do 1 minuty, do poprawy
def transcribe_with_gcloud(audio_file_path: str, update_status: any) -> tuple[str, str | None]:
    """
    Transkrypcja audio z wykorzystaniem API do usługi Speech to Text na Google Cloud

    Args:
        audio_file_path: ścieżka do pliku z audio
        update_status: metoda aplikacji gui (aktualizacja wiadomości statusu)

    Returns:
        nazwa pliku audio, którego dotyczy transkrypcja i przetranskrybowany tekst | nazwa pliku i None w razie błędu
    """


    log_status("Przygotowanie do transkrypcji audio.", "info", update_status)

    filename_and_path, ext = os.path.splitext(audio_file_path)
    filename = (filename_and_path.replace("\\", "/")).split("/")[-1]
    audio_file_path = audio_file_path.replace("\\", "/")

    log.debug(f"Filename: {filename}  |  Ext: {ext}")

    """
    Utworzenie obiektu do autoryzacji dostępu do usług Google Cloud
    Uwaga: Użytkownik sam musi pozyskać plik JSON do autoryzacji w Google Cloud API
    """
    try:
        client_file = '../sa_gc.json'
        credentials = service_account.Credentials.from_service_account_file(client_file)
        client = speech.SpeechClient(credentials=credentials)
        log_status("Załadowanie pliku autoryzacyjnego do usług Google Cloud, konfiguracja.", "info", update_status)
    except Exception as err:
        log_status("Brak pliku autoryzacyjnego do usług Google Cloud, brak dostępu.", "error", update_status)
        log.error(f"Błąd: {err}")
        return filename, None

    try:
        with io.open(audio_file_path, mode="rb") as audio_file:
            content = audio_file.read()
            audio = speech.RecognitionAudio(content=content)
        log.debug("Wczytano plik audio.")
    except Exception as err:
        log_status(f"Błąd w czasie wczytywania pliku audio.", "error", update_status)
        log.error(f"Błąd: {err}")
        return filename, None

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

        log_status("Sukces. Dokonano transkrypcji audio.", "success", update_status)
        print("Przetranskrybowany tekst:\n", transcribed_text)
    except Exception as err:
        log_status(f"Wystąpił problem w czasie transkrypcji audio: {err}", "error", update_status)
        return filename, None

    return filename, transcribed_text

def text_formatting(text: str) -> str:
    """
    Formatowanie tekstu

    Transformacja tekstu w taki sposób, by każda linijka tekstu zajmowała maksymalnie 30 słów.

    Args:
        text: tekst do sformatowania

    Returns:
        sformatowany tekst
    """
    i = 1
    result = ""
    for word in text.split(" "):
        i += 1
        if i % 30 == 0:
            result += f"{word}\n"
        else:
            result += f"{word} "
    return result
