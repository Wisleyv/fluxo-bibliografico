import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from scripts import consolidar_decisoes_goias_20261115 as lote


class ConsolidarDecisoesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pasta = tempfile.TemporaryDirectory()
        cls.saida = Path(cls.pasta.name) / "saida.xlsx"
        lote.integrar(lote.BASE, lote.BRUTOS, lote.METADADOS, cls.saida)
        cls.antes = load_workbook(lote.BASE)
        cls.depois = load_workbook(cls.saida)
        cls.col = lote.cabecalhos(cls.antes["Triagem"])
        cls.indices = lote.indice_unico(cls.antes["Triagem"], cls.col["Código"], 1317)

    @classmethod
    def tearDownClass(cls):
        cls.antes.close()
        cls.depois.close()
        cls.pasta.cleanup()

    def test_decisoes_e_limites(self):
        aba = self.depois["Triagem"]
        decisoes = {codigo: aba.cell(n, self.col["Decisão de elegibilidade"]).value
                    for codigo, n in self.indices.items()}
        self.assertEqual({c for c, v in decisoes.items() if v == "Incluir"}, lote.INCLUIDOS)
        self.assertEqual(sum(v == "Excluir" for v in decisoes.values()), 110)
        for codigo in ("a3e7321c", "69c845eb", "4a213f79", "05cbfe1e"):
            self.assertEqual(decisoes[codigo], "Pendente")
        for codigo in lote.INCLUIDOS:
            linha = self.indices[codigo]
            self.assertEqual(aba.cell(linha, self.col["Duplicidade"]).value, "Não verificada")
        auditoria = self.depois["Decisões Goiás"]
        excluido = next(r[0] for r in list(auditoria.values)[1:] if r[2] == "Excluir")
        self.assertIn("panorama nacional", aba.cell(
            self.indices[excluido], self.col["Limitações e pendências"]).value)
        self.assertEqual(auditoria.max_row, 122)
        self.assertEqual(auditoria.tables["DecisoesGoias"].ref, "A1:E122")
        self.assertEqual(auditoria.tables["DecisoesGoias"].autoFilter.ref, "A1:E122")

    def test_preservacao(self):
        antes, depois = self.antes["Triagem"], self.depois["Triagem"]
        alterados = {r[0] for r in list(self.depois["Decisões Goiás"].values)[1:]}
        permitidos = {"Decisão de elegibilidade", "Limitações e pendências", "Observações"}
        for codigo, numero in self.indices.items():
            for campo, coluna in self.col.items():
                if codigo not in alterados or campo not in permitidos:
                    self.assertEqual(antes.cell(numero, coluna).value, depois.cell(numero, coluna).value,
                                     f"{codigo}: {campo}")
        for nome in self.antes.sheetnames:
            if nome not in {"Triagem", "Limites da integração"}:
                self.assertEqual(list(self.antes[nome].values), list(self.depois[nome].values), nome)
            self.assertEqual(str(self.antes[nome].data_validations), str(self.depois[nome].data_validations))
        formulas = lambda livro: {(s.title, c.coordinate, c.value) for s in livro
                                  for row in s for c in row if c.data_type == "f"}
        self.assertEqual(formulas(self.antes), formulas(self.depois))
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())

    def test_recusa_sobrescrita_e_conflitos(self):
        with self.assertRaises(FileExistsError):
            lote.integrar(lote.BASE, lote.BRUTOS, lote.METADADOS, self.saida)
        for codigo, campo, valor in (
            ("95dee571", "Produção acadêmica", "Incerto"),
            ("95dee571", "Ano de publicação", 2018),
        ):
            with self.subTest(campo=campo), tempfile.TemporaryDirectory() as pasta:
                base, saida = Path(pasta) / "base.xlsx", Path(pasta) / "saida.xlsx"
                livro = load_workbook(lote.BASE)
                livro["Triagem"].cell(self.indices[codigo], self.col[campo]).value = valor
                livro.save(base)
                livro.close()
                with self.assertRaises(ValueError):
                    lote.integrar(base, lote.BRUTOS, lote.METADADOS, saida)
                self.assertFalse(saida.exists())


if __name__ == "__main__":
    unittest.main()
