# app/window.py

"""Aplikacj GUI, trzon programu.

Główny skrypt w paczce, zawiera definicje i implementacje metod aplikacji GUI naszego programu.

Skrypt wymaga aby w środowisku Pythona w którym uruchamiasz ten skrypt zostały
zainstalowane następujące zależności:

    - `tkinter`
    - `loguru`

Do poprawnego działania skryptu należy zaimportować następujące funkcje:

    - `start_recording`,`stop_recording` z modułu app.recorder

Ten plik zawiera następujące funkcje:

    * update_status - aktualizuje wiadomość statusu w gui
    * generate_notes - zaczyna proces generowania notatek
    * open_file - pozwala na wczytanie pliku mp4
    * show_settings - włącza widok okna ustawień w gui
    * show_help - włącza widok okna z pomocą w gui
"""

# TODO(altGreG): Zaktualizować docstrings

import tkinter as tk
from tkinter import messagebox, filedialog

from app.start_recording_and_screenshots import start_recording_and_screenshots, stop_recording_and_screenshots
from recorder_audio import start_recording, stop_recording
from loguru import logger as log
from PIL import Image, ImageDraw, ImageTk, ImageFont
import os  # Do obsługi ścieżek plików
import webbrowser
import subprocess




# Ścieżka do pliku czcionki Open Sans
font_path = r".\styles\OpenSans-ExtraBoldItalic.ttf"
selected_audio_device = None  # Globalna zmienna na wybrane urządzenie
if not os.path.exists(font_path):
    raise FileNotFoundError(f"Plik czcionki nie został znaleziony: {font_path}")

def update_status(new_status):
    """
    Aktualizuje tekst widżetu statusu i wyśrodkowuje go.
    """
    def update_label():
        font_size = 20
        font = ImageFont.truetype(font_path, font_size)
        text = f"Status: {new_status}"

        # Obliczamy wymiary tekstu
        text_bbox = font.getbbox(text)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
        img_width, img_height = 600, 50  # Wymiary obrazu dopasowane do aplikacji
        img = Image.new("RGBA", (img_width, img_height), (102, 98, 151, 0))
        draw = ImageDraw.Draw(img)

        # Rysujemy tekst na środku obrazu
        x = (img_width - text_width) // 2
        y = (img_height - text_height) // 2
        draw.text((x, y), text, font=font, fill="black")

        # Konwertujemy obraz na format zgodny z tkinter
        tk_image = ImageTk.PhotoImage(img)

        # Ustawiamy obraz w widżecie status_label
        status_label.config(image=tk_image)
        status_label.image = tk_image

    # Wykonaj aktualizację w głównym wątku
    app.after(0, update_label)


def generate_notes() -> None:
    """
    Uruchamia proces generowania notatek.
    """
    # Placeholder funkcjonalność generowania notatek
    log.debug("Generowanie notatek...")
    messagebox.showinfo("Notatki", "Notatki zostały wygenerowane!")

def open_file() -> None:
    """
    Pozwala na pobranie ścieżki do pliku mp4 wybranego w eksploratorze plików.
    """
    file_path = filedialog.askopenfilename(title="Wybierz plik")
    if file_path:
        log.debug(f"Wybrano plik: {file_path}")
        # Dodaj obsługę wczytywania pliku
        # Placeholder

selected_audio_device = None  # Globalna zmienna na wybrane urządzenie

