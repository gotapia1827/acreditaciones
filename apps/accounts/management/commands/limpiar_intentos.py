from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import LoginAttempt


class Command(BaseCommand):
    help = 'Elimina registros de intentos de login anteriores a 24 horas'

    def handle(self, *args, **kwargs):
        limite = timezone.now() - timedelta(hours=24)
        eliminados, _ = LoginAttempt.objects.filter(fecha__lt=limite).delete()
        self.stdout.write(
            self.style.SUCCESS(f'✅ {eliminados} registros de intentos eliminados.')
        )