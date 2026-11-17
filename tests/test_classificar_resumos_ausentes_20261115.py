import hashlib
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from scripts import classificar_resumos_ausentes_20261115 as tratamento
from scripts.preanalise_e_validacao_20261115 import cabecalhos


class ResumosAusentesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pasta = tempfile.TemporaryDirectory()
        cls.saida = Path(cls.pasta.name) / "saida.xlsx"
        cls.hash_antes = hashlib.sha256(tratamento.BASE.read_bytes()).hexdigest()
        tratamento.integrar(tratamento.BASE, tratamento.CONFERENCIA, cls.saida)
        cls.antes = load_workbook(tratamento.BASE)
        cls.depois = load_workbook(cls.saida)

    @classmethod
    def tearDownClass(cls):
        cls.antes.close()
        cls.depois.close()
        cls.pasta.cleanup()

    def test_classificacao_preserva_sinais_e_decisoes(self):
        antes, depois = self.antes["Triagem"], self.depois["Triagem"]
        col = cabecalhos(antes)
        indices = tratamento.indice_unico(antes, col["Código"], 1317)
        audit = self.depois[tratamento.ABA]
        dados = {linha[0]: linha for linha in list(audit.values)[1:]}
        self.assertEqual(len(dados), 209)
        por_sinal = Counter(
            (r[1], r[4], r[5], r[6] != "Não identificado nesta conferência")
            for r in dados.values()
        )
        self.assertEqual(por_sinal[("Portal CAPES", "Não identificado por regra", "Não identificado por regra", False)], 27)
        self.assertEqual(por_sinal[("BDTD", "Não identificado por regra", "Não identificado por regra", False)], 35)
        self.assertEqual(por_sinal[("BDTD", "Não identificado por regra", "Sim", False)], 2)
        self.assertEqual(dados["7d7f7dda"][4:6], ("Não identificado por regra", "Não identificado por regra"))
        self.assertIn("Portal", dados["7d7f7dda"][6])
        self.assertEqual(dados["5dceaa56"][4:6], ("Não identificado por regra", "Sim"))
        self.assertIn("possível referência", dados["a3e7321c"][3])
        self.assertEqual(dados["a3e7321c"][4], "Não identificado por regra")
        for codigo, numero in indices.items():
            esperado = tratamento.REDUZIDA if codigo in dados else tratamento.NAO_AVALIADA
            self.assertEqual(depois.cell(numero, 36).value, esperado)
            for campo, coluna in col.items():
                anterior, novo = antes.cell(numero, coluna).value, depois.cell(numero, coluna).value
                if codigo in dados and campo == "Limitações e pendências":
                    self.assertIn(tratamento.NOTA, novo)
                    if anterior:
                        self.assertIn(anterior, novo)
                else:
                    self.assertEqual(anterior, novo, f"{codigo}: {campo}")

    def test_integridade_e_recusa(self):
        for nome in self.antes.sheetnames:
            if nome not in {"Triagem", "Limites da integração"}:
                self.assertEqual(list(self.antes[nome].values), list(self.depois[nome].values), nome)
            self.assertEqual(str(self.antes[nome].data_validations), str(self.depois[nome].data_validations))
        formulas = lambda livro: {(s.title, c.coordinate, c.value) for s in livro for row in s for c in row if c.data_type == "f"}
        self.assertEqual(formulas(self.antes), formulas(self.depois))
        for aba, nome, referencia in (("Triagem", "Triagem", "A1:AJ1318"),
                                     (tratamento.ABA, "QualidadeResumos", "A1:J210")):
            tabela = self.depois[aba].tables[nome]
            self.assertEqual(tabela.ref, referencia)
            self.assertEqual(tabela.autoFilter.ref, referencia)
            self.assertEqual(len(tabela.tableColumns), self.depois[aba].max_column)
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())
        self.assertEqual(hashlib.sha256(tratamento.BASE.read_bytes()).hexdigest(), self.hash_antes)
        with self.assertRaises(FileExistsError):
            tratamento.integrar(tratamento.BASE, tratamento.CONFERENCIA, self.saida)
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            modificado = load_workbook(tratamento.BASE)
            col = cabecalhos(modificado["Triagem"])
            numero = tratamento.indice_unico(modificado["Triagem"], col["Código"], 1317)["7d7f7dda"]
            modificado["Triagem"].cell(numero, col["Título"], "Título divergente")
            base, saida = pasta / "base.xlsx", pasta / "saida.xlsx"
            modificado.save(base)
            modificado.close()
            with self.assertRaisesRegex(ValueError, "Conferência anterior divergente"):
                tratamento.integrar(base, tratamento.CONFERENCIA, saida)
            self.assertFalse(saida.exists())


if __name__ == "__main__":
    unittest.main()
