from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from .models import UserProfile


def _sincronizar_grupo(user, rol):
    """Asigna el grupo de Django correspondiente al rol."""
    user.groups.clear()
    rol_a_grupo = {
        'cliente': 'Cliente',
        'evaluador': 'Evaluador',
        'administrador': 'Administrador',
    }
    nombre_grupo = rol_a_grupo.get(rol)
    if nombre_grupo:
        try:
            grupo = Group.objects.get(name=nombre_grupo)
            user.groups.add(grupo)
        except Group.DoesNotExist:
            pass


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crea el perfil solo cuando el usuario es nuevo."""
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=UserProfile)
def sincronizar_grupo_al_guardar_perfil(sender, instance, **kwargs):
    """
    Cada vez que se guarda el UserProfile sincroniza el grupo.
    Esto se dispara cuando el admin cambia el rol.
    """
    print(f"DEBUG SIGNAL - Sincronizando grupo para {instance.user.username} con rol {instance.rol}")
    _sincronizar_grupo(instance.user, instance.rol)