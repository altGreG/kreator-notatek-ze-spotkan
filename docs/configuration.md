# Linux

#### Instalacja Pythona
```bash
sudo apt-get install python3 python3-pip
sudo apt-get install python3-tk
```
#### Instalacja oprogramowania FFMPEG
```bash
sudo apt update && sudo apt install ffmpeg
```
#### Stworzenie wirtualnego środowiska
```bash
pip install virtualenv 
python3 -m venv venv
# wejdź do stworzonego środowiska
source venv/bin/activate
```
---
# Windows
#### Instalacja Pythona
1. Ze strony python.org (https://www.python.org/downloads/windows/) pobierz najnowszą stabilną wersję Pythona.
2. W czasie instalacji kliknij 'Customize Installation' i upewnij się że masz zaznaczone opcje 'pip' oraz 'tcl/tk and idle'. Reszta jest opcjonalna.
3. Zainstaluj

#### Instalacja oprogramowania FFMPEG
1. Ze strony https://www.gyan.dev/ffmpeg/builds/ pobierz odpowiednią wersję ffpmpeg. Zip z programem znajdziesz w zakładce 'release builds'.
2. Rozpakuj program na swoim komputerze w wybranym miejscu, gdzie program zostanie już na stałe.
3. Nastepnie, aby mieć dostęp do funkcjonalności programu z poziomu terminala, dodaj ścieżkę do folder z plikiem ffmpeg.exe w zmiennych środowiskowych do zmiennej 'PATH'.
   Robimy to graficznie lub za pomocą komendy:
```bash
set PATH=%PATH%;C:\your\path\here;
```

#### Konfiguracja ustawień audio
Włącz urządzenie audio o nazwie typu 'Mix Stereo', pozwoli ona na nagrywanie dżwięku na twoim komputerze.

![StereoMixConfiguration](./assets/StereoMixConfigurationCompressed.gif)

#### Stworzenie wirtualne środowisko
```bash
pip install virtualenv 
python -m venv env
# wejdź do stworzonego środowiska
env\Scripts\activate
```
---

# Konfiguracja Pythona i uruchomienie programu (Windows i Linux)

1. Zainstaluj potrzebne zaleźności (zrób to w wirtualnym środowisku)
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
python -m pip install "mkdocstrings[python]"
pip install -r requirements.txt
# or
pip install -U openai-whisper
pip install setuptools-rust
pip install speechrecognition
pip install openai
pip install google-cloud-speech
pip install protobuf
pip install loguru
python -m pip install mkdocs
python -m pip install mkdocs-material

python -m pip list
```
1. Otwórz projekt w Pycharmie, a IDE samo zaproponuje wykorzystanie stworzonego przez nas środowiska.
2. Uruchom program, aby to zrobić należy uruchomić główny skrypt, którym jest `window.py`.