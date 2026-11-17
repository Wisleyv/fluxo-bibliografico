import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openpyxl import Workbook, load_workbook

from scripts import integrar_teses_e_datas_uel_20261115 as lote


class LoteTesesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporario = tempfile.TemporaryDirectory()
        cls.saida = Path(cls.temporario.name) / "saida.xlsx"
        cls.hash_antes = hashlib.sha256(lote.BASE.read_bytes()).hexdigest()
        lote.integrar(lote.BASE, lote.DECISOES, lote.DATAS, cls.saida)
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

    def test_defesa_corrigida_nao_vira_publicacao_ou_exclusao(self):
        for codigo, esperado in (("236bd660", "2016"), ("e7a9290f", "2018"), ("5f5f63ba", "2019"),
                                 ("da928d3e", "2020")):
            self.assertEqual(self.obter(codigo, "Ano de defesa"), esperado)
            self.assertIsNone(self.obter(codigo, "Ano de publicação"))
            self.assertEqual(self.obter(codigo, "Publicação em 2020–2026"), "Só ano de defesa disponível")
            self.assertEqual(self.obter(codigo, "Triagem de título e resumo"), "Pendente")
            self.assertIn("BDTD informava defesa 2024", self.obter(codigo, "Limitações e pendências"))

    def test_ano_de_emissao_e_defesa_nao_confirmada_ficam_distintos(self):
        self.assertEqual(self.obter("fe0699e5", "Ano de publicação"), 2024)
        self.assertEqual(self.obter("fe0699e5", "Ano de defesa"), "2024")
        self.assertEqual(self.obter("fe0699e5", "Publicação em 2020–2026"), "Publicação 2020–2026 confirmada")
        self.assertIn("não foi confirmada", self.obter("fe0699e5", "Limitações e pendências"))
        self.assertIsNone(self.obter("223fc435", "Ano de publicação"))

    def test_analise_e_pares_nao_geram_decisoes_finais(self):
        self.assertEqual(self.obter("d9c78129", "Contexto de Goiás"), "Pesquisa realizada em Goiás")
        self.assertEqual(self.obter("d9c78129", "Relação com PIBID"), "Relação substantiva com PIBID")
        self.assertEqual(self.obter("ca6145ae", "Relação com PIBID"), "Incerto")
        self.assertEqual(self.obter("4420812c", "Contexto de Goiás"), "Pesquisa realizada em Goiás")
        self.assertEqual(self.obter("f213a983", "Duplicidade"), "Não verificada")
        self.assertEqual(self.obter("264e25f7", "Duplicidade"), "Não verificada")
        self.assertEqual(self.obter("d9c78129", "Duplicidade"), "Duplicata confirmada")
        for codigo in ("d9c78129", "ca6145ae", "f213a983", "fe0699e5"):
            self.assertEqual(self.obter(codigo, "Decisão de elegibilidade"), "Pendente")
            self.assertEqual(self.obter(codigo, "Triagem de título e resumo"), "Pendente")

    def test_rejeita_reaproveitar_resumo_diferente(self):
        origem = self.antes["Triagem"]
        livro = Workbook()
        aba = livro.active
        aba.append([c.value for c in origem[1]])
        for codigo in ("f213a983", "264e25f7"):
            aba.append([c.value for c in origem[self.indices[codigo]]])
        col = lote.cabecalhos(aba)
        lote.validar_par_fontes(aba, col, 2, 3, "a", "b")
        aba.cell(3, col["Resumo"]).value += " conteúdo diferente"
        with self.assertRaisesRegex(ValueError, "Resumo"):
            lote.validar_par_fontes(aba, col, 2, 3, "a", "b")

    def test_rejeita_data_de_deposito_como_data_de_defesa(self):
        with lote.DATAS.open(encoding="utf-8") as arquivo:
            consulta = next(x for x in json.load(arquivo)["registros"] if x["codigo"] == "236bd660")
        n = self.indices["236bd660"]
        celula = lambda campo: self.antes["Triagem"].cell(n, self.col[campo])
        consulta["metadados"]["dc.date.defesa"] = []
        with self.assertRaisesRegex(ValueError, "Datas UEL incompletas"):
            lote.validar_datas(consulta, celula)

    def test_preserva_entrada_e_celulas_fora_do_escopo(self):
        self.assertEqual(hashlib.sha256(lote.BASE.read_bytes()).hexdigest(), self.hash_antes)
        antes, depois = self.antes["Triagem"], self.depois["Triagem"]
        codigos_lote = {r[0] for r in list(self.depois["Lote teses recente"].values)[1:]}
        codigos_uel = {r[0] for r in list(self.depois["Datas UEL conferidas"].values)[1:]}
        self.assertEqual(len(codigos_lote), 35)
        self.assertEqual(len(codigos_uel), 31)
        campos_lote = {self.col[nome] for nome in (
            "Relação com PIBID", "Contexto de Goiás", "Decisão de elegibilidade", "Evidência do contexto",
            "Fontes das evidências", "Material consultado", "Limitações e pendências",
            "Observações", "Revisor", "Data da triagem",
        )}
        campos_uel = {self.col[nome] for nome in (
            "Ano de defesa", "Ano de publicação", "Publicação em 2020–2026",
            "Fontes das evidências", "Limitações e pendências", "Observações",
        )}
        for numero in range(1, antes.max_row + 1):
            codigo = antes.cell(numero, self.col["Código"]).value
            for coluna in range(1, antes.max_column + 1):
                if (codigo in codigos_lote and coluna in campos_lote) or (codigo in codigos_uel and coluna in campos_uel):
                    continue
                self.assertEqual(antes.cell(numero, coluna).value, depois.cell(numero, coluna).value, (codigo, coluna))
        for nome in self.antes.sheetnames:
            if nome in {"Triagem", "Eixos de análise", "Limites da integração"}:
                continue
            self.assertEqual(list(self.antes[nome].values), list(self.depois[nome].values), nome)
        anteriores = list(self.antes["Eixos de análise"].values)
        self.assertEqual(anteriores, list(self.depois["Eixos de análise"].values)[:len(anteriores)])

    def test_estrutura_e_integridade(self):
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())
        self.assertEqual(self.depois["Lote teses recente"].max_row, 36)
        self.assertEqual(self.depois["Datas UEL conferidas"].max_row, 32)
        eixos = self.depois["Eixos de análise"]
        self.assertEqual(eixos.max_row, self.antes["Eixos de análise"].max_row + 105)
        self.assertEqual(eixos.tables["Eixos"].ref, f"A1:K{eixos.max_row}")
        self.assertEqual(eixos.tables["Eixos"].autoFilter.ref, f"A1:K{eixos.max_row}")
        self.assertEqual(str(eixos.data_validations.dataValidation[0].sqref), f"D2:D{eixos.max_row}")
        for nome in self.antes.sheetnames:
            if nome != "Eixos de análise":
                self.assertEqual(str(self.antes[nome].data_validations), str(self.depois[nome].data_validations))
        formulas_antes = {(s.title, c.coordinate, c.value) for s in self.antes for linha in s for c in linha if c.data_type == "f"}
        formulas_depois = {(s.title, c.coordinate, c.value) for s in self.depois for linha in s for c in linha if c.data_type == "f"}
        self.assertEqual(formulas_antes, formulas_depois)

    def test_nao_sobrescreve(self):
        with self.assertRaises(FileExistsError):
            lote.integrar(lote.BASE, lote.DECISOES, lote.DATAS, self.saida)


if __name__ == "__main__":
    unittest.main()
