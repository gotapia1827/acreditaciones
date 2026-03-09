from django.urls import path
from . import views

app_name = 'evaluations'

urlpatterns = [
    path('', views.ColaDocumentosView.as_view(), name='cola_documentos'),
    path('revisar/<int:pk>/', views.RevisarDocumentoView.as_view(), name='revisar_documento'),
    path('historial/', views.HistorialEvaluacionesView.as_view(), name='historial'),
]