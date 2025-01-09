### Linux

W terminalu wykonujemy następujące komendy.
```bash
sudo apt-get install python3 python3-pip
sudo apt-get install python3-tk
sudo apt update && sudo apt install ffmpeg
pip install virtualenv 
python3 -m venv venv
source venv/bin/activate
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
---
### Windows
Ze strony python.org (https://www.python.org/downloads/windows/) pobieramy najnowszą stabilną wersję Pythona.
W czasie instalacji klikamy Customize Installation i upewniamy się że mamy zaznaczone opcje pip oraz tcl/tk and idle reszta jest opcjonalna. Instalujemy.

Ze strony https://www.gyan.dev/ffmpeg/builds/ pobieramy odpowiednią wrsję ffpmpeg. Zip z programem znajdziemy w zakładce release builds.
Program rozpakowujemy na naszym komputerze w wybranym przez nas miejscu gdzie program zostanie już na stałe.

Nastepnie aby mieć dostęp do funkcjonalności programu z poziomu terminala, dodajemy ścieżkę do folder z plikiem ffmpeg.exe w środku, robimy to graficznie lub za pomocą komendy
```bash
set PATH=%PATH%;C:\your\path\here;
```

W powershellu wykonujemy następujące komendy.
```bash
pip install virtualenv 
python -m venv env
env\Scripts\activate
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
---

Następnie możemy otworzyć projekt w Pycharmie, a IDE samo zaproponuje wykorzystanie stworzonego przez nas środowiska.

Aby uruchomić program, należy uruchomić główny skrypt, którym jest `window.py`.