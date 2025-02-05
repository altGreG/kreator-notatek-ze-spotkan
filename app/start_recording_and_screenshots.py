#app/start_recording_and_screenshots.py

"""Moduł zarządzania sesjami nagrań, zrzutów ekranu i transkrypcji

Skrypt umożliwia jednoczesne nagrywanie dźwięku, wykonywanie zrzutów ekranu oraz transkrypcję nagranego materiału audio, zapewniając pełne zarządzanie tymi procesami.

Wymagane zależności

Aby skrypt działał poprawnie, wymagane jest zainstalowanie następujących pakietów:

    - threading: Wbudowany moduł umożliwiający równoległe wykonywanie operacji.
    - loguru: Biblioteka do zaawansowanego logowania.

Skrypt współpracuje z następującymi modułami:

    - app.recorder_audio: Nagrywanie dźwięku
    - app.screenshots: Wybór obszaru ekranu oraz wykonywanie zrzutów
    - app.transcriptor: Transkrypcja nagrań audio
    - app.utilities.recording_utils: Zarządzanie katalogami dla danych sesji

Skrypt może być używany jako moduł i zawiera następujące funkcje:

    * start_recording_and_screenshots — uruchamia równoczesne nagrywanie dźwięku, wykonywanie zrzutów ekranu oraz transkrypcję audio w osobnych wątkach.
    * stop_recording_and_screenshots — zatrzymuje nagrywanie dźwięku, wykonywanie zrzutów ekranu

Każda funkcja posiada odpowiednie mechanizmy obsługi błędów, aktualizację statusu użytkownika oraz integrację z systemami logowania.

Dzięki modułowi użytkownik ma możliwość kompleksowego zarządzania sesjami, obejmującymi rejestrację dźwięku, wizualne zrzuty ekranu i przetwarzanie materiału audio na tekst.
"""

import threading
from recorder_audio import start_recording, stop_recording
from screenshots import select_area, monitor_and_capture, create_output_folder, stop_monitor_and_capture
from app.transcriptor import transcribe_audio_from_folder
from app.utilities.recording_utils import create_output_folder
from loguru import logger as log
from typing import Callable

# Flaga kontrolująca zrzuty ekranu
recording_active = False
screenshot_thread = None
transcriptor_thread = None

def start_recording_and_screenshots(update_status, selected_audio_device, app, transription_false_update):
    """
    Funkcja uruchamiająca jednocześnie nagrywanie dźwięku i zrzuty ekranu.

    Args:
        update_status: Funkcja do aktualizacji statusu w GUI.
        selected_audio_device: Nazwa wybranego urządzenia audio.
        app: Główna instancja Tkinter.
        transription_false_update: metoda gui, odblokowuje przycisk play
    """
    global recording_active, screenshot_thread, transcriptor_thread
    capture_area=None

    # Tworzenie folderu na zrzuty ekranu
    output_folders = create_output_folder()
    print(output_folders)

    # Flaga aktywności
    recording_active = True

    # Funkcja uruchamiająca zrzuty ekranu
    def run_screenshots():
        # Wybór obszaru ekranu
        global  recording_active
        capture_area = select_area()
        if not capture_area:
            app.after(0, lambda: update_status("Nie wybrano obszaru do zrzutów ekranu."))
            return
        monitor_and_capture(capture_area, output_folders[2])

    def run_transcription():
        global recording_active
        transcribe_status = transcribe_audio_from_folder(output_folders[1], update_status, app, transription_false_update)

        if transcribe_status is not None:
            log.info("Nie udało się przeprowadzić transkrypcji audio.")
        else:
            log.info("Sukces. Dokonano pełnej transkrypcji audio.")

    # Uruchomienie nagrywania dźwięku w osobnym wątku
    audio_thread = threading.Thread(target=start_recording, args=(update_status, selected_audio_device, output_folders[1]))
    screenshot_thread = threading.Thread(target=run_screenshots)
    transcriptor_thread = threading.Thread(target=run_transcription)

    audio_thread.start()
    screenshot_thread.start()
    transcriptor_thread.start()

    app.after(0, lambda: update_status("Rozpoczęto nagrywanie dźwięku i zrzuty ekranu. Rozpoczęto transkrypcje."))

def stop_recording_and_screenshots(update_status: Callable[[str], None]) -> None:
    """
    Zatrzymuje zarówno nagrywanie dźwięku, jak i proces wykonywania zrzutów ekranu.

    Działanie:
        - Wywołuje `stop_recording(update_status)`, aby zatrzymać nagrywanie dźwięku.
        - Ustawia `recording_active` na `False`, co kończy proces monitorowania zmian na ekranie.
        - Jeśli wątek `screenshot_thread` jest aktywny, wywołuje `stop_monitor_and_capture()` i czeka na jego zakończenie.
        - Aktualizuje status w GUI.

    Args:
        update_status (Callable[[str], None]):
            Funkcja aktualizująca status w interfejsie użytkownika.

    Returns:
        None

    Notes:
        - Funkcja zapewnia, że zarówno audio, jak i zrzuty ekranu są zatrzymane w odpowiedni sposób.
        - Sprawdza, czy `screenshot_thread` jest aktywny przed próbą jego zatrzymania.
        - Aktualizacja statusu w GUI informuje użytkownika o zakończeniu nagrywania.
    """

    global recording_active, screenshot_thread

    # Zatrzymaj nagrywanie dźwięku
    stop_recording(update_status)

    # Zatrzymaj zrzuty ekranu
    recording_active = False
    if screenshot_thread and screenshot_thread.is_alive():
        stop_monitor_and_capture()
        screenshot_thread.join()

    update_status("Nagrywanie i zrzuty ekranu zakończone.")
