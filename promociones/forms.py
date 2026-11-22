from datetime import date

from django import forms

from productos.models import Producto

from .models import Promocion


class PromocionForm(forms.ModelForm):
    class Meta:
        model = Promocion
        fields = ["nombre", "descripcion", "descuento", "fecha_inicio", "fecha_fin", "productos", "estado"]
        widgets = {
            "fecha_inicio": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "fecha_fin": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "descripcion": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["productos"].queryset = Producto.objects.filter(estado="ACTIVO")
        self.fields["productos"].error_messages["required"] = "Selecciona al menos un producto."
        for campo in self.fields.values():
            if isinstance(campo.widget, forms.Select):
                campo.widget.attrs["class"] = "form-select"
            else:
                campo.widget.attrs["class"] = "form-control"

    # VM-706 — Datos obligatorios completos antes de guardar
    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio.")
        return nombre

    def clean(self):
        datos = super().clean()
        inicio = datos.get("fecha_inicio")
        fin = datos.get("fecha_fin")
        estado = datos.get("estado")

        if inicio and fin and fin < inicio:
            self.add_error("fecha_fin", "La fecha de fin no puede ser anterior a la de inicio.")
        elif fin and estado == "ACTIVA" and fin < date.today():
            self.add_error(
                "fecha_fin",
                "No puedes activar una promoción que ya venció. Cambia la fecha de fin o márcala como Inactiva.",
            )
        return datos

    # VM-709 — Si una persona cambia el estado, deja de ser "por vencimiento"
    def save(self, commit=True):
        promocion = super().save(commit=False)
        estaba_activa = self.initial.get("estado") == "ACTIVA"
        if promocion.estado == "ACTIVA" or estaba_activa:
            promocion.inactiva_por_vencimiento = False
        if commit:
            promocion.save()
            self.save_m2m()
        return promocion