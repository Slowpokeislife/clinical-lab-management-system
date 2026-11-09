import tkinter as tk
from tkinter import ttk, messagebox
from core import DB, connect, password_hash, DEMO_USER
from gui_utils import BG,title,error

class Informacion(ttk.Frame):
    def __init__(self,parent):
        super().__init__(parent)
        w=tk.Frame(self,bg=BG);w.pack(fill='both',expand=True)
        title(w,'Acerca de esta demostración','Aplicación de escritorio sin conexión a Internet')
        for line in ('Identidad ficticia: Laboratory Operations Demo',
                     f'Base SQLite local: {DB}',
                     'No contiene información real ni realiza envíos de correo.',
                     'Los reportes financieros calculan margen bruto estimado, no utilidad neta.',
                     'No está destinada a producción ni a almacenar datos médicos reales.'):
            tk.Label(w,text=line,bg=BG,anchor='w').pack(fill='x',padx=16,pady=6)
        tk.Label(w,text='Actualizar contraseña local de demostración',bg=BG,font=('Segoe UI',12,'bold')).pack(anchor='w',padx=16,pady=(18,5))
        self.password=ttk.Entry(w,show='*',width=38);self.password.pack(anchor='w',padx=16)
        ttk.Button(w,text='Guardar contraseña nueva',command=self.update).pack(anchor='w',padx=16,pady=10)

    def update(self):
        try:
            value=self.password.get()
            if len(value)<10:raise ValueError('Usa al menos 10 caracteres')
            with connect() as db:
                db.execute('UPDATE users SET password_hash=? WHERE username=?',(password_hash(value),DEMO_USER))
            self.password.delete(0,'end');messagebox.showinfo('Guardado','Contraseña local actualizada')
        except Exception as exc:error(exc)
