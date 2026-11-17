import hashlib
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from scripts import integrar_catalogo_lote3_20261115 as lote


class CatalogoLote3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pasta = tempfile.TemporaryDirectory()
        cls.saida = Path(cls.pasta.name) / "saida.xlsx"
        cls.hash_antes = hashlib.sha256(lote.BASE.read_bytes()).hexdigest()
        lote.integrar(lote.BASE, lote.DECISOES, lote.BRUTO, cls.saida)
        cls.antes = load_workbook(lote.BASE)
        cls.depois = load_workbook(cls.saida)
        cls.col = lote.cabecalhos(cls.antes["Triagem"])
        cls.indices = lote.indice_unico(cls.antes["Triagem"], cls.col["Código"], 1317)

    @classmethod
    def tearDownClass(cls):
        cls.antes.close()
        cls.depois.close()
        cls.pasta.cleanup()

    def valor(self, codigo, campo):
        return self.depois["Triagem"].cell(self.indices[codigo], self.col[campo]).value

    def test_leituras_e_qualidade_documental(self):
        lidos_antes = set()
        for nome in ("Resumos Catálogo CAPES", "Revisão bilíngue CAPES", "CAPES bilíngue lote 2"):
            lidos_antes.update(r[0] for r in list(self.antes[nome].values)[1:])
        restantes = [r[0] for r in list(self.antes["Inventário inglês CAPES"].values)[1:]
                     if r[0] not in lidos_antes]
        self.assertEqual(len(restantes), 40)
        self.assertEqual([x["codigo"] for x in lote.ler_decisoes(lote.DECISOES)], restantes[:10])
        self.assertEqual(self.valor("2fda2cb6", "Relação com PIBID"), "Incerto")
        self.assertEqual(self.valor("9f3cb0ea", "Relação com PIBID"), "Incerto")
        self.assertIn("espanhol", self.valor("bc0f1ea5", "Limitações e pendências"))
        self.assertIn("proposta conceitual", self.valor("8e68ac12", "Limitações e pendências"))
        for codigo in ("53af6244", "68880406", "3d2681de", "b12efbcb"):
            self.assertEqual(self.valor(codigo, "Qualidade documental do resumo"), lote.REDUZIDA)
            self.assertIn(lote.NOTA, self.valor(codigo, "Limitações e pendências"))
            self.assertEqual(self.valor(codigo, "Triagem de título e resumo"),
                             self.antes["Triagem"].cell(self.indices[codigo], self.col["Triagem de título e resumo"]).value)
        for codigo in ("0082c6a2", "af936121", "793eb1aa"):
            self.assertEqual(self.valor(codigo, "Qualidade documental do resumo"), lote.NAO_AVALIADA)
        for item in lote.ler_decisoes(lote.DECISOES):
            self.assertEqual(self.valor(item["codigo"], "Triagem de título e resumo"), "Pendente")
            self.assertEqual(self.valor(item["codigo"], "Decisão de elegibilidade"), "Pendente")
            self.assertEqual(self.valor(item["codigo"], "Afiliação em Goiás"), "Incerto")
            self.assertIsNone(self.valor(item["codigo"], "Ano de publicação"))
        eixo = self.depois["Eixos de análise"]
        ce = lote.cabecalhos(eixo)
        por_codigo = {}
        for linha in list(eixo.values)[1:]:
            por_codigo.setdefault(linha[ce["Código"] - 1], []).append(linha[ce["Estado"] - 1])
        self.assertEqual(por_codigo["2fda2cb6"], ["Não verificável"] * 3)
        self.assertEqual(por_codigo["c7fd8559"], ["Presente", "Presente", "Não verificável"])

    def test_preservacao_e_integridade(self):
        antes, depois = self.antes["Triagem"], self.depois["Triagem"]
        lidos = {x["codigo"] for x in lote.ler_decisoes(lote.DECISOES)}
        corrigidos = {codigo for codigo, numero in self.indices.items()
                      if antes.cell(numero, self.col["Qualidade documental do resumo"]).value == lote.NAO_AVALIADA
                      and lote.tipo_metadado(antes.cell(numero, self.col["Resumo"]).value)}
        self.assertEqual(len(corrigidos), 64)
        campos_leitura = {"Relação com PIBID", "Contexto de Goiás", "Decisão de elegibilidade",
                          "Evidência do contexto", "Fontes das evidências", "Material consultado",
                          "Limitações e pendências", "Observações", "Revisor", "Data da triagem"}
        for codigo, numero in self.indices.items():
            for campo, coluna in self.col.items():
                if codigo in lidos and campo in campos_leitura:
                    continue
                if codigo in corrigidos and campo in {"Qualidade documental do resumo", "Limitações e pendências"}:
                    continue
                self.assertEqual(antes.cell(numero, coluna).value, depois.cell(numero, coluna).value, f"{codigo}: {campo}")
        for nome in self.antes.sheetnames:
            if nome not in {"Triagem", "Eixos de análise", "Qualidade dos resumos", "Limites da integração"}:
                self.assertEqual(list(self.antes[nome].values), list(self.depois[nome].values), nome)
            if nome != "Eixos de análise":
                self.assertEqual(str(self.antes[nome].data_validations), str(self.depois[nome].data_validations))
        for nome in ("Eixos de análise", "Qualidade dos resumos"):
            old, new = self.antes[nome], self.depois[nome]
            self.assertEqual(list(old.values), list(new.values)[:old.max_row])
        eixo = self.depois["Eixos de análise"]
        self.assertEqual(eixo.max_row, self.antes["Eixos de análise"].max_row + 30)
        self.assertEqual(eixo.tables["Eixos"].ref, f"A1:K{eixo.max_row}")
        self.assertEqual(eixo.tables["Eixos"].autoFilter.ref, eixo.tables["Eixos"].ref)
        self.assertEqual(str(eixo.data_validations.dataValidation[0].sqref), f"D2:D{eixo.max_row}")
        tabela = self.depois["Qualidade dos resumos"].tables["QualidadeResumos"]
        self.assertEqual(tabela.ref, "A1:J274")
        self.assertEqual(tabela.autoFilter.ref, tabela.ref)
        formulas = lambda livro: {(s.title, c.coordinate, c.value) for s in livro for row in s for c in row if c.data_type == "f"}
        self.assertEqual(formulas(self.antes), formulas(self.depois))
        self.assertEqual(hashlib.sha256(lote.BASE.read_bytes()).hexdigest(), self.hash_antes)
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())

    def test_recusa_sobrescrita_e_estado_incompativel(self):
        with self.assertRaises(FileExistsError):
            lote.integrar(lote.BASE, lote.DECISOES, lote.BRUTO, self.saida)
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            livro = load_workbook(lote.BASE)
            livro["Triagem"].cell(self.indices["3424e29d"], self.col["Revisor"]).value = "Avaliação anterior"
            base, saida = pasta / "base.xlsx", pasta / "saida.xlsx"
            livro.save(base)
            livro.close()
            with self.assertRaisesRegex(ValueError, "Estado anterior"):
                lote.integrar(base, lote.DECISOES, lote.BRUTO, saida)
            self.assertFalse(saida.exists())


if __name__ == "__main__":
    unittest.main()
