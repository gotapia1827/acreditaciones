from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.views import View
from django.db.models import Count, Q
from apps.accounts.mixins import (
    ClienteRequeridoMixin,
    EvaluadorRequeridoMixin,
    AdministradorRequeridoMixin,
)
from apps.accounts.models import UserProfile
from apps.documents.models import Documento, TipoDocumento
from apps.evaluations.models import Evaluacion
from .forms import CrearUsuarioForm, EditarUsuarioForm
from django.db import models
from .exports import exportar_excel, exportar_pdf

@login_required
def inicio_view(request):
    if request.user.is_superuser:
        return redirect('dashboard:admin')
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
    """Dashboard principal del administrador con KPIs."""
    template_name = 'dashboard/admin.html'

    def get(self, request):
        # KPIs globales — excluir administradores del conteo de clientes
        total_clientes = UserProfile.objects.filter(rol='cliente', activo=True).count()
        total_documentos = Documento.objects.filter(esta_vigente=True).count()
        total_aprobados = Documento.objects.filter(esta_vigente=True, estado='aprobado').count()
        total_rechazados = Documento.objects.filter(esta_vigente=True, estado='rechazado').count()
        total_pendientes = Documento.objects.filter(esta_vigente=True, estado='pendiente').count()
        total_tipos = TipoDocumento.objects.filter(activo=True, obligatorio=True).count()

        # Solo clientes reales, nunca administradores ni evaluadores
        clientes = UserProfile.objects.filter(
            rol='cliente',
            activo=True
        ).select_related('user').order_by('user__first_name')

        clientes_data = []
        for perfil in clientes:
            aprobados = Documento.objects.filter(
                cliente=perfil.user,
                esta_vigente=True,
                estado='aprobado',
                tipo_documento__obligatorio=True
            ).count()
            cumplimiento = round((aprobados / total_tipos) * 100) if total_tipos > 0 else 0
            pendientes = Documento.objects.filter(
                cliente=perfil.user,
                esta_vigente=True,
                estado='pendiente'
            ).count()
            clientes_data.append({
                'perfil': perfil,
                'aprobados': aprobados,
                'cumplimiento': cumplimiento,
                'pendientes': pendientes,
            })

        return render(request, self.template_name, {
            'total_clientes': total_clientes,
            'total_documentos': total_documentos,
            'total_aprobados': total_aprobados,
            'total_rechazados': total_rechazados,
            'total_pendientes': total_pendientes,
            'clientes_data': clientes_data,
        })

class DetalleClienteAdminView(AdministradorRequeridoMixin, View):
    """Vista detalle de un cliente con todos sus documentos."""
    template_name = 'dashboard/detalle_cliente.html'

    def get(self, request, user_id):
        cliente = get_object_or_404(User, pk=user_id)
        perfil = get_object_or_404(UserProfile, user=cliente, rol='cliente')

        tipos_requeridos = TipoDocumento.objects.filter(
            activo=True,
            obligatorio=True
        ).order_by('orden')

        documentos = Documento.objects.filter(
            cliente=cliente,
            esta_vigente=True
        ).select_related('tipo_documento').order_by('tipo_documento__orden')

        docs_por_tipo = {doc.tipo_documento_id: doc for doc in documentos}

        total_tipos = tipos_requeridos.count()
        aprobados = sum(
            1 for doc in documentos
            if doc.estado == 'aprobado' and doc.tipo_documento.obligatorio
        )
        cumplimiento = round((aprobados / total_tipos) * 100) if total_tipos > 0 else 0

        return render(request, self.template_name, {
            'cliente': cliente,
            'perfil': perfil,
            'tipos_requeridos': tipos_requeridos,
            'docs_por_tipo': docs_por_tipo,
            'cumplimiento': cumplimiento,
            'aprobados': aprobados,
            'total_tipos': total_tipos,
        })


