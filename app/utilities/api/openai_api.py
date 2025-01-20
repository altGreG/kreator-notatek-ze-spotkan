import os
from openai import OpenAI
from loguru import logger as log

# Inicjalizacja klienta OpenAI
client = OpenAI(
    api_key=os.environ.get("GPT_API_KEY")  # Pobierz klucz API z zmiennych środowiskowych
)

def summarize_transcription(file_path):
    """
    Podsumowuje tekst transkrypcji z podanego pliku.

    Args:
        file_path (str): Ścieżka do pliku tekstowego z transkrypcją.

    Returns:
        str: Podsumowanie transkrypcji.
    """
    try:
        # Wczytaj treść transkrypcji z pliku
        with open(file_path, "r", encoding="utf-8") as file:
            transcription_text = file.read()

        # Wywołaj API OpenAI, aby wygenerować podsumowanie
        response = client.chat.completions.create(
            model="gpt-4o",  # Użyj modelu GPT-4o
            messages=[
                {"role": "system", "content": "Jesteś asystentem pomagającym podsumować transkrypcje w zwięzłej formie."},
                {"role": "user", "content": f"Podsumuj ten tekst:\n\n{transcription_text}. Usuń halucynacje"}
            ],
            max_tokens=200,  # Maksymalna długość podsumowania
            temperature=0.5  # Kontrola losowości w generacji tekstu
        )

        # Pobierz wygenerowane podsumowanie
        summary = response.choices[0].message.content
        return summary

    except Exception as e:
        log.error(f"Błąd podczas generowania podsumowania: {e}")
        return None

# Przykład użycia
if __name__ == "__main__":
    transcription_file = r"F:\kreator-notatek-ze-spotkan\app\spotkania\2025-01-18_23-07-50\full-2025-01-18_23-07-50.txt"  # Ścieżka do pliku transkrypcji
    summary = summarize_transcription(transcription_file)
    if summary:
        print("Podsumowanie:\n", summary)
