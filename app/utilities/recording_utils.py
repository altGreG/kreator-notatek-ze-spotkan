from datetime import datetime
import os
from typing import List, Any


def create_output_folder() -> list[str]:
    """Tworzy folder na zrzuty ekranu i nagrania audio.

    Returns:
        list[str, str, str] -- [meeting_directory, recording_directory, screenshots_directory]
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

    output_list = [meeting_directory.replace("\\", "/"), recording_directory.replace("\\", "/"), screenshots_directory.replace("\\", "/")]

    return output_list