class ListaUsuariosView(AdministradorRequeridoMixin, View):
    template_name = 'dashboard/lista_usuarios.html'

    def get(self, request):
        from django.core.paginator import Paginator
        busqueda = request.GET.get('q', '').strip()

        usuarios = UserProfile.objects.select_related('user').order_by('rol', 'user__first_name')

        if busqueda:
            usuarios = usuarios.filter(
                models.Q(user__first_name__icontains=busqueda) |
                models.Q(user__last_name__icontains=busqueda) |
                models.Q(user__username__icontains=busqueda) |
                models.Q(user__email__icontains=busqueda) |
                models.Q(empresa__icontains=busqueda)
            )

        paginator = Paginator(usuarios, 20)
        page = request.GET.get('page', 1)
        usuarios_paginados = paginator.get_page(page)

        return render(request, self.template_name, {
            'usuarios': usuarios_paginados,
            'busqueda': busqueda,
        })

class CrearUsuarioView(AdministradorRequeridoMixin, View):
    """Vista para crear un nuevo usuario desde el panel admin."""
    template_name = 'dashboard/crear_usuario.html'

    def get(self, request):
        form = CrearUsuarioForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CrearUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f'Usuario "{user.username}" creado correctamente con rol '
                f'{user.profile.get_rol_display()}.'
            )
            return redirect('dashboard:lista_usuarios')
        return render(request, self.template_name, {'form': form})

class EditarUsuarioView(AdministradorRequeridoMixin, View):
    """Vista para editar rol y datos de un usuario."""
    template_name = 'dashboard/editar_usuario.html'

    def get(self, request, user_id):
        usuario = get_object_or_404(User, pk=user_id)
        perfil = get_object_or_404(UserProfile, user=usuario)
        form = EditarUsuarioForm(instance=perfil, user=usuario)
        return render(request, self.template_name, {
            'form': form,
            'usuario': usuario,
        })

    def post(self, request, user_id):
        usuario = get_object_or_404(User, pk=user_id)
        perfil = get_object_or_404(UserProfile, user=usuario)
        form = EditarUsuarioForm(
            request.POST,
            instance=perfil,
            user=usuario
        )
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Usuario "{usuario.username}" actualizado correctamente.'
            )
            return redirect('dashboard:lista_usuarios')
        return render(request, self.template_name, {
            'form': form,
            'usuario': usuario,
        })

class ToggleUsuarioView(AdministradorRequeridoMixin, View):
    """Activar o desactivar un usuario."""

    def post(self, request, user_id):
        usuario = get_object_or_404(User, pk=user_id)
        perfil = get_object_or_404(UserProfile, user=usuario)

        # No permitir desactivar al propio usuario
        if usuario == request.user:
            messages.error(request, 'No puedes desactivarte a ti mismo.')
            return redirect('dashboard:lista_usuarios')

        perfil.activo = not perfil.activo
        perfil.save()
        usuario.is_active = perfil.activo
        usuario.save()

        estado = 'activado' if perfil.activo else 'desactivado'
        messages.success(request, f'Usuario "{usuario.username}" {estado} correctamente.')
        return redirect('dashboard:lista_usuarios')

class ExportarReporteView(AdministradorRequeridoMixin, View):
    def get(self, request):
        formato = request.GET.get('formato', 'excel')

        total_tipos = TipoDocumento.objects.filter(activo=True, obligatorio=True).count()

        clientes = UserProfile.objects.filter(
            rol='cliente',
            activo=True
        ).select_related('user').order_by('user__first_name')

        clientes_data = []
        for perfil in clientes:
            aprobados = Documento.objects.filter(
                cliente=perfil.user,
                esta_vigente=True,
                estado='aprobado',
                tipo_documento__obligatorio=True
            ).count()
            cumplimiento = round((aprobados / total_tipos) * 100) if total_tipos > 0 else 0
            clientes_data.append({
                'perfil': perfil,
                'aprobados': aprobados,
                'cumplimiento': cumplimiento,
            })

        if formato == 'pdf':
            return exportar_pdf(clientes_data, total_tipos)
        return exportar_excel(clientes_data, total_tipos)

cliente_view = ClienteDashboardView.as_view()
evaluador_view = EvaluadorDashboardView.as_view()
admin_view = AdminDashboardView.as_view()