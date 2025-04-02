from app.core.config_file import config
from app.tasks.email import send_email_task


class MailService:
    def send_activation_email(self, email: str, token: str):
        url = f"{config.app.url}/activate?token={token}"
        subject = "Activate your account"
        body = f"Hi!\n\nPlease activate your account by clicking the link:\n{url}"
        send_email_task.delay(email, subject, body)

    def send_reset_email(self, email: str, token: str):
        url = f"{config.app.url}/reset-password?token={token}"
        subject = "Reset your password"
        body = f"To reset your password, click here:\n{url}"
        send_email_task.delay(email, subject, body)
