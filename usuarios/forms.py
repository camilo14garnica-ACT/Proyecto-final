
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



    
