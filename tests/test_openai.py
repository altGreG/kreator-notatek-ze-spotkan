# Przykład użycia
from app.utilities.api.openai_api import summarize_transcription
import json
if __name__ == "__main__":
    transcription_file = r"F:\kreator-notatek-ze-spotkan\app\spotkania\2025-01-18_23-07-50\full-2025-01-18_23-07-50.txt"
    summary = summarize_transcription(transcription_file)
    if summary:
        print("Podsumowanie:")
        print(json.dumps(summary, indent=4, ensure_ascii=False))