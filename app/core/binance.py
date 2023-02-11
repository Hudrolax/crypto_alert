import requests
from decimal import Decimal
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


def get_last_price(symbol: str, interval='1m') -> Decimal:
    """Get last price for symbol"""
    route = f'https://testnet.binancefuture.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit=1'
    try:
        klines = requests.get(route).json()
        return Decimal(klines[0][2])
    except Exception as ex:
        logger.error(ex)
        return Decimal('0')
