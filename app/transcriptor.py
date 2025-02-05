# app/transcriptor.py

"""Moduł transkrypcji audio

Skrypt umożliwia transkrypcję plików audio do formatu tekstowego.

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

    * transcribe_with_whisper_offline -  transkrypcja plików audio lokalnie przy użyciu modelu Whisper.
    * transcribe_audio_from_folder - automatyczna transkrypcja wszystkich plików audio z wybranego folderu.

Każda funkcja posiada odpowiednie mechanizmy obsługi błędów, logowania oraz komunikatów dla użytkownika.
"""

import os
import glob
import tkinter
import whisper
import torch
import time
import warnings
from typing import Callable, Optional
from loguru import logger as log
from app.utilities.logger import log_status
from app.utilities.saving import save_text_to_txt

extracting_process = -1
warnings.filterwarnings("ignore", module="whisper")

def transcribe_with_whisper_offline(audio_file_path: str, update_status: Callable[[str], None]) -> tuple[str, str | None]:
    """
    Transkrybuje plik audio offline z wykorzystaniem modelu Whisper od OpenAI.

    Args:
        audio_file_path:
            Ścieżka do pliku z audio.
        update_status:
            Funkcja aktualizująca wiadomości statusu w aplikacji GUI.

    Returns:
        nazwa pliku audio, którego dotyczy transkrypcja i przetranskrybowany tekst | nazwa transkrybowanego pliku i None w razie błędu
    """


    filename_and_path, ext = os.path.splitext(audio_file_path)
    filename = (filename_and_path.replace("\\", "/")).split("/")[-1]
    audio_file_path = audio_file_path.replace("\\", "/")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        torch.cuda.init()

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

        # Tekst z transkrypcji
        transcribed_text = result["text"]
        log.success(f"Skutecznie dokonano transkrypcji audio: {filename}.mp3")
    except Exception as err:
        log_status(f"Wystąpił problem w czasie transkrypcji!", "error", update_status)
        log.error(f"Błąd: {err}", "error", update_status)
        return filename, None

    return filename, transcribed_text

def transcribe_audio_from_folder(folder_path: str, update_status: Callable[[str], None], app: tkinter.Tk, transription_false_update: Callable[[None], None]) -> Optional[str]:
    """
    Uruchamia transkrypcję audio z wykorzystaniem modelu Whisper dla każdego pliku audio we wskazanym folderze.

    Funkcja szuka nowych plików do transkrypcji we wskazanym folderze. Robi to tak długo aż nie natrafi
    na plik o nazwie koniec.txt. Wtedy wykonuje jeszcze tylko transkrypcję audio, które jeszcze nie
    wykonał, a następnie kończy proces transkrypcji.

    Args:
        folder_path:
            Ścieżka do folderu z plikami audio.
        update_status:
            Funkcja aktualizująca wiadomości statusu w interfejsie GUI.
        app:
            Główna instancja Tkinter.
        transription_false_update:
            Funkcja GUI odblokowująca przycisk "play" po zakończeniu transkrypcji.

    Returns:
        Optional[str]:
            Ścieżka do pliku tekstowego z wynikami transkrypcji lub None w przypadku błędu.
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
        filepaths = glob.glob(folder_path_pattern)
        is_end = glob.glob(end_path)
        if (is_end) == []:
            is_end = None

        filepaths.sort()
        for filepath in filepaths:
            if filepath not in transcribed_files:
                filename, transcribed_text = transcribe_with_whisper_offline(filepath, update_status)
                transcribed_files.append(filepath)
                count_of_transcribed += 1

                filename_and_path, ext = os.path.splitext(filepath)
                filename = (filename_and_path.replace("\\", "/")).split("/")[-1]

                # zapis tranksrypcji do odpowiedniego pliku .txt
                save_text_to_txt(filename, transcribed_text,update_status,transcription_folder)
                log.debug(f"Liczba przetranskrybowanych plików: {count_of_transcribed}")
                log_status(f"Czas nagrywania: {(count_of_transcribed*30)/60} min")

        time.sleep(0.1)

    log.info("Dokonano transkrypcji wszystkich plików audio.")
    app.after(0, lambda: transription_false_update())

