from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.inicio_view, name='inicio'),
    path('cliente/', views.cliente_view, name='cliente'),
    path('evaluador/', views.evaluador_view, name='evaluador'),
    path('admin/', views.admin_view, name='admin'),
]