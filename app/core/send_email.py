import smtplib
import ssl
from celery.utils.log import get_task_logger
import os

logger = get_task_logger(__name__)


class Mail:

    def __init__(self):
        self.port = int(os.environ.get('EMAIL_SERVER_PORT', 465))
        self.smtp_server_domain_name = os.environ.get('EMAIL_SERVER', '')
        self.sender_mail = os.environ.get('EMAIL_ACCOUNT', '')
        self.password = os.environ.get('EMAIL_PASSWORD', '')

        ssl_context = ssl.create_default_context()
        self.service = smtplib.SMTP_SSL(
            self.smtp_server_domain_name, self.port, context=ssl_context)
        self.service.login(self.sender_mail, self.password)

    def send(self, emails, subject, content) -> bool:
        try:
            for email in emails:
                result = self.service.sendmail(
                    self.sender_mail, email, f"Subject: {subject}\n{content}")

            self.service.quit()
            return True
        except Exception as ex:
            logger.error(ex)
            return False
