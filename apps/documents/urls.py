from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('subir/', views.SubirDocumentoView.as_view(), name='subir_documento'),
    path('mis-documentos/', views.MisDocumentosView.as_view(), name='mis_documentos'),
    path('detalle/<int:pk>/', views.DetalleDocumentoView.as_view(), name='detalle_documento'),
    path('descargar/<int:pk>/', views.descargar_documento, name='descargar_documento'),
]