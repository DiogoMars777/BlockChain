import io
from datetime import datetime
from typing import List, Dict, Any, Optional
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)


def generate_excel_bytes(
    report_title: str,
    tenant_name: str,
    tenant_nit: str,
    voice_summary: str,
    executive_summary: str,
    kpis: List[Dict[str, Any]],
    table_headers: List[str],
    table_rows: List[List[Any]],
    generated_at: str,
    user_email: str = "Admin",
) -> io.BytesIO:
    """
    Genera un archivo Excel (.xlsx) profesional, formateado y estilizado.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reporte Ejecutivo"
    ws.views.sheetView[0].showGridLines = True

    # Estilos Corporativos (Dark Slate & Cyan)
    header_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    
    accent_fill = PatternFill(start_color="0284C7", end_color="0284C7", fill_type="solid")
    accent_font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    
    kpi_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    kpi_label_font = Font(name="Calibri", size=9, bold=False, color="64748B")
    kpi_val_font = Font(name="Calibri", size=14, bold=True, color="0F172A")
    
    zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    white_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    
    thin_border = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1"),
    )

    # 1. Encabezado Corporativo
    ws.merge_cells("A1:G1")
    title_cell = ws["A1"]
    title_cell.value = f"🏢 {tenant_name.upper()} | NIT: {tenant_nit}"
    title_cell.fill = accent_fill
    title_cell.font = accent_font
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30

    ws.merge_cells("A2:G2")
    sub_cell = ws["A2"]
    sub_cell.value = f"Reporte de Inteligencia Artificial: {report_title}"
    sub_cell.font = Font(name="Calibri", size=12, bold=True, color="0F172A")
    sub_cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[2].height = 22

    ws.merge_cells("A3:G3")
    meta_cell = ws["A3"]
    meta_cell.value = f"Fecha de Emisión: {generated_at} (BOT UTC-4) | Solicitado por: {user_email} | Auditoría: Registrado en Bitácora"
    meta_cell.font = Font(name="Calibri", size=9, italic=True, color="64748B")
    meta_cell.alignment = Alignment(horizontal="left", vertical="center")

    # 2. Resumen Ejecutivo de la IA
    ws.merge_cells("A5:G5")
    ws["A5"].value = "💡 SÍNTESIS EJECUTIVA DE LA IA:"
    ws["A5"].font = Font(name="Calibri", size=11, bold=True, color="0284C7")

    ws.merge_cells("A6:G7")
    ai_box = ws["A6"]
    clean_summary = voice_summary.replace("**", "").replace("#", "")
    ai_box.value = clean_summary
    ai_box.font = Font(name="Calibri", size=10, italic=False, color="1E293B")
    ai_box.fill = kpi_fill
    ai_box.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

    # 3. KPIs
    row_kpi = 9
    if kpis:
        col_idx = 1
        for k in kpis[:5]:
            c1 = ws.cell(row=row_kpi, column=col_idx)
            c2 = ws.cell(row=row_kpi + 1, column=col_idx)
            c1.value = k.get("label", "").upper()
            c1.font = kpi_label_font
            c1.fill = kpi_fill
            c1.alignment = Alignment(horizontal="center", vertical="center")
            c1.border = thin_border
            
            c2.value = k.get("value", "")
            c2.font = kpi_val_font
            c2.fill = kpi_fill
            c2.alignment = Alignment(horizontal="center", vertical="center")
            c2.border = thin_border
            col_idx += 1
        row_kpi += 3

    # 4. Tabla de Datos
    start_table_row = row_kpi + 1
    if table_headers:
        for c_idx, h in enumerate(table_headers, start=1):
            cell = ws.cell(row=start_table_row, column=c_idx)
            cell.value = str(h).upper()
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
        ws.row_dimensions[start_table_row].height = 24

        curr_row = start_table_row + 1
        for r_idx, row in enumerate(table_rows):
            fill = zebra_fill if r_idx % 2 == 0 else white_fill
            for c_idx, val in enumerate(row, start=1):
                cell = ws.cell(row=curr_row, column=c_idx)
                cell.value = val
                cell.fill = fill
                cell.font = Font(name="Calibri", size=10, color="0F172A")
                cell.border = thin_border

                # Formateo numérico y alineación
                if isinstance(val, (int, float)):
                    if isinstance(val, float) and val > 100:
                        cell.number_format = '$#,##0.00'
                        cell.alignment = Alignment(horizontal="right", vertical="center")
                    else:
                        cell.alignment = Alignment(horizontal="center", vertical="center")
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="center")
            ws.row_dimensions[curr_row].height = 20
            curr_row += 1

    # Ajuste automático de anchos de columna
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            # ignorar celdas combinadas de los primeros rows
            if cell.row in [1, 2, 3, 5, 6, 7]:
                continue
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 14)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


def generate_pdf_bytes(
    report_title: str,
    tenant_name: str,
    tenant_nit: str,
    voice_summary: str,
    executive_summary: str,
    kpis: List[Dict[str, Any]],
    table_headers: List[str],
    table_rows: List[List[Any]],
    generated_at: str,
    user_email: str = "Admin",
) -> io.BytesIO:
    """
    Genera un informe PDF corporativo de alta calidad con membrete multi-tenant,
    análisis ejecutivo, métricas destacadas y tabla formateada.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    brand_blue = colors.HexColor("#0284C7")
    dark_slate = colors.HexColor("#0F172A")
    gray_muted = colors.HexColor("#64748B")
    card_bg = colors.HexColor("#F8FAFC")
    line_border = colors.HexColor("#CBD5E1")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=dark_slate,
        leading=20,
    )

    tenant_style = ParagraphStyle(
        "TenantHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=brand_blue,
        leading=14,
    )

    meta_style = ParagraphStyle(
        "DocMeta",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        textColor=gray_muted,
        leading=11,
    )

    ai_box_style = ParagraphStyle(
        "AIBox",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=dark_slate,
        leading=13,
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        textColor=colors.white,
        alignment=1,  # Centrado
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        textColor=dark_slate,
        leading=10,
    )

    story = []

    # 1. Cabecera Corporativa con Membrete Multi-Tenant
    header_data = [
        [
            Paragraph(f"<b>{tenant_name.upper()}</b><br/><font size='8' color='#64748B'>NIT: {tenant_nit} • Bolivia</font>", tenant_style),
            Paragraph(f"<b>SISTEMA DE TRAZABILIDAD</b><br/><font size='8' color='#64748B'>Módulo de IA & Analítica Oficial</font>", ParagraphStyle("Right", parent=tenant_style, alignment=2)),
        ]
    ]
    t_header = Table(header_data, colWidths=[300, 240])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_header)

    story.append(HRFlowable(width="100%", thickness=1.5, color=brand_blue, spaceBefore=4, spaceAfter=8))

    # 2. Título del Reporte y Metadatos
    story.append(Paragraph(f"Reporte Dinámico: {report_title}", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Emisión: {generated_at} (Hora oficial Bolivia BOT) | Solicitante: {user_email} | Estado: Verificado", meta_style))
    story.append(Spacer(1, 10))

    # 3. Cuadro de Síntesis de la IA
    clean_voice = voice_summary.replace("**", "").replace("#", "")
    ai_box_data = [
        [
            Paragraph("<b>💡 CONCLUSIÓN Y ANÁLISIS DE LA INTELIGENCIA ARTIFICIAL:</b>", ParagraphStyle("TitleAI", parent=ai_box_style, fontName="Helvetica-Bold", textColor=brand_blue)),
        ],
        [
            Paragraph(clean_voice, ai_box_style),
        ]
    ]
    t_ai_box = Table(ai_box_data, colWidths=[540])
    t_ai_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), card_bg),
        ('BOX', (0, 0), (-1, -1), 1, brand_blue),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(t_ai_box)
    story.append(Spacer(1, 12))

    # 4. KPIs en tarjetas
    if kpis:
        kpi_cells = []
        for k in kpis[:4]:
            cell_p = Paragraph(
                f"<font size='7' color='#64748B'><b>{k.get('label', '').upper()}</b></font><br/>"
                f"<font size='12' color='#0F172A'><b>{k.get('value', '')}</b></font>",
                ParagraphStyle("KPICell", parent=styles["Normal"], alignment=1)
            )
            kpi_cells.append(cell_p)

        col_w = 540 / max(len(kpi_cells), 1)
        t_kpi = Table([kpi_cells], colWidths=[col_w] * len(kpi_cells))
        t_kpi.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), card_bg),
            ('BOX', (0, 0), (-1, -1), 0.8, line_border),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, line_border),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t_kpi)
        story.append(Spacer(1, 14))

    # 5. Tabla de Datos
    if table_headers and table_rows:
        story.append(Paragraph("<b>Detalle de Registros Consolidados:</b>", ParagraphStyle("TableTitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10, textColor=dark_slate)))
        story.append(Spacer(1, 6))

        # Construir contenido para ReportLab Table
        header_row_flowables = [Paragraph(str(h).upper(), table_header_style) for h in table_headers]
        grid_data = [header_row_flowables]

        for r_idx, row in enumerate(table_rows[:60]):  # Cap a 60 filas para optimizar páginas
            row_flowables = []
            for cell_val in row:
                s_val = str(cell_val)
                # Formato monetario si es float
                if isinstance(cell_val, float):
                    s_val = f"${cell_val:,.2f}"
                row_flowables.append(Paragraph(s_val, table_cell_style))
            grid_data.append(row_flowables)

        num_cols = len(table_headers)
        avail_w = 540
        w_per_col = avail_w / num_cols
        # Ajuste inteligente de anchos si hay descripción o nombres largos
        col_widths = [w_per_col] * num_cols

        t_grid = Table(grid_data, colWidths=col_widths, repeatRows=1)
        t_style = [
            ('BACKGROUND', (0, 0), (-1, 0), dark_slate),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, line_border),
        ]
        # Zebra striping
        for i in range(1, len(grid_data)):
            if i % 2 == 0:
                t_style.append(('BACKGROUND', (0, i), (-1, i), card_bg))
        t_grid.setStyle(TableStyle(t_style))
        story.append(t_grid)

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=line_border, spaceBefore=4, spaceAfter=8))
    story.append(Paragraph("Este documento fue generado de forma automática mediante comandos de voz auditados en el Sistema de Trazabilidad Multi-Tenant. La información contenida refleja el estado inmutable de los registros a la fecha de corte.", meta_style))

    doc.build(story)
    buf.seek(0)
    return buf
