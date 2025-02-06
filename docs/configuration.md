# Windows
#### Instalacja Pythona
1. Ze strony python.org (https://www.python.org/downloads/windows/) pobierz najnowszą stabilną wersję Pythona.
2. W czasie instalacji kliknij 'Customize Installation' i upewnij się że masz zaznaczone opcje 'pip' oraz 'tcl/tk and idle'. Reszta jest opcjonalna.
3. Zainstaluj

#### Instalacja oprogramowania FFMPEG
1. Ze strony https://www.gyan.dev/ffmpeg/builds/ pobierz odpowiednią wersję ffpmpeg. Zip z programem znajdziesz w zakładce 'release builds'.
2. Rozpakuj program na swoim komputerze w wybranym miejscu, gdzie program zostanie już na stałe.
3. Nastepnie, aby mieć dostęp do funkcjonalności programu z poziomu terminala, dodaj ścieżkę do folder z plikiem ffmpeg.exe w zmiennych środowiskowych do zmiennej 'PATH'.
   Robimy to graficznie:

![EnvironmentVariables](./assets/EnvironmentVariableConfiguration.gif)

#### Konfiguracja ustawień audio
Włącz urządzenie audio o nazwie typu 'Mix Stereo', pozwoli ona na nagrywanie dżwięku na twoim komputerze.

![StereoMixConfiguration](./assets/StereoMixConfigurationCompressed.gif)

#### Dodanie klucza API do OPENAI
Aby dodać klucz api wykonaj komendę:
```bash
setx OPENAI_API_KEY "twój_klucz_api"
```

#### Dodanie hasła do serwera pocztowego
Aby dodać hasło aplikacji dla skonfigurowanego konta pocztowego gmail wykonaj komendę:
```bash
setx EMAIL_PASSWORD "twoje_hasło_aplikaci_google"
```
---

# Konfiguracja Pythona i uruchomienie programu (Windows i Linux)

### 1. Uruchom Pycharma i skonfiguruj środowisko

Otwórz projekt w Pycharmie, a IDE samo zaproponuje wykorzystanie do pobrania bibliotek zawartość requirements.txt i skonfiguruje środowisko.

### 2. Doinstaluj w konsoli z poziomu Pycharma dodatkowe zależności

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 
python -m pip install "mkdocstrings[python]"
```

### 3. Uruchom program, aby to zrobić należy uruchomić główny skrypt, którym jest `window.py`.

---

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

#### Dodanie klucza API do OPENAI
Aby dodać klucz api wykonaj komendę:
```bash
export OPENAI_API_KEY="twój_klucz_api"
```

#### Dodanie hasła do serwera pocztowego
Aby dodać hasło aplikacjii dla skonfigurowanego konta pocztowego gmail wykonaj komendę:
```bash
export EMAIL_PASSWORD="twoje_hasło_aplikaci_google"
```