from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger('security')


def notificar_documento_evaluado(documento, evaluacion):
    """
    Envía email al cliente cuando su documento es aprobado o rechazado.
    """
    cliente = documento.cliente
    if not cliente.email:
        return

    if evaluacion.resultado == 'aprobado':
        asunto = f'Documento aprobado: {documento.tipo_documento.nombre}'
        mensaje = (
            f'Estimado/a {cliente.get_full_name()},\n\n'
            f'Su documento "{documento.tipo_documento.nombre}" '
            f'ha sido APROBADO.\n\n'
            f'Puede ingresar al sistema para ver el detalle.\n\n'
            f'Saludos,\nEquipo de Acreditaciones Mineras'
        )
    else:
        asunto = f'Documento rechazado: {documento.tipo_documento.nombre}'
        observacion = evaluacion.observacion or 'Sin observaciones.'
        mensaje = (
            f'Estimado/a {cliente.get_full_name()},\n\n'
            f'Su documento "{documento.tipo_documento.nombre}" '
            f'ha sido RECHAZADO.\n\n'
            f'Motivo: {observacion}\n\n'
            f'Por favor ingrese al sistema y suba una nueva versión del documento.\n\n'
            f'Saludos,\nEquipo de Acreditaciones Mineras'
        )

    try:
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[cliente.email],
            fail_silently=False,
        )
        logger.info(f'Email enviado a {cliente.email} — {asunto}')
    except Exception as e:
        logger.error(f'Error enviando email a {cliente.email}: {str(e)}')