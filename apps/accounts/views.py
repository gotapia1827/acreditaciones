from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from .models import LoginAttempt


def get_client_ip(request):
    """Obtiene la IP real del cliente."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:inicio')
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        ip = get_client_ip(request)

        # Verificar bloqueo por intentos fallidos
        if LoginAttempt.esta_bloqueado(ip):
            messages.error(
                request,
                'Demasiados intentos fallidos. Espera 15 minutos antes de intentar nuevamente.'
            )
            return render(request, self.template_name)

        if not username or not password:
            messages.error(request, 'Por favor ingresa usuario y contraseña.')
            return render(request, self.template_name)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                user.refresh_from_db()
                try:
                    user.profile.refresh_from_db()
                except Exception:
                    pass
                # Registrar intento exitoso
                LoginAttempt.objects.create(
                    ip_address=ip,
                    username=username,
                    exitoso=True
                )
                return redirect(self._get_redirect_url(user))
            else:
                messages.error(request, 'Tu cuenta está desactivada.')
                LoginAttempt.objects.create(
                    ip_address=ip,
                    username=username,
                    exitoso=False
                )
        else:
            # Registrar intento fallido
            LoginAttempt.objects.create(
                ip_address=ip,
                username=username,
                exitoso=False
            )
            intentos = LoginAttempt.intentos_fallidos_recientes(ip)
            restantes = max(0, 5 - intentos)
            if restantes > 0:
                messages.error(
                    request,
                    f'Usuario o contraseña incorrectos. '
                    f'Te quedan {restantes} intentos antes del bloqueo.'
                )
            else:
                messages.error(
                    request,
                    'Cuenta bloqueada temporalmente por múltiples intentos fallidos.'
                )

        return render(request, self.template_name)

    def _get_redirect_url(self, user):
        if user.is_superuser:
            return 'dashboard:admin'
        try:
            perfil = user.profile
            rutas = {
                'cliente': 'dashboard:cliente',
                'evaluador': 'dashboard:evaluador',
                'administrador': 'dashboard:admin',
            }
            return rutas.get(perfil.rol, 'dashboard:inicio')
        except Exception:
            return 'dashboard:inicio'


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.success(request, 'Sesión cerrada correctamente.')
        return redirect('accounts:login')


@login_required
def perfil_view(request):
    return render(request, 'accounts/perfil.html', {
        'perfil': request.user.profile
    })