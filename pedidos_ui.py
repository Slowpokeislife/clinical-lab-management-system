import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from datetime import date
from core import fetch,sales_between
from pedidos import export_receipts, export_financial_report
from gui_utils import BG,title,form_entry,table,fill_table,error

class Pedidos(ttk.Frame):
    def __init__(self,parent):
        super().__init__(parent)
        w=tk.Frame(self,bg=BG);w.pack(fill='both',expand=True)
        title(w,'Reportes y recibos','Generación de documentos Excel por intervalo de fechas')
        controls=tk.Frame(w,bg=BG);controls.pack(fill='x',padx=16)
        today=date.today().isoformat()
        self.start=form_entry(controls,'Inicio YYYY-MM-DD',today[:4]+'-01-01')
        self.end=form_entry(controls,'Fin YYYY-MM-DD',today)
        branches=fetch('SELECT id,name FROM branches ORDER BY id')
        self.branch=ttk.Combobox(controls,state='readonly',values=['Todas las sucursales']+[f"{r['id']} | {r['name']}" for r in branches],width=36)
        self.branch.current(0);self.branch.pack(anchor='w',pady=8)
        buttons=tk.Frame(w,bg=BG);buttons.pack(fill='x',padx=16,pady=8)
        ttk.Button(buttons,text='Consultar',command=self.refresh).pack(side='left')
        ttk.Button(buttons,text='Generar recibos Excel',command=lambda:self.export(export_receipts)).pack(side='left',padx=8)
        ttk.Button(buttons,text='Generar reporte económico',command=lambda:self.export(export_financial_report)).pack(side='left')
        self.view=table(w,('Fecha','Folio','Sucursal','Cliente','Total','Costos','Abono','Saldo'))
        self.refresh()

    def branch_id(self):
        return int(self.branch.get().split(' | ',1)[0]) if self.branch.current()>0 else None

    def bounds(self):
        start=self.start.get().strip();end=self.end.get().strip()
        if date.fromisoformat(start)>date.fromisoformat(end):raise ValueError('Fecha inicial posterior a la final')
        return start,end,self.branch_id()

    def refresh(self):
        try:
            rows=sales_between(*self.bounds())
            fill_table(self.view,[(r['created_at'],r['folio'],r['branch'],r['customer'],f"${r['total']:.2f}",
                                  f"${r['cost']:.2f}",f"${r['payment']:.2f}",f"${r['due']:.2f}") for r in rows])
        except Exception as exc:error(exc)

    def export(self,fn):
        try:
            bounds=self.bounds()
            path=filedialog.asksaveasfilename(defaultextension='.xlsx',filetypes=[('Excel','*.xlsx')])
            if not path:return
            count=fn(path,*bounds)
            messagebox.showinfo('Exportación',f'Archivo generado con {count} registros')
        except Exception as exc:error(exc)
