from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from apps.accounts.mixins import ClienteRequeridoMixin
from .models import Documento, TipoDocumento
from .forms import DocumentoUploadForm


class SubirDocumentoView(ClienteRequeridoMixin, View):
    """Vista para que el cliente suba un documento."""
    template_name = 'documents/subir_documento.html'

    def get(self, request):
        form = DocumentoUploadForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
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
    """Vista para que el cliente vea sus documentos y cumplimiento."""
    template_name = 'documents/mis_documentos.html'

    def get(self, request):
        # Documentos vigentes del cliente
        documentos = Documento.objects.filter(
            cliente=request.user,
            esta_vigente=True
        ).select_related('tipo_documento').order_by('tipo_documento__orden')

        # Tipos de documentos requeridos
        tipos_requeridos = TipoDocumento.objects.filter(
            activo=True,
            obligatorio=True
        ).order_by('orden')

        # Calcular cumplimiento
        cumplimiento = self._calcular_cumplimiento(request.user, tipos_requeridos)

        # Documentos subidos indexados por tipo
        docs_por_tipo = {doc.tipo_documento_id: doc for doc in documentos}

        return render(request, self.template_name, {
            'documentos': documentos,
            'tipos_requeridos': tipos_requeridos,
            'docs_por_tipo': docs_por_tipo,
            'cumplimiento': cumplimiento,
        })

    def _calcular_cumplimiento(self, cliente, tipos_requeridos):
        """
        Calcula el porcentaje de cumplimiento del cliente.
        Solo cuenta documentos vigentes y aprobados.
        """
        total = tipos_requeridos.count()
        if total == 0:
            return 100

        aprobados = Documento.objects.filter(
            cliente=cliente,
            esta_vigente=True,
            estado=Documento.ESTADO_APROBADO,
            tipo_documento__obligatorio=True
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