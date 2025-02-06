[//]: # (TODO: Uzupełnić dokumentacjcję)

## Wstęp
Strona dokumentacji do projektu `Kreator Notatek
ze Spotkań`, projektu wykonywanego w ramach zajęć z IO 2024/2025.

Celem projektu jest zbudowanie programu, który będzie w stanie na podstawie
nagrań spotkań z aplikacji do telekonferencji, stworzyć notatki. Wygenerowane notatki będą się składać z transkrypcji audio
słów wypowiedzianych przez uczestników i zrzutów ekranu prezentacji przedstawianych na spotkaniu.

---

## Spis Treści

1. [Konfiguracja](configuration.md)
2. [Referencja](reference.md)

---

## Struktura Katalogowa

```
kreator-notatek-ze-spotkan
├── .venv
├── app
│   ├── spotkania
│   ├── styles
│   ├── utilities
│   │   ├── api
│   │   │   ├── __init__.py
│   │   │   ├── api_key.txt
│   │   │   ├── openai_api.py
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── mail_sender.py
│   │   ├── pdf_generator.py
│   │   ├── recording_utils.py
│   │   ├── saving.py
│   ├── recorder_audio.py
│   ├── screenshots.py
│   ├── start_recording_and_screenshots.py
│   ├── transcriptor.py
│   └── window.py
├── docs
│   ├── assets
│   ├── modules
│   │   ├── utilities
│   │   │   └── ...
│   │   ├── recorder_audio.md
│   │   ├── screenshots.md
│   │   ├── start_recording_and_screenshots.md
│   │   ├── transcriptor.md
│   │   └──  window.md
│   ├── configuration.md
│   └── index.md
├── site
├── software
├── tests
├── .gitignore
├── mkdocs.yml
├── README.md
└── requirements.txt
```

--- 

## Przegląd Projektu

::: app

---

## Implementacje funkcjonalności

1. [Moduł window.py](modules/window.md)
2. [Moduł transcriptor.py](modules/transcriptor.md)
3. [Moduł screenshots.py](modules/screenshots.md)
4. [Moduł recorder_audio.py](modules/recorder_audio.md)
5. [Moduł start_recording_and_screenshots.py](modules/start_recording_and_screenshots.md)
6. [Moduł saving.py](modules/utilities/saving.md)
7. [Moduł recording_utils.py](modules/utilities/recording_utils.md)
8. [Moduł pdf_generator.py](modules/utilities/pdf_generator.md)
9. [Moduł mail_sender.py](modules/utilities/mail_sender.md)
10. [Moduł logger.py](modules/utilities/logger.md)
11. [Moduł openai_api.py](modules/utilities/api/openai_api.md)

