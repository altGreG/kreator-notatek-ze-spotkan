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
import json

# Inicjalizacja klienta OpenAI
client = OpenAI(
    api_key=os.environ.get("GPT_API_KEY")  # Pobierz klucz API z zmiennych środowiskowych
)


def summarize_transcription(file_path: str) -> dict:
    """
    Podsumowuje tekst transkrypcji z podanego pliku, generując format JSON.

    Args:
        file_path (str): Ścieżka do pliku tekstowego z transkrypcją.

    Returns:
        dict: Słownik zawierający podsumowanie transkrypcji w formacie JSON.
    """
    try:
        # Wczytaj treść transkrypcji z pliku
        with open(file_path, "r", encoding="utf-8") as file:
            transcription_text = file.read().strip()

        if not transcription_text:
            log.warning(f"Plik {file_path} jest pusty. Nie można wygenerować podsumowania.")
            return {
                "title": "Brak treści",
                "summary": "Nie znaleziono treści do podsumowania.",
                "key_points": []
            }

        # Wywołanie API OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Jesteś asystentem pomagającym podsumować transkrypcje w zwięzłej formie wraz ze szczegółami."
                },
                {
                    "role": "user",
                    "content": f"""
                    Podsumuj szczegółowo ten tekst w formacie JSON:\n\n{transcription_text}. 
                    Struktura powinna wyglądać następująco:

                    {{
                        "title": "Tytuł podsumowania",
                        "summary": "Krótki opis spotkania",
                        "key_points": [
                            "Najważniejszy punkt 1",
                            "Najważniejszy punkt 2",
                            "Najważniejszy punkt 3"
                        ]
                    }}

                    Usuń halucynacje i bądź precyzyjny.
                    """
                }
            ],
            max_tokens=1000,
            temperature=0.5
        )

        # **🔹 Logowanie pełnej odpowiedzi API**
        response_content = response.choices[0].message.content.strip()
        log.info(f"Treść odpowiedzi OpenAI: {response_content}")

        # **🔹 Usunięcie znaczników ```json i ```**
        if response_content.startswith("```json"):
            response_content = response_content[7:]  # Usuń pierwsze 7 znaków (```json)
        if response_content.endswith("```"):
            response_content = response_content[:-3]  # Usuń ostatnie 3 znaki (```)

        log.info(f"Oczyszczona treść JSON: {response_content}")

        # **🔹 Parsowanie JSON**
        try:
            summary_data = json.loads(response_content)
            log.info(f"Poprawnie sparsowane podsumowanie JSON: {summary_data}")
            return summary_data

        except json.JSONDecodeError as e:
            log.error(f"Błąd parsowania odpowiedzi JSON: {e}")
            log.error(f"Odpowiedź OpenAI po usunięciu znaczników: {response_content}")
            return {
                "title": "Błąd w generowaniu podsumowania",
                "summary": "Nie udało się wygenerować poprawnego podsumowania.",
                "key_points": []
            }

    except Exception as e:
        log.error(f"Błąd podczas generowania podsumowania: {e}")
        return {
            "title": "Błąd wewnętrzny",
            "summary": "Wystąpił nieoczekiwany błąd podczas generowania podsumowania.",
            "key_points": []
        }


# Przykład użycia
if __name__ == "__main__":
    transcription_file = r"F:\kreator-notatek-ze-spotkan\app\spotkania\2025-01-18_23-07-50\full-2025-01-18_23-07-50.txt"
    summary = summarize_transcription(transcription_file)
    if summary:
        print("Podsumowanie:")
        print(json.dumps(summary, indent=4, ensure_ascii=False))