def show_settings():
    """
    Wyświetla okno ustawień, w którym użytkownik może wybrać urządzenie audio.
    """
    global selected_audio_device

    # Tworzenie okna ustawień
    settings_window = tk.Toplevel(app)
    settings_window.title("Ustawienia")
    settings_window.geometry("300x300")  # Ustawienie rozmiaru okna
    settings_window.resizable(False, False)  # Zablokowanie możliwości zmiany rozmiaru
    settings_window.configure(bg="#ebe4d6")

    tk.Label(settings_window, text="Wybierz urządzenie audio:", bg="#ebe4d6", font=("Arial", 12)).pack(pady=10)

    # Pobierz listę urządzeń audio
    devices = get_audio_devices()
    if not devices:
        tk.Label(settings_window, text="Brak dostępnych urządzeń audio.", bg="#ebe4d6", fg="red").pack()
        return

    # Pole wyboru urządzenia audio - brak domyślnego zaznaczenia
    device_var = tk.StringVar(value="UNSELECTED")  # Ustaw wartość początkową na niestandardową

    # Tworzenie przycisków radiowych
    for device in devices:
        tk.Radiobutton(
            settings_window,
            text=device,
            variable=device_var,
            value=device,
            bg="#ebe4d6",
            font=("Arial", 10)
        ).pack(anchor="w", padx=20)

    def save_settings():
        nonlocal device_var
        global selected_audio_device
        if device_var.get() == "UNSELECTED":
            messagebox.showwarning("Brak wyboru", "Proszę wybrać urządzenie audio przed zapisaniem ustawień.")
            return
        selected_audio_device = device_var.get()
        log.debug(f"Wybrane urządzenie audio: {selected_audio_device}")
        settings_window.destroy()

    # Tworzenie okrągłego przycisku zapisu
    save_button = create_circle_button(
        settings_window,
        x=125,  # Pozycja przycisku w oknie
        y=200,
        size=50,  # Rozmiar przycisku
        text="✔️",  # Tekst na przycisku
        fill_color="#ad9d99",  # Kolor wypełnienia przycisku
        outline_color="black",  # Kolor obramowania
        command=save_settings  # Funkcja wywoływana po kliknięciu
    )


def show_help() -> None:
    """
    Przekierowuje do dokumentacji pomocy online.
    """
    url = "https://github.com/altGreG/kreator-notatek-ze-spotkan/blob/main/docs/configuration.md"
    webbrowser.open_new_tab(url)

def show_transcription_window():
    """
    Otwiera nowe okno do wyświetlania transkrypcji z paskiem przewijania, z możliwością zmiany rozmiaru.
    """
    # Sprawdź, czy okno transkrypcji już istnieje
    if hasattr(show_transcription_window, "transcription_window") and show_transcription_window.transcription_window.winfo_exists():
        show_transcription_window.transcription_window.deiconify()  # Przywróć okno, jeśli zostało zminimalizowane
        return

    # Tworzenie nowego okna
    transcription_window = tk.Toplevel(app)
    transcription_window.title("Transkrypcja")
    transcription_window.geometry("400x400")  # Początkowy rozmiar okna
    transcription_window.configure(bg="#ebe4d6")

    # Tworzenie ramki dla paska przewijania i pola tekstowego
    frame = tk.Frame(transcription_window, bg="#ebe4d6")
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Tworzenie paska przewijania
    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")

    # Tworzenie pola tekstowego
    transcription_text = tk.Text(
        frame,
        bg="white",
        fg="black",
        font=("Arial", 12),  # Czcionka dla tekstu w transkrypcji
        relief=tk.FLAT,  # Brak obramowania tekstowego
        state="disabled",  # Ustawienie pola jako tylko do odczytu
        wrap="word",  # Zawijanie tekstu w oknie
        yscrollcommand=scrollbar.set  # Powiązanie paska przewijania z polem tekstowym
    )
    transcription_text.pack(side="left", fill="both", expand=True)

    # Powiązanie paska przewijania z polem tekstowym
    scrollbar.config(command=transcription_text.yview)

    # Przechowywanie odniesienia do pola tekstowego
    show_transcription_window.transcription_text = transcription_text
    show_transcription_window.transcription_window = transcription_window

# Tworzenie głównego okna aplikacji
app = tk.Tk()
app.title("Aplikacja do Nagrywania Spotkań")
app.resizable(False, False)
app.configure(bg="#ebe4d6")
app.attributes("-topmost", True)  # Always on top

# Obliczanie pozycji dla prawego dolnego rogu
screen_width = app.winfo_screenwidth()  # Szerokość ekranu
screen_height = app.winfo_screenheight()  # Wysokość ekranu

# Rozmiar okna aplikacji
window_width = 550
window_height = 225

