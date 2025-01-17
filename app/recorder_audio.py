import platform
import subprocess
import os
from datetime import datetime
from tkinter import messagebox
from loguru import logger as log
from logger import log_status

recording_process = None  # Zmienna globalna do przechowywania procesu nagrywania

def start_recording(update_status: any, selected_audio_device: str) -> None:
    """
    Funkcja rozpoczynająca nagrywanie dźwięku z wybranego urządzenia.

    Args:
        update_status: metoda aplikacji gui (aktualizacja wiadomości statusu)
        selected_audio_device: zmienna zawierająca nazwę urządzenia audio nagrywającego dźwięk
    """
    global recording_process
    system_name = platform.system()

    if selected_audio_device is None:
        messagebox.showerror("Błąd", "Nie wybrano urządzenia audio. Skonfiguruj ustawienia.")
        log.warning("Nie wybrano urządzenia audio. Skonfiguruj ustawienia.")
        return

    if update_status:
        log_status("Nagrywanie dźwięku w toku...", "info", update_status)

    output_dir = os.path.join(os.getcwd(), "nagrania_audio")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = os.path.join(output_dir, f"Nagranie_{timestamp}.mp3")

    ffmpeg_command = [
        "ffmpeg",
        "-y",
        "-f", "dshow",
        "-i", f"audio={selected_audio_device}",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        output_file
    ]

    try:
        if system_name == "Linux":
            recording_process = subprocess.Popen(
                ffmpeg_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
        elif system_name == "Windows":
            recording_process = subprocess.Popen(
                ffmpeg_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
        log.debug(f"Nagrywanie dźwięku rozpoczęte. Plik zostanie zapisany jako: {output_file}")
    except Exception as e:
        if update_status:
            log_status(f"Błąd podczas rozpoczynania nagrywania dźwięku: {e}", "error", update_status)


def stop_recording(update_status: any) -> None:
    """
    Funkcja kończąca nagrywanie dźwięku.

    Args:
        update_status: metoda aplikacji gui (aktualizacja wiadomości statusu)
    """
    global recording_process
    system_name = platform.system()

    # Wywołanie aktualizacji statusu w GUI
    if update_status:
        log_status("Kończenie nagrywania dźwięku...", "info", update_status)

    if recording_process:
        try:
            if system_name == "Linux":
                # Przekazanie polecenia 'q' do procesu, jeśli jest dostępne stdin
                if recording_process.stdin:
                    recording_process.stdin.write(b"q\n")
                    recording_process.stdin.flush()

                # Oczekiwanie na zakończenie procesu
                recording_process.wait()

                # Przechwycenie i zapisanie wyjścia błędów
                stderr_output = recording_process.stderr.read().decode()
                if stderr_output:
                    log.debug(f"Ffmep output message: {stderr_output}")
            elif system_name == "Windows":
                # Przekazanie polecenia 'q' do procesu, jeśli jest dostępne stdin
                if recording_process.stdin:
                    stderr_output = recording_process.communicate(input=f"q\n")[1]
                    log.debug(f"Ffmep output message: {stderr_output}")
                else:
                    log.error("There is no stdin in subprocess. Cannot end a process!")

            if update_status:
                log_status("Nagrywanie zakończone. Plik został zapisany.", "info", update_status)
        except Exception as e:
            if update_status:
                log_status(f"Błąd podczas zakończania nagrywania dźwięku: {e}", "error", update_status)
        finally:
            recording_process = None
    else:
        if update_status:
            log_status("Nie znaleziono aktywnego nagrywania.", "warning", update_status)

# Funkcje start_recording i stop_recording są teraz gotowe do użycia w innej aplikacji (tylko Stereo Mix, zapis do MP3).
