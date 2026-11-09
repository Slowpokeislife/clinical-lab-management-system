"""Safe Excel interchange for demo catalogs and customers; no destructive table replacement."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from openpyxl import Workbook, load_workbook
from core import connect, fetch
from gui_utils import BG,title,error

TABLES={
 'Clientes':('customers',('name','dob','gender','email','phone')),
 'Estudios':('studies',('name','sample','instructions','days','price','cost')),
}

class Proveedor(ttk.Frame):
    def __init__(self,parent):
        super().__init__(parent)
        w=tk.Frame(self,bg=BG);w.pack(fill='both',expand=True)
        title(w,'Importar y exportar Excel','Intercambio de catálogos; no se admite importar datos reales en esta versión pública')
        self.choice=ttk.Combobox(w,state='readonly',values=list(TABLES));self.choice.pack(anchor='w',padx=16,pady=10)
        self.choice.current(0)
        ttk.Button(w,text='Exportar tabla seleccionada',command=self.export).pack(anchor='w',padx=16,pady=7)
        ttk.Button(w,text='Importar datos de prueba desde Excel',command=self.import_xlsx).pack(anchor='w',padx=16,pady=7)
        tk.Label(w,text='Importación acumulativa con validación. No elimina registros existentes.',bg=BG,fg='#506477').pack(anchor='w',padx=16,pady=14)

    def export(self):
        try:
            table,cols=TABLES[self.choice.get()]
            path=filedialog.asksaveasfilename(defaultextension='.xlsx',filetypes=[('Excel','*.xlsx')])
            if not path:return
            wb=Workbook();ws=wb.active;ws.title=self.choice.get()
            ws.append(list(cols))
            for record in fetch(f'SELECT {",".join(cols)} FROM {table}'):
                ws.append([record[col] for col in cols])
            wb.save(path);messagebox.showinfo('Exportación','Excel guardado')
        except Exception as exc:error(exc)

    def import_xlsx(self):
        try:
            table,cols=TABLES[self.choice.get()]
            path=filedialog.askopenfilename(filetypes=[('Excel','*.xlsx')])
            if not path:return
            if Path(path).stat().st_size > 5_000_000:
                raise ValueError('El archivo supera el máximo de 5 MB para la demostración')
            wb=load_workbook(path,read_only=True,data_only=True)
            ws=wb.active
            records=ws.iter_rows(values_only=True)
            header=next(records,None)
            if tuple(header or ()) != cols:
                raise ValueError('Columnas esperadas: '+', '.join(cols))
            data=[]
            for row in records:
                if not any(v is not None for v in row):continue
                if len(row)!=len(cols) or not row[0]:raise ValueError('Hay filas con datos incompletos')
                if table=='studies':
                    row=(*row[:3],int(row[3]),float(row[4]),float(row[5]))
                    if row[4]<0 or row[5]<0:raise ValueError('Importes inválidos')
                data.append(row)
                if len(data)>1000:raise ValueError('Máximo 1000 registros por importación')
            wb.close()
            if not data:raise ValueError('El archivo está vacío')
            if not messagebox.askyesno('Confirmar',f'Agregar {len(data)} registros ficticios de {self.choice.get()}?'):
                return
            placeholder=','.join('?' for _ in cols)
            with connect() as db:
                db.executemany(f'INSERT OR IGNORE INTO {table}({",".join(cols)}) VALUES({placeholder})',data)
            messagebox.showinfo('Importación','Operación completada; revisa el catálogo.')
        except Exception as exc:error(exc)
