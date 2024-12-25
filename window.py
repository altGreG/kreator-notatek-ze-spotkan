import tkinter as tk
from tkinter import messagebox, filedialog
from recorder import start_recording, stop_recording

# def start_recording():
#     status_label.config(text="Status: Nagrywanie w toku...")
#     # Placeholder funkcjonalność do nagrywania
#     print("Rozpoczynam nagrywanie...")
#
# def stop_recording():
#     status_label.config(text="Status: Nagrywanie zakończone.")
#     # Placeholder funkcjonalność zakończenia nagrywania
#     print("Nagrywanie zakończone.")

def generate_notes():
    # Placeholder funkcjonalność generowania notatek
    print("Generowanie notatek...")
    messagebox.showinfo("Notatki", "Notatki zostały wygenerowane!")

def open_file():
    file_path = filedialog.askopenfilename(title="Wybierz plik")
    if file_path:
        print(f"Wybrano plik: {file_path}")
        # Dodaj obsługę wczytywania pliku
        #Placeholder
def show_settings():
    # Placeholder okno ustawień
    messagebox.showinfo("Ustawienia", "Ustawienia aplikacji.")

def show_help():
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
file_menu.add_command(label="Nowe nagranie", command=start_recording)
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

start_button = tk.Button(record_frame, text="Rozpocznij nagrywanie", command=start_recording)
start_button.grid(row=0, column=0, padx=10)

stop_button = tk.Button(record_frame, text="Zakończ nagrywanie", command=stop_recording)
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
