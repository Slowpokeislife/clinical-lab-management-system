"""Local storage and business logic for a synthetic laboratory demo."""
from __future__ import annotations
import hashlib
import hmac
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, date
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / 'local_data'
DB = DATA / 'demo.sqlite3'
DEMO_USER = 'demo'

def password_hash(value: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', value.encode('utf-8'), salt, 260_000)
    return f'{salt.hex()}:{key.hex()}'

def password_ok(value: str, stored: str) -> bool:
    try:
        salt_hex, _ = stored.split(':', 1)
        return hmac.compare_digest(password_hash(value, bytes.fromhex(salt_hex)), stored)
    except (ValueError, TypeError):
        return False

@contextmanager
def connect():
    DATA.mkdir(exist_ok=True)
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def initialize():
    with connect() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
          username TEXT PRIMARY KEY, password_hash TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS branches (
          id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
        CREATE TABLE IF NOT EXISTS customers (
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
          dob TEXT, gender TEXT, email TEXT, phone TEXT);
        CREATE TABLE IF NOT EXISTS studies (
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE,
          sample TEXT, instructions TEXT, days INTEGER DEFAULT 1,
          price REAL NOT NULL CHECK(price >= 0), cost REAL NOT NULL DEFAULT 0 CHECK(cost >= 0));
        CREATE TABLE IF NOT EXISTS sales (
          id INTEGER PRIMARY KEY AUTOINCREMENT, folio TEXT UNIQUE NOT NULL,
          created_at TEXT NOT NULL, customer_id INTEGER NOT NULL,
          doctor TEXT NOT NULL DEFAULT '', branch_id INTEGER NOT NULL,
          payment REAL NOT NULL DEFAULT 0 CHECK(payment >= 0),
          collection_time TEXT, fasting TEXT, urination TEXT, notes TEXT,
          result_delivery TEXT,
          FOREIGN KEY(customer_id) REFERENCES customers(id),
          FOREIGN KEY(branch_id) REFERENCES branches(id));
        CREATE TABLE IF NOT EXISTS sale_items (
          id INTEGER PRIMARY KEY AUTOINCREMENT, sale_id INTEGER NOT NULL,
          study_id INTEGER NOT NULL, quantity INTEGER NOT NULL CHECK(quantity > 0),
          unit_price REAL NOT NULL CHECK(unit_price >= 0),
          unit_cost REAL NOT NULL CHECK(unit_cost >= 0),
          FOREIGN KEY(sale_id) REFERENCES sales(id) ON DELETE CASCADE,
          FOREIGN KEY(study_id) REFERENCES studies(id));
        ''')
        db.execute('INSERT OR IGNORE INTO branches(id,name) VALUES(1, ?)', ('Demo Branch A',))
        db.execute('INSERT OR IGNORE INTO branches(id,name) VALUES(2, ?)', ('Demo Branch B',))
    return DB

def setup_demo_user(password: str):
    if len(password) < 10:
        raise ValueError('La contraseña debe tener al menos 10 caracteres.')
    with connect() as db:
        db.execute('INSERT OR REPLACE INTO users(username,password_hash) VALUES(?,?)',
                   (DEMO_USER, password_hash(password)))

def authenticate(username: str, password: str) -> bool:
    with connect() as db:
        row = db.execute('SELECT password_hash FROM users WHERE username=?', (username,)).fetchone()
    return bool(row and password_ok(password, row['password_hash']))

def fetch(query: str, params=()):
    with connect() as db:
        return [dict(r) for r in db.execute(query, params).fetchall()]

def add_customer(name, dob='', gender='', email='', phone=''):
    if not name.strip():
        raise ValueError('Nombre requerido')
    with connect() as db:
        cur = db.execute('INSERT INTO customers(name,dob,gender,email,phone) VALUES(?,?,?,?,?)',
                         (name.strip(), dob, gender, email, phone))
        return cur.lastrowid

def add_study(name, sample='', instructions='', days=1, price=0, cost=0):
    price, cost = float(price), float(cost)
    if price < 0 or cost < 0:
        raise ValueError('Los importes no pueden ser negativos')
    with connect() as db:
        return db.execute('INSERT INTO studies(name,sample,instructions,days,price,cost) VALUES(?,?,?,?,?,?)',
                          (name, sample, instructions, int(days), price, cost)).lastrowid

def create_sale(customer_id: int, doctor: str, branch_id: int, items: list[tuple[int,int]],
                payment: float, collection_time='', fasting='', urination='', notes='', result_delivery=''):
    if not items or any(int(q) < 1 for _,q in items):
        raise ValueError('Agrega al menos un estudio y una cantidad válida')
    payment = float(payment)
    if payment < 0:
        raise ValueError('El abono no puede ser negativo')
    created = datetime.now().isoformat(timespec='seconds')
    with connect() as db:
        products = []
        for study_id, qty in items:
            product = db.execute('SELECT price,cost FROM studies WHERE id=?', (study_id,)).fetchone()
            if product is None:
                raise ValueError('Estudio no encontrado')
            products.append((study_id, int(qty), float(product['price']), float(product['cost'])))
        total = sum(qty * price for _,qty,price,_ in products)
        if payment > total:
            raise ValueError('El abono no puede superar el total')
        # Folio based on the SQLite row id, unique even across application restarts.
        provisional = f'TEMP-{os.urandom(8).hex()}'
        cur = db.execute('''INSERT INTO sales(folio,created_at,customer_id,doctor,branch_id,payment,
            collection_time,fasting,urination,notes,result_delivery) VALUES(?,?,?,?,?,?,?,?,?,?,?)''',
            (provisional,created,customer_id,doctor,branch_id,payment,collection_time,fasting,urination,notes,result_delivery))
        sale_id = cur.lastrowid
        folio = f'DEMO-{date.today():%y%m%d}-{sale_id:05d}'
        db.execute('UPDATE sales SET folio=? WHERE id=?', (folio,sale_id))
        db.executemany('INSERT INTO sale_items(sale_id,study_id,quantity,unit_price,unit_cost) VALUES(?,?,?,?,?)',
                       [(sale_id,study_id,qty,price,cost) for study_id,qty,price,cost in products])
        return folio

def sales_between(start: str, end: str, branch_id: int | None = None):
    clause = ' AND s.branch_id=?' if branch_id else ''
    params = [start+'T00:00:00', end+'T23:59:59'] + ([branch_id] if branch_id else [])
    return fetch('''SELECT s.id,s.folio,s.created_at,c.name AS customer,c.dob,c.gender,c.phone,c.email,
        s.doctor,b.name AS branch,s.payment,s.collection_time,s.fasting,s.urination,s.notes,s.result_delivery,
        COALESCE(SUM(i.quantity*i.unit_price),0) AS total,
        COALESCE(SUM(i.quantity*i.unit_cost),0) AS cost,
        COALESCE(SUM(i.quantity*i.unit_price),0)-s.payment AS due
        FROM sales s JOIN customers c ON c.id=s.customer_id JOIN branches b ON b.id=s.branch_id
        JOIN sale_items i ON i.sale_id=s.id
        WHERE s.created_at BETWEEN ? AND ?'''+clause+'''
        GROUP BY s.id ORDER BY s.created_at DESC,s.id DESC''', params)

def sale_items(sale_id):
    return fetch('''SELECT st.name AS study,i.quantity,i.unit_price,i.unit_cost,
        i.quantity*i.unit_price AS subtotal FROM sale_items i
        JOIN studies st ON st.id=i.study_id WHERE i.sale_id=?''', (sale_id,))
