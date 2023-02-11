"""
Tests for recipe APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Alert, Symbol, User
from alert.serializers import (
    AlertSerializer,
    SymbolSerializer,
)

ALERTS_URL = reverse('alert:alert-list')
SYMBOLS_URL = reverse('alert:symbol-list')


def alert_detail_url(alert_id) -> str:
    """Create and return an alert detail URL."""
    return reverse('alert:alert-detail', args=[alert_id])


def symbol_detail_url(symbol_id) -> str:
    """Create and return a symbol detail URL."""
    return reverse('alert:symbol-detail', args=[symbol_id])


def create_symbol(**params) -> Symbol:
    """Create and return a simple symbol"""
    return Symbol.objects.create(name='BTCUSDT')


def create_alert(user, **params) -> Alert:
    """Create and return a simple alert"""
    symbol = Symbol.objects.create()
    defaults = {
        'symbol': symbol,
        'price': Decimal('25000'),
        'condition': 'above',
    }
    defaults.update(**params)

    alert = Alert.objects.create(user=user, **defaults)
    return alert


def create_user(**params) -> User:
    """Create and return new user."""
    return get_user_model().objects.create_user(**params)  # type: ignore


class PublicSymbolAPITests(TestCase):
    """Tests for unautheticated API requests."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_retrieve_symbols(self) -> None:
        """Test retieving a list of symbols."""
        create_symbol()
        create_symbol()

        res = self.client.get(SYMBOLS_URL)

        symbols = Symbol.objects.all().order_by('-id')
        serializer = SymbolSerializer(symbols, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)  # type: ignore

class PrivateSymbolAPITests(TestCase):
    """Tests authenticated API requests."""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='testpas14')
        self.client.force_authenticate(self.user)

    def test_create_symbol(self) -> None:
        """Test creating a symbol via API"""
        payload = {
            'name': 'BTCUSDT',
        }
        res = self.client.post(SYMBOLS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        symbol = Symbol.objects.get(id=res.data['id'])  # type: ignore
        self.assertEqual(symbol.name, payload['name'])

    def test_update(self) -> None:
        """Test uptade of a symbol."""
        symbol = create_symbol()
        payload = {'name': 'LTCBTC'}
        url = symbol_detail_url(symbol.id)  # type: ignore
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        symbol.refresh_from_db()
        self.assertEqual(symbol.name, payload['name'])

class PublicAlertAPITests(TestCase):
    """Tests for unautheticated API requests."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        """Test auth required to call API."""
        res = self.client.get(ALERTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAlertAPITests(TestCase):
    """Tests authenticated API requests."""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='testpas14')
        self.client.force_authenticate(self.user)

    def test_retrieve_alerts(self) -> None:
        """Test retieving a list of alerts."""
        create_alert(user=self.user)
        create_alert(user=self.user)

        res = self.client.get(ALERTS_URL)

        alerts = Alert.objects.all().order_by('-id')
        serializer = AlertSerializer(alerts, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)  # type: ignore

    def test_alert_list_limited_to_user(self) -> None:
        """Test list of alerts is limited to authenticated user."""
        other_user = create_user(email='other@example.com',
                                 password='otherpassword1234')

        create_alert(user=other_user)
        create_alert(user=self.user)

        res = self.client.get(ALERTS_URL)

        alerts = Alert.objects.filter(user=self.user)
        serializer = AlertSerializer(alerts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)  # type: ignore

    def test_create_alert(self) -> None:
        """Test creating an alert via API"""
        payload = {
            'symbol': 'BTCUSDT',
            'price': Decimal('25000'),
            'condition': 'above',
        }
        res = self.client.post(ALERTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        alert = Alert.objects.get(id=res.data['id'])  # type: ignore
        for k, v in payload.items():
            if k == 'symbol':
                self.assertEqual(str(getattr(alert, k)), v)
            else:
                self.assertEqual(getattr(alert, k), v)
        self.assertEqual(alert.user, self.user)

    def test_partial_update(self) -> None:
        """Test partial uptade of an alert."""
        alert = create_alert(
            user=self.user,
            price=Decimal('25000')
        )
        payload = {'price': Decimal('26000')}
        url = alert_detail_url(alert.id)  # type: ignore
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        alert.refresh_from_db()
        self.assertEqual(alert.price, payload['price'])
        self.assertEqual(alert.user, self.user)
