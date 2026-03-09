import os
from django import forms
from .models import Documento, TipoDocumento
from .validators import validar_archivo_completo


class DocumentoUploadForm(forms.ModelForm):
    """
    Formulario para que el cliente suba un documento.
    Incluye validación completa del archivo.
    """

    class Meta:
        model = Documento
        fields = ['tipo_documento', 'archivo']
        widgets = {
            'tipo_documento': forms.Select(attrs={
                'class': 'form-select',
            }),
            'archivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png',
            }),
        }
        labels = {
            'tipo_documento': 'Tipo de documento',
            'archivo': 'Archivo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar tipos de documentos activos
        self.fields['tipo_documento'].queryset = TipoDocumento.objects.filter(
            activo=True
        ).order_by('orden', 'nombre')

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            validar_archivo_completo(archivo)
        return archivo

    def save(self, commit=True, cliente=None):
        documento = super().save(commit=False)
        if cliente:
            documento.cliente = cliente
        # Guardar nombre original antes del renombrado UUID
        documento.nombre_original = self.cleaned_data['archivo'].name
        if commit:
            # Marcar documentos anteriores del mismo tipo como no vigentes
            if cliente:
                Documento.objects.filter(
                    cliente=cliente,
                    tipo_documento=documento.tipo_documento,
                    esta_vigente=True
                ).update(esta_vigente=False)
            documento.save()
        return documento