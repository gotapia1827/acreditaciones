from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.accounts.mixins import (
    ClienteRequeridoMixin,
    EvaluadorRequeridoMixin,
    AdministradorRequeridoMixin
)
from django.views import View


@login_required
def inicio_view(request):
    if request.user.is_superuser:
        return render(request, 'dashboard/admin.html')
    try:
        rol = request.user.profile.rol
        templates = {
            'cliente': 'dashboard/cliente.html',
            'evaluador': 'dashboard/evaluador.html',
            'administrador': 'dashboard/admin.html',
        }
        template = templates.get(rol, 'dashboard/inicio.html')
        return render(request, template)
    except Exception:
        return render(request, 'dashboard/inicio.html')


class ClienteDashboardView(ClienteRequeridoMixin, View):
    def get(self, request):
        return render(request, 'dashboard/cliente.html')


class EvaluadorDashboardView(EvaluadorRequeridoMixin, View):
    def get(self, request):
        return render(request, 'dashboard/evaluador.html')


class AdminDashboardView(AdministradorRequeridoMixin, View):
    def get(self, request):
        return render(request, 'dashboard/admin.html')


cliente_view = ClienteDashboardView.as_view()
evaluador_view = EvaluadorDashboardView.as_view()
admin_view = AdminDashboardView.as_view()