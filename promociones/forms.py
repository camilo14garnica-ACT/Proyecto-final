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
        for campo in self.fields.values():
            if isinstance(campo.widget, forms.Select):
                campo.widget.attrs["class"] = "form-select"
            else:
                campo.widget.attrs["class"] = "form-control"