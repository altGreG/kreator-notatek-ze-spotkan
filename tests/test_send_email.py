
from loguru import logger as log
from app.utilities.mail_sender import send_email

# Przykład użycia
if __name__ == "__main__":
    recipient = "sdworak@student.agh.edu.pl"
    file_to_send = r"example.pdf"
    result = send_email(recipient, file_to_send)
    log.info(f"Result: {result}")
