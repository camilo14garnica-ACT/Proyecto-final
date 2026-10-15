
from django import forms
from .models import Usuario


class CrearUsuarioForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Contraseña"
    )

    password_confirmacion = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirmar contraseña"
    )

    class Meta:
        model = Usuario

        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'Document_Type',
            'Number_Document',
            'Date_of_birth',
            'password',
        ]
        
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'Document_Type': 'Tipo de documento',
            'Number_Document': 'Número de documento',
            'Date_of_birth': 'Fecha de nacimiento',
            'password': 'Contraseña',           
        }
        
        widgets = {
            'username': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'first_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'email': forms.EmailInput(
                attrs={'class': 'form-control'}
            ),
            'Document_Type': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'Number_Document': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'Date_of_birth': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
            }
        ),
    }
    
    error_messages = {
        'username': {
            'required': 'El nombre de usuario es obligatorio',
        },
        'email': {
            'required': 'El correo electronico es obligatorio',
        },
        'Number_Document': {
            'required':'El numero de documento es obligatorio',
            'unique': 'Este documento ya esta registrado',
        },
        'Date_of_birth':{
            'invalid': 'Introduce una fecha de nacimiento valida.',
        }   
    }


    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_confirmacion = cleaned_data.get(
            'password_confirmacion'
        )

        if password and password_confirmacion:
            if password != password_confirmacion:
                raise forms.ValidationError(
                    "Las contraseñas no coinciden."
                )

        return cleaned_data


#El cliente modifica su propio perfil
class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'first_name',
            'last_name',
            'email',
            'Document_Type',
            'Number_Document',
            'Date_of_birth',
        ]
        
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'Document_Type': 'Tipo de documento',
            'Number_Document': 'Número de documento',
            'Date_of_birth': 'Fecha de nacimiento',
            'rol': 'Rol del usuario',
            'is_active': 'Cuenta activa',           
        }
        
        widgets = {
            'username': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'first_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'last_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'email': forms.EmailInput(
                attrs={'class': 'form-control'}
            ),

            'Document_Type': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'Number_Document': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'Date_of_birth': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),

            'rol': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'is_active': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),            
        }
        
        error_messages = {
            'username': {
                'required': 'El nombre de usuario es obligatorio.',
                'unique': 'Este nombre de usuario ya está registrado.',
            },

            'email': {
                'invalid': 'Introduce un correo electrónico válido.',
            },

            'Number_Document': {
                'required': 'El número de documento es obligatorio.',
                'unique': 'Este documento ya está registrado.',
            },           
        }


# Edita el administrador cuentas registradas
class EditarUsuarioForm(forms.ModelForm):

    class Meta:
        model = Usuario

        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'Document_Type',
            'Number_Document',
            'Date_of_birth',
            'rol',
            'is_active',
        ]

        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'Document_Type': 'Tipo de documento',
            'Number_Document': 'Número de documento',
            'Date_of_birth': 'Fecha de nacimiento',
            'rol': 'Rol del usuario',
            'is_active': 'Cuenta activa',
        }

        widgets = {
            'username': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'first_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'email': forms.EmailInput(
                attrs={'class': 'form-control'}
            ),
            'Document_Type': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'Number_Document': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'Date_of_birth': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),
            'rol': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'is_active': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
        }

        error_messages = {
            'username': {
                'required': 'El nombre de usuario es obligatorio.',
                'unique': 'Este nombre de usuario ya está registrado.',
            },
            'Number_Document': {
                'required': 'El número de documento es obligatorio.',
                'unique': 'Este documento ya está registrado.',
            },
        }

    
