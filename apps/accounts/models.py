from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel
from apps.accounts.validators import validar_rut_chileno


class UserProfile(TimeStampedModel):

    ROL_CHOICES = [
        ('cliente', 'Cliente'),
        ('evaluador', 'Evaluador'),
        ('administrador', 'Administrador'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default='cliente'
    )
    empresa = models.CharField(max_length=200, blank=True, null=True)
    rut = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        unique=True,
        validators=[validar_rut_chileno],
        help_text='Formato: 12345678-9'
    )
    telefono = models.CharField(max_length=20, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.get_rol_display()})'

    def es_cliente(self):
        return self.rol == 'cliente'

    def es_evaluador(self):
        return self.rol == 'evaluador'

    def es_administrador(self):
        return self.rol == 'administrador'

class LoginAttempt(models.Model):
    """
    Registra intentos fallidos de login por IP.
    Bloquea temporalmente si supera el límite.
    """
    ip_address = models.GenericIPAddressField()
    username = models.CharField(max_length=150, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    exitoso = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Intento de login'
        verbose_name_plural = 'Intentos de login'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.ip_address} — {self.username} — {"OK" if self.exitoso else "FAIL"}'

    @classmethod
    def intentos_fallidos_recientes(cls, ip, minutos=15):
        """Cuenta intentos fallidos en los últimos N minutos."""
        from django.utils import timezone
        from datetime import timedelta
        desde = timezone.now() - timedelta(minutes=minutos)
        return cls.objects.filter(
            ip_address=ip,
            exitoso=False,
            fecha__gte=desde
        ).count()

    @classmethod
    def esta_bloqueado(cls, ip, max_intentos=5, minutos=15):
        """Retorna True si la IP está bloqueada."""
        return cls.intentos_fallidos_recientes(ip, minutos) >= max_intentos