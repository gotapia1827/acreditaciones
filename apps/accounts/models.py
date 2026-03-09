from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel


class UserProfile(TimeStampedModel):
    """
    Extiende el User de Django con datos adicionales del cliente o evaluador.
    Relación OneToOne: cada User tiene exactamente un UserProfile.
    """

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
    empresa = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text='Nombre de la empresa del cliente'
    )
    rut = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        unique=True,
        help_text='RUT de la empresa o persona'
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
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