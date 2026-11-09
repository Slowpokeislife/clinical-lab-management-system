import tkinter as tk
from tkinter import ttk
from gui_utils import BG,NAV
from clientes import Clientes
from inventario import Inventario
from ventas import Ventas
from pedidos_ui import Pedidos
from proveedor import Proveedor
from informacion import Informacion

class Container(ttk.Frame):
    def __init__(self,parent):
        super().__init__(parent)
        self.pack(fill='both',expand=True)
        nav=tk.Frame(self,bg=NAV,width=200);nav.pack(side='left',fill='y');nav.pack_propagate(False)
        tk.Label(nav,text='LAB DEMO',bg=NAV,fg='white',font=('Segoe UI',17,'bold')).pack(pady=(22,26))
        self.area=ttk.Frame(self);self.area.pack(side='right',fill='both',expand=True)
        self.pages={}
        for caption,cls in [('Ventas',Ventas),('Clientes',Clientes),('Estudios',Inventario),('Reportes',Pedidos),('Excel',Proveedor),('Información',Informacion)]:
            btn=tk.Button(nav,text=caption,anchor='w',bg=NAV,fg='white',activebackground='#284862',activeforeground='white',bd=0,
                          padx=19,pady=10,font=('Segoe UI',11),command=lambda c=cls:self.show(c))
            btn.pack(fill='x',padx=8,pady=3)
        self.show(Ventas)

    def show(self,cls):
        for item in self.area.winfo_children():item.destroy()
        page=cls(self.area);page.pack(fill='both',expand=True)
