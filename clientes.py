import tkinter as tk
from tkinter import ttk, messagebox
from core import add_customer, fetch, connect
from gui_utils import BG, title, form_entry, table, fill_table, error

class Clientes(ttk.Frame):
    def __init__(self,parent):
        super().__init__(parent)
        self.configure(padding=0)
        wrapper=tk.Frame(self,bg=BG);wrapper.pack(fill='both',expand=True)
        title(wrapper,'Clientes','Registro local de personas ficticias en la demostración')
        form=tk.Frame(wrapper,bg=BG);form.pack(fill='x',padx=16)
        self.fields=[form_entry(form,label) for label in ('Nombre','Nacimiento YYYY-MM-DD','Género','Correo','Teléfono')]
        controls=tk.Frame(wrapper,bg=BG);controls.pack(fill='x',padx=16,pady=7)
        ttk.Button(controls,text='Agregar cliente',command=self.add).pack(side='left')
        ttk.Button(controls,text='Actualizar lista',command=self.refresh).pack(side='left',padx=8)
        ttk.Button(controls,text='Guardar cambios seleccionados',command=self.update).pack(side='left')
        self.view=table(wrapper,('ID','Nombre','Nacimiento','Género','Correo','Teléfono'))
        self.view.bind('<<TreeviewSelect>>',self.select)
        self.refresh()

    def refresh(self):
        fill_table(self.view,[(r['id'],r['name'],r['dob'],r['gender'],r['email'],r['phone']) for r in fetch('SELECT * FROM customers ORDER BY id DESC')])

    def select(self,event=None):
        selection=self.view.selection()
        if not selection:return
        values=self.view.item(selection[0],'values')
        for entry,value in zip(self.fields,values[1:]):
            entry.delete(0,'end');entry.insert(0,value)

    def add(self):
        try:
            add_customer(*(entry.get().strip() for entry in self.fields))
            self.refresh()
        except Exception as exc:error(exc)

    def update(self):
        sel=self.view.selection()
        if not sel:
            messagebox.showwarning('Selección','Selecciona una fila');return
        try:
            values=[e.get().strip() for e in self.fields]
            if not values[0]:raise ValueError('Nombre requerido')
            record_id=int(self.view.item(sel[0],'values')[0])
            with connect() as db:
                db.execute('UPDATE customers SET name=?,dob=?,gender=?,email=?,phone=? WHERE id=?',(*values,record_id))
            self.refresh()
        except Exception as exc:error(exc)
