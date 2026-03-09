from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.inicio_view, name='inicio'),
    path('cliente/', views.cliente_view, name='cliente'),
    path('evaluador/', views.evaluador_view, name='evaluador'),
    path('admin/', views.admin_view, name='admin'),
    path('usuarios/', views.ListaUsuariosView.as_view(), name='lista_usuarios'),
    path('usuarios/crear/', views.CrearUsuarioView.as_view(), name='crear_usuario'),
    path('usuarios/<int:user_id>/editar/', views.EditarUsuarioView.as_view(), name='editar_usuario'),
    path('usuarios/<int:user_id>/toggle/', views.ToggleUsuarioView.as_view(), name='toggle_usuario'),
    path('clientes/<int:user_id>/', views.DetalleClienteAdminView.as_view(), name='detalle_cliente'),
]