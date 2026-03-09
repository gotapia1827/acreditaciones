from django import forms
from .models import Evaluacion


class EvaluacionForm(forms.Form):
    resultado = forms.ChoiceField(
        choices=Evaluacion.RESULTADO_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
        }),
        label='Resultado'
    )
    observacion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Agrega observaciones o motivo del rechazo...',
        }),
        label='Observación'
    )