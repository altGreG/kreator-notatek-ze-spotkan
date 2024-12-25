import platform
import subprocess
import os
import signal

def start_recording():
    system_name = platform.system()
    if system_name == "Linux":
        """
           Funkcja rozpoczynająca nagrywanie ekranu i dźwięku Dla linuxa.
           """
        global recording_process

        # Ścieżka do zapisu pliku wideo
        output_dir = os.path.join(os.getcwd(), "nagrania")
        os.makedirs(output_dir, exist_ok=True)  # Tworzenie folderu, jeśli nie istnieje
        output_file = os.path.join(output_dir, "nagranie.mp4")

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
            print(f"Błąd podczas rozpoczynania nagrywania: {e}")

        pass
    elif system_name == "Windows":
        # Implementacja dla Windowsa
        pass
    else:
        raise NotImplementedError(f"Nagrywanie nie jest wspierane na tym systemie: {system_name}")

def stop_recording():
    system_name = platform.system()
    if system_name == "Linux":
        """
           Funkcja kończąca nagrywanie ekranu i dźwięku.
           """
        global recording_process

        if recording_process:
            try:
                # Wysłanie sygnału do zakończenia procesu FFmpeg
                recording_process.send_signal(signal.SIGINT)
                recording_process.wait()
                print("Nagrywanie zakończone.")
            except Exception as e:
                print(f"Błąd podczas zakończania nagrywania: {e}")
            finally:
                recording_process = None
        else:
            print("Nie znaleziono aktywnego nagrywania.")
        pass
    elif system_name == "Windows":
        # Implementacja dla Windowsa
        pass
    else:
        raise NotImplementedError(f"Nagrywanie nie jest wspierane na tym systemie: {system_name}")
