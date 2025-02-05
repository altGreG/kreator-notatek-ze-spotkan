# app/utilities/api/openai_api.py

"""Moduł podsumowania transkrypcji przy użyciu OpenAI GPT-4

Skrypt umożliwia generowanie zwięzłego podsumowania tekstów transkrypcji przy użyciu modelu GPT-4. Użytkownik podaje
ścieżkę do pliku tekstowego z transkrypcją, a skrypt wywołuje API OpenAI w celu wygenerowania streszczenia, które
następnie zwraca. Funkcja `summarize_transcription` obsługuje wczytanie pliku, komunikację z API OpenAI oraz zwrócenie
podsumowanego tekstu.

Wymagane zależności

Aby uruchomić skrypt, należy zainstalować następujące pakiety w środowisku Python:

    - openai: Klient do korzystania z API OpenAI GPT
    - loguru: Rozbudowany system logowania

Do prawidłowego działania aplikacji należy zaimportować:

    - log z biblioteki loguru, służącej do logowania komunikatów o błędach i informacji o działaniu aplikacji.

Skrypt może być używany jako moduł i zawiera następującą funkcję:

    * summarize_transcription - Przyjmuje plik transkrypcji tekstowej, przesyła jego zawartość do API OpenAI GPT-4, a następnie generuje podsumowanie tekstu.

Każda funkcja zawiera odpowiednie mechanizmy obsługi błędów, logowania oraz komunikatów dla użytkownika.
"""

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
