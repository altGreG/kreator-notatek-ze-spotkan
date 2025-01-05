from app.transcriptor import extract_audio_from_video
from loguru import logger as log

log.info("Test funkcji służącej do ekstrakcji audio.")

path_to_video = r"D:\Studia\InzynieriaOprogramowania\kreator-notatek-ze-spotkan\app\nagrania\test.mkv"
update_status = "placeholder"

path_to_audio = extract_audio_from_video(path_to_video, update_status)

if path_to_audio is None:
    log.info("Nie udało się przeprowadzić ekstrackcji audio.")
else:
    log.info("Sukces.")