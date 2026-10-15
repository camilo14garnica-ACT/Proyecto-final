from django import forms
from django.contrib.auth import get_user_model
from .models import Especie, Raza, Mascota
from .permisos import es_personal



class EspecieForm(forms.ModelForm):

    class Meta:
        model = Especie

        fields = [
            'nombre',
            'descripcion',
            'estado',
        ]

        labels = {
            'nombre': 'Nombre de la especie',
            'descripcion': 'Descripción',
            'estado': 'Estado de la especie',
        }

        widgets = {
            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej. Canino',
                }
            ),

            'descripcion': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Describe la especie',
                }
            ),

            'estado': forms.Select(
                attrs={'class': 'form-select'}
            ),
        }

        error_messages = {
            'nombre': {
                'required': 'El nombre de la especie es obligatorio.',
            },
            'estado': {
                'required': 'Debes seleccionar un estado.',
            },
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()

        repetida = Especie.objects.filter(
            nombre__iexact=nombre
        ).exclude(
            pk=self.instance.pk
        )

        if repetida.exists():
            raise forms.ValidationError(
                'Ya existe una especie con ese nombre.'
            )

        return nombre
      
    
    
    
class MascotaForm(forms.ModelForm):

    class Meta:
        model = Mascota

        fields = [
            'Cliente',
            'nombre',
            'especie',
            'raza',
            'sexo',
            'fecha_nacimiento',
            'edad_aproximada_meses',
            'peso_kg',
            'color',
            'esterilizado',
            'microchip',
            'observaciones',
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
            'microchip': 'Número de microchip',
            'observaciones': 'Observaciones',
        }

        widgets = {
            'Cliente': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'nombre': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'especie': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'raza': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'sexo': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'fecha_nacimiento': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),

            'edad_aproximada_meses': forms.NumberInput(
                attrs={'class': 'form-control'}
            ),

            'peso_kg': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                }
            ),

            'color': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'esterilizado': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej. Sí, No o Pendiente',
                }
            ),

            'microchip': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'observaciones': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                }
            ),
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