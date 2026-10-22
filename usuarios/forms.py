
from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import Usuario



from django import forms
from .models import Usuario


class CrearUsuarioForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa una contraseña',
        }),
        error_messages={'required': 'La contraseña es obligatoria.'}
    )
    password_confirmacion = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirma tu contraseña',
        }),
        error_messages={'required': 'Debes confirmar tu contraseña.'}
    )

    class Meta:
        model = Usuario
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'Document_Type', 'Number_Document', 'Date_of_birth', 'password',
        ]
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'Document_Type': 'Tipo de documento',
            'Number_Document': 'Número de documento',
            'Date_of_birth': 'Fecha de nacimiento',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Crea tu nombre de usuario',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa tus nombres',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresa tus apellidos',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@correo.com',
            }),
            'Document_Type': forms.Select(attrs={'class': 'form-select'}),
            'Number_Document': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de documento',
            }),
            'Date_of_birth': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }
        error_messages = {
            'username': {
                'required': 'El nombre de usuario es obligatorio.',
                'unique': 'Este nombre de usuario ya está registrado.',
            },
            'first_name': {'required': 'Los nombres son obligatorios.'},
            'last_name': {'required': 'Los apellidos son obligatorios.'},
            'email': {
                'required': 'El correo electrónico es obligatorio.',
                'invalid': 'Introduce un correo electrónico válido.',
            },
            'Document_Type': {'required': 'Selecciona un tipo de documento.'},
            'Number_Document': {
                'required': 'El número de documento es obligatorio.',
                'unique': 'Este documento ya está registrado.',
            },
            'Date_of_birth': {
                'required': 'La fecha de nacimiento es obligatoria.',
                'invalid': 'Introduce una fecha de nacimiento válida.',
            },
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
<<<<<<< HEAD
        password_confirmacion = cleaned_data.get('password_confirmacion')

        if password and password_confirmacion:
            if password != password_confirmacion:
                self.add_error('password_confirmacion', "Las contraseñas no coinciden.")
            else:
                try:
                    validate_password(password, self.instance)
                except forms.ValidationError as error:
                    self.add_error('password', error)
=======
        confirmacion = cleaned_data.get('password_confirmacion')

        if password and confirmacion and password != confirmacion:
            self.add_error('password_confirmacion', 'Las contraseñas no coinciden.')
>>>>>>> 4877cb84795950d378de70a9c5694b3ce7374643

        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['password'])
        if commit:
            usuario.save()
        return usuario


# El cliente modifica su propio perfil
class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'first_name', 'last_name', 'email',
            'Document_Type', 'Number_Document', 'Date_of_birth',
        ]
        labels = {
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'Document_Type': 'Tipo de documento',
            'Number_Document': 'Número de documento',
            'Date_of_birth': 'Fecha de nacimiento',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'Document_Type': forms.Select(attrs={'class': 'form-select'}),
            'Number_Document': forms.TextInput(attrs={'class': 'form-control'}),
            'Date_of_birth': forms.DateInput(format='%Y-%m-%d', attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }
        error_messages = {
            'first_name': {'required': 'Los nombres son obligatorios.'},
            'last_name': {'required': 'Los apellidos son obligatorios.'},
            'email': {'invalid': 'Introduce un correo electrónico válido.'},
            'Number_Document': {
                'required': 'El número de documento es obligatorio.',
                'unique': 'Este documento ya está registrado.',
            },
            'Date_of_birth': {'invalid': 'Introduce una fecha válida.'},
        }


# El administrador edita las cuentas registradas
class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'Document_Type', 'Number_Document', 'Date_of_birth',
            'rol', 'is_active',
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
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'Document_Type': forms.Select(attrs={'class': 'form-select'}),
            'Number_Document': forms.TextInput(attrs={'class': 'form-control'}),
            'Date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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

