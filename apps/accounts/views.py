from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View


class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        # Si ya está autenticado, redirigir al dashboard
        if request.user.is_authenticated:
            return redirect('dashboard:inicio')
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, 'Por favor ingresa usuario y contraseña.')
            return render(request, self.template_name)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                # Recargar el perfil fresco desde la BD
                user.refresh_from_db()
                try:
                    user.profile.refresh_from_db()
                except Exception:
                    pass
                return redirect(self._get_redirect_url(user))
            else:
                messages.error(request, 'Tu cuenta está desactivada.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
        return render(request, self.template_name)

    def _get_redirect_url(self, user):
        """Redirige al panel correspondiente según el rol."""
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
        except Exception as e:
            print(f"DEBUG - Error: {e}")
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