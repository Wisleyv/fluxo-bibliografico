import csv
import hashlib
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from scripts import conferir_campos_portal_20261115 as conferencia
from scripts.preanalise_e_validacao_20261115 import cabecalhos


class CamposPortalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pasta = tempfile.TemporaryDirectory()
        cls.saida = Path(cls.pasta.name) / "saida.xlsx"
        cls.hash_antes = hashlib.sha256(conferencia.BASE.read_bytes()).hexdigest()
        conferencia.integrar(conferencia.BASE, conferencia.DECISOES, conferencia.BRUTOS, cls.saida)
        cls.antes = load_workbook(conferencia.BASE)
        cls.depois = load_workbook(cls.saida)

    @classmethod
    def tearDownClass(cls):
        cls.antes.close()
        cls.depois.close()
        cls.pasta.cleanup()

    def test_evidencias_e_preservacao(self):
        antes, depois = self.antes["Triagem"], self.depois["Triagem"]
        col = cabecalhos(antes)
        indices = conferencia.indice_unico(antes, col["Código"], 1317)
        linhas = conferencia.ler_decisoes(conferencia.DECISOES)
        codigos = {item["codigo"] for item in linhas}
        permitidos = {"Link da fonte", "Fontes das evidências", "Material consultado", "Limitações e pendências"}
        for item in linhas:
            numero = indices[item["codigo"]]
            self.assertEqual(depois.cell(numero, col["Link da fonte"]).value, conferencia.URL + item["id"])
            self.assertIn(item["evidencia"], depois.cell(numero, col["Fontes das evidências"]).value)
            self.assertIn("não comprova", depois.cell(numero, col["Limitações e pendências"]).value)
            self.assertEqual(depois.cell(numero, col["Decisão de elegibilidade"]).value, "Pendente")
        for codigo, numero in indices.items():
            for campo, coluna in col.items():
                if codigo not in codigos or campo not in permitidos:
                    self.assertEqual(antes.cell(numero, coluna).value, depois.cell(numero, coluna).value,
                                     f"{codigo}: {campo}")
        for nome in self.antes.sheetnames:
            if nome not in {"Triagem", "Limites da integração"}:
                self.assertEqual(list(self.antes[nome].values), list(self.depois[nome].values), nome)
            self.assertEqual(str(self.antes[nome].data_validations), str(self.depois[nome].data_validations))
        self.assertEqual(hashlib.sha256(conferencia.BASE.read_bytes()).hexdigest(), self.hash_antes)
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())
        tabela = self.depois["Campos Portal CAPES"].tables["CamposPortalCAPES"]
        self.assertEqual(tabela.ref, "A1:H9")
        self.assertEqual(tabela.autoFilter.ref, tabela.ref)
        formulas = lambda livro: {(s.title, c.coordinate, c.value) for s in livro for row in s for c in row if c.data_type == "f"}
        self.assertEqual(formulas(self.antes), formulas(self.depois))

    def test_recusa_identidade_divergente_e_sobrescrita(self):
        with self.assertRaises(FileExistsError):
            conferencia.integrar(conferencia.BASE, conferencia.DECISOES, conferencia.BRUTOS, self.saida)
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            linhas = conferencia.ler_decisoes(conferencia.DECISOES)
            linhas[0]["doi"] = "10.0000/errado"
            decisoes, saida = pasta / "decisoes.csv", pasta / "saida.xlsx"
            with decisoes.open("w", encoding="utf-8", newline="") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=conferencia.CAMPOS)
                escritor.writeheader()
                escritor.writerows(linhas)
            with self.assertRaisesRegex(ValueError, "Identidade divergente"):
                conferencia.integrar(conferencia.BASE, decisoes, conferencia.BRUTOS, saida)
            self.assertFalse(saida.exists())


if __name__ == "__main__":
    unittest.main()
