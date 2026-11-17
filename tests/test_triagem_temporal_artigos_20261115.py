import hashlib
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from scripts import triagem_temporal_artigos_20261115 as lote


class TriagemTemporalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporario = tempfile.TemporaryDirectory()
        cls.saida = Path(cls.temporario.name) / "saida.xlsx"
        cls.hash_antes = hashlib.sha256(lote.BASE.read_bytes()).hexdigest()
        lote.integrar(lote.BASE, lote.BRUTOS, cls.saida)
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

    def test_triagem_exclui_so_do_recorte_goiano(self):
        for codigo in ("58fb681e", "b0441893", "062d3f9a"):
            self.assertEqual(self.obter(codigo, "Triagem de título e resumo"), "Excluir")
            self.assertEqual(self.obter(codigo, "Motivo da exclusão"), "Fora do período")
            self.assertEqual(self.obter(codigo, "Decisão de elegibilidade"), "Pendente")
            self.assertEqual(self.obter(codigo, "Relação com PIBID"), "Incerto")
            self.assertIn("panorama nacional", self.obter(codigo, "Limitações e pendências"))
        self.assertEqual(self.obter("b0441893", "Tipo de produção"), "Outro: Editorial")
        self.assertEqual(self.obter("910fa3c6", "Triagem de título e resumo"), "Avançar para avaliação")
        self.assertEqual(self.obter("fdfb1cc1", "Triagem de título e resumo"), "Pendente")
        self.assertEqual(self.obter("fdfb1cc1", "Publicação em 2020–2026"), "Só ano de defesa disponível")

    def test_rejeita_ano_ausente_divergente_e_posterior(self):
        registro = {"Código": "x", "Fonte": "SciELO", "Título": "Título", "Autoria": "Ana Souza",
                    "Ano de publicação": "2019", "Ano de defesa": "2019", "DOI": None}
        tags = {"TI": ["Título"], "AU": ["Souza, Ana"], "PY": ["2019"], "DA": ["2019/05/01"]}
        indice = {("SciELO", lote.texto_comparavel("Título")): [(Path("origem.ris"), tags, [])]}
        lote.conferir_ris(registro, indice)
        for valor in (None, "2018", "2020"):
            with self.subTest(ano=valor):
                with self.assertRaisesRegex(ValueError, "Ano de publicação"):
                    lote.conferir_ris({**registro, "Ano de publicação": valor}, indice)
        with self.assertRaisesRegex(ValueError, "Data RIS divergente"):
            lote.conferir_ris(registro, {("SciELO", "titulo"): [(Path("origem.ris"), {**tags, "DA": ["2020/01/01"]}, [])]})

    def test_rejeita_correspondencia_ambigua_e_autoria_divergente(self):
        registro = {"Código": "x", "Fonte": "SciELO", "Título": "Título", "Autoria": "Ana Souza",
                    "Ano de publicação": "2019", "DOI": None}
        tags = {"TI": ["Título"], "AU": ["Ana Souza"], "PY": ["2019"]}
        origem = (Path("origem.ris"), tags, [])
        with self.assertRaisesRegex(ValueError, "ambígua"):
            lote.conferir_ris(registro, {("SciELO", "titulo"): [origem, origem]})
        with self.assertRaisesRegex(ValueError, "Autoria divergente"):
            lote.conferir_ris({**registro, "Autoria": "Outra pessoa"}, {("SciELO", "titulo"): [origem]})

    def test_preserva_entrada_e_celulas_fora_do_escopo(self):
        self.assertEqual(hashlib.sha256(lote.BASE.read_bytes()).hexdigest(), self.hash_antes)
        antes, depois = self.antes["Triagem"], self.depois["Triagem"]
        codigos = {r[0] for r in list(self.depois["Triagem temporal artigos"].values)[1:]}
        permitidos = {self.col[nome] for nome in (
            "Triagem de título e resumo", "Decisão de elegibilidade", "Motivo da exclusão",
            "Fontes das evidências", "Material consultado", "Limitações e pendências",
            "Observações", "Revisor", "Data da triagem",
        )}
        self.assertEqual(len(codigos), 85)
        for numero in range(1, antes.max_row + 1):
            codigo = antes.cell(numero, self.col["Código"]).value
            for coluna in range(1, antes.max_column + 1):
                if codigo in codigos and coluna in permitidos:
                    continue
                self.assertEqual(antes.cell(numero, coluna).value, depois.cell(numero, coluna).value, (codigo, coluna))
        for nome in self.antes.sheetnames:
            if nome in {"Triagem", "Limites da integração"}:
                continue
            self.assertEqual(list(self.antes[nome].values), list(self.depois[nome].values), nome)
        anteriores = list(self.antes["Limites da integração"].values)
        self.assertEqual(anteriores, list(self.depois["Limites da integração"].values)[:len(anteriores)])

    def test_estrutura_e_integridade(self):
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())
        audit = self.depois["Triagem temporal artigos"]
        self.assertEqual(audit.max_row, 86)
        self.assertEqual(audit.tables["TriagemTemporalArtigos"].ref, "A1:L86")
        for nome in self.antes.sheetnames:
            self.assertEqual(str(self.antes[nome].data_validations), str(self.depois[nome].data_validations))
            for tabela in self.antes[nome].tables:
                self.assertEqual(self.antes[nome].tables[tabela].ref, self.depois[nome].tables[tabela].ref)
        formulas_antes = {(s.title, c.coordinate, c.value) for s in self.antes for linha in s for c in linha if c.data_type == "f"}
        formulas_depois = {(s.title, c.coordinate, c.value) for s in self.depois for linha in s for c in linha if c.data_type == "f"}
        self.assertEqual(formulas_antes, formulas_depois)

    def test_nao_sobrescreve(self):
        with self.assertRaises(FileExistsError):
            lote.integrar(lote.BASE, lote.BRUTOS, self.saida)


if __name__ == "__main__":
    unittest.main()
