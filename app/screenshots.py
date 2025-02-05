# app/screenshots.py

"""Moduł monitorowania ekranu i zapisu zrzutów ekranu

Skrypt umożliwia użytkownikowi wybór obszaru ekranu do monitorowania, a następnie automatyczne wykonywanie zrzutów ekranu w przypadku wykrycia znaczących zmian w obrazie.

Wymagane zależności

Aby uruchomić skrypt, należy zainstalować następujące pakiety w środowisku Python:

    - Pillow: Biblioteka do obsługi grafiki, w tym zrzutów ekranu
    - loguru: Rozbudowany system logowania

Do prawidłowego działania aplikacji należy zaimportować:

    - create_output_folder z modułu app.utilities.recording_utils, służącą do tworzenia folderów wyjściowych.

Skrypt może być używany jako moduł i zawiera następujące funkcje:

    * select_area — pozwala użytkownikowi zaznaczyć obszar ekranu za pomocą dynamicznej nakładki GUI.
    * monitor_and_capture — monitoruje zmiany w wybranym obszarze ekranu i zapisuje zrzuty w przypadku wykrycia zmian.
    * stop_monitor_and_capture — zatrzymuje proces monitorowania.

Każda funkcja posiada odpowiednie mechanizmy obsługi błędów, logowania oraz komunikatów dla użytkownika.
"""

import os
import time
from tkinter import Tk, Canvas, Button
from PIL import ImageGrab, ImageChops
from loguru import logger as log
from datetime import datetime

from app.utilities.recording_utils import create_output_folder

recording_active = False


def select_area():
    """
    Tworzy nakładkę na ekranie, pozwalając użytkownikowi zaznaczyć obszar do przechwytywania.

    Funkcja otwiera przezroczyste okno Tkinter jako nakładkę, umożliwiając użytkownikowi zaznaczenie
    prostokątnego obszaru za pomocą myszy. Po wybraniu obszaru, zwraca jego współrzędne i rozmiar.

    Returns:
        list: Lista zawierająca cztery wartości [x, y, width, height], gdzie:
            - x (int): Współrzędna X górnego lewego rogu zaznaczonego obszaru.
            - y (int): Współrzędna Y górnego lewego rogu zaznaczonego obszaru.
            - width (int): Szerokość zaznaczonego obszaru.
            - height (int): Wysokość zaznaczonego obszaru.

    Example:
        >>> selected_area = select_area()
        >>> print(selected_area)
        [100, 150, 800, 600]  # Przykładowe współrzędne
    """
    root = Tk()
    root.attributes("-topmost", True)  # Nakładka nad innymi oknami
    try:
        root.attributes("-alpha", 0.3)  # Przezroczystość, jeśli obsługiwana
    except:
        root.configure(bg="white")  # Fallback dla starszych wersji Tkinter

    # Dopasowanie nakładki do rozmiaru ekranu
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}")

    # Tworzenie płótna do zaznaczania obszaru
    canvas = Canvas(root, cursor="cross", bg="black")
    canvas.pack(fill="both", expand=True)

    start_x = start_y = None
    rect_id = None
    area = []

    def on_mouse_press(event):
        nonlocal start_x, start_y, rect_id
        start_x, start_y = event.x, event.y
        rect_id = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="red", width=2)

    def on_mouse_drag(event):
        nonlocal rect_id
        canvas.coords(rect_id, start_x, start_y, event.x, event.y)

    def on_mouse_release(event):
        nonlocal start_x, start_y, area
        end_x, end_y = event.x, event.y
        area = [min(start_x, end_x), min(start_y, end_y), abs(end_x - start_x), abs(end_y - start_y)]
        root.destroy()

    def close_overlay():
        """Funkcja zamykająca nakładkę po kliknięciu X."""
        root.destroy()

    # Dodaj przycisk zamykający nakładkę
    close_button = Button(root, text="X", command=close_overlay, bg="red", fg="white", font=("Arial", 14))
    close_button.place(x=10, y=10, width=30, height=30)  # Pozycjonowanie przycisku "X"

    # Obsługa zdarzeń myszy
    canvas.bind("<ButtonPress-1>", on_mouse_press)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_release)

    root.mainloop()
    return area

