"""Local sales capture. Network email sending is intentionally not included."""
import tkinter as tk
from tkinter import ttk, messagebox
from core import fetch, create_sale
from gui_utils import BG, title, form_entry, table, fill_table, error

class Ventas(ttk.Frame):
    def __init__(self,parent):
        super().__init__(parent)
        w=tk.Frame(self,bg=BG);w.pack(fill='both',expand=True)
        title(w,'Registro de ventas','Captura de estudios y datos operativos de demostración')
        columns=tk.Frame(w,bg=BG);columns.pack(fill='x',padx=16)
        left=tk.Frame(columns,bg=BG);left.pack(side='left',fill='both',expand=True,padx=(0,18))
        right=tk.Frame(columns,bg=BG);right.pack(side='left',fill='both',expand=True)
        tk.Label(left,text='Cliente',bg=BG).pack(anchor='w')
        self.customer=ttk.Combobox(left,state='readonly',width=36);self.customer.pack(fill='x')
        tk.Label(left,text='Sucursal',bg=BG).pack(anchor='w')
        self.branch=ttk.Combobox(left,state='readonly',width=36);self.branch.pack(fill='x')
        self.doctor=form_entry(left,'Médico','Médico de prueba')
        self.payment=form_entry(left,'Abono','0')
        self.notes=form_entry(left,'Observaciones','')
        self.fasting=form_entry(left,'Ayuno','')
        self.collection=form_entry(left,'Recolección','')
        self.urination=form_entry(left,'Micción','')
        self.delivery=form_entry(left,'Entrega','En mostrador')
        tk.Label(right,text='Estudio',bg=BG).pack(anchor='w')
        self.study=ttk.Combobox(right,state='readonly',width=36);self.study.pack(fill='x')
        self.quantity=form_entry(right,'Cantidad','1')
        ttk.Button(right,text='Añadir concepto',command=self.add_item).pack(anchor='w',pady=6)
        ttk.Button(right,text='Retirar concepto',command=self.remove_item).pack(anchor='w')
        self.view=table(w,('Estudio','Cantidad','Precio','Subtotal'))
        buttons=tk.Frame(w,bg=BG);buttons.pack(fill='x',padx=16,pady=8)
        ttk.Button(buttons,text='Actualizar catálogos',command=self.refresh).pack(side='left')
        ttk.Button(buttons,text='Guardar venta',command=self.save).pack(side='left',padx=8)
        self.total_label=tk.Label(buttons,text='Total: $0.00',bg=BG,font=('Segoe UI',12,'bold'));self.total_label.pack(side='right')
        self.items=[];self.refresh()

    def refresh(self):
        self.customers=fetch('SELECT id,name FROM customers ORDER BY name')
        self.branches=fetch('SELECT id,name FROM branches ORDER BY id')
        self.studies=fetch('SELECT id,name,price FROM studies ORDER BY name')
        self.customer['values']=[f"{r['id']} | {r['name']}" for r in self.customers]
        self.branch['values']=[f"{r['id']} | {r['name']}" for r in self.branches]
        self.study['values']=[f"{r['id']} | {r['name']} (${r['price']:.2f})" for r in self.studies]
        for combo in (self.customer,self.branch,self.study):
            if combo['values'] and not combo.get():combo.current(0)

    @staticmethod
    def selected(combo):
        if not combo.get():raise ValueError('Selecciona una opción válida')
        return int(combo.get().split(' | ',1)[0])

    def add_item(self):
        try:
            study_id=self.selected(self.study);qty=int(self.quantity.get())
            if qty<=0:raise ValueError('Cantidad inválida')
            found=next(r for r in self.studies if r['id']==study_id)
            self.items.append((study_id,qty,found['name'],found['price']))
            self.refresh_items()
        except Exception as exc:error(exc)

    def refresh_items(self):
        fill_table(self.view,[(name,qty,f'${price:.2f}',f'${qty*price:.2f}') for _,qty,name,price in self.items])
        self.total_label.config(text=f"Total: ${sum(q*p for _,q,_,p in self.items):,.2f}")

    def remove_item(self):
        sel=self.view.selection()
        if sel:
            index=self.view.index(sel[0]);self.items.pop(index);self.refresh_items()

    def save(self):
        try:
            folio=create_sale(self.selected(self.customer),self.doctor.get(),self.selected(self.branch),
               [(study_id,qty) for study_id,qty,_,_ in self.items],float(self.payment.get()),
               self.collection.get(),self.fasting.get(),self.urination.get(),self.notes.get(),self.delivery.get())
            messagebox.showinfo('Venta registrada',f'Folio: {folio}')
            self.items.clear();self.refresh_items()
        except Exception as exc:error(exc)
