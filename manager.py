import tkinter as tk
from core import initialize
from login import LogIn
from container import Container

class Manager(tk.Tk):
    def __init__(self):
        super().__init__()
        initialize()
        self.title('Clinical Laboratory Management — Public Demo')
        self.geometry('1180x760')
        self.minsize(980,680)
        self.show_login()

    def show_login(self):
        for w in self.winfo_children():w.destroy()
        LogIn(self,self.show_app).pack(fill='both',expand=True)

    def show_app(self):
        for w in self.winfo_children():w.destroy()
        Container(self)
