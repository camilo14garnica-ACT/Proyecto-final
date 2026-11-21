from decimal import Decimal, InvalidOperation

from django import forms
from django.db.models import Q

from .models import Categoria, Producto


def estilizar(form):
    """Pone el estilo de Bootstrap a todos los campos."""
    for campo in form.fields.values():
        if isinstance(campo.widget, forms.Select):
            campo.widget.attrs["class"] = "form-select"
        else:
            campo.widget.attrs["class"] = "form-control"


def convertir_precio(texto):
    """Acepta 10000, 10.000, 1.250.000, 1.250,50 y $10.000."""
    t = texto.replace("$", "").replace(" ", "").strip()
    if "," in t:
        # Coma = decimales, punto = miles (1.250,50)
        t = t.replace(".", "").replace(",", ".")
    elif t.count(".") > 1:
        # Varios puntos = miles (1.250.000)
        t = t.replace(".", "")
    elif "." in t and len(t.split(".")[1]) == 3:
        # Un punto con 3 dígitos después = miles (10.000)
        t = t.replace(".", "")
    return Decimal(t)


class ProductoForm(forms.ModelForm):
    # Campo de texto para poder escribir 10.000 sin que lo rechace
    precio = forms.CharField(label="Precio")

    class Meta:
        model = Producto
        fields = ["nombre", "descripcion", "categoria", "precio", "stock", "imagen", "estado"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["descripcion"].required = True
        # Solo categorías activas (más la actual, si se está editando)
        activas = Q(estado="ACTIVO")
        if self.instance.pk:
            activas |= Q(pk=self.instance.categoria_id)
        self.fields["categoria"].queryset = Categoria.objects.filter(activas)
        self.fields["categoria"].empty_label = "Selecciona una categoría"
        estilizar(self)
        self.fields["descripcion"].widget.attrs["rows"] = 3
        self.fields["precio"].widget.attrs["placeholder"] = "Ej: 10000 o 10.000"

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio.")
        return nombre

    def clean_precio(self):
        texto = str(self.cleaned_data["precio"])
        try:
            precio = convertir_precio(texto)
        except InvalidOperation:
            raise forms.ValidationError("Escribe un precio válido, por ejemplo 10000 o 10.000.")
        if not precio.is_finite():
            raise forms.ValidationError("Escribe un precio válido, por ejemplo 10000 o 10.000.")
        if precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor a 0.")
        if precio.as_tuple().exponent < -2:
            raise forms.ValidationError("El precio admite máximo 2 decimales.")
        if precio >= 100000000:
            raise forms.ValidationError("El precio es demasiado alto.")
        return precio

    def clean_stock(self):
        stock = self.cleaned_data["stock"]
        if stock is None or stock < 0:
            raise forms.ValidationError("El stock no puede ser negativo.")
        return stock


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion", "estado"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        estilizar(self)

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if not nombre:
            raise forms.ValidationError("El nombre es obligatorio.")
        repetida = Categoria.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk)
        if repetida.exists():
            raise forms.ValidationError("Ya existe una categoría con ese nombre.")
        return nombre


class AjusteStockForm(forms.Form):
    TIPOS = [("ENTRADA", "Entrada (sumar)"), ("SALIDA", "Salida (restar)")]

    tipo = forms.ChoiceField(choices=TIPOS, label="Tipo de movimiento")
    cantidad = forms.IntegerField(min_value=1, label="Cantidad")

    def __init__(self, *args, producto=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.producto = producto
        estilizar(self)

    def clean(self):
        datos = super().clean()
        tipo = datos.get("tipo")
        cantidad = datos.get("cantidad")
        if tipo == "SALIDA" and cantidad and cantidad > self.producto.stock:
            self.add_error(
                "cantidad",
                f"No hay suficiente stock. Disponible: {self.producto.stock}.",
            )
        return datos