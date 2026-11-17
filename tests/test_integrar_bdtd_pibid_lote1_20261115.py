import hashlib
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from scripts import integrar_bdtd_pibid_lote1_20261115 as lote


class BDTDPIBIDLote1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pasta = tempfile.TemporaryDirectory()
        cls.saida = Path(cls.pasta.name) / "saida.xlsx"
        cls.hash_antes = hashlib.sha256(lote.BASE.read_bytes()).hexdigest()
        lote.integrar(lote.BASE, lote.DECISOES, cls.saida)
        cls.antes = load_workbook(lote.BASE)
        cls.depois = load_workbook(cls.saida)
        cls.col = lote.cabecalhos(cls.depois["Triagem"])
        cls.indices = lote.indice_unico(cls.depois["Triagem"], cls.col["Código"], 1317)

    @classmethod
    def tearDownClass(cls):
        cls.antes.close()
        cls.depois.close()
        cls.pasta.cleanup()

    def valor(self, codigo, campo):
        return self.depois["Triagem"].cell(self.indices[codigo], self.col[campo]).value

    def test_contexto_nacional_e_institucional_sem_inferir_afiliacao(self):
        for codigo in ("1cd0fc3b", "193ba189", "f366cc08"):
            self.assertEqual(self.valor(codigo, "Contexto de Goiás"), "Incerto")
        self.assertEqual(self.valor("c0cbc957", "Contexto de Goiás"), "Sem evidência de contexto goiano")
        self.assertEqual(self.valor("de544b6f", "Relação com PIBID"), "Relação substantiva com PIBID")
        for item in lote.ler_decisoes(lote.DECISOES):
            codigo = item["codigo"]
            self.assertEqual(self.valor(codigo, "Afiliação em Goiás"), "Incerto")
            self.assertEqual(self.valor(codigo, "Triagem de título e resumo"), "Pendente")
            self.assertEqual(self.valor(codigo, "Decisão de elegibilidade"), "Pendente")
            self.assertEqual(self.valor(codigo, "Duplicidade"), "Não verificada")
            self.assertIsNone(self.valor(codigo, "Ano de publicação"))

    def test_preservacao_e_integridade(self):
        self.assertEqual(hashlib.sha256(lote.BASE.read_bytes()).hexdigest(), self.hash_antes)
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())
        codigos = {x["codigo"] for x in lote.ler_decisoes(lote.DECISOES)}
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
        formulas = lambda livro: {(s.title, c.coordinate, c.value) for s in livro for row in s for c in row if c.data_type == "f"}
        self.assertEqual(formulas(self.antes), formulas(self.depois))
        with self.assertRaises(FileExistsError):
            lote.integrar(lote.BASE, lote.DECISOES, self.saida)

    def test_recusa_estado_anterior_incompativel(self):
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            livro = load_workbook(lote.BASE)
            livro["Triagem"].cell(self.indices["5d59e0fd"], self.col["Revisor"]).value = "Avaliação anterior"
            base, saida = pasta / "base.xlsx", pasta / "saida.xlsx"
            livro.save(base)
            livro.close()
            with self.assertRaisesRegex(ValueError, "Estado anterior"):
                lote.integrar(base, lote.DECISOES, saida)
            self.assertFalse(saida.exists())


if __name__ == "__main__":
    unittest.main()
