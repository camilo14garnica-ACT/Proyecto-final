from django import forms

from .models import Categoria, Producto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "nombre",
            "descripcion",
            "categoria",
            "precio",
            "stock",
            "imagen",
            "estado",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # La descripción es opcional en el modelo, pero el Jira pide campos obligatorios
        self.fields["descripcion"].required = True
        # Solo se pueden elegir categorías activas
        self.fields["categoria"].queryset = Categoria.objects.filter(estado="ACTIVO")
        self.fields["categoria"].empty_label = "Selecciona una categoría"
        self.fields["descripcion"].widget.attrs["rows"] = 3
        # Estilo de Bootstrap para que se vea igual que el resto del panel
        for nombre, campo in self.fields.items():
            if isinstance(campo.widget, forms.Select):
                campo.widget.attrs["class"] = "form-select"
            else:
                campo.widget.attrs["class"] = "form-control"

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio.")
        return nombre

    def clean_precio(self):
        precio = self.cleaned_data["precio"]
        if precio is None or precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor a 0.")
        return precio

    def clean_stock(self):
        stock = self.cleaned_data["stock"]
        if stock is None or stock < 0:
            raise forms.ValidationError("El stock no puede ser negativo.")
        return stock