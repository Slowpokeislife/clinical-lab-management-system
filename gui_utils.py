import tkinter as tk
from tkinter import ttk, messagebox

BG='#F3F6FA'
NAV='#12283F'
ACCENT='#D67A39'

def title(parent, text, description=''):
    tk.Label(parent,text=text,font=('Segoe UI',20,'bold'),fg=NAV,bg=BG).pack(anchor='w',padx=16,pady=(12,3))
    if description:
        tk.Label(parent,text=description,font=('Segoe UI',10),fg='#506477',bg=BG).pack(anchor='w',padx=16,pady=(0,12))

def form_entry(parent,label,default='',width=36):
    row=tk.Frame(parent,bg=BG)
    row.pack(fill='x',pady=3)
    tk.Label(row,text=label,width=19,anchor='w',bg=BG).pack(side='left')
    entry=ttk.Entry(row,width=width)
    entry.insert(0,str(default))
    entry.pack(side='left',fill='x',expand=True)
    return entry

def table(parent, headings, widths=None):
    wrap=tk.Frame(parent,bg=BG)
    wrap.pack(fill='both',expand=True,padx=16,pady=10)
    view=ttk.Treeview(wrap,columns=headings,show='headings',height=13)
    for i,h in enumerate(headings):
        view.heading(h,text=h)
        view.column(h,width=(widths or {}).get(h,130),anchor='w',stretch=True)
    sb=ttk.Scrollbar(wrap,command=view.yview)
    view.configure(yscrollcommand=sb.set)
    view.pack(side='left',fill='both',expand=True)
    sb.pack(side='right',fill='y')
    return view

def fill_table(view, rows):
    view.delete(*view.get_children())
    for row in rows:
        view.insert('','end',values=row)

def error(exc):
    messagebox.showerror('Error',str(exc))
