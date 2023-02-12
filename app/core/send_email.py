import smtplib
import ssl
from celery.utils.log import get_task_logger
import os

logger = get_task_logger(__name__)


def send_mail(emails, subject, content) -> bool:
    try:
        port = int(os.environ.get('EMAIL_SERVER_PORT', 465))
        smtp_server_domain_name = os.environ.get('EMAIL_SERVER', '')
        sender_mail = os.environ.get('EMAIL_ACCOUNT', '')
        password = os.environ.get('EMAIL_PASSWORD', '')

        ssl_context = ssl.create_default_context()
        service = smtplib.SMTP_SSL(
            smtp_server_domain_name, port, context=ssl_context)
        service.login(sender_mail, password)

        for email in emails:
            result = service.sendmail(
                sender_mail, email, f"Subject: {subject}\n{content}")

        service.quit()
        return True
    except Exception as ex:
        logger.error(ex)
        return False
