import asyncio
from email.message import EmailMessage

from aiosmtplib import send

from app.celery_worker import celery_app
from app.config import config


@celery_app.task(name="app.tasks.email.send_email_task")
def send_email_task(to: str, subject: str, body: str):
    message = EmailMessage()
    message["From"] = config.smtp.from_email
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    return asyncio.run(
        send(
            message,
            hostname=config.smtp.host,
            port=config.smtp.port,
            username=config.smtp.user,
            password=config.smtp.password,
            start_tls=True,
        )
    )
