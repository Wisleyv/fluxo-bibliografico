import hashlib
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from scripts import conferir_termos_e_resumos_20261115 as lote


class ConferenciaTermosTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporario = tempfile.TemporaryDirectory()
        cls.saida = Path(cls.temporario.name) / "saida.xlsx"
        cls.hash_antes = hashlib.sha256(lote.BASE.read_bytes()).hexdigest()
        lote.integrar(lote.BASE, lote.DECISOES, lote.FONTES_UNB, cls.saida)
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

    def test_exclusao_de_metadados_e_provisoria_e_nao_afirma_ausencia_no_texto(self):
        for codigo in ("842977f5", "f06af347", "c71706a2", "9a81aa29"):
            self.assertEqual(self.obter(codigo, "Triagem de título e resumo"), "Excluir")
            self.assertEqual(self.obter(codigo, "Decisão de elegibilidade"), "Pendente")
            self.assertEqual(self.obter(codigo, "Motivo da exclusão"), "Outro")
            self.assertEqual(self.obter(codigo, "Relação com PIBID"), "Incerto")
            self.assertIn("Não comprova ausência", self.obter(codigo, "Limitações e pendências"))

    def test_resumos_unb_revelam_pibid_e_goias_e_datas_nao_sao_confundidas(self):
        for codigo in ("a3e7321c", "69c845eb", "e92d970d", "6fb14721"):
            self.assertEqual(self.obter(codigo, "Relação com PIBID"), "Relação substantiva com PIBID")
            self.assertEqual(self.obter(codigo, "Contexto de Goiás"), "Pesquisa realizada em Goiás")
            self.assertEqual(self.obter(codigo, "Decisão de elegibilidade"), "Pendente")
            self.assertIn("repositório UnB", self.obter(codigo, "Fontes das evidências"))
        for codigo in ("a3e7321c", "69c845eb"):
            self.assertEqual(self.obter(codigo, "Ano de publicação"), 2017)
            self.assertEqual(self.obter(codigo, "Triagem de título e resumo"), "Excluir")
            self.assertEqual(self.obter(codigo, "Motivo da exclusão"), "Fora do período")
        for codigo in ("e92d970d", "6fb14721"):
            self.assertIsNone(self.obter(codigo, "Ano de publicação"))
            self.assertEqual(self.obter(codigo, "Publicação em 2020–2026"), "Incerto")
            self.assertEqual(self.obter(codigo, "Triagem de título e resumo"), "Pendente")
            self.assertIn("incorporação", self.obter(codigo, "Limitações e pendências"))

    def test_detecao_de_termos_e_salvaguarda_das_exportacoes(self):
        self.assertTrue(lote.tem_termo("Pibidianos e PÍBID"))
        self.assertTrue(lote.tem_termo("Programa Institucional de Bolsas de Iniciação à Docência"))
        self.assertFalse(lote.tem_termo("Programa de apoio às licenciaturas interculturais"))
        with tempfile.TemporaryDirectory() as pasta:
            livro = load_workbook(lote.BASE)
            livro["Triagem"].cell(self.indices["f06af347"], self.col["Resumo"]).value = "Resumo alterado sobre PIBID."
            base = Path(pasta) / "alterada.xlsx"
            saida = Path(pasta) / "saida.xlsx"
            livro.save(base)
            livro.close()
            with self.assertRaises(ValueError):
                lote.integrar(base, lote.DECISOES, lote.FONTES_UNB, saida)
            self.assertFalse(saida.exists())

    def test_preserva_entrada_historico_e_celulas_fora_do_escopo(self):
        self.assertEqual(hashlib.sha256(lote.BASE.read_bytes()).hexdigest(), self.hash_antes)
        antes, depois = self.antes["Triagem"], self.depois["Triagem"]
        codigos = {r[0] for r in list(self.depois["Conferência termos e UnB"].values)[1:]}
        self.assertEqual(len(codigos), 32)
        campos = {self.col[nome] for nome in (
            "Relação com PIBID", "Contexto de Goiás", "Ano de publicação", "Publicação em 2020–2026",
            "Triagem de título e resumo", "Motivo da exclusão", "Evidência do contexto",
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
        ea, ed = self.antes["Eixos de análise"], self.depois["Eixos de análise"]
        ce = lote.cabecalhos(ea)
        self.assertEqual(ea.max_row, ed.max_row)
        unb = {"a3e7321c", "69c845eb", "e92d970d", "6fb14721"}
        alteraveis = {ce[x] for x in ("Estado", "Achado ou observação", "Limites da evidência",
                                      "Trecho ou localização", "Tipo de fonte", "Link ou referência consultada")}
        for linha in range(1, ea.max_row + 1):
            codigo = ea.cell(linha, ce["Código"]).value
            for coluna in range(1, ea.max_column + 1):
                if codigo in unb and coluna in alteraveis:
                    continue
                self.assertEqual(ea.cell(linha, coluna).value, ed.cell(linha, coluna).value, (codigo, coluna))

    def test_integridade_validacoes_e_formulas(self):
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())
        self.assertEqual(self.depois["Conferência termos e UnB"].max_row, 33)
        for nome in self.antes.sheetnames:
            self.assertEqual(str(self.antes[nome].data_validations), str(self.depois[nome].data_validations))
        for nome in ("Triagem", "Eixos de análise"):
            for tabela in self.antes[nome].tables:
                self.assertEqual(self.antes[nome].tables[tabela].ref, self.depois[nome].tables[tabela].ref)
        formulas_antes = {(s.title, c.coordinate, c.value) for s in self.antes for linha in s for c in linha if c.data_type == "f"}
        formulas_depois = {(s.title, c.coordinate, c.value) for s in self.depois for linha in s for c in linha if c.data_type == "f"}
        self.assertEqual(formulas_antes, formulas_depois)
        with self.assertRaises(FileExistsError):
            lote.integrar(lote.BASE, lote.DECISOES, lote.FONTES_UNB, self.saida)


if __name__ == "__main__":
    unittest.main()
