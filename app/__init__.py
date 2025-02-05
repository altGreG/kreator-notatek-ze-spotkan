# app/__init__.py

"""Twórz notatki ze spotkań.

Moduły eksportowane przez tę paczkę:

- `window`: aplikacja GUI umożliwiająca zarządzanie sesjami nagrań i transkrypcji za pomocą intuicyjnego interfejsu użytkownika.
- `recorder`: zestaw funkcji do nagrywania obrazu i dźwięku na komputerze, w tym wybór obszaru ekranu oraz zapisanie fragmentów audio.
- `transcriptor`: zestaw funkcji do transkrypcji nagrań audio oraz formatowania uzyskanego tekstu w przejrzystą strukturę.
- `openai_api`: funkcje do generowania podsumowań transkrypcji za pomocą API OpenAI GPT-4.
- `mail_sender`: funkcje do wysyłania e-maili z załącznikami, np. z transkrypcjami lub podsumowaniami.
- `logger`: narzędzie do logowania informacji i komunikatów o błędach w aplikacji.
- `start_recording_and_screenshots`: moduł koordynujący procesy równoległego nagrywania, wykonywania zrzutów ekranu oraz transkrypcji.

Każdy z modułów odpowiada za określoną funkcjonalność, umożliwiając tworzenie pełnych notatek ze spotkań z wykorzystaniem nagrań, transkrypcji i podsumowań.
"""