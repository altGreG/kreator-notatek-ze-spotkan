# app/utilities/saving.py

"""Moduł zapisu transkrypcji tekstowych

Ten skrypt pozwala na zapis przetworzonych transkrypcji audio do plików tekstowych.

Wymagane zależności

Skrypt wymaga, aby w środowisku Pythona, w którym uruchamiasz ten skrypt, była zainstalowana biblioteka:

    - loguru: Rozbudowany system logowania

Do poprawnego działania skryptu należy zaimportować funkcję:

    - log_status z modułu app.utilities.logger, służącą do logowania komunikatów statusowych.

Ten plik może zostać zaimportowany również jako moduł i zawiera następujące funkcje:

    * save_text_to_txt - zapis przetranskrybowanego tekstu do pliku .txt
    * format_text - formatowanie zawartości pliku tekstowego zgodnie z podaną maksymalną szerokością linii

"""

import os
from loguru import logger as log
from typing import Callable
from app.utilities.logger import log_status

def save_text_to_txt(filename: str, transcribed_text: str, update_status: Callable[[str], None], transcription_folder: str | None = None) -> str | None:
    """
    Zapis przetranskrybowanego tekstu do pliku .txt

    Args:
        filename:
            nazwa dla pliku txt
        transcribed_text:
            przetranskrybowany tekst z pliku audio
        update_status:
            Funkcja aktualizująca wiadomości statusu w aplikacji GUI.
        transcription_folder:
            ścieżka do folderu na tranksrypcję fragmentów nagrania

    Returns:
        string z ścieżką do zapisanego pliku txt | None
    """
    full_transcription_path = None

    if transcription_folder is None:
        output_dir = (os.path.dirname(__file__) + "/txt").replace("\\", "/")
        os.makedirs(output_dir, exist_ok=True)  # Tworzenie folderu, jeśli nie istnieje
        txt_path = (output_dir + f"/{filename}.txt").replace("\\", "/")
    else:
        base_path, timestamp = (transcription_folder.replace("\\", "/")).rsplit("/txt-", 1)
        full_transcript_path = base_path + "/" + f"full-{timestamp}.txt"
        txt_path = (transcription_folder + f"/{filename}.txt").replace("\\", "/")

    try:
        with open(txt_path, 'a', encoding='utf-8') as file:
            file.write(transcribed_text, )
            log_status(f"Dokonano zapisu txt: {txt_path.rsplit("/",1)[1]}", "success", update_status)

        format_text(txt_path, 80)

        if transcription_folder is not None:
            with open(full_transcript_path, 'a', encoding='utf-8') as file:
                file.write(transcribed_text, )
            log_status(f"Dokonano zapisu txt (pelna transkrypcja): {txt_path.rsplit("/",1)[1]}", "success", update_status)

        return txt_path
    except Exception as err:
        log_status(f"Wystąpił problem w czasie zapisu do pliku txt: {err}", "error", update_status)
        return None

def format_text(txt_path: str, line_width: int = 80) -> None:
    """
    Funkcja dokonująca formatu pliku txt, do odpowiedniej szerokości linii

    Arguments:
        txt_path:
            Ścieżka pliku TXT
        line_width:
            Maksymalna szerokość linii w znakach.
    """

    text = ""
    with open(txt_path, 'r', encoding='utf-8') as f:
        text = f.read()

    with open(txt_path, "w", encoding="utf-8") as f:

        lines = text.splitlines()  # Podział na linie wejściowe

        for line in lines:
            words = line.split()  # Podział linii na słowa
            line_buffer = ""

            for word in words:
                # Sprawdzanie, czy bieżąca linia mieści kolejne słowo
                if len(line_buffer) + len(word) + 1 <= line_width:
                    line_buffer += (word + " ")
                else:
                    # Zapis linii do pliku
                    f.write(line_buffer.strip() + "\n")
                    line_buffer = word + " "

            # Zapis pozostałości linii (jeśli istnieje)
            if line_buffer:
                f.write(line_buffer.strip() + "\n")