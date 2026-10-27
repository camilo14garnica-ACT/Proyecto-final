from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import Usuario


class CrearUsuarioForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa una contraseña'}),
        error_messages={'required': 'La contraseña es obligatoria.'}
    )
    password_confirmacion = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirma tu contraseña'}),
        error_messages={'required': 'Debes confirmar tu contraseña.'}
    )

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'Document_Type', 'Number_Document', 'Date_of_birth', 'password']
        labels = {
            'username': 'Nombre de usuario', 'first_name': 'Nombres', 'last_name': 'Apellidos',
            'email': 'Correo electrónico', 'Document_Type': 'Tipo de documento',
            'Number_Document': 'Número de documento', 'Date_of_birth': 'Fecha de nacimiento',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Crea tu nombre de usuario'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tus nombres'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tus apellidos'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'}),
            'Document_Type': forms.Select(attrs={'class': 'form-select'}),
            'Number_Document': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de documento'}),
            'Date_of_birth': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirmacion = cleaned_data.get('password_confirmacion')
        if password and password_confirmacion:
            if password != password_confirmacion:
                self.add_error('password_confirmacion', 'Las contraseñas no coinciden.')
            else:
                try:
                    validate_password(password, self.instance)
                except forms.ValidationError as error:
                    self.add_error('password', error)
        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['password'])
        if commit:
            usuario.save()
        return usuario


class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'Document_Type', 'Number_Document', 'Date_of_birth']
        labels = {
            'first_name': 'Nombres', 'last_name': 'Apellidos', 'email': 'Correo electrónico',
            'Document_Type': 'Tipo de documento', 'Number_Document': 'Número de documento',
            'Date_of_birth': 'Fecha de nacimiento',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'Document_Type': forms.Select(attrs={'class': 'form-select'}),
            'Number_Document': forms.TextInput(attrs={'class': 'form-control'}),
            'Date_of_birth': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
        }


class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'Document_Type', 'Number_Document', 'Date_of_birth', 'rol', 'is_active']
        labels = {
            'username': 'Nombre de usuario', 'first_name': 'Nombres', 'last_name': 'Apellidos',
            'email': 'Correo electrónico', 'Document_Type': 'Tipo de documento',
            'Number_Document': 'Número de documento', 'Date_of_birth': 'Fecha de nacimiento',
            'rol': 'Rol del usuario', 'is_active': 'Cuenta activa',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'Document_Type': forms.Select(attrs={'class': 'form-select'}),
            'Number_Document': forms.TextInput(attrs={'class': 'form-control'}),
            'Date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
