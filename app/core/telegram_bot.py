from celery.utils.log import get_task_logger
import telebot
import os

logger = get_task_logger(__name__)

TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
# You can set parse_mode by default. HTML or MARKDOWN
bot = telebot.TeleBot(TOKEN, parse_mode=None)

def send_message(user_id:str, message: str) -> bool:
    if user_id == 'test':
        return True
    try:
        bot.send_message(int(user_id), message)
    except Exception as ex:
        logger.error(ex)
        return False
    return True
