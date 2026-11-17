import hashlib
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from scripts import integrar_bdtd_pibid_lote2_20261115 as lote
from scripts.integrar_bdtd_pibid_lote1_20261115 import cabecalhos, indice_unico, ler_decisoes


class BDTDPIBIDLote2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pasta = tempfile.TemporaryDirectory()
        cls.saida = Path(cls.pasta.name) / "saida.xlsx"
        cls.hash_antes = hashlib.sha256(lote.BASE.read_bytes()).hexdigest()
        lote.integrar(lote.BASE, lote.DECISOES, cls.saida, lote_recente=True)
        cls.antes = load_workbook(lote.BASE)
        cls.depois = load_workbook(cls.saida)
        cls.col = cabecalhos(cls.depois["Triagem"])
        cls.indices = indice_unico(cls.depois["Triagem"], cls.col["Código"], 1317)

    @classmethod
    def tearDownClass(cls):
        cls.antes.close()
        cls.depois.close()
        cls.pasta.cleanup()

    def valor(self, codigo, campo):
        return self.depois["Triagem"].cell(self.indices[codigo], self.col[campo]).value

    def test_incertezas_nao_se_convertem_em_elegibilidade(self):
        self.assertEqual(self.valor("fbe0a70f", "Relação com PIBID"), "Incerto")
        self.assertEqual(self.valor("01d34bae", "Relação com PIBID"), "Relação substantiva com PIBID")
        for codigo in ("28de0b69", "b66fff4f", "fbe0a70f", "9da923d6", "42007bfd"):
            self.assertEqual(self.valor(codigo, "Contexto de Goiás"), "Incerto")
        self.assertIn("08/11/2026", self.valor("44752b85", "Limitações e pendências"))
        for item in ler_decisoes(lote.DECISOES):
            codigo = item["codigo"]
            self.assertEqual(self.valor(codigo, "Decisão de elegibilidade"), "Pendente")
            self.assertEqual(self.valor(codigo, "Triagem de título e resumo"), "Pendente")
            self.assertEqual(self.valor(codigo, "Afiliação em Goiás"), "Incerto")
            self.assertIsNone(self.valor(codigo, "Ano de publicação"))

    def test_preservacao_e_integridade(self):
        self.assertEqual(hashlib.sha256(lote.BASE.read_bytes()).hexdigest(), self.hash_antes)
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())
        codigos = {x["codigo"] for x in ler_decisoes(lote.DECISOES)}
        campos = {self.col[x] for x in (
            "Relação com PIBID", "Contexto de Goiás", "Decisão de elegibilidade",
            "Evidência do contexto", "Fontes das evidências", "Material consultado",
            "Limitações e pendências", "Observações", "Revisor", "Data da triagem",
        )}
        a, b = self.antes["Triagem"], self.depois["Triagem"]
        for row in a:
            codigo = a.cell(row[0].row, self.col["Código"]).value
            for cell in row:
                if codigo not in codigos or cell.column not in campos:
                    self.assertEqual(cell.value, b[cell.coordinate].value, cell.coordinate)
        for nome in self.antes.sheetnames:
            if nome not in {"Triagem", "Limites da integração"}:
                self.assertEqual(list(self.antes[nome].values), list(self.depois[nome].values), nome)
            self.assertEqual(str(self.antes[nome].data_validations), str(self.depois[nome].data_validations))
        ea, ed = self.antes["Eixos de análise"], self.depois["Eixos de análise"]
        self.assertEqual(ea.tables["Eixos"].ref, ed.tables["Eixos"].ref)
        self.assertEqual(ea.tables["Eixos"].autoFilter.ref, ed.tables["Eixos"].autoFilter.ref)
        tabela = self.depois["BDTD PIBID recentes"].tables["BDTDPIBIDRecentes"]
        self.assertEqual(tabela.ref, "A1:H21")
        self.assertEqual(tabela.autoFilter.ref, tabela.ref)
        formulas = lambda livro: {(s.title, c.coordinate, c.value) for s in livro for row in s for c in row if c.data_type == "f"}
        self.assertEqual(formulas(self.antes), formulas(self.depois))
        with self.assertRaises(FileExistsError):
            lote.integrar(lote.BASE, lote.DECISOES, self.saida, lote_recente=True)

    def test_recusa_defesa_fora_da_selecao(self):
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            livro = load_workbook(lote.BASE)
            livro["Triagem"].cell(self.indices["11d40c59"], self.col["Ano de defesa"]).value = "2019"
            base, saida = pasta / "base.xlsx", pasta / "saida.xlsx"
            livro.save(base)
            livro.close()
            with self.assertRaisesRegex(ValueError, "Ano de defesa incompatível"):
                lote.integrar(base, lote.DECISOES, saida, lote_recente=True)
            self.assertFalse(saida.exists())


if __name__ == "__main__":
    unittest.main()
