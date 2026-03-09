from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel
from apps.documents.models import Documento


class Evaluacion(TimeStampedModel):
    """
    Registro de la revisión de un documento por parte de un evaluador.
    Cada vez que un evaluador aprueba o rechaza un documento, se crea una Evaluacion.
    Permite mantener historial completo de revisiones.
    """

    RESULTADO_APROBADO = 'aprobado'
    RESULTADO_RECHAZADO = 'rechazado'

    RESULTADO_CHOICES = [
        (RESULTADO_APROBADO, 'Aprobado'),
        (RESULTADO_RECHAZADO, 'Rechazado'),
    ]

    documento = models.ForeignKey(
        Documento,
        on_delete=models.CASCADE,
        related_name='evaluaciones',
        help_text='Documento que fue evaluado'
    )
    evaluador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='evaluaciones_realizadas',
        help_text='Evaluador que realizó la revisión'
    )
    resultado = models.CharField(
        max_length=20,
        choices=RESULTADO_CHOICES
    )
    observacion = models.TextField(
        blank=True,
        null=True,
        help_text='Observaciones o motivo del rechazo'
    )
    fecha_evaluacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Evaluación'
        verbose_name_plural = 'Evaluaciones'
        ordering = ['-fecha_evaluacion']

    def __str__(self):
        return f'Evaluación de {self.documento} por {self.evaluador.get_full_name()} — {self.get_resultado_display()}'