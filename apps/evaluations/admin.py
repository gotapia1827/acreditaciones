from django.contrib import admin
from .models import Evaluacion

@admin.register(Evaluacion)
class EvaluacionAdmin(admin.ModelAdmin):
    list_display = ['documento', 'evaluador', 'resultado', 'fecha_evaluacion']
    list_filter = ['resultado']
    search_fields = ['evaluador__username', 'documento__nombre_original']
    readonly_fields = ['fecha_evaluacion']