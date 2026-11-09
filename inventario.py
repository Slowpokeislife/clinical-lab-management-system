import tkinter as tk
from tkinter import ttk, messagebox
from core import add_study, fetch, connect
from gui_utils import BG, title, form_entry, table, fill_table, error

class Inventario(ttk.Frame):
    def __init__(self,parent):
        super().__init__(parent)
        w=tk.Frame(self,bg=BG);w.pack(fill='both',expand=True)
        title(w,'Catálogo de estudios','Precios y costos de demostración; no representan tarifas reales')
        form=tk.Frame(w,bg=BG);form.pack(fill='x',padx=16)
        labels=('Estudio','Muestra','Condiciones','Días de entrega','Precio','Costo directo')
        self.fields=[form_entry(form,s) for s in labels]
        buttons=tk.Frame(w,bg=BG);buttons.pack(fill='x',padx=16,pady=8)
        ttk.Button(buttons,text='Agregar estudio',command=self.add).pack(side='left')
        ttk.Button(buttons,text='Guardar cambios seleccionados',command=self.update).pack(side='left',padx=8)
        self.view=table(w,('ID',*labels))
        self.view.bind('<<TreeviewSelect>>',self.select)
        self.refresh()

    def refresh(self):
        fill_table(self.view,[(r['id'],r['name'],r['sample'],r['instructions'],r['days'],r['price'],r['cost']) for r in fetch('SELECT * FROM studies ORDER BY id')])

    def select(self,event=None):
        if not self.view.selection():return
        values=self.view.item(self.view.selection()[0],'values')
        for e,value in zip(self.fields,values[1:]):e.delete(0,'end');e.insert(0,value)

    def values(self):
        values=[e.get().strip() for e in self.fields]
        if not values[0]:raise ValueError('Nombre del estudio requerido')
        return (values[0],values[1],values[2],int(values[3]),float(values[4]),float(values[5]))

    def add(self):
        try:add_study(*self.values());self.refresh()
        except Exception as exc:error(exc)

    def update(self):
        if not self.view.selection():messagebox.showwarning('Selección','Selecciona un estudio');return
        try:
            record_id=int(self.view.item(self.view.selection()[0],'values')[0])
            values=self.values()
            if min(values[-2:])<0:raise ValueError('Los importes no pueden ser negativos')
            with connect() as db:
                db.execute('''UPDATE studies SET name=?,sample=?,instructions=?,days=?,price=?,cost=? WHERE id=?''',(*values,record_id))
            self.refresh()
        except Exception as exc:error(exc)
