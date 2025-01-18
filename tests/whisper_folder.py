from app.transcriptor import transcribe_with_whisper_offline, transcribe_audio_from_folder
from loguru import logger as log

log.info("Test funkcji służącej do transkrypcji listy audio z wybranego folderu przy pomocy modelu Whisper od OpenAI.")

folder_path = r"D:\Studia\InzynieriaOprogramowania\template\kreator-notatek-ze-spotkan\app\spotkania\2025-01-18_23-07-50\audio-2025-01-18_23-07-50"
update_status = "placeholder"
transcribe_status = transcribe_audio_from_folder(folder_path, update_status)

if transcribe_status is not None:
    log.info("Nie udało się przeprowadzić transkrypcji audio.")
else:
    log.info("Sukces.")