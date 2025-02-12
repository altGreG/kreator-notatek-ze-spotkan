# app/recorder_audio.py

"""Moduł nagrywania dźwięku

Skrypt umożliwia nagrywanie dźwięku z wybranego urządzenia audio, podział nagrania na fragmenty oraz zapis plików audio w formacie MP3.

Wymagane zależności

Aby uruchomić skrypt, należy zainstalować następujące pakiety w środowisku Python:

    - pydub: Biblioteka do manipulacji plikami audio
    - loguru: Rozbudowany system logowania

Do prawidłowego działania aplikacji należy zaimportować:

    - log_status z modułu app.utilities.logger, służącą do logowania komunikatów statusowych.

Skrypt może być używany jako moduł i zawiera następujące funkcje:

    * start_recording — rozpoczyna proces nagrywania dźwięku z wybranego urządzenia.
    * stop_recording — zatrzymuje nagrywanie audio
    * _save_audio_fragments — zapisuje fragmenty audio o określonej długości podczas aktywnego nagrywania.

Każda funkcja posiada odpowiednie mechanizmy obsługi błędów, logowania oraz komunikatów dla użytkownika.
"""

import platform
import subprocess
import os
import threading
from typing import Callable
from datetime import datetime
from pydub import AudioSegment
from io import BytesIO
from tkinter import messagebox
from loguru import logger as log
from app.utilities.logger import log_status

recording_process = None
recording_active = True
recording_directory = None


def start_recording(update_status: Callable[[str], None], selected_audio_device: str, recording_folder: str) -> None:
    """
    Funkcja rozpoczynająca nagrywanie dźwięku z wybranego urządzenia.

    Args:
        update_status:
            Funkcja aktualizująca wiadomości statusu w aplikacji GUI.
        selected_audio_device:
            Zmienna zawierająca nazwę urządzenia audio nagrywającego dźwięk
        recording_folder:
            Zmienna zawierająca ścieżkę do folderu w którym będzie zapisywane audio
    """
    global recording_process, recording_active, recording_directory

    recording_directory = recording_folder

    if not selected_audio_device:
        messagebox.showerror("Błąd", "Nie wybrano urządzenia audio. Skonfiguruj ustawienia.")
        log.warning("Nie wybrano urządzenia audio. Skonfiguruj ustawienia.")
        return

    if update_status:
        log_status("Nagrywanie dźwięku w toku...", "info", update_status)


    # Konfiguracja polecenia FFmpeg
    ffmpeg_command = [
        "ffmpeg",
        "-y",
        "-f", "dshow",
        "-i", f"audio={selected_audio_device}",
        "-f", "s16le",  # Surowy format PCM (16-bitowy)
        "-ar", "44100",  # Częstotliwość próbkowania
        "-ac", "2",  # Liczba kanałów audio
        "pipe:1"
    ]

    try:
        # Uruchomienie FFmpeg z wyjściem na stdout
        recording_process = subprocess.Popen(
            ffmpeg_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=False,  # Dane binarne
            shell=(platform.system() == "Windows")
        )
        recording_active = True

        # Uruchomienie wątku do zapisywania fragmentów
        threading.Thread(target=_save_audio_fragments, daemon=True).start()
        log.debug(f"Nagrywanie dźwięku rozpoczęte w katalogu: {recording_directory}")
    except Exception as e:
        if update_status:
            log_status(f"Błąd podczas rozpoczynania nagrywania dźwięku: {e}", "error", update_status)


def _save_audio_fragments() -> None:
    """
    Zapisuje fragmenty audio co 20 sekund bez zatrzymywania nagrywania.

    Działanie:
        - Odczytuje dane audio z procesu FFmpeg w czasie rzeczywistym.
        - Buforuje surowe dane audio.
        - Po osiągnięciu 20-sekundowego fragmentu zapisuje go jako plik MP3.
        - Przechowuje nieprzetworzone dane w buforze, aby zachować ciągłość nagrywania.

    Notes:
        - Fragmenty audio są zapisywane w katalogu `recording_directory` jako pliki MP3.
        - Nazwa każdego pliku to jego timestamp w formacie "HH-MM-SS.mp3".
        - Nagrywanie odbywa się w formacie MP3 o bitrate 192 kbps.
        - Jeśli `recording_active` zostanie ustawiona na `False`, nagrywanie zostanie zakończone.
    """

    global recording_process, recording_active, recording_directory

    buffer = BytesIO()
    fragment_duration = 20 * 1000  # 20 sekund w milisekundach

    try:
        while recording_active and recording_process.poll() is None:
            # Odczyt surowych danych audio z FFmpeg
            data = recording_process.stdout.read(4096)
            if not data:
                continue

            buffer.write(data)

            # Jeśli bufor zawiera dane o długości >= 10 sekund, zapisz fragment
            audio_segment = AudioSegment.from_raw(
                BytesIO(buffer.getvalue()), sample_width=2, frame_rate=44100, channels=2
            )

            if len(audio_segment) >= fragment_duration:
                timestamp = datetime.now().strftime("%H-%M-%S")
                output_file = os.path.join(recording_directory, f"{timestamp}.mp3")

                # Zapisz fragment
                audio_segment[:fragment_duration].export(output_file, format="mp3", bitrate="192k")
                log.debug(f"Zapisano fragment audio: {output_file.replace("\\", "/").rsplit("/",1)[1]}")

                # Usuń zapisane dane z bufora
                buffer = BytesIO(audio_segment[fragment_duration:].raw_data)
    except Exception as e:
        log.error(f"Błąd podczas zapisywania fragmentów audio: {e}")


def stop_recording(update_status: Callable[[str], None]) -> None:
    """
    Zatrzymuje proces nagrywania dźwięku i zapisuje informację o zakończeniu.

    Działanie:
        - Ustawia flagę `recording_active` na `False`, co zatrzymuje nagrywanie fragmentów.
        - Terminatuje proces FFmpeg odpowiedzialny za nagrywanie.
        - Tworzy plik `koniec.txt` w katalogu nagrania, informując o zakończeniu nagrywania.
        - Aktualizuje status w GUI.

    Args:
        update_status:
            Funkcja aktualizująca wiadomości statusu w aplikacji GUI.

    Notes:
        - Jeśli `recording_directory` jest ustawione, plik `koniec.txt` zostaje utworzony w folderze nagrania.
        - Funkcja obsługuje błędy związane z zamykaniem procesu oraz tworzeniem pliku.
        - W przypadku błędów, logi zawierają informacje diagnostyczne.
    """

    global recording_active, recording_process, recording_directory

    if update_status:
        log_status("Kończenie nagrywania dźwięku...", "info", update_status)

    recording_active = False

    if recording_process:
        try:
            recording_process.terminate()
            recording_process.wait()
            log.debug("Nagrywanie zakończone.")
        except Exception as e:
            log.error(f"Błąd podczas zatrzymywania nagrywania: {e}")

    # Tworzenie pliku `koniec.txt`
    if recording_directory:
        try:
            with open(os.path.join(recording_directory, "koniec.txt"), "w") as f:
                f.write("Nagrywanie zakończone.")
            log.debug("Utworzono plik: koniec.txt")
        except Exception as e:
            log.error(f"Błąd podczas tworzenia pliku `koniec.txt`: {e}")

    if update_status:
        log_status("Nagrywanie zakończone. Pliki zostały zapisane.", "info", update_status)
