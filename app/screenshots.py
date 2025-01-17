import os
import time
from datetime import datetime
from tkinter import Tk, Canvas
from PIL import ImageGrab, ImageChops

def select_area():
    """Pozwala użytkownikowi zaznaczyć obszar ekranu."""
    root = Tk()
    root.attributes('-fullscreen', True)
    root.attributes('-alpha', 0.3)
    root.title("Zaznacz obszar")

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
        root.quit()

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

def monitor_and_capture(area, folder, threshold=2):
    """Monitoruje zmiany w wybranym obszarze i zapisuje obraz, jeśli różnice przekraczają próg."""
    x, y, width, height = area
    bbox = (x, y, x + width, y + height)

    previous_screenshot = None
    count = 0
    print("Monitoring zmian. Naciśnij Ctrl+C, aby zatrzymać.")

    try:
        while True:
            # Zrób aktualny zrzut ekranu
            current_screenshot = ImageGrab.grab(bbox).convert("RGB")  # Upewnij się, że obraz jest w trybie RGB

            if previous_screenshot is not None:
                # Oblicz różnicę między poprzednim a bieżącym obrazem
                diff = ImageChops.difference(previous_screenshot, current_screenshot)
                diff_bbox = diff.getbbox()  # Sprawdź, czy jest jakakolwiek zmiana

                if diff_bbox:
                    # Oblicz procent różnicy
                    diff_data = diff.crop(diff_bbox).getdata()
                    diff_pixels = sum(sum(pixel) for pixel in diff_data)  # Sumujemy wartości R, G, B
                    total_pixels = width * height * 255 * 3  # 255 * 3 to maksymalna różnica (R+G+B) dla jednego piksela
                    diff_percent = (diff_pixels / total_pixels) * 100

                    if diff_percent > threshold:
                        # Zapisz obraz, jeśli różnica przekracza próg
                        output_file = os.path.join(folder, f"screenshot_{count:03d}.jpg")
                        current_screenshot.save(output_file, "JPEG", quality=85)
                        print(f"Zapisano zrzut ekranu: {output_file}")
                        count += 1

            # Zaktualizuj poprzedni obraz
            previous_screenshot = current_screenshot
            time.sleep(3)  # Monitoruj co sekundę

    except KeyboardInterrupt:
        print("Monitoring zakończony.")

if __name__ == "__main__":
    capture_area = select_area()
    if capture_area:
        print(f"Wybrano obszar: {capture_area}")
        output_folder = create_output_folder()
        monitor_and_capture(capture_area, output_folder)
    else:
        print("Nie wybrano obszaru. Zamykanie aplikacji.")