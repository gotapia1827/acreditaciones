from django.contrib import admin
from .models import UserProfile, LoginAttempt


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'rol', 'empresa', 'rut', 'activo']
    list_filter = ['rol', 'activo']
    search_fields = ['user__username', 'user__email', 'empresa', 'rut']


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'username', 'exitoso', 'fecha']
    list_filter = ['exitoso']
    search_fields = ['ip_address', 'username']
    readonly_fields = ['ip_address', 'username', 'exitoso', 'fecha']