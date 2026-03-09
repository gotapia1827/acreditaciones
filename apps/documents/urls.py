from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # Cliente
    path('subir/', views.SubirDocumentoView.as_view(), name='subir_documento'),
    path('subir/<int:tipo_id>/', views.SubirDocumentoView.as_view(), name='subir_documento_tipo'),
    path('mis-documentos/', views.MisDocumentosView.as_view(), name='mis_documentos'),
    path('detalle/<int:pk>/', views.DetalleDocumentoView.as_view(), name='detalle_documento'),
    path('descargar/<int:pk>/', views.descargar_documento, name='descargar_documento'),

    # Admin — Tipos de documentos
    path('tipos/', views.ListaTiposDocumentoView.as_view(), name='lista_tipos'),
    path('tipos/crear/', views.CrearTipoDocumentoView.as_view(), name='crear_tipo'),
    path('tipos/<int:pk>/editar/', views.EditarTipoDocumentoView.as_view(), name='editar_tipo'),
    path('tipos/<int:pk>/eliminar/', views.EliminarTipoDocumentoView.as_view(), name='eliminar_tipo'),

    # Admin — Documentos requeridos por cliente
    path('requeridos/', views.ListaClientesDocumentosView.as_view(), name='lista_clientes_documentos'),
    path('requeridos/<int:user_id>/', views.GestionDocumentosClienteView.as_view(), name='gestion_documentos_cliente'),
]