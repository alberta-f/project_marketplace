from app.tasks.email import send_email_task


class MailService:
    def send_registration_email(self, email: str):
        subject = "Registration"
        body = "Thanks for registration"
        send_email_task.delay(email, subject, body)


def get_mail_service():
    return MailService()