# Pozycja w prawym dolnym rogu
x_position = screen_width - window_width - 10  # 10px od prawej krawędzi
y_position = screen_height - window_height - 20  # 50px od dolnej krawędzi (dla taskbara)

# Ustawienie pozycji okna
app.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")



# Funkcja do animowanego rozwijania i zwijania przycisków
def animate_buttons(buttons, target_positions, duration=200, step=10):
    """Animuje przesuwanie przycisków do docelowych pozycji.

    Args:
        buttons: Lista przycisków do animacji.
        target_positions: Lista docelowych współrzędnych (x, y) dla każdego przycisku.
        duration: Całkowity czas animacji w ms.
        step: Liczba kroków w animacji.
    """
    current_positions = [(button.winfo_x(), button.winfo_y()) for button in buttons]
    dx_dy = [
        ((tx - cx) / step, (ty - cy) / step)
        for (cx, cy), (tx, ty) in zip(current_positions, target_positions)
    ]

    def move_step(i=0):
        if i < step:
            for button, (dx, dy) in zip(buttons, dx_dy):
                button.place(x=button.winfo_x() + dx, y=button.winfo_y() + dy)
            app.after(duration // step, lambda: move_step(i + 1))
        else:
            # Ustaw przyciski na dokładne pozycje docelowe
            for button, (tx, ty) in zip(buttons, target_positions):
                button.place(x=tx, y=ty)

    move_step()

# Funkcja do rozwijania i zwijania przycisków z animacją
def toggle_menu_buttons(canvas, main_button, buttons):
    # Sprawdź, czy menu jest rozwinięte
    if not hasattr(toggle_menu_buttons, "menu_visible"):
        toggle_menu_buttons.menu_visible = False

    if toggle_menu_buttons.menu_visible:  # Jeśli menu jest rozwinięte
        # Ukryj przyciski przez animację w kierunku głównego przycisku
        target_positions = [(10, 10) for _ in buttons]
        animate_buttons(buttons, target_positions, duration=200, step=10)
        app.after(210, lambda: [button.place_forget() for button in buttons])  # Ukryj przyciski po animacji
    else:
        # Wyświetl przyciski w odpowiednich pozycjach z animacją
        for button in buttons:
            button.place(x=10, y=10)  # Ustaw startową pozycję przycisków
        target_positions = [(60, 10), (110, 10), (160, 10)]
        animate_buttons(buttons, target_positions, duration=200, step=10)

    # Zmień stan menu
    toggle_menu_buttons.menu_visible = not toggle_menu_buttons.menu_visible


# Funkcja do stworzenia przycisku okrągłego (z obrazem lub tekstem)
def create_circle_button(parent, x, y, size, text, fill_color, outline_color, command):
    scale = 2
    high_res_size = size * scale

    # Tworzenie obrazu
    img = Image.new("RGBA", (high_res_size, high_res_size), (102, 98, 151, 0))  # Przezroczyste tło dopasowane do aplikacji
    draw = ImageDraw.Draw(img)
    draw.ellipse((0, 0, high_res_size-1, high_res_size-1), fill=fill_color, outline=outline_color, width=2 * scale)

    # Zmniejszenie obrazu do oryginalnego rozmiaru
    img_resized = img.resize((size, size), resample=Image.Resampling.LANCZOS)
    button_image = ImageTk.PhotoImage(img_resized)

    # Tworzenie przycisku
    button = tk.Button(
        parent,
        text=text,
        image=button_image,
        compound="center",
        font=("Arial", 12),
        fg="black",
        bg="#ebe4d6",  # Kolor tła zgodny z aplikacją
        activebackground="#ebe4d6",  # Tło w stanie aktywnym
        highlightthickness=0,  # Usunięcie obramowania
        bd=0,  # Brak ramki
        command=command
    )
    button.image = button_image  # Zachowanie referencji do obrazu
    button.place(x=x, y=y, width=size, height=size)  # Umieszczanie przycisku
    return button

# Funkcja tworząca główny przycisk menu
def create_main_menu(canvas, app):
    # Przyciski dodatkowe
    buttons = []

    # Dodanie przycisku "Ustawienia"
    settings_button = create_circle_button(app, x=0, y=0, size=40, text="⚙", fill_color="#ad9d99",
                                           outline_color="black", command=show_settings)
    buttons.append(settings_button)

    # Dodanie przycisku "Pomoc"
    help_button = create_circle_button(app, x=0, y=0, size=40, text="?", fill_color="#ad9d99",
                                       outline_color="black", command=show_help)
    buttons.append(help_button)

    # Dodanie przycisku "Wyjdź"
    exit_button = create_circle_button(app, x=0, y=0, size=40, text="✖", fill_color="#ad9d99",
                                       outline_color="black", command=app.quit)
    buttons.append(exit_button)

    # Ukrywanie przycisków na starcie
    for button in buttons:
        button.place_forget()

    # Główny przycisk menu
    main_menu_button = create_circle_button(app, x=10, y=10, size=40, text="☰", fill_color="#ad9d99",
                                            outline_color="black",
                                            command=lambda: toggle_menu_buttons(canvas, main_menu_button, buttons))
    return main_menu_button, buttons

# Tworzenie głównego przycisku menu i dodatkowych przycisków
main_menu_button, buttons = create_main_menu(None, app)

# Tworzenie płótna dla przycisku menu (niepotrzebne w tej wersji, ale zostaje)
canvas = tk.Canvas(app, width=50, height=50, bg="#ebe4d6", highlightthickness=0)
canvas.place(x=1, y=1)

# Tworzenie głównego menu z rozwijanymi przyciskami
create_main_menu(canvas, app)

# Ładowanie czcionki Open Sans
open_sans_font = (font_path, 20)

# Tworzenie widżetu status_label
status_label = tk.Label(app, bg="#ebe4d6")
status_label.place(relx=0.5, y=80, anchor="center")  # Wyśrodkowanie względem okna
# Ustawienie początkowego statusu
update_status("Gotowe")

# Przyciski
button_frame = tk.Frame(app, bg="#ebe4d6")
button_frame.place(relx=0.5, y=160, anchor="center")


# Rozpocznij nagrywanie
start_button = create_circle_button(
    button_frame,
    x=0,
    y=0,
    size=60,
    text="▶",
    fill_color="#ad9d99",
    outline_color="black",
    command=lambda: start_recording_and_screenshots(update_status, selected_audio_device, app)
)
start_button.config(font=("Arial", 24))
start_button.grid(row=0, column=0, padx=10)

# Zatrzymaj nagrywanie
stop_button = create_circle_button(
    button_frame,
    x=0,
    y=0,
    size=60,
    text="◼",
    fill_color="#ad9d99",
    outline_color="black",
    command=lambda: stop_recording_and_screenshots(update_status)
)
stop_button.config(font=("Arial", 24))
stop_button.grid(row=0, column=1, padx=10)

# Pokaż transkrypcję
show_transcription_button = create_circle_button(
    button_frame,
    x=0,
    y=0,
    size=60,
    text="📄",
    fill_color="#ad9d99",
    outline_color="black",
    command=show_transcription_window
)
show_transcription_button.config(font=("Arial", 22))
show_transcription_button.grid(row=0, column=2, padx=10)

# Generuj notatki
notes_button = create_circle_button(
    button_frame,
    x=0,
    y=0,
    size=60,
    text="✎",
    fill_color="#ad9d99",
    outline_color="black",
    command=generate_notes
)
notes_button.config(font=("Arial", 24))
notes_button.grid(row=0, column=3, padx=10)

def get_audio_devices():
    """
    Pobiera listę dostępnych urządzeń audio za pomocą FFmpeg.
    """
    try:
        result = subprocess.run(
            ["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
        devices = []
        for line in result.stderr.splitlines():
            if "(audio)" in line:
                # Wyodrębnij nazwę urządzenia
                device = line.split('"')[1]
                devices.append(device)
        return devices
    except Exception as e:
        log.error(f"Błąd podczas pobierania urządzeń audio: {e}")
        return []


# Uruchomienie aplikacji
app.mainloop()
