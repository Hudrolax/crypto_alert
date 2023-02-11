"""Django command for add core settings"""
from django.core.management.base import BaseCommand
from core.models import CoreSettings
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
    """Django command to wait for database"""

    def handle(self, *args, **options):
        """Entrypoint for command."""
        try:
            core_settings = CoreSettings.objects.get(id=1)
        except ObjectDoesNotExist: 
            CoreSettings.objects.create()
            self.stdout.write('Default core settings is maked.')