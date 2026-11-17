import csv
import hashlib
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from scripts import conferir_catalogo_resumos_20261115 as lote


class ResumosCatalogoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporario = tempfile.TemporaryDirectory()
        cls.saida = Path(cls.temporario.name) / "saida.xlsx"
        cls.hash_antes = hashlib.sha256(lote.BASE.read_bytes()).hexdigest()
        lote.integrar(lote.BASE, lote.DECISOES, lote.BRUTO, cls.saida)
        cls.antes = load_workbook(lote.BASE)
        cls.depois = load_workbook(cls.saida)
        cls.col = lote.cabecalhos(cls.depois["Triagem"])
        cls.indices = lote.indice_unico(cls.depois["Triagem"], cls.col["Código"], 1317)

    @classmethod
    def tearDownClass(cls):
        cls.antes.close()
        cls.depois.close()
        cls.temporario.cleanup()

    def obter(self, codigo, campo):
        return self.depois["Triagem"].cell(self.indices[codigo], self.col[campo]).value

    def test_resumo_ingles_e_projeto_geram_pendencias(self):
        for codigo in ("11047151", "598f4ee2"):
            self.assertEqual(self.obter(codigo, "Triagem de título e resumo"), "Pendente")
            self.assertEqual(self.obter(codigo, "Relação com PIBID"), "Incerto")
            self.assertEqual(self.obter(codigo, "Decisão de elegibilidade"), "Pendente")
            self.assertIsNone(self.obter(codigo, "Ano de publicação"))
        self.assertIn("seis dos sete", self.obter("11047151", "Fontes das evidências"))
        self.assertIn("proximidade temática", self.obter("598f4ee2", "Limitações e pendências"))

    def test_exclusao_e_provisoria_e_projeto_nao_se_torna_achado(self):
        for codigo in ("261fc5ed", "212d112f", "6f4cd734", "fb661bfd", "ce5f325a",
                       "4378082f", "7d03e5e5", "93186a4e", "535e2a30"):
            self.assertEqual(self.obter(codigo, "Triagem de título e resumo"), "Excluir")
            self.assertEqual(self.obter(codigo, "Motivo da exclusão"), "Outro")
            self.assertEqual(self.obter(codigo, "Decisão de elegibilidade"), "Pendente")
            self.assertEqual(self.obter(codigo, "Relação com PIBID"), "Incerto")
            self.assertIn("reversível", self.obter(codigo, "Limitações e pendências"))

    def test_resumo_ingles_impede_exclusao_automatica(self):
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            linhas = lote.ler_decisoes(lote.DECISOES)
            for item in linhas:
                if item["codigo"] == "11047151":
                    item["tratamento"] = "E"
                elif item["codigo"] == "261fc5ed":
                    item["tratamento"] = "P"
            decisoes = pasta / "decisoes.csv"
            with decisoes.open("w", encoding="utf-8", newline="") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0]))
                escritor.writeheader()
                escritor.writerows(linhas)
            saida = pasta / "saida.xlsx"
            with self.assertRaises(ValueError):
                lote.integrar(lote.BASE, decisoes, lote.BRUTO, saida)
            self.assertFalse(saida.exists())

    def test_preserva_entrada_e_conteudo_fora_do_lote(self):
        self.assertEqual(hashlib.sha256(lote.BASE.read_bytes()).hexdigest(), self.hash_antes)
        antes, depois = self.antes["Triagem"], self.depois["Triagem"]
        codigos = {r[0] for r in list(self.depois["Resumos Catálogo CAPES"].values)[1:]}
        self.assertEqual(len(codigos), 11)
        campos = {self.col[nome] for nome in (
            "Triagem de título e resumo", "Decisão de elegibilidade", "Motivo da exclusão",
            "Fontes das evidências", "Material consultado", "Limitações e pendências",
            "Observações", "Revisor", "Data da triagem",
        )}
        for numero in range(1, antes.max_row + 1):
            codigo = antes.cell(numero, self.col["Código"]).value
            for coluna in range(1, antes.max_column + 1):
                if codigo in codigos and coluna in campos:
                    continue
                self.assertEqual(antes.cell(numero, coluna).value, depois.cell(numero, coluna).value, (codigo, coluna))
        for nome in self.antes.sheetnames:
            if nome not in {"Triagem", "Eixos de análise", "Limites da integração"}:
                self.assertEqual(list(self.antes[nome].values), list(self.depois[nome].values), nome)
        anteriores = list(self.antes["Eixos de análise"].values)
        self.assertEqual(anteriores, list(self.depois["Eixos de análise"].values)[:len(anteriores)])

    def test_estrutura_e_integridade(self):
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())
        self.assertEqual(self.depois["Resumos Catálogo CAPES"].max_row, 12)
        inventario = list(self.depois["Inventário inglês CAPES"].values)
        self.assertEqual(len(inventario), 79)
        linha = next(x for x in inventario[1:] if x[0] == "11047151")
        self.assertEqual(linha[3:6], ("Não", "Sim", "Sim"))
        eixos = self.depois["Eixos de análise"]
        self.assertEqual(eixos.max_row, self.antes["Eixos de análise"].max_row + 6)
        self.assertEqual(eixos.tables["Eixos"].ref, f"A1:K{eixos.max_row}")
        self.assertEqual(eixos.tables["Eixos"].autoFilter.ref, f"A1:K{eixos.max_row}")
        self.assertEqual(str(eixos.data_validations.dataValidation[0].sqref), f"D2:D{eixos.max_row}")
        for nome in self.antes.sheetnames:
            if nome != "Eixos de análise":
                self.assertEqual(str(self.antes[nome].data_validations), str(self.depois[nome].data_validations))
        formulas_antes = {(s.title, c.coordinate, c.value) for s in self.antes for linha in s for c in linha if c.data_type == "f"}
        formulas_depois = {(s.title, c.coordinate, c.value) for s in self.depois for linha in s for c in linha if c.data_type == "f"}
        self.assertEqual(formulas_antes, formulas_depois)
        with self.assertRaises(FileExistsError):
            lote.integrar(lote.BASE, lote.DECISOES, lote.BRUTO, self.saida)


if __name__ == "__main__":
    unittest.main()
