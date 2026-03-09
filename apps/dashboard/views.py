from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views import View
from apps.accounts.mixins import (
    ClienteRequeridoMixin,
    EvaluadorRequeridoMixin,
    AdministradorRequeridoMixin
)
from apps.documents.models import Documento


@login_required
def inicio_view(request):
    if request.user.is_superuser:
        return render(request, 'dashboard/admin.html')
    try:
        rol = request.user.profile.rol
        rutas = {
            'cliente': 'dashboard:cliente',
            'evaluador': 'dashboard:evaluador',
            'administrador': 'dashboard:admin',
        }
        return redirect(rutas.get(rol, 'dashboard:inicio'))
    except Exception:
        return render(request, 'dashboard/inicio.html')


class ClienteDashboardView(ClienteRequeridoMixin, View):
    def get(self, request):
        return redirect('documents:mis_documentos')


class EvaluadorDashboardView(EvaluadorRequeridoMixin, View):
    def get(self, request):
        return redirect('evaluations:cola_documentos')


class AdminDashboardView(AdministradorRequeridoMixin, View):
    def get(self, request):
        return render(request, 'dashboard/admin.html')


cliente_view = ClienteDashboardView.as_view()
evaluador_view = EvaluadorDashboardView.as_view()
admin_view = AdminDashboardView.as_view()