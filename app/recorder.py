# app/recorder.py

"""Narzędzia nagrywania audio i wideo z komputera

Ten skrypt pozwala użytkownikowi na nagrywanie audio i wideo z komputera przy
pomocy oprogramowania ffmpeg.

Skrypt wymaga aby w środowisku Pythona w którym uruchamiasz ten skrypt zostały
zainstalowane następujące zależności:

    - `loguru`

Do poprawnego działania skryptu należy zaimportować następujące funkcje:

    - `log_status` z modułu app.loger

W systemie musi być zainstalowane oprogramowanie `ffmpeg`, ścieżka do folderu z plikiem ffmpeg.exe
musi zostać ustawiona w zmiennych środowiskowych systemu (Windows) lub dodana do zmiennej PATH (Linux)

Ten plik może zostać zaimportowany również jako moduł i zawiera następujące funkcje:

    * start_recording - rozpoczyna nagrywanie audio i wideo
    * stop_recording - kończy nagrywanie, zapisuje plik mp4 w folderze nagrania
"""

import platform
import subprocess
import os
import signal
from datetime import datetime
from loguru import logger as log
from logger import log_status

recording_process = None  # Zmienna globalna do przechowywania procesu nagrywania

def start_recording(update_status: any) -> None:
    """
    Funkcja rozpoczynająca nagrywanie ekranu i dźwięku Dla linuxa i Windowsa.

    Args:
        update_status: metoda aplikacji gui (aktualizacja wiadomości statusu)
    """
    global recording_process

    # Wywołanie aktualizacji statusu w GUI
    log_status("Nagrywanie w toku...", "info" ,update_status)

    system_name = platform.system()
    # Ścieżka do zapisu pliku wideo
    output_dir = os.path.join(os.getcwd(), "nagrania")
    os.makedirs(output_dir, exist_ok=True)  # Tworzenie folderu, jeśli nie istnieje

    # Tworzenie unikalnej nazwy pliku na podstawie daty i czasu
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = os.path.join(output_dir, f"Nagranie_{timestamp}.mp4")

    if system_name == "Linux":
        # Polecenie FFmpeg dla Linuxa
        ffmpeg_command = [
            "ffmpeg",
            "-y",  # Nadpisywanie istniejących plików
            "-f", "x11grab",  # Przechwytywanie ekranu na Linux GNOME
            "-i", os.environ["DISPLAY"],  # Wyświetlacz (np. ":0")
            "-f", "pulse",  # Przechwytywanie dźwięku z PulseAudio
            "-i", "default",  # Domyślne źródło dźwięku
            "-c:v", "libx264",  # Kodowanie wideo
            "-preset", "ultrafast",  # Szybkie kodowanie
            "-c:a", "aac",  # Kodowanie audio
            "-b:a", "192k",  # Jakość dźwięku
            "-pix_fmt", "yuv420p",  # Format pikseli
            output_file
        ]
    elif system_name == "Windows":
        # Polecenie FFmpeg dla Windowsa
        ffmpeg_command = [
            "ffmpeg",
            "-y",  # Nadpisywanie istniejących plików
            "-f", "gdigrab",  # Przechwytywanie ekranu
            "-i", "desktop",  # Desktop jako źródło obrazu
            "-f", "dshow",  # Przechwytywanie dźwięku
            "-i", "audio=Stereo Mix",  # Nazwa urządzenia dźwiękowego
            "-c:v", "libx264",  # Kodowanie wideo
            "-preset", "ultrafast",  # Szybkie kodowanie
            "-c:a", "aac",  # Kodowanie audio
            "-b:a", "192k",  # Jakość dźwięku
            "-pix_fmt", "yuv420p",  # Format pikseli
            output_file
        ]
    else:
        log_status(f"Nagrywanie nie jest wspierane na tym systemie: {system_name}", "critical", update_status)
        return

    # Uruchomienie procesu FFmpeg
    try:
        recording_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log.debug(f"Nagrywanie rozpoczęte. Plik zostanie zapisany jako: {output_file}")
    except Exception as e:
        log_status(f"Błąd podczas rozpoczynania nagrywania: {e}", "error", update_status)

def stop_recording(update_status: any) -> None:
    """
    Funkcja kończąca nagrywanie ekranu i dźwięku.

    Args:
        update_status: metoda aplikacji gui (aktualizacja wiadomości statusu)
    """
    global recording_process

    # Wywołanie aktualizacji statusu w GUI
    log_status("Kończenie nagrywania...", "info", update_status)

    system_name = platform.system()
    if system_name in ["Linux", "Windows"]:
        if recording_process:
            try:
                # Wysłanie sygnału do zakończenia procesu FFmpeg
                recording_process.send_signal(signal.SIGINT)
                recording_process.wait()
                update_status("Gotowe")
                log_status("Nagrywanie zakończone.", "success", update_status)
            except Exception as e:
                log_status(f"Błąd podczas zakończania nagrywania: {e}", "error", update_status)
            finally:
                recording_process = None
        else:
            log_status("Nie znaleziono aktywnego nagrywania.", "warning", update_status)
    else:
        log_status(f"Nagrywanie nie jest wspierane na tym systemie: {system_name}", "critical", update_status)
