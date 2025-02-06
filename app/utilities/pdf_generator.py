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
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, ListFlowable, ListItem
from app.utilities.api.openai_api import summarize_transcription
from textwrap import wrap
import markdown2
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib.units import inch


def create_horizontal_line(width=450):
    """
    Tworzy poziomą linię jako element PDF.

    Args:
        width (int): Szerokość linii w punktach.

    Returns:
        Drawing: Obiekt rysunku do umieszczenia w dokumencie PDF.
    """
    line = Drawing(width, 5)
    line.add(Line(0, 0, width, 0, strokeWidth=1, strokeColor=colors.black))
    return line

def generate_pdf_from_files(output_pdf, screenshots_folder, transcripts_folder, full_transcription_path):
    """
    Generuje plik PDF na podstawie zrzutów ekranu (*.jpg) i transkrypcji (*.txt),
    sortując pliki według timestampów w nazwach.

    Args:
        output_pdf (str): Ścieżka do wyjściowego pliku PDF.
        screenshots_folder (str): Ścieżka do folderu zawierającego pliki zrzutów ekranu.
        transcripts_folder (str): Ścieżka do folderu zawierającego pliki transkrypcji.
        full_transcription_path (str): Ścieżka do pełnej transkrypcji do podsumowania.
    """
    # **Załaduj czcionkę obsługującą polskie znaki**
    styles_path = (os.getcwd().replace("\\", "/")).rsplit(r"/kreator-notatek-ze-spotkan")[0] + "/kreator-notatek-ze-spotkan/app/styles"
    font_path = f"{styles_path}/DejaVuSans.ttf"
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Nie znaleziono pliku czcionki: {font_path}")

    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))

    # **Pobierz podsumowanie AI**
    summary_data = summarize_transcription(full_transcription_path)

    # **Style dokumentu**
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontName="DejaVuSans",
        fontSize=18,
        alignment=1,
        spaceAfter=20,
    )
    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["Normal"],
        fontName="DejaVuSans",
        fontSize=12,
        leading=14,
    )

    list_style = ParagraphStyle(
        "ListStyle",
        parent=styles["Normal"],
        fontName="DejaVuSans",
        fontSize=12,
        leftIndent=20,
        leading=14,
    )

    # **Tworzenie dokumentu**
    doc = SimpleDocTemplate(output_pdf, pagesize=A4)
    elements = []

    # **Strona tytułowa**
    elements.append(Spacer(1, inch * 1.5))
    elements.append(Paragraph(" RAPORT ZE SPOTKANIA ", title_style))
    elements.append(create_horizontal_line())
    elements.append(Spacer(1, 10))
    elements.append(Spacer(1, 20))

    # **Tytuł spotkania**
    elements.append(Paragraph(f"<b>{summary_data.get('title', 'Brak tytułu')}</b>", title_style))
    elements.append(Spacer(1, 10))

    # **Podsumowanie**
    elements.append(Paragraph("<b>Podsumowanie spotkania:</b>", normal_style))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(summary_data.get("summary", "Brak podsumowania."), normal_style))
    elements.append(Spacer(1, 20))

    # **Najważniejsze punkty**
    elements.append(Paragraph("<b>Najważniejsze punkty:</b>", normal_style))
    key_points = summary_data.get("key_points", [])

    if key_points:
        points_list = [ListItem(Paragraph(f"• {point}", list_style)) for point in key_points]
        elements.append(ListFlowable(points_list, bulletType="bullet"))
    else:
        elements.append(Paragraph("Brak szczególnych punktów do wyróżnienia.", normal_style))

    elements.append(PageBreak())  # Przejście do nowej strony

    # **Dodawanie screenshotów i transkrypcji**
    screenshots = sorted([f for f in os.listdir(screenshots_folder) if f.endswith('.jpg')])
    transcripts = sorted([f for f in os.listdir(transcripts_folder) if f.endswith('.txt')])

    def extract_timestamp(filename):
        return tuple(map(int, filename.split('.')[0].split('-')))

    combined = sorted(
        [(f, 'screenshot') for f in screenshots] + [(f, 'transcript') for f in transcripts],
        key=lambda x: extract_timestamp(x[0])
    )

    for filename, file_type in combined:
        if file_type == 'screenshot':
            file_path = os.path.join(screenshots_folder, filename)
            try:
                elements.append(Image(file_path, width=400, height=250))
                elements.append(Spacer(1, 10))
            except Exception as e:
                print(f"Błąd dodawania obrazu {filename}: {e}")

        elif file_type == 'transcript':
            file_path = os.path.join(transcripts_folder, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()

                elements.append(Paragraph(text, normal_style))
                elements.append(Spacer(1, 15))
            except Exception as e:
                print(f"Błąd dodawania tekstu {filename}: {e}")

    # **Zapisz dokument**
    doc.build(elements)
    print(f"Raport PDF wygenerowany: {output_pdf}")