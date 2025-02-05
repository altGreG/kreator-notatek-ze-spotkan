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
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph, Image
from app.utilities.api.openai_api import summarize_transcription
from textwrap import wrap
import markdown2
from reportlab.lib import colors

def generate_pdf_from_files(output_pdf, screenshots_folder, transcripts_folder, full_transcription_path):
    """
    Generuje plik PDF na podstawie zrzutów ekranu (*.jpg) i transkrypcji (*.txt),
    sortując pliki według timestampów w nazwach. Dodaje stronę tytułową z podsumowaniem AI.

    Args:
        output_pdf (str): Ścieżka do wyjściowego pliku PDF.
        screenshots_folder (str): Ścieżka do folderu zawierającego pliki zrzutów ekranu.
        transcripts_folder (str): Ścieżka do folderu zawierającego pliki transkrypcji.
        full_transcription_path (str): Ścieżka do pełnej transkrypcji dla podsumowania AI.
    """

    # Rejestracja czcionki obsługującej polskie znaki
    styles_path = os.path.join(os.getcwd(), "styles")
    font_path = os.path.join(styles_path, "DejaVuSans.ttf")
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Nie znaleziono pliku czcionki: {font_path}")

    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))

    # Pobranie podsumowania AI i konwersja Markdown → HTML
    summary = summarize_transcription(full_transcription_path)
    summary_html = markdown2.markdown(summary)

    # Tworzenie dokumentu PDF
    doc = SimpleDocTemplate(output_pdf, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # STRONA TYTUŁOWA
    title_style = styles["Title"]
    title_style.fontName = "DejaVuSans"
    title_style.textColor = colors.black
    title_style.alignment = 1  # Wyśrodkowanie
    elements.append(Paragraph("📄 RAPORT ZE SPOTKANIA 📄", title_style))
    elements.append(Spacer(1, 20))

    # PODSUMOWANIE
    body_style = styles["BodyText"]
    body_style.fontName = "DejaVuSans"
    body_style.leading = 14  # Odstępy między liniami

    summary_paragraph = Paragraph(summary_html, body_style)
    elements.append(summary_paragraph)
    elements.append(Spacer(1, 30))

    # Nowa strona po podsumowaniu
    elements.append(Spacer(1, 50))

    # LISTA PLIKÓW (SCREENSHOTY + TRANSKRYPCJE)
    screenshots = sorted([f for f in os.listdir(screenshots_folder) if f.endswith('.jpg')])
    transcripts = sorted([f for f in os.listdir(transcripts_folder) if f.endswith('.txt')])

    def extract_timestamp(filename):
        return tuple(map(int, filename.split('.')[0].split('-')))

    screenshots = sorted(screenshots, key=extract_timestamp)
    transcripts = sorted(transcripts, key=extract_timestamp)

    combined = sorted([(f, 'screenshot') for f in screenshots] + [(f, 'transcript') for f in transcripts],
                      key=lambda x: extract_timestamp(x[0]))

    # Dodanie obrazów i transkrypcji do PDF
    for filename, file_type in combined:
        if file_type == 'screenshot':
            file_path = os.path.join(screenshots_folder, filename)
            try:
                img = Image(file_path, width=400, height=300)  # Ustawienie szerokości i wysokości obrazu
                elements.append(Spacer(1, 20))
                elements.append(img)
                elements.append(Spacer(1, 20))
            except Exception as e:
                print(f"Błąd podczas dodawania obrazu {filename}: {e}")

        elif file_type == 'transcript':
            file_path = os.path.join(transcripts_folder, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()

                text_html = markdown2.markdown(text)
                transcript_paragraph = Paragraph(text_html, body_style)
                elements.append(transcript_paragraph)
                elements.append(Spacer(1, 15))
            except Exception as e:
                print(f"Błąd podczas dodawania tekstu {filename}: {e}")

    # Zapisanie dokumentu PDF
    doc.build(elements)
    print(f"Raport PDF został wygenerowany: {output_pdf}")