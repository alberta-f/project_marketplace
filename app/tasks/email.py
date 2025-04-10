import asyncio
from email.message import EmailMessage

from aiosmtplib import send

from app.celery_worker import celery_app
from app.core.config import config


async def send_email_async(to: str, subject: str, body: str):
    message = EmailMessage()
    message["From"] = config.smtp.from_email
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    await send(
            message,
            hostname=config.smtp.host,
            port=config.smtp.port,
            username=config.smtp.user,
            password=config.smtp.password,
            start_tls=True,
        )

@celery_app.task(name="app.tasks.email.send_registration_email")
def send_email_task(to: str, subject: str, body: str):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(send_email_async(to, subject, body))
