from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from apps.accounts.mixins import EvaluadorOAdminMixin
from apps.documents.models import Documento, TipoDocumento
from .models import Evaluacion
from .forms import EvaluacionForm
from django.db import models
from django.core.paginator import Paginator




class ColaDocumentosView(EvaluadorOAdminMixin, View):
    template_name = 'evaluations/cola_documentos.html'

    def get(self, request):
        # Filtros
        busqueda = request.GET.get('q', '').strip()
        filtro_estado = request.GET.get('estado', 'pendiente')
        filtro_tipo = request.GET.get('tipo', '')

        # Query base
        documentos = Documento.objects.filter(
            esta_vigente=True
        ).select_related(
            'cliente',
            'tipo_documento',
            'cliente__profile'
        )

        # Aplicar filtro de estado
        if filtro_estado == 'pendiente':
            documentos = documentos.filter(estado=Documento.ESTADO_PENDIENTE)
        elif filtro_estado == 'aprobado':
            documentos = documentos.filter(estado=Documento.ESTADO_APROBADO)
        elif filtro_estado == 'rechazado':
            documentos = documentos.filter(estado=Documento.ESTADO_RECHAZADO)

        # Aplicar búsqueda
        if busqueda:
            documentos = documentos.filter(
                models.Q(cliente__first_name__icontains=busqueda) |
                models.Q(cliente__last_name__icontains=busqueda) |
                models.Q(cliente__username__icontains=busqueda) |
                models.Q(cliente__profile__empresa__icontains=busqueda) |
                models.Q(tipo_documento__nombre__icontains=busqueda) |
                models.Q(nombre_original__icontains=busqueda)
            )

        # Aplicar filtro de tipo de documento
        if filtro_tipo:
            documentos = documentos.filter(tipo_documento_id=filtro_tipo)

        documentos = documentos.order_by('fecha_subida')

        # Paginación
        from django.core.paginator import Paginator
        paginator = Paginator(documentos, 15)
        page = request.GET.get('page', 1)
        documentos_paginados = paginator.get_page(page)

        # Tipos para el filtro
        from apps.documents.models import TipoDocumento
        tipos = TipoDocumento.objects.filter(activo=True).order_by('nombre')

        return render(request, self.template_name, {
            'documentos': documentos_paginados,
            'tipos': tipos,
            'busqueda': busqueda,
            'filtro_estado': filtro_estado,
            'filtro_tipo': filtro_tipo,
            'total_resultados': documentos_paginados.paginator.count,
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