"""
Datebase models.
"""
import uuid
import os

from django.conf import settings

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from decimal import Decimal


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_field):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_field)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    telegram_id = models.CharField(max_length=12, default='')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Symbol(models.Model):
    """Symbol object"""
    name = models.CharField(max_length=15)
    last_price = models.DecimalField(max_digits=15, decimal_places=8, default=Decimal('0'))

    def __str__(self) -> str:
        return self.name


class Alert(models.Model):
    """Alert object."""
    conditions = (
        ('above', 'above'),
        ('below', 'below'),
        ('cross', 'cross')
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=15, decimal_places=8)
    is_active = models.BooleanField(default=True)
    condition = models.CharField(max_length=5, choices=conditions)

    @property
    def title(self) -> str:
        return f'{self.symbol} {self.condition} {"{:f}".format(self.price.normalize())}'
    
    def __str__(self) -> str:
        return self.title

class CoreSettings(models.Model):
    """Core settings model"""
    update_last_prices = models.BooleanField(default=True, verbose_name='Update last price') 
    send_alert_via_telegram = models.BooleanField(default=True, verbose_name=' Send alerts via Telegram')
    send_alert_via_email = models.BooleanField(default=True, verbose_name='Send alerts via E-mail')