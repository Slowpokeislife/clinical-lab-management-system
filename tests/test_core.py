"""Run from project root: python -m unittest discover -s tests"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import core

class CoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.patch_data=patch.object(core,'DATA',Path(self.tmp.name))
        self.patch_db=patch.object(core,'DB',Path(self.tmp.name)/'test.sqlite3')
        self.patch_data.start();self.patch_db.start()
        core.initialize()

    def tearDown(self):
        self.patch_db.stop();self.patch_data.stop();self.tmp.cleanup()

    def test_authentication(self):
        core.setup_demo_user('long-demo-password')
        self.assertTrue(core.authenticate('demo','long-demo-password'))
        self.assertFalse(core.authenticate('demo','wrong'))

    def test_sale_snapshots_and_partial_payment(self):
        customer=core.add_customer('Synthetic Record')
        study=core.add_study('Synthetic Study',price=100,cost=30)
        folio=core.create_sale(customer,'Demo Doctor',1,[(study,2)],payment=50)
        result=core.sales_between('2020-01-01','2099-12-31')[0]
        self.assertEqual(folio,result['folio'])
        self.assertEqual(result['total'],200)
        self.assertEqual(result['cost'],60)
        self.assertEqual(result['due'],150)
        with core.connect() as db:
            db.execute('UPDATE studies SET price=900,cost=800 WHERE id=?',(study,))
        result=core.sales_between('2020-01-01','2099-12-31')[0]
        self.assertEqual(result['total'],200)
        self.assertEqual(result['cost'],60)

    def test_cannot_overpay(self):
        c=core.add_customer('Synthetic Record')
        s=core.add_study('Synthetic Study',price=10,cost=3)
        with self.assertRaises(ValueError):
            core.create_sale(c,'',1,[(s,1)],payment=20)
        self.assertEqual(len(core.fetch('SELECT * FROM sales')),0)

if __name__=='__main__':unittest.main()
