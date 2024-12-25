import platform
import subprocess
import os
import signal
from datetime import datetime

recording_process = None  # Zmienna globalna do przechowywania procesu nagrywania

def start_recording(update_status):
    """
    Funkcja rozpoczynająca nagrywanie ekranu i dźwięku Dla linuxa.
    """
    global recording_process

    # Wywołanie aktualizacji statusu w GUI
    update_status("Nagrywanie w toku...")

    system_name = platform.system()
    if system_name == "Linux":
        # Ścieżka do zapisu pliku wideo
        output_dir = os.path.join(os.getcwd(), "nagrania")
        os.makedirs(output_dir, exist_ok=True)  # Tworzenie folderu, jeśli nie istnieje

        # Tworzenie unikalnej nazwy pliku na podstawie daty i czasu
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = os.path.join(output_dir, f"Nagranie_{timestamp}.mp4")

        # Polecenie FFmpeg
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

        # Uruchomienie procesu FFmpeg
        try:
            recording_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Nagrywanie rozpoczęte. Plik zostanie zapisany jako: {output_file}")
        except Exception as e:
            update_status(f"Błąd podczas rozpoczynania nagrywania: {e}")
    elif system_name == "Windows":
        update_status("Nagrywanie dla Windows nie jest jeszcze zaimplementowane.")
    else:
        update_status(f"Nagrywanie nie jest wspierane na tym systemie: {system_name}")

def stop_recording(update_status):
    """
    Funkcja kończąca nagrywanie ekranu i dźwięku.
    """
    global recording_process

    # Wywołanie aktualizacji statusu w GUI
    update_status("Kończenie nagrywania...")

    system_name = platform.system()
    if system_name == "Linux":
        if recording_process:
            try:
                # Wysłanie sygnału do zakończenia procesu FFmpeg
                recording_process.send_signal(signal.SIGINT)
                recording_process.wait()
                update_status("Gotowe")
                print("Nagrywanie zakończone.")
            except Exception as e:
                update_status(f"Błąd podczas zakończania nagrywania: {e}")
            finally:
                recording_process = None
        else:
            update_status("Nie znaleziono aktywnego nagrywania.")
    elif system_name == "Windows":
        update_status("Nagrywanie dla Windows nie jest jeszcze zaimplementowane.")
    else:
        update_status(f"Nagrywanie nie jest wspierane na tym systemie: {system_name}")
