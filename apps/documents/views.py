import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import FileResponse, Http404
from django.views import View
from apps.accounts.mixins import ClienteRequeridoMixin, AdministradorRequeridoMixin
from apps.accounts.models import UserProfile
from .models import Documento, TipoDocumento, DocumentoRequerido
from .forms import DocumentoUploadForm, TipoDocumentoForm


class SubirDocumentoView(ClienteRequeridoMixin, View):
    template_name = 'documents/subir_documento.html'

    def get(self, request, tipo_id=None):
        initial = {}
        if tipo_id:
            initial['tipo_documento'] = tipo_id
        form = DocumentoUploadForm(initial=initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, tipo_id=None):
        form = DocumentoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                documento = form.save(cliente=request.user)
                messages.success(
                    request,
                    f'Documento "{documento.nombre_original}" subido correctamente. '
                    f'Quedará en revisión.'
                )
                return redirect('documents:mis_documentos')
            except Exception as e:
                messages.error(request, f'Error al guardar el documento: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
        return render(request, self.template_name, {'form': form})

class MisDocumentosView(ClienteRequeridoMixin, View):
    template_name = 'documents/mis_documentos.html'

    def get(self, request):
        # Documentos vigentes del cliente
        documentos = Documento.objects.filter(
            cliente=request.user,
            esta_vigente=True
        ).select_related('tipo_documento').order_by('tipo_documento__orden')

        # Tipos requeridos: primero buscar asignaciones específicas del cliente
        tipos_asignados = DocumentoRequerido.objects.filter(
            cliente=request.user
        ).values_list('tipo_documento_id', flat=True)

        if tipos_asignados.exists():
            # Usar los tipos asignados específicamente a este cliente
            tipos_requeridos = TipoDocumento.objects.filter(
                id__in=tipos_asignados,
                activo=True
            ).order_by('orden')
        else:
            # Fallback: usar todos los tipos obligatorios globales
            tipos_requeridos = TipoDocumento.objects.filter(
                activo=True,
                obligatorio=True
            ).order_by('orden')

        cumplimiento = self._calcular_cumplimiento(request.user, tipos_requeridos)
        docs_por_tipo = {doc.tipo_documento_id: doc for doc in documentos}

        return render(request, self.template_name, {
            'documentos': documentos,
            'tipos_requeridos': tipos_requeridos,
            'docs_por_tipo': docs_por_tipo,
            'cumplimiento': cumplimiento,
        })

    def _calcular_cumplimiento(self, cliente, tipos_requeridos):
        total = tipos_requeridos.count()
        if total == 0:
            return 100
        aprobados = Documento.objects.filter(
            cliente=cliente,
            esta_vigente=True,
            estado=Documento.ESTADO_APROBADO,
            tipo_documento__in=tipos_requeridos
        ).count()
        return round((aprobados / total) * 100)

class DetalleDocumentoView(ClienteRequeridoMixin, View):
    """Vista para ver el detalle y el historial de un documento."""
    template_name = 'documents/detalle_documento.html'

    def get(self, request, pk):
        documento = get_object_or_404(
            Documento,
            pk=pk,
            cliente=request.user  # Solo puede ver sus propios documentos
        )
        evaluaciones = documento.evaluaciones.all().order_by('-fecha_evaluacion')
        return render(request, self.template_name, {
            'documento': documento,
            'evaluaciones': evaluaciones,
        })

class ListaTiposDocumentoView(AdministradorRequeridoMixin, View):
    template_name = 'documents/tipos/lista.html'

    def get(self, request):
        tipos = TipoDocumento.objects.all().order_by('orden', 'nombre')
        return render(request, self.template_name, {'tipos': tipos})


class CrearTipoDocumentoView(AdministradorRequeridoMixin, View):
    template_name = 'documents/tipos/form.html'

    def get(self, request):
        form = TipoDocumentoForm()
        return render(request, self.template_name, {'form': form, 'titulo': 'Crear tipo de documento'})

    def post(self, request):
        form = TipoDocumentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de documento creado correctamente.')
            return redirect('documents:lista_tipos')
        return render(request, self.template_name, {'form': form, 'titulo': 'Crear tipo de documento'})


class EditarTipoDocumentoView(AdministradorRequeridoMixin, View):
    template_name = 'documents/tipos/form.html'

    def get(self, request, pk):
        tipo = get_object_or_404(TipoDocumento, pk=pk)
        form = TipoDocumentoForm(instance=tipo)
        return render(request, self.template_name, {'form': form, 'titulo': 'Editar tipo de documento', 'tipo': tipo})

    def post(self, request, pk):
        tipo = get_object_or_404(TipoDocumento, pk=pk)
        form = TipoDocumentoForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de documento actualizado correctamente.')
            return redirect('documents:lista_tipos')
        return render(request, self.template_name, {'form': form, 'titulo': 'Editar tipo de documento', 'tipo': tipo})


class EliminarTipoDocumentoView(AdministradorRequeridoMixin, View):
    def post(self, request, pk):
        tipo = get_object_or_404(TipoDocumento, pk=pk)
        try:
            tipo.delete()
            messages.success(request, f'Tipo "{tipo.nombre}" eliminado correctamente.')
        except Exception:
            messages.error(request, f'No se puede eliminar "{tipo.nombre}" porque tiene documentos asociados.')
        return redirect('documents:lista_tipos')

class GestionDocumentosClienteView(AdministradorRequeridoMixin, View):
    """
    Vista para asignar múltiples tipos de documentos a un cliente específico.
    """
    template_name = 'documents/requeridos/gestion.html'

    def get(self, request, user_id):
        cliente = get_object_or_404(User, pk=user_id)
        todos_los_tipos = TipoDocumento.objects.filter(activo=True).order_by('orden', 'nombre')

        # IDs ya asignados a este cliente
        asignados_ids = DocumentoRequerido.objects.filter(
            cliente=cliente
        ).values_list('tipo_documento_id', flat=True)

        return render(request, self.template_name, {
            'cliente': cliente,
            'todos_los_tipos': todos_los_tipos,
            'asignados_ids': list(asignados_ids),
        })

    def post(self, request, user_id):
        cliente = get_object_or_404(User, pk=user_id)

        # IDs seleccionados en el formulario (puede ser lista vacía)
        seleccionados = request.POST.getlist('tipos_documentos')

        # Eliminar todas las asignaciones actuales
        DocumentoRequerido.objects.filter(cliente=cliente).delete()

        # Crear las nuevas asignaciones seleccionadas
        for tipo_id in seleccionados:
            try:
                tipo = TipoDocumento.objects.get(pk=tipo_id, activo=True)
                DocumentoRequerido.objects.create(
                    cliente=cliente,
                    tipo_documento=tipo
                )
            except TipoDocumento.DoesNotExist:
                pass

        messages.success(
            request,
            f'Documentos requeridos para {cliente.get_full_name()} actualizados correctamente.'
        )
        return redirect('documents:gestion_documentos_cliente', user_id=user_id)


class ListaClientesDocumentosView(AdministradorRequeridoMixin, View):
    """
    Lista de clientes para gestionar sus documentos requeridos.
    """
    template_name = 'documents/requeridos/lista_clientes.html'

    def get(self, request):
        from apps.accounts.models import UserProfile
        clientes = UserProfile.objects.filter(
            rol='cliente',
            activo=True
        ).select_related('user').order_by('user__first_name')

        clientes_data = []
        for perfil in clientes:
            total_asignados = DocumentoRequerido.objects.filter(
                cliente=perfil.user
            ).count()
            clientes_data.append({
                'perfil': perfil,
                'total_asignados': total_asignados,
            })

        return render(request, self.template_name, {
            'clientes_data': clientes_data,
        })
@login_required
def descargar_documento(request, pk):
    """
    Sirve el archivo solo si el usuario tiene permiso de verlo.
    - Cliente: solo sus propios documentos
    - Evaluador/Admin: cualquier documento
    """
    documento = get_object_or_404(Documento, pk=pk)

    # Verificar permiso
    try:
        rol = request.user.profile.rol
    except Exception:
        raise Http404

    if rol == 'cliente' and documento.cliente != request.user:
        raise Http404

    # Verificar que el archivo existe
    if not documento.archivo or not os.path.exists(documento.archivo.path):
        raise Http404

    return FileResponse(
        open(documento.archivo.path, 'rb'),
        as_attachment=False,
        filename=documento.nombre_original
    )