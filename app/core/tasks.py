from celery import shared_task
from celery.utils.log import get_task_logger

from core.models import Symbol, Alert, CoreSettings
from core.binance_api import get_last_price
from core.telegram_bot import send_message as send_telegram_message 
from core.send_email import send_mail
from binance.spot import Spot


logger = get_task_logger(__name__)


@shared_task
def get_and_save_last_prices() -> None:
    """Get and save last prices for all symbols"""
    core_settings = CoreSettings.objects.get()
    if not core_settings.update_last_prices:
        return
    client = Spot()

    symbols = Symbol.objects.all()
    for symbol in symbols:
        symbol.last_price = get_last_price(client, symbol.name)
        symbol.save()

@shared_task
def send_alerts() -> None:
    """Send alert to users"""
    core_settings = CoreSettings.objects.get()
    alerts = Alert.objects.filter(is_active=True)

    def send_alert(alert, message) -> None:
        alert_sended = False
        if core_settings.send_alert_via_telegram:
            if send_telegram_message(alert.user.telegram_id, message):
                alert_sended = True
        if core_settings.send_alert_via_email:
            if alert.user.telegram_id == 'test' or send_mail.send(
                emails=[alert.user.email], 
                subject='Crypto alert!',
                content=message,
                ):
                alert_sended = True
        if alert_sended:
            alert.is_active = False
            alert.save()

    for alert in alerts:
        match alert.condition:
            case 'above':
                if alert.symbol.last_price > alert.price:
                    send_alert(alert, f'{alert.symbol} is above {alert.price}')
            case 'below':
                if alert.symbol.last_price < alert.price:
                    send_alert(alert, f'{alert.symbol} is below {alert.price}')
            case 'cross':
                if alert.symbol.last_price > alert.price:
                    alert.condition = 'below'
                    alert.save()
                elif alert.symbol.last_price < alert.price:
                    alert.condition = 'above'
                    alert.save()