from celery import shared_task
from celery.utils.log import get_task_logger
from core.models import Symbol

import requests
from decimal import Decimal


logger = get_task_logger(__name__)


def _get_last_price(symbol: str, interval='1m') -> Decimal:
    """Get last price for symbol"""
    route = f'https://testnet.binancefuture.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit=1'
    try:
        klines = requests.get(route).json()
        return Decimal(klines[0][2])
    except Exception as ex:
        logger.error(ex)
        return Decimal('0')


@shared_task
def get_and_save_last_prices() -> None:
    """Get and save last prices for all symbols"""
    symbols = Symbol.objects.all()
    for symbol in symbols:
        symbol.last_price = _get_last_price(symbol.name)
        symbol.save()
