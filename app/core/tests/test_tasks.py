"""
Tests for tasks
"""
from unittest.mock import patch
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models
from core.tasks import (
    get_and_save_last_prices,
    send_alerts,
)


def create_user(email='user@example.com', password='testpass123', **kwargs):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email=email, password=password, **kwargs)


class TasksTest(TestCase):
    """Test tasks."""
    def setUp(self) -> None:
        models.CoreSettings.objects.create()

    def test_get_and_save_last_price(self):
        """Test get and save last price for symbols"""
        symbol = models.Symbol.objects.create(name='BTCUSDT')
        get_and_save_last_prices()
        symbol.refresh_from_db()
        self.assertNotEqual(symbol.last_price, Decimal('0'))

    def test_send_alerts(self):
        """Test send alert"""
        # test condition above
        symbol = models.Symbol.objects.create(name='BTCUSDT', last_price=Decimal('25000'))
        user = create_user(telegram_id='test')
        alert = models.Alert.objects.create(
            user=user,
            symbol=symbol,
            price=Decimal('100'),
            condition='above',
            is_active=True
        )
        send_alerts()
        alert.refresh_from_db()
        self.assertEqual(alert.is_active, False)

        # test condition below
        alert.condition = 'below'
        alert.price = Decimal('25500')
        alert.is_active = True
        alert.save()
        send_alerts()
        alert.refresh_from_db()
        self.assertEqual(alert.is_active, False)

        # test condition cross (when alert price above last price)
        alert.condition = 'cross'
        alert.price = Decimal('26000')
        alert.is_active = True
        alert.save()
        send_alerts()
        symbol.last_price = Decimal('27000')
        symbol.save()
        send_alerts()
        alert.refresh_from_db()
        self.assertEqual(alert.condition, 'above')
        self.assertEqual(alert.is_active, False)

        # test condition cross (when alert price below last price)
        alert.condition = 'cross'
        alert.price = Decimal('26000')
        alert.is_active = True
        alert.save()
        send_alerts()
        symbol.last_price = Decimal('25000')
        symbol.save()
        send_alerts()
        alert.refresh_from_db()
        self.assertEqual(alert.condition, 'below')
        self.assertEqual(alert.is_active, False)
