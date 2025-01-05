from app.transcriptor import transcribe_with_gcloud
from loguru import logger as log

log.info("Test funkcji służącej do transkrypcji audio przy pomocy modelu Whisper od OpenAI.")

path_to_audio = r"D:\Studia\InzynieriaOprogramowania\kreator-notatek-ze-spotkan\app\nagrania\audio\test.mp3"
update_status = "placeholder"
filename, transcribed_text  = transcribe_with_gcloud(path_to_audio, update_status)

if transcribed_text is None:
    log.info("Nie udało się przeprowadzić transkrypcji audio.")
else:
    log.info("Sukces.")