import logging

logger = logging.getLogger('security')


class SecurityHeadersMiddleware:
    """
    Agrega headers de seguridad adicionales a todas las respuestas.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        return response


class LoginAuditMiddleware:
    """
    Registra en logs los accesos a URLs sensibles.
    """
    URLS_SENSIBLES = ['/admin/', '/dashboard/']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Loggear accesos a áreas sensibles
        for url in self.URLS_SENSIBLES:
            if request.path.startswith(url):
                user = request.user.username if request.user.is_authenticated else 'anónimo'
                logger.info(
                    f'Acceso a {request.path} | '
                    f'Usuario: {user} | '
                    f'IP: {self._get_ip(request)} | '
                    f'Status: {response.status_code}'
                )
                break

        return response

    def _get_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')