import tempfile
import unittest
from pathlib import Path
from openpyxl import Workbook, load_workbook
from scripts.entregar_marco5 import line, format_table


class DeliveryWorkbookTests(unittest.TestCase):
    def test_source_text_is_not_executed_as_formula(self):
        w=Workbook();s=w.active
        line(s,['=1+1','+título','@texto',123])
        self.assertEqual(s['A1'].data_type,'s')
        self.assertEqual(s['A1'].value,'=1+1')
        self.assertEqual(s['D1'].value,123)

    def test_tables_filters_and_unicode_survive_save(self):
        w=Workbook();s=w.active;line(s,['Identificador','Decisão']);line(s,['obra-1','Não verificável'])
        format_table(s,'ObrasTeste')
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'test.xlsx';w.save(p);r=load_workbook(p)
            self.assertEqual(r.active['B2'].value,'Não verificável')
            self.assertEqual(r.active.tables['ObrasTeste'].ref,'A1:B2')
            self.assertIsNotNone(r.active.tables['ObrasTeste'].autoFilter)
            self.assertIsNone(r.active.auto_filter.ref)
            self.assertEqual(r.active.freeze_panes,'B2')

    def test_excel_cell_reference_is_not_a_valid_table_name(self):
        w=Workbook();line(w.active,['Campo']);line(w.active,['Valor'])
        with self.assertRaises(ValueError):format_table(w.active,'T1')


if __name__=='__main__':unittest.main()
