"""Excel exports: laboratory work sheets and financial reports."""
from datetime import date, datetime
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from core import sales_between, sale_items


def _style(ws):
    ws.freeze_panes = 'A5'
    for cell in ws[1]:
        cell.font = Font(bold=True, size=14, color='FFFFFF')
        cell.fill = PatternFill('solid', fgColor='17324D')
    for col in ws.columns:
        letter = get_column_letter(col[0].column)
        width = min(55, max(14, max(len(str(c.value or '')) for c in col) + 3))
        ws.column_dimensions[letter].width = width
    ws.sheet_view.showGridLines = False


def export_receipts(path, start, end, branch_id=None):
    """One worksheet for each synthetic patient sale in the selected date range."""
    rows = sales_between(start, end, branch_id)
    if not rows:
        raise ValueError('No hay ventas en el intervalo seleccionado.')
    book = Workbook()
    book.remove(book.active)
    for row in rows:
        ws = book.create_sheet(f"Recibo {row['id']}")
        ws.append(['LABORATORY OPERATIONS — DEMO DATA'])
        ws.append(['Información sintética; no es un resultado clínico ni un comprobante fiscal'])
        ws.append(['Sucursal',row['branch'],'Folio',row['folio']])
        ws.append(['Paciente',row['customer'],'Nacimiento',row['dob']])
        ws.append(['Género',row['gender'],'Teléfono',row['phone']])
        ws.append(['Correo',row['email'],'Médico',row['doctor']])
        ws.append(['Fecha',row['created_at']])
        ws.append(['Recolección',row['collection_time'],'Ayuno',row['fasting']])
        ws.append(['Micción',row['urination'],'Entrega',row['result_delivery']])
        ws.append(['Observaciones',row['notes']])
        ws.append([])
        ws.append(['ESTUDIO','CANTIDAD','PRECIO UNITARIO','SUBTOTAL'])
        for item in sale_items(row['id']):
            ws.append([item['study'],item['quantity'],item['unit_price'],item['subtotal']])
        ws.append(['TOTAL',None,None,row['total']])
        ws.append(['ABONO',None,None,row['payment']])
        ws.append(['SALDO',None,None,row['due']])
        _style(ws)
        ws.column_dimensions['A'].width=42
        ws.column_dimensions['B'].width=24
        ws.column_dimensions['C'].width=23
        ws.column_dimensions['D'].width=29
        for row_cells in ws.iter_rows(min_row=13, min_col=3, max_col=4):
            for cell in row_cells:
                cell.number_format = '"$"#,##0.00'
    book.save(Path(path))
    return len(rows)


def export_financial_report(path, start, end, branch_id=None):
    """Revenue, direct cost and gross margin—not net profit."""
    rows = sales_between(start, end, branch_id)
    if not rows:
        raise ValueError('No hay ventas en el intervalo seleccionado.')
    wb = Workbook()
    detail = wb.active
    detail.title = 'Ventas'
    detail.append(['ECONOMIC REPORT — SYNTHETIC DATA'])
    detail.append([f'Period: {start} to {end}'])
    detail.append([])
    detail.append(['Fecha','Folio','Sucursal','Paciente ficticio','Ingresos','Costos directos','Margen bruto','Abonos','Saldos'])
    for sale in rows:
        detail.append([sale['created_at'],sale['folio'],sale['branch'],sale['customer'],sale['total'],sale['cost'],sale['total']-sale['cost'],sale['payment'],sale['due']])
    for cells in detail.iter_rows(min_row=5,min_col=5,max_col=9):
        for cell in cells:
            cell.number_format='"$"#,##0.00'
    _style(detail)
    metrics = wb.create_sheet('Resumen')
    metrics.append(['FINANCIAL SUMMARY — SYNTHETIC DATA'])
    metrics.append(['Métrica','Valor'])
    income = sum(s['total'] for s in rows)
    costs = sum(s['cost'] for s in rows)
    payments = sum(s['payment'] for s in rows)
    for name, value in [('Ventas registradas',len(rows)),('Ingresos facturados',income),('Costos directos estimados',costs),('Margen bruto estimado',income-costs),('Abonos recibidos',payments),('Saldo pendiente',income-payments)]:
        metrics.append([name,value])
    metrics.append(['NOTA','Margen bruto no equivale a utilidad neta. No incluye gastos indirectos ni impuestos.'])
    _style(metrics)
    wb.save(Path(path))
    return len(rows)
