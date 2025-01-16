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
project-folder/
│
├── app/
│   ├── nagrania/
│   │   └── audio/
│   │
│   ├── txt/
│   │
│   ├── __init__.py
│   ├── logger.py
│   ├── recorder.py
│   ├── saving.py
│   ├── transcriptor.py
│   └── window.py
│
├── docs/
│   ├── configuration.md
│   ├── index.md
│   └── reference.md
│
├── mkdocs.yml
└── requirements.txt
```

--- 

## Przegląd Projektu

::: app

