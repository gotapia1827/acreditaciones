from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from apps.accounts.mixins import EvaluadorOAdminMixin
from apps.documents.models import Documento
from .models import Evaluacion
from .forms import EvaluacionForm


class ColaDocumentosView(EvaluadorOAdminMixin, View):
    """Lista de documentos pendientes de revisión."""
    template_name = 'evaluations/cola_documentos.html'

    def get(self, request):
        documentos_pendientes = Documento.objects.filter(
            esta_vigente=True,
            estado=Documento.ESTADO_PENDIENTE
        ).select_related(
            'cliente',
            'tipo_documento',
            'cliente__profile'
        ).order_by('fecha_subida')

        documentos_revisados = Documento.objects.filter(
            esta_vigente=True,
            estado__in=[Documento.ESTADO_APROBADO, Documento.ESTADO_RECHAZADO]
        ).select_related(
            'cliente',
            'tipo_documento',
            'cliente__profile'
        ).order_by('-updated_at')[:20]

        return render(request, self.template_name, {
            'documentos_pendientes': documentos_pendientes,
            'documentos_revisados': documentos_revisados,
            'total_pendientes': documentos_pendientes.count(),
        })


class RevisarDocumentoView(EvaluadorOAdminMixin, View):
    """Vista para revisar un documento específico."""
    template_name = 'evaluations/revisar_documento.html'

    def get(self, request, pk):
        documento = get_object_or_404(
            Documento,
            pk=pk,
            esta_vigente=True
        )
        form = EvaluacionForm()
        evaluaciones_previas = documento.evaluaciones.all().order_by('-fecha_evaluacion')

        return render(request, self.template_name, {
            'documento': documento,
            'form': form,
            'evaluaciones_previas': evaluaciones_previas,
        })

    def post(self, request, pk):
        documento = get_object_or_404(
            Documento,
            pk=pk,
            esta_vigente=True
        )
        form = EvaluacionForm(request.POST)

        if form.is_valid():
            resultado = form.cleaned_data['resultado']
            observacion = form.cleaned_data.get('observacion', '')

            # Validar que rechazo tenga observación
            if resultado == Evaluacion.RESULTADO_RECHAZADO and not observacion:
                messages.error(request, 'Debes agregar una observación al rechazar un documento.')
                return render(request, self.template_name, {
                    'documento': documento,
                    'form': form,
                    'evaluaciones_previas': documento.evaluaciones.all(),
                })

            # Crear evaluación
            Evaluacion.objects.create(
                documento=documento,
                evaluador=request.user,
                resultado=resultado,
                observacion=observacion
            )

            # Actualizar estado del documento
            documento.estado = resultado
            documento.save()

            if resultado == Evaluacion.RESULTADO_APROBADO:
                messages.success(
                    request,
                    f'Documento "{documento.nombre_original}" aprobado correctamente.'
                )
            else:
                messages.warning(
                    request,
                    f'Documento "{documento.nombre_original}" rechazado.'
                )

            return redirect('evaluations:cola_documentos')

        return render(request, self.template_name, {
            'documento': documento,
            'form': form,
            'evaluaciones_previas': documento.evaluaciones.all(),
        })


class HistorialEvaluacionesView(EvaluadorOAdminMixin, View):
    """Historial de evaluaciones realizadas por el evaluador."""
    template_name = 'evaluations/historial.html'

    def get(self, request):
        evaluaciones = Evaluacion.objects.filter(
            evaluador=request.user
        ).select_related(
            'documento',
            'documento__cliente',
            'documento__tipo_documento'
        ).order_by('-fecha_evaluacion')

        return render(request, self.template_name, {
            'evaluaciones': evaluaciones,
        })