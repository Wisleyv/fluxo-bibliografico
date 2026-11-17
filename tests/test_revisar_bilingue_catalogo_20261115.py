import hashlib
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from scripts import revisar_bilingue_catalogo_20261115 as lote


class RevisaoBilingueTests(unittest.TestCase):
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

    def test_exclusoes_sao_preliminares_e_com_motivos_distintos(self):
        for codigo in ("5dec546a", "16954ac9"):
            self.assertEqual(self.obter(codigo, "Triagem de título e resumo"), "Excluir")
            self.assertEqual(self.obter(codigo, "Motivo da exclusão"), "Sem relação substantiva com PIBID")
            self.assertEqual(self.obter(codigo, "Relação com PIBID"), "Menção incidental")
            self.assertEqual(self.obter(codigo, "Decisão de elegibilidade"), "Pendente")
        self.assertEqual(self.obter("401f22b2", "Triagem de título e resumo"), "Excluir")
        self.assertEqual(self.obter("401f22b2", "Motivo da exclusão"), "Outro")
        self.assertIn("o inglês usa futuro", self.obter("401f22b2", "Limitações e pendências"))

    def test_relacao_incerta_nao_atribui_resultados_ao_programa(self):
        self.assertEqual(self.obter("011e7d10", "Relação com PIBID"), "Incerto")
        self.assertEqual(self.obter("011e7d10", "Triagem de título e resumo"), "Pendente")
        self.assertIn("não esclarece se os encontros integram ações do programa",
                      self.obter("011e7d10", "Limitações e pendências"))
        self.assertIn("vinte e sete por extenso e 30", self.obter("223fc435", "Limitações e pendências"))

    def test_revisao_dos_eixos_exige_achados_e_preserva_historico(self):
        aba = self.depois["Eixos de análise"]
        col = lote.cabecalhos(aba)
        estados = {}
        for linha in aba.iter_rows(min_row=2, values_only=True):
            estados[(linha[col["Código"] - 1], linha[col["Eixo"] - 1])] = linha[col["Estado"] - 1]
        nomes = list(lote.EIXOS.values())
        for codigo, esperado in (("fe0ff0a0", ["Não verificável", "Não informado", "Não verificável"]),
                                 ("bebf73ba", ["Não verificável"] * 3),
                                 ("011e7d10", ["Não verificável"] * 3)):
            self.assertEqual([estados[(codigo, eixo)] for eixo in nomes], esperado)
        auditoria = {r[0]: r for r in list(self.depois["Revisão bilíngue CAPES"].values)[1:]}
        self.assertEqual(auditoria["bebf73ba"][6], "Presente | Presente | Presente")
        self.assertEqual(auditoria["bebf73ba"][7], "Não verificável | Não verificável | Não verificável")

    def test_recusa_estado_anterior_incompativel(self):
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            livro = load_workbook(lote.BASE)
            livro["Triagem"].cell(self.indices["401f22b2"], self.col["Triagem de título e resumo"]).value = "Excluir"
            base, saida = pasta / "base.xlsx", pasta / "saida.xlsx"
            livro.save(base)
            livro.close()
            with self.assertRaisesRegex(ValueError, "Estado anterior"):
                lote.integrar(base, lote.DECISOES, lote.BRUTO, saida)
            self.assertFalse(saida.exists())

    def test_preservacao_e_integridade(self):
        self.assertEqual(hashlib.sha256(lote.BASE.read_bytes()).hexdigest(), self.hash_antes)
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())
        antes, depois = self.antes["Triagem"], self.depois["Triagem"]
        codigos = {r[0] for r in list(self.depois["Revisão bilíngue CAPES"].values)[1:]}
        self.assertEqual(len(codigos), 17)
        campos = {self.col[nome] for nome in (
            "Relação com PIBID", "Triagem de título e resumo", "Motivo da exclusão",
            "Fontes das evidências", "Material consultado", "Limitações e pendências", "Observações",
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
            self.assertEqual(str(self.antes[nome].data_validations), str(self.depois[nome].data_validations))
        ea, ed = self.antes["Eixos de análise"], self.depois["Eixos de análise"]
        ce = lote.cabecalhos(ea)
        self.assertEqual(ea.max_row, ed.max_row)
        alteraveis = {ce[x] for x in ("Estado", "Achado ou observação", "Limites da evidência")}
        for linha in range(1, ea.max_row + 1):
            codigo = ea.cell(linha, ce["Código"]).value
            for coluna in range(1, ea.max_column + 1):
                if codigo in lote.ANTERIORES and coluna in alteraveis:
                    continue
                self.assertEqual(ea.cell(linha, coluna).value, ed.cell(linha, coluna).value, (codigo, coluna))
        self.assertEqual(ea.tables["Eixos"].ref, ed.tables["Eixos"].ref)
        self.assertEqual(ea.tables["Eixos"].autoFilter.ref, ed.tables["Eixos"].autoFilter.ref)
        formulas_antes = {(s.title, c.coordinate, c.value) for s in self.antes for linha in s for c in linha if c.data_type == "f"}
        formulas_depois = {(s.title, c.coordinate, c.value) for s in self.depois for linha in s for c in linha if c.data_type == "f"}
        self.assertEqual(formulas_antes, formulas_depois)
        with self.assertRaises(FileExistsError):
            lote.integrar(lote.BASE, lote.DECISOES, lote.BRUTO, self.saida)


if __name__ == "__main__":
    unittest.main()
