from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'rol', 'empresa', 'rut', 'activo']
    list_filter = ['rol', 'activo']
    search_fields = ['user__username', 'user__email', 'empresa', 'rut']