import hashlib
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from scripts import integrar_catalogo_lote2_20261115 as lote


class CatalogoLote2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pasta = tempfile.TemporaryDirectory()
        cls.saida = Path(cls.pasta.name) / "saida.xlsx"
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
        cls.pasta.cleanup()

    def valor(self, codigo, campo):
        return self.depois["Triagem"].cell(self.indices[codigo], self.col[campo]).value

    def test_decisoes_preservam_incerteza_e_exclusao_reversivel(self):
        for codigo in ("978a3b06", "dc90d61c", "b73823c3", "2f6de541"):
            self.assertEqual(self.valor(codigo, "Relação com PIBID"), "Incerto")
            self.assertEqual(self.valor(codigo, "Triagem de título e resumo"), "Pendente")
        self.assertEqual(self.valor("2d401ae4", "Triagem de título e resumo"), "Excluir")
        self.assertEqual(self.valor("2d401ae4", "Motivo da exclusão"), "Sem relação substantiva com PIBID")
        self.assertIn("reversível", self.valor("2d401ae4", "Limitações e pendências"))
        for item in lote.ler_decisoes(lote.DECISOES):
            codigo = item["codigo"]
            self.assertEqual(self.valor(codigo, "Decisão de elegibilidade"), "Pendente")
            self.assertEqual(self.valor(codigo, "Afiliação em Goiás"), "Incerto")
            self.assertIsNone(self.valor(codigo, "Ano de publicação"))

    def test_eixos_e_divergencia_de_resumos(self):
        s = self.depois["Eixos de análise"]
        c = lote.cabecalhos(s)
        por_codigo = {}
        for row in list(s.values)[1:]:
            por_codigo.setdefault(row[c["Código"] - 1], []).append(row[c["Estado"] - 1])
        self.assertEqual(por_codigo["978a3b06"], ["Não verificável"] * 3)
        self.assertEqual(por_codigo["ad83dff8"], ["Presente", "Não informado", "Presente"])
        self.assertEqual(por_codigo["3d19b827"], ["Não informado", "Não informado", "Presente"])
        self.assertNotIn("2d401ae4", por_codigo)
        self.assertIn("inglês termina antes", self.valor("ad83dff8", "Limitações e pendências"))

    def test_preservacao_e_integridade(self):
        self.assertEqual(hashlib.sha256(lote.BASE.read_bytes()).hexdigest(), self.hash_antes)
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())
        codigos = {x["codigo"] for x in lote.ler_decisoes(lote.DECISOES)}
        campos = {self.col[x] for x in (
            "Relação com PIBID", "Contexto de Goiás", "Decisão de elegibilidade",
            "Triagem de título e resumo", "Motivo da exclusão", "Evidência do contexto",
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
            if nome not in {"Triagem", "Eixos de análise", "Limites da integração"}:
                self.assertEqual(list(self.antes[nome].values), list(self.depois[nome].values), nome)
            if nome != "Eixos de análise":
                self.assertEqual(str(self.antes[nome].data_validations), str(self.depois[nome].data_validations))
        ea, ed = self.antes["Eixos de análise"], self.depois["Eixos de análise"]
        self.assertEqual(list(ea.values), list(ed.values)[:ea.max_row])
        self.assertEqual(ed.max_row, ea.max_row + 27)
        self.assertEqual(ed.tables["Eixos"].ref, f"A1:K{ed.max_row}")
        self.assertEqual(ed.tables["Eixos"].autoFilter.ref, ed.tables["Eixos"].ref)
        self.assertEqual(str(ed.data_validations.dataValidation[0].sqref), f"D2:D{ed.max_row}")
        formulas = lambda livro: {(s.title, c.coordinate, c.value) for s in livro for row in s for c in row if c.data_type == "f"}
        self.assertEqual(formulas(self.antes), formulas(self.depois))
        with self.assertRaises(FileExistsError):
            lote.integrar(lote.BASE, lote.DECISOES, lote.BRUTO, self.saida)

    def test_recusa_estado_anterior_incompativel(self):
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            livro = load_workbook(lote.BASE)
            livro["Triagem"].cell(self.indices["978a3b06"], self.col["Revisor"]).value = "Avaliação anterior"
            base, saida = pasta / "base.xlsx", pasta / "saida.xlsx"
            livro.save(base)
            livro.close()
            with self.assertRaisesRegex(ValueError, "Estado anterior"):
                lote.integrar(base, lote.DECISOES, lote.BRUTO, saida)
            self.assertFalse(saida.exists())


if __name__ == "__main__":
    unittest.main()
