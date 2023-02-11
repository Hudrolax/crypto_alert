import logging
from decimal import Decimal
import requests


def get_klines(symbol:str, interval='1m') -> Decimal | None:
    logger = logging.getLogger('get_klines')
    route = f'https://testnet.binancefuture.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit=1'
    try:
        klines = requests.get(route).json()
        return Decimal(klines[0][2])
    except Exception as ex:
        logger.error(ex)
        return