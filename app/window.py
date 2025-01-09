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
from app.recorder import start_recording, stop_recording
from loguru import logger as log

def update_status(new_status: str) -> None:
    """
    Aktualizuje tekst widżetu statusu.

    Args:
        new_status: tekst do wyświetlenia w oknie statusu
    """
    status_label.config(text=f"Status: {new_status}")

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

def show_settings() -> None:
    """
    Włącza widoczność okna z ustawieniami programu.
    """
    # Placeholder okno ustawień
    messagebox.showinfo("Ustawienia", "Ustawienia aplikacji.")

def show_help() -> None:
    """
    Włącza widoczność okna z informacjami jak korzystać z programu.
    """
    # Placeholder okno pomocy
    messagebox.showinfo("Pomoc", "Pomoc aplikacji.")

# Tworzenie głównego okna aplikacji
app = tk.Tk()
app.title("Aplikacja do Nagrywania Spotkań")
app.geometry("600x400")

# Menu główne
menu_bar = tk.Menu(app)

# Menu Plik
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Nowe nagranie", command=lambda: start_recording(update_status))
file_menu.add_command(label="Otwórz...", command=open_file)
file_menu.add_separator()
file_menu.add_command(label="Wyjdź", command=app.quit)
menu_bar.add_cascade(label="Plik", menu=file_menu)

# Menu Ustawienia
settings_menu = tk.Menu(menu_bar, tearoff=0)
settings_menu.add_command(label="Ustawienia", command=show_settings)
menu_bar.add_cascade(label="Ustawienia", menu=settings_menu)

# Menu Pomoc
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="Pomoc", command=show_help)
menu_bar.add_cascade(label="Pomoc", menu=help_menu)

app.config(menu=menu_bar)

# Sekcja nagrywania
record_frame = tk.Frame(app)
record_frame.pack(pady=20)

start_button = tk.Button(record_frame, text="Rozpocznij nagrywanie", command=lambda: start_recording(update_status))
start_button.grid(row=0, column=0, padx=10)

stop_button = tk.Button(record_frame, text="Zakończ nagrywanie", command=lambda: stop_recording(update_status))
stop_button.grid(row=0, column=1, padx=10)

# Sekcja transkrypcji i notatek
transcription_frame = tk.LabelFrame(app, text="Transkrypcja", padx=10, pady=10)
transcription_frame.pack(fill="both", expand=True, padx=20, pady=10)

transcription_text = tk.Text(transcription_frame, height=10)
transcription_text.pack(fill="both", expand=True)

generate_notes_button = tk.Button(app, text="Generuj notatki", command=generate_notes)
generate_notes_button.pack(pady=10)

# Status
status_label = tk.Label(app, text="Status: Gotowe", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_label.pack(side=tk.BOTTOM, fill=tk.X)

# Uruchomienie aplikacji
app.mainloop()
