import threading


from recorder_audio import start_recording, stop_recording
from screenshots import select_area, monitor_and_capture, create_output_folder, stop_monitor_and_capture

# Flaga kontrolująca zrzuty ekranu
recording_active = False
screenshot_thread = None

def start_recording_and_screenshots(update_status, selected_audio_device, app):
    """
    Funkcja uruchamiająca jednocześnie nagrywanie dźwięku i zrzuty ekranu.

    Args:
        update_status: Funkcja do aktualizacji statusu w GUI.
        selected_audio_device: Nazwa wybranego urządzenia audio.
        app: Główna instancja Tkinter.
    """
    global recording_active, screenshot_thread
    capture_area=None


    # Tworzenie folderu na zrzuty ekranu
    output_folder = create_output_folder()

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
        monitor_and_capture(capture_area, output_folder)

    # Uruchomienie nagrywania dźwięku w osobnym wątku
    audio_thread = threading.Thread(target=start_recording, args=(update_status, selected_audio_device))
    screenshot_thread = threading.Thread(target=run_screenshots)

    audio_thread.start()
    screenshot_thread.start()

    app.after(0, lambda: update_status("Rozpoczęto nagrywanie dźwięku i zrzuty ekranu."))

def stop_recording_and_screenshots(update_status):
    """
    Funkcja zatrzymująca nagrywanie dźwięku i zrzuty ekranu.
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
