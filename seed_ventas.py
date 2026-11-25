import random
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from productos.models import Categoria, Producto
from reportes.models import Venta, DetalleVenta

if not Producto.objects.exists():
    cat, _ = Categoria.objects.get_or_create(nombre="Alimentos")
    for nombre, precio in [("Concentrado perro 5kg", "45000"), ("Concentrado gato 3kg", "38000"),
                           ("Shampoo antipulgas", "22000"), ("Collar", "15000"), ("Juguete mordedor", "9000")]:
        Producto.objects.create(nombre=nombre, categoria=cat, precio=Decimal(precio), stock=100)

productos = list(Producto.objects.all())
clientes = ["Laura Gómez", "Carlos Pérez", "Ana Rojas", "Miguel Torres", "Sofía Díaz"]
metodos = ["EFECTIVO", "TARJETA", "TRANSFERENCIA"]

for i in range(40):
    venta = Venta.objects.create(cliente=random.choice(clientes), metodo_pago=random.choice(metodos))
    total = Decimal("0")
    for prod in random.sample(productos, k=min(len(productos), random.randint(1, 3))):
        cant = random.randint(1, 4)
        DetalleVenta.objects.create(venta=venta, producto=prod, cantidad=cant, precio_unitario=prod.precio)
        total += prod.precio * cant
    fecha = timezone.now() - timedelta(days=random.randint(0, 90))
    Venta.objects.filter(pk=venta.pk).update(total=total, fecha=fecha)

print("Ventas creadas:", Venta.objects.count())