# app/__init__.py

"""Twórz notatki ze spotkań.

Moduły eksportowane przez tę paczkę:

- `window`: aplikacja GUI, która zarządza interfejsem użytkownika.
- `recorder`: zestaw funkcji do nagrywania obrazu i dźwięku na komputerze.
- `transcriptor`: zestaw funkcji do transkrypcji audio oraz formatowania tekstu transkrypcji.
- `openai_api`: funkcje do generowania podsumowań transkrypcji za pomocą API OpenAI GPT-4.
- `mail_sender`: funkcje do wysyłania e-maili z załącznikami, np. z transkrypcjami lub podsumowaniami.
- `logger`: narzędzie do logowania informacji i komunikatów o błędach w aplikacji.

Każdy z modułów odpowiada za określoną funkcjonalność, umożliwiając tworzenie pełnych notatek ze spotkań z wykorzystaniem nagrań, transkrypcji i podsumowań.
"""