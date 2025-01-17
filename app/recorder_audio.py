import platform
import subprocess
import os
import threading
from datetime import datetime
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO
from tkinter import messagebox
from loguru import logger as log
from logger import log_status

recording_process = None
recording_active = True
recording_directory = None


def start_recording(update_status: any, selected_audio_device: str) -> None:
    """
    Funkcja rozpoczynająca nagrywanie dźwięku z wybranego urządzenia.

    Args:
        update_status: metoda aplikacji gui (aktualizacja wiadomości statusu)
        selected_audio_device: zmienna zawierająca nazwę urządzenia audio nagrywającego dźwięk
    """
    global recording_process, recording_active, recording_directory

    if not selected_audio_device:
        messagebox.showerror("Błąd", "Nie wybrano urządzenia audio. Skonfiguruj ustawienia.")
        log.warning("Nie wybrano urządzenia audio. Skonfiguruj ustawienia.")
        return

    if update_status:
        log_status("Nagrywanie dźwięku w toku...", "info", update_status)

    # Tworzenie folderu dla bieżącego nagrania
    recording_directory = os.path.join(os.getcwd(), "nagrania_audio", datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(recording_directory, exist_ok=True)

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


def _save_audio_fragments():
    """
    Funkcja zapisująca fragmenty audio co 10 sekund bez zatrzymywania nagrywania.
    """
    global recording_process, recording_active, recording_directory

    buffer = BytesIO()
    fragment_duration = 20 * 1000  # 10 sekund w milisekundach

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
                log.debug(f"Zapisano fragment: {output_file}")

                # Usuń zapisane dane z bufora
                buffer = BytesIO(audio_segment[fragment_duration:].raw_data)
    except Exception as e:
        log.error(f"Błąd podczas zapisywania fragmentów audio: {e}")


def stop_recording(update_status: any) -> None:
    """
    Funkcja kończąca nagrywanie dźwięku.

    Args:
        update_status: metoda aplikacji gui (aktualizacja wiadomości statusu)
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
