from typing import List
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema


conf = ConnectionConfig(
    MAIL_USERNAME ="test@gmail.com",
    MAIL_PASSWORD = "",
    MAIL_FROM = "test@gmail.com",
    MAIL_PORT = 465,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

async def send_email(subject: str, recipients: List[str], message: str):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=message,
        subtype="html")

    fm = FastMail(conf)
    await fm.send_message(message)
