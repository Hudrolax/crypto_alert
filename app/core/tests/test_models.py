"""
Tests for modules
"""
from unittest.mock import patch
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test create user with email successful"""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new user."""

        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test create new superuser."""
        user = get_user_model().objects.create_superuser(
            email='test@example.com', password='test123')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_create_alert(self):
        """Test creating an alert is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        # symbol = models.Symbol.objects.filter(symbol='BTCUSDT')
        # if len(symbol) == 0:
        symbol = models.Symbol.objects.create(name='BTCUSDT')

        alert = models.Alert.objects.create(
            user=user,
            symbol=symbol,
            price=Decimal('25000'),
            condition='above',
            is_active=True
        )

        self.assertEqual(str(alert), alert.title)
    
    def test_create_symbol(self):
        """Test creating a symbol is successful."""

        symbol = models.Symbol.objects.create(
            name='BTCUSDT',
        )

        self.assertEqual(str(symbol), symbol.name)