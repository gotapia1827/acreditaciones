import uuid
import os
from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel
from django.utils import timezone


def documento_upload_path(instance, filename):
    """
    Genera la ruta de almacenamiento con UUID como nombre de archivo.
    Resultado: media/documentos/2024/03/uuid-generado.pdf
    """
    ext = os.path.splitext(filename)[1].lower()
    nuevo_nombre = f'{uuid.uuid4()}{ext}'
    return os.path.join(
        'documentos',
        str(instance.fecha_subida.year) if hasattr(instance, 'fecha_subida') and instance.fecha_subida else '0000',
        nuevo_nombre
    )


class TipoDocumento(TimeStampedModel):
    """
    Catálogo de tipos de documentos requeridos para la acreditación.
    El administrador define qué documentos son obligatorios.
    Ejemplo: Carnet de identidad, Licencia de conducir, Certificado médico.
    """
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text='Instrucciones o detalles sobre este documento'
    )
    obligatorio = models.BooleanField(
        default=True,
        help_text='Si es obligatorio para el cumplimiento'
    )
    orden = models.PositiveIntegerField(
        default=0,
        help_text='Orden de visualización en el listado'
    )
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Tipo de documento'
        verbose_name_plural = 'Tipos de documento'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre


class Documento(TimeStampedModel):
    """
    Documento subido por un cliente.
    Cada documento pertenece a un cliente y corresponde a un tipo específico.
    Un cliente puede subir múltiples versiones del mismo tipo (historial).
    """

    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_APROBADO = 'aprobado'
    ESTADO_RECHAZADO = 'rechazado'

    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_APROBADO, 'Aprobado'),
        (ESTADO_RECHAZADO, 'Rechazado'),
    ]

    cliente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='documentos',
        help_text='Usuario cliente que subió el documento'
    )
    tipo_documento = models.ForeignKey(
        TipoDocumento,
        on_delete=models.PROTECT,
        related_name='documentos',
        help_text='Tipo de documento según el catálogo'
    )
    archivo = models.FileField(
        upload_to=documento_upload_path,
        help_text='Archivo del documento'
    )
    nombre_original = models.CharField(
        max_length=255,
        help_text='Nombre original del archivo antes del renombrado UUID'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_PENDIENTE
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)
    esta_vigente = models.BooleanField(
        default=True,
        help_text='Solo el documento más reciente por tipo estará vigente'
    )
    fecha_vencimiento = models.DateField(
    blank=True,
    null=True,
    help_text='Fecha de vencimiento del documento. Dejar en blanco si no vence.'
    )

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['-fecha_subida']

    def __str__(self):
        return f'{self.cliente.get_full_name()} — {self.tipo_documento.nombre} ({self.get_estado_display()})'

    def get_extension(self):
        """Retorna la extensión del archivo original."""
        return os.path.splitext(self.nombre_original)[1].lower()

    @property
    def esta_aprobado(self):
        return self.estado == self.ESTADO_APROBADO

    @property
    def esta_rechazado(self):
        return self.estado == self.ESTADO_RECHAZADO

    @property
    def esta_pendiente(self):
        return self.estado == self.ESTADO_PENDIENTE
    
    @property
    def esta_vencido(self):
        if self.fecha_vencimiento:
            return self.fecha_vencimiento < timezone.now().date()
        return False

    @property
    def vence_pronto(self):
        """Retorna True si vence en los próximos 30 días."""
        if self.fecha_vencimiento:
            from datetime import timedelta
            return (
                timezone.now().date() <=
                self.fecha_vencimiento <=
                timezone.now().date() + timedelta(days=30)
            )
        return False

class DocumentoRequerido(TimeStampedModel):
    """
    Define qué documentos son requeridos para cada cliente específico.
    Si no tiene asignaciones propias, se usan los tipos globales activos.
    """
    cliente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='documentos_requeridos'
    )
    tipo_documento = models.ForeignKey(
        TipoDocumento,
        on_delete=models.CASCADE,
        related_name='requeridos_para'
    )

    class Meta:
        verbose_name = 'Documento requerido'
        verbose_name_plural = 'Documentos requeridos'
        unique_together = ['cliente', 'tipo_documento']

    def __str__(self):
        return f'{self.cliente.get_full_name()} — {self.tipo_documento.nombre}'