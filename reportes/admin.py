from django.contrib import admin
from .models import Venta, DetalleVenta, ReporteGuardado, RegistroAuditoria

admin.site.register(Venta)
admin.site.register(DetalleVenta)
admin.site.register(ReporteGuardado)
admin.site.register(RegistroAuditoria)