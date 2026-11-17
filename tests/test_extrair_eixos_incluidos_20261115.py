import csv
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from scripts import extrair_eixos_incluidos_20261115 as lote


class ExtrairEixosIncluidosTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pasta = tempfile.TemporaryDirectory()
        cls.saida = Path(cls.pasta.name) / "saida.xlsx"
        lote.integrar(lote.BASE, lote.DECISOES, lote.METADADOS, cls.saida)
        cls.antes = load_workbook(lote.BASE)
        cls.depois = load_workbook(cls.saida)
        cls.eixos = cls.depois["Eixos de análise"]
        cls.ce = lote.cabecalhos(cls.eixos)

    @classmethod
    def tearDownClass(cls):
        cls.antes.close()
        cls.depois.close()
        cls.pasta.cleanup()

    def eixo(self, codigo, eixo):
        return next(r for r in list(self.eixos.values)[1:]
                    if r[self.ce["Código"] - 1] == codigo and r[self.ce["Eixo"] - 1] == lote.EIXOS_CODIGO[eixo])

    def test_evidencias_e_limites(self):
        decisoes = lote.ler_decisoes(lote.DECISOES)
        for item in decisoes:
            linha = self.eixo(item["codigo"], item["eixo"])
            self.assertEqual(linha[self.ce["Estado"] - 1], lote.OPCOES["eixo"][item["estado"]])
            self.assertEqual(linha[self.ce["Achado ou observação"] - 1], item["sintese"])
            self.assertIn("não independente", linha[self.ce["Limites da evidência"] - 1])
            if item["trecho"]:
                self.assertIn(item["trecho"], linha[self.ce["Trecho ou localização"] - 1])
        self.assertEqual(self.eixo("91522d0b", "T")[self.ce["Estado"] - 1], "Não informado")
        self.assertEqual(self.eixo("00683d4e", "A")[self.ce["Estado"] - 1], "Não verificável")
        self.assertIn("expectativas", self.eixo("813fdfa6", "A")[self.ce["Limites da evidência"] - 1])

    def test_preservacao_e_integridade(self):
        antes = self.antes["Eixos de análise"]
        depois = self.depois["Eixos de análise"]
        chaves = {(item["codigo"], lote.EIXOS_CODIGO[item["eixo"]])
                  for item in lote.ler_decisoes(lote.DECISOES)}
        for n in range(2, antes.max_row + 1):
            chave = (antes.cell(n, self.ce["Código"]).value, antes.cell(n, self.ce["Eixo"]).value)
            for col in range(1, antes.max_column + 1):
                if chave not in chaves or col <= 3:
                    self.assertEqual(antes.cell(n, col).value, depois.cell(n, col).value, str(chave))
        for nome in self.antes.sheetnames:
            if nome not in {"Eixos de análise", "Limites da integração"}:
                self.assertEqual(list(self.antes[nome].values), list(self.depois[nome].values), nome)
            self.assertEqual(str(self.antes[nome].data_validations), str(self.depois[nome].data_validations))
        self.assertEqual(antes.max_row, depois.max_row)
        self.assertEqual(antes.tables["Eixos"].ref, depois.tables["Eixos"].ref)
        self.assertEqual(antes.tables["Eixos"].autoFilter.ref, depois.tables["Eixos"].autoFilter.ref)
        formulas = lambda livro: {(s.title, c.coordinate, c.value) for s in livro
                                  for row in s for c in row if c.data_type == "f"}
        self.assertEqual(formulas(self.antes), formulas(self.depois))
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())

    def test_recusa_sobrescrita_e_conflitos(self):
        with self.assertRaises(FileExistsError):
            lote.integrar(lote.BASE, lote.DECISOES, lote.METADADOS, self.saida)
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            itens = lote.ler_decisoes(lote.DECISOES)
            itens[0]["trecho"] = "trecho inexistente no resumo"
            csv_alterado = pasta / "extracoes.csv"
            with csv_alterado.open("w", encoding="utf-8", newline="") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=itens[0].keys())
                escritor.writeheader()
                escritor.writerows(itens)
            saida = pasta / "saida.xlsx"
            with self.assertRaisesRegex(ValueError, "Trecho não localizado"):
                lote.integrar(lote.BASE, csv_alterado, lote.METADADOS, saida)
            self.assertFalse(saida.exists())

            livro = load_workbook(lote.BASE)
            eixo = livro["Eixos de análise"]
            n = next(n for n in range(2, eixo.max_row + 1)
                     if eixo.cell(n, self.ce["Código"]).value == "22f73924")
            eixo.cell(n, self.ce["Estado"]).value = "Presente"
            base = pasta / "base.xlsx"
            livro.save(base)
            livro.close()
            with self.assertRaisesRegex(ValueError, "eixos vazios divergente"):
                lote.integrar(base, lote.DECISOES, lote.METADADOS, saida)
            self.assertFalse(saida.exists())


if __name__ == "__main__":
    unittest.main()
