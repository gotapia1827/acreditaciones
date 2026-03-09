from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = 'Crea los grupos y permisos iniciales del sistema'

    def handle(self, *args, **kwargs):
        # Grupo Cliente
        cliente_group, created = Group.objects.get_or_create(name='Cliente')
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Grupo Cliente creado'))
        else:
            self.stdout.write('— Grupo Cliente ya existe')

        # Grupo Evaluador
        evaluador_group, created = Group.objects.get_or_create(name='Evaluador')
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Grupo Evaluador creado'))
        else:
            self.stdout.write('— Grupo Evaluador ya existe')

        # Grupo Administrador
        admin_group, created = Group.objects.get_or_create(name='Administrador')
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Grupo Administrador creado'))
        else:
            self.stdout.write('— Grupo Administrador ya existe')

        self.stdout.write(self.style.SUCCESS('\n✅ Grupos del sistema listos'))