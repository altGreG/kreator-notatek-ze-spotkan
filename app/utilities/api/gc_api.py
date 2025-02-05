"""Moduł transkrypcji audio z wykorzystaniem Google Cloud Speech-to-Text

Skrypt umożliwia transkrypcję plików audio przy użyciu usługi Google Cloud Speech-to-Text. Użytkownik musi posiadać odpowiedni
plik autoryzacyjny w formacie JSON, aby połączyć się z API Google Cloud. Funkcja `transcribe_with_gcloud` obsługuje proces
autoryzacji, przesyłania pliku audio oraz odbierania transkrypcji, zapewniając logowanie oraz aktualizację statusu w aplikacji GUI.

Wymagane zależności

Aby uruchomić skrypt, należy zainstalować następujące pakiety w środowisku Python:

    - google-cloud-speech: Klient do korzystania z API Google Cloud Speech-to-Text
    - google-auth: Obsługa autoryzacji do usług Google Cloud
    - loguru: Rozbudowany system logowania

Do prawidłowego działania aplikacji należy zaimportować:

    - log_status z modułu app.utilities.logger, służącą do logowania komunikatów statusowych.

Skrypt może być używany jako moduł i zawiera następującą funkcję:

    * transcribe_with_gcloud - Wykonuje transkrypcję pliku audio przy pomocy API Google Cloud Speech-to-Text.
      Obsługuje autoryzację, wczytywanie pliku audio oraz transkrypcję tekstu z dźwięku w formacie MP3.

Każda funkcja zawiera odpowiednie mechanizmy obsługi błędów, logowania oraz komunikatów dla użytkownika.
"""

from loguru import logger as log
from app.utilities.logger import log_status
from google.oauth2 import service_account
from google.cloud import speech
import io
import os

# TODO(altGreG): Na razie program może obsłużyć pliki audio o długości do 1 minuty, do poprawy
def transcribe_with_gcloud(audio_file_path: str, update_status: any) -> tuple[str, str | None]:
    """
    Transkrypcja audio z wykorzystaniem API do usługi Speech to Text na Google Cloud

    Args:
        audio_file_path: ścieżka do pliku z audio
        update_status: metoda aplikacji gui (aktualizacja wiadomości statusu)

    Returns:
        nazwa pliku audio, którego dotyczy transkrypcja i przetranskrybowany tekst | nazwa pliku i None w razie błędu
    """


    log_status("Przygotowanie do transkrypcji audio.", "info", update_status)

    filename_and_path, ext = os.path.splitext(audio_file_path)
    filename = (filename_and_path.replace("\\", "/")).split("/")[-1]
    audio_file_path = audio_file_path.replace("\\", "/")

    log.debug(f"Filename: {filename}  |  Ext: {ext}")

    """
    Utworzenie obiektu do autoryzacji dostępu do usług Google Cloud
    Uwaga: Użytkownik sam musi pozyskać plik JSON do autoryzacji w Google Cloud API
    """
    try:
        client_file = '../sa_gc.json'
        credentials = service_account.Credentials.from_service_account_file(client_file)
        client = speech.SpeechClient(credentials=credentials)
        log_status("Załadowanie pliku autoryzacyjnego do usług Google Cloud, konfiguracja.", "info", update_status)
    except Exception as err:
        log_status("Brak pliku autoryzacyjnego do usług Google Cloud, brak dostępu.", "error", update_status)
        log.error(f"Błąd: {err}")
        return filename, None

    try:
        with io.open(audio_file_path, mode="rb") as audio_file:
            content = audio_file.read()
            audio = speech.RecognitionAudio(content=content)
        log.debug("Wczytano plik audio.")
    except Exception as err:
        log_status(f"Błąd w czasie wczytywania pliku audio.", "error", update_status)
        log.error(f"Błąd: {err}")
        return filename, None

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=44100,
        language_code="pl-pl",
        enable_automatic_punctuation=True,
    )

    log_status("Transkrypcja audio w toku...", "info", update_status)
    try:
        response = client.recognize(config=config, audio=audio)

        transcribed_text_before_formatting = ""
        for result in response.results:
            transcribed_text_before_formatting = result.alternatives[0].transcript

        # Proste formatowanie tekstu
        transcribed_text = transcribed_text_before_formatting

        log_status("Sukces. Dokonano transkrypcji audio.", "success", update_status)
        print("Przetranskrybowany tekst:\n", transcribed_text)
    except Exception as err:
        log_status(f"Wystąpił problem w czasie transkrypcji audio: {err}", "error", update_status)
        return filename, None

    return filename, transcribed_text
