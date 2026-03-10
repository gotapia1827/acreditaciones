import os
from django import forms
from .models import Documento, TipoDocumento, DocumentoRequerido
from .validators import validar_archivo_completo


class DocumentoUploadForm(forms.ModelForm):
    """
    Formulario para que el cliente suba un documento.
    Incluye validación completa del archivo.
    """

    class Meta:
        model = Documento
        fields = ['tipo_documento', 'archivo', 'fecha_vencimiento']
        widgets = {
            'tipo_documento': forms.Select(attrs={
                'class': 'form-select',
            }),
            'archivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png',
            }),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }
        labels = {
            'tipo_documento': 'Tipo de documento',
            'archivo': 'Archivo',
            'fecha_vencimiento': 'Fecha de vencimiento (opcional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        documento.nombre_original = self.cleaned_data['archivo'].name
        if commit:
            if cliente:
                Documento.objects.filter(
                    cliente=cliente,
                    tipo_documento=documento.tipo_documento,
                    esta_vigente=True
                ).update(esta_vigente=False)
            documento.save()
        return documento


class TipoDocumentoForm(forms.ModelForm):
    class Meta:
        model = TipoDocumento
        fields = ['nombre', 'descripcion', 'obligatorio', 'orden', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'obligatorio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nombre': 'Nombre del documento',
            'descripcion': 'Descripción / instrucciones',
            'obligatorio': 'Es obligatorio',
            'orden': 'Orden de visualización',
            'activo': 'Activo',
        }