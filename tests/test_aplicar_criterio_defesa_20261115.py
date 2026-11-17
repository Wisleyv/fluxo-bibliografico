import tempfile
import unittest
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from scripts import aplicar_criterio_defesa_20261115 as lote


class CriterioDefesaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pasta = tempfile.TemporaryDirectory()
        cls.saida = Path(cls.pasta.name) / "saida.xlsx"
        lote.integrar(lote.BASE, cls.saida)
        cls.antes = load_workbook(lote.BASE)
        cls.depois = load_workbook(cls.saida)

    @classmethod
    def tearDownClass(cls):
        cls.antes.close()
        cls.depois.close()
        cls.pasta.cleanup()

    def test_criterio_e_limites(self):
        triagem = self.depois["Triagem"]
        col = lote.cabecalhos(triagem)
        linhas = list(triagem.values)[1:]
        com_defesa = [r for r in linhas if r[col[lote.CAMPO] - 1]]
        self.assertEqual(len(com_defesa), 417)
        self.assertEqual(Counter(r[col[lote.CAMPO] - 1] for r in com_defesa),
                         {"Defesa em 2020–2025": 402, "Defesa em 2026 — evidência limitada": 15})
        self.assertEqual(Counter(r[col["Decisão de elegibilidade"] - 1] for r in com_defesa),
                         {"Não iniciada": 251, "Pendente": 113, "Excluir": 53})
        for r in com_defesa:
            self.assertIn(r[col["Tipo de produção"] - 1], lote.TIPOS)
            self.assertTrue(2020 <= int(r[col["Ano de defesa"] - 1]) <= 2026)
        auditoria = list(self.depois["Critério por defesa GO"].values)[1:]
        self.assertEqual({r[0] for r in auditoria}, {r[col["Código"] - 1] for r in com_defesa})
        casos_2026 = [r for r in auditoria if r[3] == 2026]
        self.assertEqual(len(casos_2026), 15)
        for r in casos_2026:
            self.assertIn("data individual completa não foi confirmada", r[10])
            self.assertIn("08/11/2026", r[10])
        produto = next(r for r in linhas if r[col["Código"] - 1] == "c88d5d87")
        self.assertIsNone(produto[col[lote.CAMPO] - 1])

    def test_preservacao_e_integridade(self):
        for nome in self.antes.sheetnames:
            antes, depois = self.antes[nome], self.depois[nome]
            if nome == "Triagem":
                for a, d in zip(antes.values, depois.values):
                    self.assertEqual(a, d[:len(a)])
            elif nome != "Limites da integração":
                self.assertEqual(list(antes.values), list(depois.values), nome)
            self.assertEqual(str(antes.data_validations), str(depois.data_validations), nome)
        tabela = self.depois["Triagem"].tables["Triagem"]
        self.assertEqual(tabela.ref, "A1:AK1318")
        self.assertEqual(tabela.autoFilter.ref, tabela.ref)
        self.assertEqual(len(tabela.tableColumns), 37)
        self.assertEqual(tabela.tableColumns[-1].name, lote.CAMPO)
        self.assertEqual(tabela.tableColumns[-1].id, 37)
        audit = self.depois["Critério por defesa GO"].tables["CriterioDefesaGO"]
        self.assertEqual(audit.ref, "A1:K418")
        formulas = lambda livro: {(s.title, c.coordinate, c.value) for s in livro
                                  for row in s for c in row if c.data_type == "f"}
        self.assertEqual(formulas(self.antes), formulas(self.depois))
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())

    def test_recusa_sobrescrita_e_conflito(self):
        with self.assertRaises(FileExistsError):
            lote.integrar(lote.BASE, self.saida)
        with tempfile.TemporaryDirectory() as pasta:
            base, saida = Path(pasta) / "base.xlsx", Path(pasta) / "saida.xlsx"
            livro = load_workbook(lote.BASE)
            triagem = livro["Triagem"]
            col = lote.cabecalhos(triagem)
            numero = next(n for n in range(2, triagem.max_row + 1)
                          if triagem.cell(n, col["Código"]).value == "2e073f75")
            triagem.cell(numero, col["Ano de defesa"]).value = "2018"
            livro.save(base)
            livro.close()
            with self.assertRaisesRegex(ValueError, "conjunto|Conjunto"):
                lote.integrar(base, saida)
            self.assertFalse(saida.exists())


if __name__ == "__main__":
    unittest.main()
