import os
import time
from datetime import datetime
from tkinter import Tk, Canvas, Button
from PIL import ImageGrab, ImageChops
from loguru import logger as log

recording_active = False

def select_area():
    """Pozwala użytkownikowi zaznaczyć obszar ekranu w nakładce."""
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


def create_output_folder():
    """Tworzy folder na zrzuty ekranu."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = f"screenshots/spotkanie-{timestamp}"
    os.makedirs(folder_name, exist_ok=True)
    return folder_name

def monitor_and_capture(area, folder,threshold=2.0):
    """Monitoruje zmiany w wybranym obszarze i zapisuje obraz, jeśli różnice przekraczają próg."""
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
                        output_file = os.path.join(folder, f"screenshot_{count:03d}.jpg")
                        current_screenshot.save(output_file, "JPEG", quality=85)
                        print(f"Zapisano zrzut ekranu: {output_file}")
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
        print(f"Wybrano obszar: {capture_area}")
        output_folder = create_output_folder()
        monitor_and_capture(capture_area, output_folder)
    else:
        print("Nie wybrano obszaru. Zamykanie aplikacji.")
