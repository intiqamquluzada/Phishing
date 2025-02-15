import base64
from typing import List
from fastapi import HTTPException
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from sqlalchemy.orm import Session

from external_services.inject_tracking import inject_tracking_pixel_and_links
from models.email import EmailTemplate

conf = ConnectionConfig(
    MAIL_USERNAME="quluzadintiqam@gmail.com",
    MAIL_PASSWORD="enxbyikihiqgvcmh",
    MAIL_FROM="quluzadintiqam@gmail.com",
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


async def send_email_with_tracking(template_id: int, db: Session, recipients: List[str], unique_uuid: str):
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    body_with_tracking = inject_tracking_pixel_and_links(template.body, template.id, unique_uuid)

    message = MessageSchema(
        subject=template.subject,
        recipients=recipients,
        body=body_with_tracking,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)


async def send_email(subject: str, recipients: List[str], message: str):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=message,
        subtype="html")

    fm = FastMail(conf)
    await fm.send_message(message)