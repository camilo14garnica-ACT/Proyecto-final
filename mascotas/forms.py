from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Especie, Raza, Mascota
from .permisos import es_personal


class EspecieForm(forms.ModelForm):
    class Meta:
        model = Especie
        fields = ['nombre', 'descripcion', 'estado']
        labels = {
            'nombre': 'Nombre de la especie',
            'descripcion': 'Descripción',
            'estado': 'Estado de la especie',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Canino',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe la especie',
            }),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
        error_messages = {
            'nombre': {
                'required': 'El nombre de la especie es obligatorio.',
                'max_length': 'El nombre es demasiado largo.',
            },
            'descripcion': {
                'required': 'La descripción es obligatoria.',
            },
            'estado': {
                'required': 'Debes seleccionar un estado.',
            },
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        repetida = Especie.objects.filter(
            nombre__iexact=nombre
        ).exclude(pk=self.instance.pk)

        if repetida.exists():
            raise forms.ValidationError(
                'Ya existe una especie con ese nombre.'
            )

        return nombre


class RazaForm(forms.ModelForm):
    class Meta:
        model = Raza
        fields = ['especie', 'nombre', 'descripcion', 'estado']
        labels = {
            'especie': 'Especie',
            'nombre': 'Nombre de la raza',
            'descripcion': 'Descripción',
            'estado': 'Estado',
        }
        widgets = {
            'especie': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Labrador',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe la raza',
            }),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        especies = Especie.objects.filter(estado='ACTIVO')
        if self.instance.pk:
            especies = Especie.objects.filter(
                Q(estado='ACTIVO') | Q(pk=self.instance.especie_id)
            )
        self.fields['especie'].queryset = especies.order_by('nombre')

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        especie = self.cleaned_data.get('especie')
        repetida = Raza.objects.filter(
            especie=especie,
            nombre__iexact=nombre,
        ).exclude(pk=self.instance.pk)

        if repetida.exists():
            raise forms.ValidationError(
                'Ya existe una raza con ese nombre para esta especie.'
            )

        return nombre


class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = [
            'Cliente', 'nombre', 'especie', 'raza', 'sexo',
            'fecha_nacimiento', 'edad_aproximada_meses', 'peso_kg',
            'color', 'esterilizado', 'estado', 'observaciones',
        ]
        labels = {
            'Cliente': 'Propietario',
            'nombre': 'Nombre de la mascota',
            'especie': 'Especie',
            'raza': 'Raza',
            'sexo': 'Sexo',
            'fecha_nacimiento': 'Fecha de nacimiento',
            'edad_aproximada_meses': 'Edad aproximada (meses)',
            'peso_kg': 'Peso (kg)',
            'color': 'Color',
            'esterilizado': 'Esterilización',
            'estado': 'Estado',
            'observaciones': 'Observaciones',
        }
        widgets = {
            'Cliente': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'especie': forms.Select(attrs={'class': 'form-select'}),
            'raza': forms.Select(attrs={'class': 'form-select'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'fecha_nacimiento': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'edad_aproximada_meses': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'peso_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
            }),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'esterilizado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Sí, No o Pendiente',
            }),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
            }),
        }
        error_messages = {
            'Cliente': {
                'required': 'Debes seleccionar un propietario.',
            },
            'nombre': {
                'required': 'El nombre de la mascota es obligatorio.',
            },
            'especie': {
                'required': 'Debes seleccionar una especie.',
            },
            'sexo': {
                'required': 'Debes seleccionar el sexo de la mascota.',
            },
            'fecha_nacimiento': {
                'invalid': 'Introduce una fecha válida.',
            },
            'peso_kg': {
                'invalid': 'Introduce un peso válido.',
            },
        }

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

        if self.usuario is not None and not es_personal(self.usuario):
            self.fields.pop('Cliente')
        else:
            self.fields['Cliente'].queryset = (
                get_user_model().objects
                .filter(rol='CLIENTE')
                .order_by('first_name', 'last_name', 'username')
            )

        especie_id = (
            self.data.get('especie')
            or self.initial.get('especie')
            or getattr(self.instance, 'especie_id', None)
        )
        self.fields['especie'].queryset = Especie.objects.filter(
            Q(estado='ACTIVO') | Q(pk=getattr(self.instance, 'especie_id', None))
        ).order_by('nombre')

        razas = Raza.objects.filter(estado='ACTIVO')
        if especie_id:
            razas = razas.filter(especie_id=especie_id)
        else:
            razas = razas.none()

        if self.instance.pk and self.instance.raza_id:
            razas = Raza.objects.filter(
                Q(estado='ACTIVO', especie_id=especie_id)
                | Q(pk=self.instance.raza_id)
            )

        self.fields['raza'].queryset = razas.order_by('nombre')