def monitor_and_capture(area, folder, threshold=2.0):
    """
    Monitoruje zmiany w wybranym obszarze ekranu i zapisuje zrzut ekranu, jeśli różnice przekraczają określony próg.

    Funkcja stale wykonuje zrzuty ekranu zaznaczonego obszaru i porównuje je z poprzednimi.
    Jeśli różnice między kolejnymi obrazami przekraczają ustalony procent `threshold`, zapisuje nowy zrzut ekranu w formacie JPG.

    Args:
        area (list): Lista czterech wartości [x, y, width, height], określająca zaznaczony obszar ekranu.
            - x (int): Współrzędna X górnego lewego rogu zaznaczonego obszaru.
            - y (int): Współrzędna Y górnego lewego rogu zaznaczonego obszaru.
            - width (int): Szerokość zaznaczonego obszaru.
            - height (int): Wysokość zaznaczonego obszaru.
        folder (str): Ścieżka do katalogu, w którym zapisywane będą zrzuty ekranu.
        threshold (float, optional): Procentowa wartość określająca, jak duża zmiana w obrazie powoduje zapis nowego zrzutu ekranu.
            Wartość domyślna to 2.0%.

    Raises:
        KeyboardInterrupt: Zatrzymuje pętlę monitorowania w przypadku przerwania programu.

    Example:
        >>> monitor_and_capture([100, 150, 800, 600], "./screenshots", threshold=3.5)

    Notes:
        - Funkcja działa w pętli nieskończonej, dopóki `recording_active` nie zostanie ustawiona na `False`.
        - Domyślnie zapisuje obrazy jako pliki JPG o jakości 85.
        - Próg detekcji zmian (`threshold`) można dostosować dla lepszej czułości.
    """

    global recording_active
    recording_active = True
    x, y, width, height = area
    bbox = (x, y, x + width, y + height)

    previous_screenshot = None
    count = 0
    recording_active = True  # Flaga kontrolna

    try:
        while recording_active:
            # Zrób aktualny zrzut ekranu
            current_screenshot = ImageGrab.grab(bbox).convert("RGB")

            if previous_screenshot is not None:
                # Oblicz różnicę między poprzednim a bieżącym obrazem
                diff = ImageChops.difference(previous_screenshot, current_screenshot)
                diff_bbox = diff.getbbox()

                if diff_bbox:
                    diff_data = diff.crop(diff_bbox).getdata()
                    diff_pixels = sum(sum(pixel) for pixel in diff_data)
                    total_pixels = width * height * 255 * 3
                    diff_percent = (diff_pixels / total_pixels) * 100

                    if diff_percent > threshold:
                        output_file = os.path.join(folder, f"{datetime.now().strftime("%H-%M-%S")}.jpg")
                        current_screenshot.save(output_file, "JPEG", quality=85)
                        log.success(f"Zapisano zrzut ekranu: {output_file.replace("\\", "/").rsplit("/", 1)[1]}")
                        count += 1

            previous_screenshot = current_screenshot
            time.sleep(3)

    except KeyboardInterrupt:
        print("Monitoring zakończony.")

def stop_monitor_and_capture():
    global recording_active
    recording_active = False
    log.debug(f"Screenshotowanie zakończone. Screenshoty zostały zapisane")

if __name__ == "__main__":
    capture_area = select_area()
    if capture_area:
        log.info(f"Wybrano obszar: {capture_area}")
        output_folder = create_output_folder()
        monitor_and_capture(capture_area, output_folder)
    else:
        log.warning("Nie wybrano obszaru. Zamykanie aplikacji.")
