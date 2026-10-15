
from django import forms
from django.contrib.auth.password_validation import validate_password
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

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_confirmacion = cleaned_data.get('password_confirmacion')

        if password and password_confirmacion:
            if password != password_confirmacion:
                self.add_error('password_confirmacion', "Las contraseñas no coinciden.")
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
        fields = [
            'first_name',
            'last_name',
            'email',
            'Document_Type',
            'Number_Document',
            'Date_of_birth',
        ]
    


    
