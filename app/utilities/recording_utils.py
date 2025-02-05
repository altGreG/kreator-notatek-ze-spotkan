#app/utilities/recording_utils.py

"""Moduł zarządzania plikami spotkań

Skrypt umożliwia automatyczne tworzenie katalogów na potrzeby zrzutów ekranu, nagrań audio oraz transkrypcji, a także agregację plików tekstowych w spójne dokumenty.

Wymagane zależności

Do poprawnego działania skryptu nie są wymagane dodatkowe pakiety zewnętrzne poza standardowymi bibliotekami Pythona.

Skrypt może być używany jako moduł i zawiera następujące funkcje:

    * create_output_folder — tworzy hierarchię katalogów dla bieżącego spotkania, w tym podfoldery dla nagrań audio, transkrypcji i zrzutów ekranu.
    * txt_files_aggregation — łączy poszczególne fragmenty transkrypcji z plików .txt między zrzutami ekranu, sortując je chronologicznie oraz przenosząc stare pliki do folderu archiwum.

Każda funkcja posiada odpowiednie mechanizmy obsługi błędów, sortowania plików i organizacji struktury katalogów dla lepszej przejrzystości danych ze spotkań.
"""

from datetime import datetime
import os
import glob
from typing import List, Any

def create_output_folder() -> list[str]:
    """Tworzy foldery wynikowe na zapisywane pliki .jpg, .txt i .mp3

    Funkcja tworzy folder główny a nim trzy podfoldery na zrzuty ekranu, nagrane fragmenty audio
    oraz tekst z transkrypcji.

    Returns:
        Lista zawieracjąca ścieżki do folderów [meeting_directory, recording_directory, screenshots_directory, transcription_directory]
    """

    if (os.getcwd().replace("\\", "/")).rsplit("/", 1)[1] == "app":
        base_folder = (os.getcwd().replace("\\", "/")).rsplit("app", 1)[0] + "/app"
    else:
        base_folder = os.getcwd()

    os.makedirs(base_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Tworzenie folderu dla bieżącego spotkania
    meeting_directory = os.path.join(base_folder, "spotkania", timestamp)
    os.makedirs(meeting_directory, exist_ok=True)

    # Tworzenie folderu dla bieżącego txt
    transcription_directory = os.path.join(meeting_directory, f"txt-{timestamp}")
    os.makedirs(transcription_directory, exist_ok=True)

    # Tworzenie folderu dla bieżącego nagrania
    recording_directory = os.path.join(meeting_directory, f"audio-{timestamp}")
    os.makedirs(recording_directory, exist_ok=True)

    screenshots_directory = os.path.join(meeting_directory, f"screenshots-{timestamp}")
    os.makedirs(screenshots_directory, exist_ok=True)

    output_list = [meeting_directory.replace("\\", "/"), recording_directory.replace("\\", "/"), screenshots_directory.replace("\\", "/"), transcription_directory.replace("\\", "/")]

    return output_list

def txt_files_aggregation(meeting_folder: str) -> None:
    """
    Funkcja łączy poszczególne fragmenty transkrypcji między screenami ekranu w większą całość.

    Funkcja buduje listę ścieżek do txt i jpg. Sortuje ją po timestampie. Następnie łączy pliki transkrypcji,
    która była między poszczególnymi momentami wykonania zrzutów ekranu w jeden plik txt, który nosi nazwę
    najwcześniejszego timestampu audio z grupy.

    Notes:
        Stare pliki funkcja przenosi do folderu archiwum w folderze z transkrypcjami (timestamp/txt-timestamp/archiwum).

    Arguments:
        meeting_folder:
            ścieżka do folderu głównego spotkania
    """

    timestamp = (meeting_folder.replace("\\", "/")).rsplit("/", 1)[1]
    txt_pattern = meeting_folder + f"/txt-{timestamp}/*.txt"
    screenshots_pattern = meeting_folder + f"/screenshots-{timestamp}/*.jpg"

    archiwum_path = meeting_folder + f"/txt-{timestamp}/archiwum"
    os.makedirs(archiwum_path, exist_ok=True)

    txt_files = glob.glob(txt_pattern)
    jpg_files = glob.glob(screenshots_pattern)

    files = txt_files + jpg_files

    print("Posortowane pliki, patrz na timestamp(nazwe pliku jpg lub txt)")
    files.sort(key= lambda f: ((f.replace("\\", "/")).rsplit("/", 1)[1]).rsplit(".", 1)[0])
    for file in files:
        print(file)

    done_files = []
    temp_done_list = []
    for file in files:
        if file not in done_files:
            ext = file.rsplit(".",1)[1]
            filename = ((file.rsplit(".",1)[0]).replace("\\", "/")).rsplit("/", 1)[1]

            if ext == "txt":
                if temp_done_list == []:
                    temp_done_list.append(file)
                else:
                    with open(file, 'r', encoding='utf-8') as f:
                        text = f.read()
                    with open(temp_done_list[0], 'a', encoding='utf-8') as f:
                        f.write(text, )
                    done_files.append(file)

                    os.rename(file, f"{file.replace('\\', '/').rsplit('/', 1)[0]}/archiwum/{filename}.{ext}")
            elif ext == "jpg":
                temp_done_list = []
