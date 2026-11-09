import tkinter as tk
from tkinter import ttk, messagebox
from core import authenticate
from gui_utils import BG,NAV

class LogIn(ttk.Frame):
    def __init__(self,parent,on_success):
        super().__init__(parent)
        self.on_success=on_success
        w=tk.Frame(self,bg=BG);w.pack(fill='both',expand=True)
        card=tk.Frame(w,bg='white',padx=36,pady=32)
        card.place(relx=.5,rely=.5,anchor='center')
        tk.Label(card,text='Laboratory Operations Demo',font=('Segoe UI',19,'bold'),bg='white',fg=NAV).pack(pady=12)
        tk.Label(card,text='Datos ficticios · funcionamiento local',bg='white').pack(pady=(0,18))
        tk.Label(card,text='Usuario',bg='white').pack(anchor='w')
        self.username=ttk.Entry(card,width=35);self.username.insert(0,'demo');self.username.pack(pady=5)
        tk.Label(card,text='Contraseña',bg='white').pack(anchor='w')
        self.password=ttk.Entry(card,width=35,show='*');self.password.pack(pady=5)
        self.password.bind('<Return>',lambda e:self.check())
        ttk.Button(card,text='Iniciar sesión',command=self.check).pack(pady=16)

    def check(self):
        if authenticate(self.username.get().strip(),self.password.get()):self.on_success()
        else:messagebox.showerror('Acceso denegado','Credenciales incorrectas. Inicializa la demostración con scripts/init_demo.py')
