from django import forms
from .models import EncuestaSatisfaccion, PQRS, LoteProducto, NoConformidad
from mascotas.models import Cita


class PQRSForm(forms.ModelForm):
    """Formulario para que los clientes radiquen PQRS."""
    class Meta:
        model = PQRS
        fields = ['tipo', 'descripcion']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-select',
                'aria-label': 'Selecciona el tipo de solicitud',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe detalladamente tu petición, queja, reclamo o sugerencia...',
            }),
        }
        labels = {
            'tipo': 'Tipo de solicitud',
            'descripcion': 'Detalle de la solicitud',
        }
        help_texts = {
            'tipo': 'Petición (solicitud de información), Queja (inconformidad con la atención), Reclamo (inconformidad con un servicio/producto), Sugerencia (propuesta de mejora).',
        }


class AtenderPQRSForm(forms.ModelForm):
    """Formulario para que el administrador actualice el estado de una PQRS."""
    class Meta:
        model = PQRS
        fields = ['estado']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }


class EncuestaSatisfaccionForm(forms.ModelForm):
    """Formulario para que el cliente evalúe el servicio."""
    class Meta:
        model = EncuestaSatisfaccion
        fields = ['cita', 'puntuacion', 'comentarios']
        widgets = {
            'cita': forms.Select(attrs={'class': 'form-select'}),
            'puntuacion': forms.Select(
                choices=[
                    ('', '--- Selecciona una calificación ---'),
                    (5, '⭐⭐⭐⭐⭐ (5) Excelente'),
                    (4, '⭐⭐⭐⭐ (4) Bueno'),
                    (3, '⭐⭐⭐ (3) Regular'),
                    (2, '⭐⭐ (2) Malo'),
                    (1, '⭐ (1) Muy malo'),
                ],
                attrs={'class': 'form-select'}
            ),
            'comentarios': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Cuéntanos cómo fue tu experiencia y la de tu mascota...',
            }),
        }
        labels = {
            'cita': 'Cita / Servicio recibido',
            'puntuacion': 'Calificación del servicio',
            'comentarios': 'Comentarios u observaciones',
        }

    def __init__(self, *args, **kwargs):
        cliente = kwargs.pop('cliente', None)
        super().__init__(*args, **kwargs)
        if cliente:
            self.fields['cita'].queryset = Cita.objects.filter(
                mascota__Cliente=cliente
            ).order_by('-fecha_hora')
        self.fields['cita'].required = False
        self.fields['cita'].empty_label = 'Evaluación general (sin vincular a cita específica)'


class LoteProductoForm(forms.ModelForm):
    """Formulario para registro y edición de lotes de productos."""
    class Meta:
        model = LoteProducto
        fields = ['producto', 'numero_lote', 'fecha_vencimiento', 'estado_calidad']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'numero_lote': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. LOT-2026-001'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado_calidad': forms.Select(attrs={'class': 'form-select'}),
        }


class NoConformidadForm(forms.ModelForm):
    """Formulario para registrar no conformidades y acciones correctivas."""
    class Meta:
        model = NoConformidad
        fields = ['pqrs', 'encuesta', 'descripcion_problema', 'accion_correctiva', 'estado']
        widgets = {
            'pqrs': forms.Select(attrs={'class': 'form-select'}),
            'encuesta': forms.Select(attrs={'class': 'form-select'}),
            'descripcion_problema': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe el fallo o no conformidad detectada...'}),
            'accion_correctiva': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Plan de acción correctiva y preventiva adoptado...'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pqrs'].required = False
        self.fields['encuesta'].required = False
        self.fields['pqrs'].empty_label = 'Sin vincular a PQRS'
        self.fields['encuesta'].empty_label = 'Sin vincular a Encuesta'

