import hashlib
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from scripts import integrar_bdtd_termos_lote_20261115 as lote


class BDTDTermosTests(unittest.TestCase):
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

    def test_traducao_nao_sustenta_exclusao_automatica(self):
        for codigo in ("05895f12", "9d2082d5"):
            self.assertEqual(self.valor(codigo, "Triagem de título e resumo"), "Pendente")
            self.assertIsNone(self.valor(codigo, "Motivo da exclusão"))
            self.assertEqual(self.valor(codigo, "Decisão de elegibilidade"), "Pendente")
        self.assertEqual(self.valor("05895f12", "Relação com PIBID"), "Relação substantiva com PIBID")
        self.assertIn("riufs/11943", self.valor("05895f12", "Fontes das evidências"))
        self.assertEqual(self.valor("9d2082d5", "Relação com PIBID"), "Incerto")
        self.assertTrue(lote.possivel_traducao("Institutional Program of Initiation to Teaching Scholarship"))
        self.assertTrue(lote.possivel_traducao("Institutional Program for Teaching Initiation Scholarships"))

    def test_exclusao_e_reversivel_e_nao_decide_duplicidade(self):
        for codigo in ("a11ef5d1", "2f1faf79", "7d880e9f"):
            self.assertEqual(self.valor(codigo, "Triagem de título e resumo"), "Excluir")
            self.assertEqual(self.valor(codigo, "Motivo da exclusão"), "Outro")
            self.assertEqual(self.valor(codigo, "Decisão de elegibilidade"), "Pendente")
            self.assertEqual(self.valor(codigo, "Duplicidade"), "Não verificada")
            self.assertIn("reversível", self.valor(codigo, "Limitações e pendências"))
        self.assertIn("palavras-chave disponíveis", self.valor("7d880e9f", "Limitações e pendências"))

    def test_preservacao_e_integridade(self):
        self.assertEqual(hashlib.sha256(lote.BASE.read_bytes()).hexdigest(), self.hash_antes)
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())
        codigos = {x["codigo"] for x in lote.ler_decisoes(lote.DECISOES)}
        campos = {self.col[x] for x in (
            "Decisão de elegibilidade", "Triagem de título e resumo", "Motivo da exclusão", "Relação com PIBID",
            "Fontes das evidências", "Material consultado", "Limitações e pendências",
            "Observações", "Revisor", "Data da triagem",
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

    def test_recusa_exclusao_de_possivel_traducao(self):
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            conteudo = lote.DECISOES.read_text(encoding="utf-8")
            conteudo = conteudo.replace("05895f12,P,", "05895f12,E,").replace("2abb80aa,E,", "2abb80aa,P,")
            decisoes = pasta / "decisoes.csv"
            decisoes.write_text(conteudo, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "tradução"):
                lote.integrar(lote.BASE, decisoes, pasta / "saida.xlsx")


if __name__ == "__main__":
    unittest.main()
