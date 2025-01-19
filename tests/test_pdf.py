from app.utilities.pdf_generator import generate_pdf_from_files

transcription_folder = r"D:\Studia\InzynieriaOprogramowania\template\kreator-notatek-ze-spotkan\app\spotkania\2025-01-18_23-07-50\txt-2025-01-18_23-07-50"
screenshot_folder = r"D:\Studia\InzynieriaOprogramowania\template\kreator-notatek-ze-spotkan\app\spotkania\2025-01-18_23-07-50\screenshots-2025-01-18_23-07-50"
output_file = r"D:\Studia\InzynieriaOprogramowania\template\kreator-notatek-ze-spotkan\app\spotkania\2025-01-18_23-07-50\plik.pdf"

generate_pdf_from_files(output_file,screenshot_folder,transcription_folder)