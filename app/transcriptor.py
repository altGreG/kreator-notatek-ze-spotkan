# app/transcriptor.py

"""Moduł transkrypcji audio

Skrypt umożliwia transkrypcję plików audio do formatu tekstowego oraz ekstrakcję ścieżki audio z plików wideo.

Wymagane zależności

Aby uruchomić skrypt, należy zainstalować następujące pakiety w środowisku Python:

    - openai-whisper: Model do transkrypcji mowy
    - torch, torchvision, torchaudio: Narzędzia do przetwarzania danych audio
    - loguru: Rozbudowany system logowania
    - setuptools-rust: Wsparcie dla rozszerzeń w Rust

Do prawidłowego działania aplikacji należy zaimportować:

    - log_status z modułu app.utilities.loger, służącą do logowania komunikatów statusowych.
    - save_text_to_txt z modułu app.utilities.saving

Skrypt może być używany jako moduł i zawiera następujące funkcje:

    * extract_audio_from_video -  ekstrakcja ścieżki audio z plików wideo przy użyciu narzędzia ffmpeg.
    * transcribe_with_whisper_offline -  transkrypcja plików audio lokalnie przy użyciu modelu Whisper.
    * transcribe_audio_from_folder - automatyczna transkrypcja wszystkich plików audio z wybranego folderu.

Każda funkcja posiada odpowiednie mechanizmy obsługi błędów, logowania oraz komunikatów dla użytkownika.
"""

import platform
import subprocess
import os
import glob
import whisper
import torch
import time
import warnings
from loguru import logger as log
from app.utilities.logger import log_status
from app.utilities.saving import save_text_to_txt

extracting_process = -1
warnings.filterwarnings("ignore", module="whisper")

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


    filename_and_path, ext = os.path.splitext(audio_file_path)
    filename = (filename_and_path.replace("\\", "/")).split("/")[-1]
    audio_file_path = audio_file_path.replace("\\", "/")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        torch.cuda.init()
    # log.debug(f"Urządzenie na którym zostanie wykonana transkrypcja: {device}")

    # tiny, base, small, medium, large, turbo
    model = whisper.load_model("medium").to(device)
    try:
        audio = whisper.load_audio(audio_file_path)
    except Exception as err:
        log_status(f"Błąd w czasie wczytywania pliku audio. Sprawdź poprawność ścieżki do pliku.")
        log.error(f"Błąd: \n {err}")
        return filename, None
    log.debug(f"Transkrypcja pliku audio: {filename}.mp3")
    log_status("Transkrypcja audio w toku...", "info", update_status)
    try:
        if device == "cuda":
            with torch.cuda.device(device):
                result = model.transcribe(audio=audio, language="pl")
        else:
            result = model.transcribe(audio=audio, language="pl")

        # Proste formatowanie tekstu
        transcribed_text = result["text"]

        log_status(f"Skutecznie dokonano transkrypcji audio: {filename}.mp3", "success", update_status)
        # print("Przetranskrybowany tekst:\n", transcribed_text)
    except Exception as err:
        log_status(f"Wystąpił problem w czasie transkrypcji audio: {err}", "error", update_status)
        return filename, None

    return filename, transcribed_text

def transcribe_audio_from_folder(folder_path: str, update_status: any, app, transription_false_update) -> str:
    """
    Uruchamia transkrypcję przy pomocy modelu Whisper dla każdego pliku audio, wedlug daty
    utworzenia z timestampa.

    Funkcja szuka nowych plików do transkrypcji we wskazanym folderze. Robi to tak długo aż nie natrafi
    na plik o nazwie koniec.txt. Wtedy wykonuje jeszcze tylko transkrypcję audio, które jeszcze nie
    wykonał a następnie kończy proces transkrypcji. A wynik zapisuje w pliku txt o nazwie jak folder.

    Args:
        folder_path: ścieżka do folderu z plikami audio
        update_status: metoda aplikacji gui (aktualizacja wiadomości statusu)
        app: Główna instancja Tkinter.
        transription_false_update: metoda gui, odblokowuje przycisk play

    Returns:
        Zwraca None w przypdku błędu lub ścieżkę do pliku txt z transkrypcją
    """
    count_of_transcribed = 0
    is_end = None
    transcribed_files = []

    folder_path_pattern = f"{folder_path}/*.mp3"
    end_path = f"{folder_path}/koniec.txt"

    base_path, timestamp = (folder_path.replace("\\", "/")).rsplit("/audio-", 1)
    transcription_folder = base_path + "/" + f"txt-{timestamp}"
    log.debug(f"Txt folder path: {transcription_folder}")

    log.debug("Rozpoczęto transkrypcję plików audio z folderu")

    while is_end is None:
        # TODO(altGreG): Dodać sortowanie po dacie utworzenia lub timestampach
        filepaths = glob.glob(folder_path_pattern)
        is_end = glob.glob(end_path)
        if (is_end) == []:
            is_end = None
        filepaths.sort()

        # print(f"Paths for audios to transcribe: ")
        # for path in filepaths:
        #     if path not in transcribed_files:
        #         print(f" - {path}")

        for filepath in filepaths:
            if filepath not in transcribed_files:
                filename, transcribed_text = transcribe_with_whisper_offline(filepath, update_status)
                transcribed_files.append(filepath)
                count_of_transcribed += 1

                filename_and_path, ext = os.path.splitext(filepath)
                filename = (filename_and_path.replace("\\", "/")).split("/")[-1]

                save_text_to_txt(filename, transcribed_text,update_status,transcription_folder)
                log.debug(f"Liczba przetranskrybowanych plików: {count_of_transcribed}")

            # else:
                # log.warning("Already transcribed")

        time.sleep(2.5)

    log.info("Dokonano transkrypcji wszystkich plików audio.")
    app.after(0, lambda: transription_false_update())

