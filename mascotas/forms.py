from django import forms
from django.contrib.auth import get_user_model
from .models import Especie, Raza, Mascota
from .permisos import es_personal



class EspecieForm(forms.ModelForm):
    class   Meta:
        model = Especie
        fields = ['nombre', 'descripcion']
    
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        repetida = Especie.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk)
        if repetida.exists():
            raise forms.ValidationError('Ya existe una especie con ese nombre')
        return nombre
        
    
    
    
class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ['Cliente', 'nombre', 'especie', 'raza', 'sexo',
                  'fecha_nacimiento', 'edad_aproximada_meses', 'peso_kg',
                  'color', 'esterilizado', 'microchip', 'observaciones']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }
        
    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Solo especie activas
        self.fields['especie'].queryset = Especie.objects.filter(estado='ACTIVO')
        
        #Razas : solo las activas de la especie elegida 
        especie_id = self.data.get('especie') or self.initial.get('especie')
        razas = Raza.objects.filter(estado='ACTIVO')
        if especie_id and str(especie_id).isdigit():
            razas = razas.filter(especie_id=especie_id)
        else:
            razas = razas.none()
        self.fields['raza'].queryset = razas
        self.fields['raza'].empty_label = 'Sin raza definida'
        
        
        # Dueño: el cliente no lo ve; el persomal escoge entre los clientes activos
        
        if usuario and es_personal(usuario):
            self.fields['Cliente'].queryset = get_user_model().objects.filter(
                rol='CLIENTE', is_active=True
            )
        else:
            del self.fields['Cliente']
        
    def clean(self):
        datos = super().clean()
        if not datos.get('fecha_nacimiento') and datos.get ('edad_aproximada_meses') is None:
            self.add_error('edad_aproximada_meses',
                           'Escriba la fecha de nacimiento o la edad aproximada en meses.')
        return datos
        