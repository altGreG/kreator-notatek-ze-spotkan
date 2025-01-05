import os
from loguru import logger as log
from app.logger import log_status

def save_text_to_txt(filename, transcribed_text, update_status):
    """
    Zapis przetranskrybowanego tekstu do pliku .txt
    (pliki są zapisywane w folderze app/txt)

    :param filename: nazwa dla pliku txt
    :param transcribed_text: przetranskrybowany tekst z pliku audio
    :param update_status: metoda aplikacji gui służąca do aktualizacji wiadomości statusu w GUI
    :return: string z ścieżką do zapisanego pliku txt lub None
    """


    log_status("Przygotowanie do zapisu transkrypcji w pliku txt.", "info", update_status)
    output_dir = (os.path.dirname(__file__) + "/txt").replace("\\", "/")
    os.makedirs(output_dir, exist_ok=True)  # Tworzenie folderu, jeśli nie istnieje

    txt_path = (output_dir + f"/{filename}.txt").replace("\\", "/")
    log.debug(f"Miejsce zapisu pliku txt: {txt_path}", "info", update_status )

    log_status("Zapis do pliku txt w toku...", "info", update_status)
    try:
        with open(txt_path, 'w', encoding='utf-8') as file:
            file.write(transcribed_text, )
            log_status("Dokonano zapisu tekstu do pliku txt", "success", update_status)
            return txt_path
    except Exception as err:
        log_status(f"Wystąpił problem w czasie zapisu do pliku txt: {err}", "error", update_status)
        return None