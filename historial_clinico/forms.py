from django import forms
from django.utils import timezone

from .models import RegistroClinico


class RegistroClinicoForm(forms.ModelForm):
    class Meta:
        model = RegistroClinico
        fields = ['fecha', 'motivo', 'diagnostico', 'tratamiento', 'observaciones']
        labels = {
            'fecha': 'Fecha de la consulta',
            'motivo': 'Motivo de la consulta',
            'diagnostico': 'Diagnóstico',
            'tratamiento': 'Tratamiento',
            'observaciones': 'Observaciones',
        }
        widgets = {
            'fecha': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
            'diagnostico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tratamiento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        error_messages = {
            'fecha': {'required': 'La fecha es obligatoria.', 'invalid': 'Introduce una fecha válida.'},
            'motivo': {'required': 'El motivo es obligatorio.'},
            'diagnostico': {'required': 'El diagnóstico es obligatorio.'},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # El calendario no deja elegir días futuros
        self.fields['fecha'].widget.attrs['max'] = timezone.localdate().isoformat()