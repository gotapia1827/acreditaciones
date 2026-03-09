from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class RolRequeridoMixin(LoginRequiredMixin):
    """
    Mixin base para requerir un rol específico.
    Uso: definir roles_permitidos = ['cliente'] en la vista.
    """
    roles_permitidos = []

    def dispatch(self, request, *args, **kwargs):
        # Primero verificar que está autenticado
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Superusuario siempre tiene acceso
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        # Verificar que tiene perfil y rol permitido
        try:
            perfil = request.user.profile
            if perfil.rol not in self.roles_permitidos:
                raise PermissionDenied
        except Exception:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class ClienteRequeridoMixin(RolRequeridoMixin):
    roles_permitidos = ['cliente']


class EvaluadorRequeridoMixin(RolRequeridoMixin):
    roles_permitidos = ['evaluador']


class AdministradorRequeridoMixin(RolRequeridoMixin):
    roles_permitidos = ['administrador']


class EvaluadorOAdminMixin(RolRequeridoMixin):
    roles_permitidos = ['evaluador', 'administrador']