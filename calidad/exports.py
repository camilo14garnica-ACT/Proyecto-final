import io
from datetime import datetime
from django.http import HttpResponse
from django.utils import timezone
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def _aplicar_estilo_tabla(ws, titulo, columnas, filas):
    """Aplica formato profesional institucional a una hoja de cálculo en Excel."""
    # Título principal
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(columnas))
    celda_titulo = ws.cell(row=1, column=1, value=f"VETERINARIA MASCOTT — {titulo.upper()}")
    celda_titulo.font = Font(name='Arial', size=14, bold=True, color='FFFFFF')
    celda_titulo.fill = PatternFill(start_color='1565C0', end_color='1565C0', fill_type='solid')
    celda_titulo.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 35

    # Subtítulo con fecha
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(columnas))
    celda_sub = ws.cell(row=2, column=1, value=f"Generado el: {timezone.now().strftime('%d/%m/%Y %H:%M')} | Sistema de Gestión de Calidad")
    celda_sub.font = Font(name='Arial', size=9, italic=True, color='555555')
    celda_sub.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[2].height = 20

    # Espacio
    ws.row_dimensions[3].height = 10

    # Encabezados de columna
    header_fill = PatternFill(start_color='0D47A1', end_color='0D47A1', fill_type='solid')
    header_font = Font(name='Arial', size=10, bold=True, color='FFFFFF')
    borde_delgado = Border(
        left=Side(style='thin', color='D0D0D0'),
        right=Side(style='thin', color='D0D0D0'),
        top=Side(style='thin', color='D0D0D0'),
        bottom=Side(style='thin', color='D0D0D0')
    )

    ws.row_dimensions[4].height = 25
    for col_idx, col_name in enumerate(columnas, 1):
        c = ws.cell(row=4, column=col_idx, value=col_name)
        c.fill = header_fill
        c.font = header_font
        c.alignment = Alignment(horizontal='center', vertical='center')
        c.border = borde_delgado

    # Filas de datos
    fill_zebra = PatternFill(start_color='F8FAFC', end_color='F8FAFC', fill_type='solid')
    for row_idx, fila in enumerate(filas, 5):
        ws.row_dimensions[row_idx].height = 20
        es_par = (row_idx % 2 == 0)
        for col_idx, valor in enumerate(fila, 1):
            c = ws.cell(row=row_idx, column=col_idx, value=valor)
            c.font = Font(name='Arial', size=9)
            c.border = borde_delgado
            if es_par:
                c.fill = fill_zebra
            if isinstance(valor, (int, float)):
                c.alignment = Alignment(horizontal='center', vertical='center')
            else:
                c.alignment = Alignment(horizontal='left', vertical='center')

    # Ajustar ancho de columnas automáticamente
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            # Ignorar filas de títulos combinadas
            if cell.row in (1, 2, 3):
                continue
            val_str = str(cell.value or '')
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)


def exportar_pqrs_excel(queryset):
    """Genera archivo Excel descargable con las solicitudes PQRS."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "PQRS y Quejas"

    columnas = [
        "Radicado #", "Tipo Solicitud", "Estado", "Cliente",
        "Documento", "Correo", "Descripción", "Fecha Radicación"
    ]
    filas = []
    for p in queryset.select_related('cliente'):
        filas.append([
            p.pk,
            p.get_tipo_display(),
            p.get_estado_display(),
            p.cliente.get_full_name() or p.cliente.username,
            getattr(p.cliente, 'Number_Document', '') or '',
            p.cliente.email or '',
            p.descripcion,
            p.fecha.strftime('%d/%m/%Y %H:%M') if p.fecha else '',
        ])

    _aplicar_estilo_tabla(ws, "Reporte de PQRS y Quejas", columnas, filas)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    nombre_archivo = f"reporte_pqrs_mascott_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    return response


def exportar_lotes_excel(queryset):
    """Genera archivo Excel descargable con el control de lotes y vencimientos."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Lotes de Productos"

    hoy = timezone.now().date()
    columnas = [
        "Lote #", "Producto", "Fecha Vencimiento", "Estado Calidad",
        "Días para Vencer", "Alerta"
    ]
    filas = []
    for l in queryset.select_related('producto'):
        dias = (l.fecha_vencimiento - hoy).days if l.fecha_vencimiento else 0
        if dias < 0:
            alerta = "VENCIDO"
        elif dias <= 30:
            alerta = "PRÓXIMO A VENCER"
        else:
            alerta = "VIGENTE"

        filas.append([
            l.numero_lote,
            l.producto.nombre if l.producto else '',
            l.fecha_vencimiento.strftime('%d/%m/%Y') if l.fecha_vencimiento else '',
            l.get_estado_calidad_display(),
            dias,
            alerta,
        ])

    _aplicar_estilo_tabla(ws, "Control de Lotes y Vencimientos", columnas, filas)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    nombre_archivo = f"reporte_lotes_mascott_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    return response


def exportar_encuestas_excel(queryset):
    """Genera archivo Excel descargable con las encuestas de satisfacción de clientes."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Satisfacción Clientes"

    columnas = [
        "ID", "Cliente", "Documento", "Cita / Mascota",
        "Puntuación (1-5)", "Comentarios", "Fecha Evaluación"
    ]
    filas = []
    for e in queryset.select_related('cliente', 'cita__mascota'):
        cita_info = ""
        if e.cita:
            cita_info = f"Cita #{e.cita.pk} - {e.cita.mascota.nombre if e.cita.mascota else 'Sin mascota'}"
        else:
            cita_info = "General"

        filas.append([
            e.pk,
            e.cliente.get_full_name() or e.cliente.username,
            getattr(e.cliente, 'Number_Document', '') or '',
            cita_info,
            f"{e.puntuacion} ★",
            e.comentarios or 'Sin comentario',
            e.fecha.strftime('%d/%m/%Y %H:%M') if e.fecha else '',
        ])

    _aplicar_estilo_tabla(ws, "Encuestas de Satisfacción de Clientes", columnas, filas)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    nombre_archivo = f"reporte_satisfaccion_mascott_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    return response


def exportar_no_conformidades_excel(queryset):
    """Genera archivo Excel descargable con las No Conformidades y Acciones Correctivas."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "No Conformidades"

    columnas = [
        "NC #", "Origen", "Estado", "Descripción del Problema",
        "Acción Correctiva Adoptada", "Fecha Registro"
    ]
    filas = []
    for nc in queryset.select_related('pqrs', 'encuesta'):
        origen = ""
        if nc.pqrs:
            origen = f"PQRS #{nc.pqrs.pk} ({nc.pqrs.get_tipo_display()})"
        elif nc.encuesta:
            origen = f"Encuesta #{nc.encuesta.pk} ({nc.encuesta.puntuacion}★)"
        else:
            origen = "Auditoría Interna"

        filas.append([
            nc.pk,
            origen,
            nc.get_estado_display(),
            nc.descripcion_problema,
            nc.accion_correctiva or 'Pendiente de definir',
            nc.fecha.strftime('%d/%m/%Y %H:%M') if nc.fecha else '',
        ])

    _aplicar_estilo_tabla(ws, "Registro de No Conformidades y Mejora Continua", columnas, filas)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    nombre_archivo = f"reporte_no_conformidades_mascott_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    return response

