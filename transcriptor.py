import platform
import subprocess
import os

def extract_audio_from_video(video_file):
    """Ekstrakcja audio z wideo z wykorzystaniem `ffmpeg`"""
    # Sprawdzenie platformy, definicja zmiennej dla kodu z procesu ffmpeg
    system_name = platform.system()
    extracting_process = -1

    # Pozyskanie nazwy pliku wideo
    filename, ext = os.path.splitext(video_file)

    # Ekstracja ścieżki audio z pliku i zapis do mp3
    # update_status("Ekstrakcja audio w toku...")
    if system_name == "Windows":
        extracting_process = subprocess.call(["./software/ffmpeg", "-y", "-i", video_file, f"{filename}.mp3"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)
    elif system_name == "Linux":
        extracting_process = subprocess.call(["ffmpeg", "-y", "-i", video_file, f"{filename}.mp3"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)

    # Aktualizacja statusu aplikacji po ekstrakcji
    # print(extracting_process)
    if extracting_process != 0:
        # update_status("Błąd w czasie ekstrakcji audio z wideo.")
        print("Błąd w czasie ekstrakcji audio z wideo.")
    else:
        # update_status("Sukces. Dokonano ekstrakcji audio z wideo.")
        print("Skutecznie dokonano ekstrakcji audio z wideo.")

# s = "./nagrania/test.mkv"
# extract_audio_from_video(s)
