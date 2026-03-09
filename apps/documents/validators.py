import filetype
import os
import re
from django.conf import settings
from django.core.exceptions import ValidationError


def validar_nombre_archivo(archivo):
    """
    Valida que el nombre del archivo no contenga
    caracteres peligrosos o rutas maliciosas.
    """
    nombre = archivo.name

    # Evitar path traversal
    if '..' in nombre or '/' in nombre or '\\' in nombre:
        raise ValidationError('El nombre del archivo contiene caracteres no permitidos.')

    # Solo permitir caracteres seguros en el nombre
    nombre_sin_ext = os.path.splitext(nombre)[0]
    if not re.match(r'^[\w\s\-\.]+$', nombre_sin_ext, re.UNICODE):
        raise ValidationError('El nombre del archivo contiene caracteres no permitidos.')


def validar_extension(archivo):
    """Valida que la extensión del archivo esté en la whitelist."""
    ext = os.path.splitext(archivo.name)[1].lower()
    if ext not in settings.ALLOWED_DOCUMENT_EXTENSIONS:
        raise ValidationError(
            f'Extensión "{ext}" no permitida. '
            f'Extensiones válidas: {", ".join(settings.ALLOWED_DOCUMENT_EXTENSIONS)}'
        )


def validar_mime_type(archivo):
    """Valida el tipo MIME real del archivo leyendo sus bytes."""
    archivo.seek(0)
    kind = filetype.guess(archivo.read(2048))
    archivo.seek(0)

    if kind is None:
        raise ValidationError(
            'No se pudo determinar el tipo del archivo. '
            'Asegúrate de subir un archivo válido.'
        )

    if kind.mime not in settings.ALLOWED_MIME_TYPES:
        raise ValidationError(
            f'Tipo de archivo no permitido (tipo detectado: {kind.mime}). '
            f'Solo se permiten PDF, Word, Excel e imágenes.'
        )


def validar_tamano(archivo):
    """Valida que el archivo no supere el tamaño máximo permitido."""
    if archivo.size > settings.MAX_UPLOAD_SIZE:
        mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
        raise ValidationError(
            f'El archivo supera el tamaño máximo permitido de {mb:.0f} MB.'
        )


def validar_archivo_completo(archivo):
    """Ejecuta todas las validaciones en orden."""
    validar_nombre_archivo(archivo)
    validar_extension(archivo)
    validar_tamano(archivo)
    validar_mime_type(archivo)