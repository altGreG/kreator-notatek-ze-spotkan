from app.utilities.pdf_generator import generate_pdf_from_files

transcription_folder = r"F:\kreator-notatek-ze-spotkan\app\spotkania\2025-01-18_23-07-50\txt-2025-01-18_23-07-50"
screenshot_folder = r"F:\kreator-notatek-ze-spotkan\app\spotkania\2025-01-18_23-07-50\screenshots-2025-01-18_23-07-50"
output_file = r"F:\kreator-notatek-ze-spotkan\app\spotkania\2025-01-18_23-07-50\raport_2025-01-18_23-07-50.pdf"
full_transcription_path = r"F:\kreator-notatek-ze-spotkan\app\spotkania\2025-01-18_23-07-50\full-2025-01-18_23-07-50.txt"
generate_pdf_from_files(output_file,screenshot_folder,transcription_folder, full_transcription_path)