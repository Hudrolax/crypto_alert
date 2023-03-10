from decimal import Decimal
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


def get_last_price(client, symbol: str) -> Decimal:
    """Get last price for symbol"""
    try:
        response = client.ticker_price(symbol)
        return Decimal(response.get('price', '0'))
    except Exception as ex:
        logger.error(ex)
        return Decimal('0')
