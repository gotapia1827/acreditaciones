from django.contrib import admin
from .models import TipoDocumento, Documento, DocumentoRequerido


@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'obligatorio', 'orden', 'activo']
    list_filter = ['obligatorio', 'activo']
    ordering = ['orden']


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'tipo_documento', 'estado', 'fecha_subida', 'esta_vigente']
    list_filter = ['estado', 'esta_vigente', 'tipo_documento']
    search_fields = ['cliente__username', 'cliente__email', 'nombre_original']
    readonly_fields = ['nombre_original', 'fecha_subida']


@admin.register(DocumentoRequerido)
class DocumentoRequeridoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'tipo_documento']
    list_filter = ['tipo_documento']
    search_fields = ['cliente__username', 'cliente__first_name']