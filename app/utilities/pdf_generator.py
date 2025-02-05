# app/utilities/pdf_generator.py

"""Moduł generowania pliku PDF z zrzutów ekranu i transkrypcji

Skrypt umożliwia generowanie pliku PDF, który łączy zrzuty ekranu (*.jpg) oraz transkrypcje (*.txt),
sortując pliki na podstawie timestampów zawartych w nazwach plików. Zrzuty ekranu i transkrypcje są dodawane
do pliku PDF w odpowiedniej kolejności.

Wymagane zależności

Aby uruchomić skrypt, należy zainstalować następujące pakiety w środowisku Python:

    - reportlab: Biblioteka do generowania plików PDF

Do prawidłowego działania aplikacji należy zaimportować:

    - generate_pdf_from_files z modułu app.pdf_generator, która generuje plik PDF na podstawie plików z folderów
      zawierających zrzuty ekranu i transkrypcje.

Skrypt może być używany jako moduł i zawiera następującą funkcję:

    * generate_pdf_from_files - Generuje plik PDF na podstawie zrzutów ekranu i transkrypcji, sortując je według
      timestampów w nazwach plików.

Każda funkcja zawiera mechanizmy obsługi błędów oraz odpowiednie komunikaty dla użytkownika.
"""


import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from app.utilities.api.openai_api import summarize_transcription
from textwrap import wrap


def generate_pdf_from_files(output_pdf, screenshots_folder, transcripts_folder, full_transcription_path):
    """
    Generuje plik PDF na podstawie zrzutów ekranu (*.jpg) i transkrypcji (*.txt),
    sortując pliki według timestampów w nazwach.

    Args:
        output_pdf (str): Ścieżka do wyjściowego pliku PDF.
        screenshots_folder (str): Ścieżka do folderu zawierającego pliki zrzutów ekranu.
        transcripts_folder (str): Ścieżka do folderu zawierającego pliki transkrypcji.
        full_transcription_path (str): Ścieżka do pełnej transkrypcji dla podsumowania AI.
    """
    # Rejestracja czcionki obsługującej polskie znaki
    styles_path = (os.getcwd().replace("\\", "/")).rsplit(r"/kreator-notatek-ze-spotkan")[0] + "/kreator-notatek-ze-spotkan/app/styles"
    font_path = f"{styles_path}/DejaVuSans.ttf"  # Ścieżka do pliku czcionki
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Nie znaleziono pliku czcionki: {font_path}")

    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))

    # Pobierz podsumowanie AI
    summary = summarize_transcription(full_transcription_path)

    # Tworzenie dokumentu PDF
    c = canvas.Canvas(output_pdf, pagesize=A4)
    width, height = A4
    margin = 50  # Marginesy dla tekstu

    ### 1️⃣ Strona tytułowa ###
    c.setFont("DejaVuSans", 22)
    c.drawCentredString(width / 2, height - 150, "📄 RAPORT ZE SPOTKANIA 📄")

    c.setFont("DejaVuSans", 12)

    # Dostosowanie podsumowania - zawijanie tekstu
    max_width = width - 2 * margin
    wrapped_summary = wrap(summary, width=80)  # Dostosuj liczbę znaków w linii

    # Ustawienie pozycji startowej dla tekstu podsumowania
    y_position = height - 200

    for line in wrapped_summary:
        c.drawString(margin, y_position, line)
        y_position -= 15  # Przesunięcie w dół

        if y_position < 100:  # Jeśli zabraknie miejsca na stronie, nowa strona
            c.showPage()
            c.setFont("DejaVuSans", 12)
            y_position = height - margin

    c.showPage()  # Przejście do kolejnej strony po podsumowaniu

    ### 2️⃣ Kolejne strony - zrzuty ekranu i transkrypcja ###
    screenshots = sorted([f for f in os.listdir(screenshots_folder) if f.endswith('.jpg')])
    transcripts = sorted([f for f in os.listdir(transcripts_folder) if f.endswith('.txt')])

    def extract_timestamp(filename):
        return tuple(map(int, filename.split('.')[0].split('-')))

    screenshots = sorted(screenshots, key=extract_timestamp)
    transcripts = sorted(transcripts, key=extract_timestamp)

    combined = sorted([(f, 'screenshot') for f in screenshots] + [(f, 'transcript') for f in transcripts],
                      key=lambda x: extract_timestamp(x[0]))

    y_position = height - margin

    for filename, file_type in combined:
        if file_type == 'screenshot':
            file_path = os.path.join(screenshots_folder, filename)
            try:
                img = ImageReader(file_path)
                img_width, img_height = img.getSize()
                aspect_ratio = img_width / img_height

                display_width = width - 2 * margin
                display_height = display_width / aspect_ratio

                if y_position - display_height < margin:
                    c.showPage()
                    y_position = height - margin

                c.drawImage(img, margin, y_position - display_height, display_width, display_height, preserveAspectRatio=True)
                y_position -= (display_height + 20)
            except Exception as e:
                print(f"Błąd podczas dodawania obrazu {filename}: {e}")

        elif file_type == 'transcript':
            file_path = os.path.join(transcripts_folder, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()

                c.setFont("DejaVuSans", 10)
                lines = text.splitlines()

                for line in lines:
                    words = line.split()
                    line_buffer = ""

                    for word in words:
                        if c.stringWidth(line_buffer + word + " ", "DejaVuSans", 10) < (width - 2 * margin):
                            line_buffer += word + " "
                        else:
                            c.drawString(margin, y_position, line_buffer.strip())
                            y_position -= 15

                            if y_position < margin:
                                c.showPage()
                                y_position = height - margin

                            line_buffer = word + " "

                    if line_buffer:
                        c.drawString(margin, y_position, line_buffer.strip())
                        y_position -= 15

                        if y_position < margin:
                            c.showPage()
                            y_position = height - margin

            except Exception as e:
                print(f"Błąd podczas dodawania tekstu {filename}: {e}")

        if y_position < margin:
            c.showPage()
            y_position = height - margin

    c.save()
    print(f"Raport PDF został wygenerowany: {output_pdf}")
