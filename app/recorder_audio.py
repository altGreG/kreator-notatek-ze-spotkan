import platform
import subprocess
import os
from datetime import datetime
from tkinter import messagebox

from loguru import logger as log


recording_process = None  # Zmienna globalna do przechowywania procesu nagrywania

def start_recording(update_status):
    """
    Funkcja rozpoczynająca nagrywanie dźwięku z wybranego urządzenia.
    """
    global recording_process

    if not selected_audio_device:
        messagebox.showerror("Błąd", "Nie wybrano urządzenia audio. Skonfiguruj ustawienia.")
        return

    if update_status:
        update_status("Nagrywanie dźwięku w toku...")

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
        recording_process = subprocess.Popen(
            ffmpeg_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        log.debug(f"Nagrywanie dźwięku rozpoczęte. Plik zostanie zapisany jako: {output_file}")
    except Exception as e:
        if update_status:
            update_status(f"Błąd podczas rozpoczynania nagrywania dźwięku: {e}")

def stop_recording(update_status):
    """
    Funkcja kończąca nagrywanie dźwięku.
    """
    global recording_process

    # Wywołanie aktualizacji statusu w GUI
    if update_status:
        update_status("Kończenie nagrywania dźwięku...")

    if recording_process:
        try:
            # Przekazanie polecenia 'q' do procesu, jeśli jest dostępne stdin
            if recording_process.stdin:
                recording_process.stdin.write(b"q\n")
                recording_process.stdin.flush()

            # Oczekiwanie na zakończenie procesu
            recording_process.wait()

            # Przechwycenie i zapisanie wyjścia błędów
            stderr_output = recording_process.stderr.read().decode()
            if stderr_output:
                log.error(f"Błędy FFmpeg: {stderr_output}")

            if update_status:
                update_status("Nagrywanie zakończone. Plik został zapisany.")
        except Exception as e:
            if update_status:
                update_status(f"Błąd podczas zakończania nagrywania dźwięku: {e}")
        finally:
            recording_process = None
    else:
        if update_status:
            update_status("Nie znaleziono aktywnego nagrywania.")

# Funkcje start_recording i stop_recording są teraz gotowe do użycia w innej aplikacji (tylko Stereo Mix, zapis do MP3).
