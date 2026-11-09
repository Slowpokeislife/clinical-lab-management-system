"""Generate isolated synthetic records. Never import production data."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core import initialize, setup_demo_user, add_customer, add_study, create_sale, fetch, DB


def seed(password: str):
    initialize()
    setup_demo_user(password)
    if fetch('SELECT id FROM customers LIMIT 1'):
        print('La base ya contiene registros; no se duplicaron los datos sintéticos.')
        return
    people = [
        ('Persona Demo Uno','2000-04-12','F','demo1@example.invalid','0000000000'),
        ('Persona Demo Dos','1998-02-18','M','demo2@example.invalid','0000000000'),
        ('Persona Demo Tres','2001-11-25','F','demo3@example.invalid','0000000000'),
    ]
    customers = [add_customer(*p) for p in people]
    studies = [
        ('Biometría hemática','Sangre','Ayuno según indicación',1,250,100),
        ('Química sanguínea','Sangre','Ayuno de 8 horas',1,390,160),
        ('Examen general de orina','Orina','Primera orina de la mañana',1,180,65),
        ('Glucosa','Sangre','Ayuno de 8 horas',1,120,40),
    ]
    ids = [add_study(*s) for s in studies]
    create_sale(customers[0],'Médico de prueba',1,[(ids[0],1),(ids[2],1)],430,
                fasting='8 horas',notes='Registro sintético',result_delivery='En mostrador')
    create_sale(customers[1],'Médico de prueba',2,[(ids[1],1)],200,
                notes='Registro sintético',result_delivery='En mostrador')
    create_sale(customers[2],'Médico de prueba',1,[(ids[3],2)],240,
                notes='Registro sintético',result_delivery='En mostrador')
    print(f'Base ficticia preparada en: {DB}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--password',required=True, help='Contraseña local de demostración (mínimo 10 caracteres)')
    args = parser.parse_args()
    seed(args.password)
