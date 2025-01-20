import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from dotenv import load_dotenv
import os
import logging
from loguru import logger as log

def send_email(recipient_email, file_path):
    """
    Wysyła e-mail z załącznikiem na podany adres.

    Args:
        recipient_email (str): Adres e-mail odbiorcy.
        file_path (str): Ścieżka do pliku, który ma być załączony.

    Returns:
        str: "Success!" jeśli wysyłanie zakończyło się sukcesem, inaczej wiadomość błędu.
    """
    sender_email = "gienio.enterprise@gmail.com"
    load_dotenv()
    password = os.getenv("EMAIL_PASSWORD")
    subject = "Notatki ze spotkania"

    # Sprawdzenie, czy plik istnieje
    if not os.path.exists(file_path):
        log.error(f"File not found: {file_path}")
        return "Error: File not found"

    try:
        # Konfiguracja serwera SMTP
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        # Utwórz obiekt wiadomości
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject

        # Dodaj treść e-maila
        with open(file_path, "rb") as attachment_file:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment_file.read())

        # Kodowanie załącznika w Base64
        encoders.encode_base64(part)

        # Ustawienie nagłówków załącznika
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(file_path)}",
        )

        # Dodanie załącznika do wiadomości
        message.attach(part)

        # Połącz się z serwerem SMTP
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Szyfrowanie połączenia
            server.login(sender_email, password)  # Logowanie
            server.sendmail(sender_email, recipient_email, message.as_string())  # Wysyłanie wiadomości
            log.debug(f"Email sent successfully to {recipient_email}")
        return "Success!"

    except smtplib.SMTPAuthenticationError:
        log.error("Authentication failed. Check your email credentials.")
        return "Error: Authentication failed."

    except smtplib.SMTPException as e:
        log.error(f"SMTP error occurred: {e}")
        return f"Error: {e}"

    except Exception as e:
        log.error(f"An error occurred: {e}")
        return f"Error: {e}"

# Przykład użycia
if __name__ == "__main__":
    recipient = "sdworak@student.agh.edu.pl"
    file_to_send = r"example.pdf"
    result = send_email(recipient, file_to_send)
    log.info(f"Result: {result}")
