import tempfile
import unittest
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from scripts import preparar_produtos_preliminares_20261115 as produto


class ProdutosPreliminaresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pasta = tempfile.TemporaryDirectory()
        cls.saida = Path(cls.pasta.name) / "produto.xlsx"
        produto.gerar(produto.BASE, cls.saida)
        cls.livro = load_workbook(cls.saida)

    @classmethod
    def tearDownClass(cls):
        cls.livro.close()
        cls.pasta.cleanup()

    def test_referencias_e_achados_da_base(self):
        base = load_workbook(produto.BASE, read_only=True)
        try:
            triagem = base["Triagem"]
            ct = produto.cabecalhos(triagem)
            selecionados = {r[ct["Código"] - 1]: r for r in list(triagem.values)[1:]
                            if r[ct["Decisão de elegibilidade"] - 1] == "Incluir"}
            refs = list(self.livro["Referências"].values)
            self.assertEqual(len(refs) - 1, 19)
            self.assertEqual({r[0] for r in refs[1:]}, set(selecionados))
            for r in refs[1:]:
                original = selecionados[r[0]]
                self.assertEqual(r[1], original[ct["Título"] - 1])
                self.assertEqual(r[4], int(original[ct["Ano de publicação"] - 1]))
                self.assertEqual(r[11], original[ct["Qualidade documental do resumo"] - 1])
            eixos = base["Eixos de análise"]
            ce = produto.cabecalhos(eixos)
            esperados = {(r[ce["Código"] - 1], r[ce["Eixo"] - 1]):
                         (r[ce["Estado"] - 1], r[ce["Achado ou observação"] - 1],
                          r[ce["Limites da evidência"] - 1])
                         for r in list(eixos.values)[1:] if r[ce["Código"] - 1] in selecionados}
            achados = list(self.livro["Achados"].values)[1:]
            self.assertEqual(len(achados), 57)
            self.assertEqual({(r[0], r[1]): (r[2], r[3], r[4]) for r in achados}, esperados)
        finally:
            base.close()

    def test_graficos_dados_e_limites(self):
        graf = self.livro["Gráficos"]
        refs = list(self.livro["Referências"].values)[1:]
        achados = list(self.livro["Achados"].values)[1:]
        for linha, eixo in enumerate(produto.EIXOS_CURTOS, 6):
            estados = Counter(r[2] for r in achados if r[1] == eixo)
            self.assertEqual([graf.cell(linha, n).value for n in range(2, 5)],
                             [estados[e] for e in produto.ESTADOS])
            self.assertEqual(sum(graf.cell(linha, n).value for n in range(2, 5)), 19)
        anos = Counter(r[4] for r in refs)
        for linha, ano in enumerate(range(2020, 2027), 13):
            self.assertEqual(graf.cell(linha, 1).value, str(ano))
            self.assertEqual(graf.cell(linha, 2).value, anos[ano])
        self.assertEqual(len(graf._charts), 2)
        self.assertEqual(len(graf._charts[0].series), 3)
        self.assertEqual(len(graf._charts[1].series), 1)
        for chart in graf._charts:
            self.assertEqual(chart.x_axis.tickLblPos, "nextTo")
            self.assertEqual(chart.y_axis.tickLblPos, "nextTo")
            self.assertFalse(chart.x_axis.delete)
            self.assertFalse(chart.y_axis.delete)
        self.assertIn("$B$6:$B$8", graf._charts[0].series[0].val.numRef.f)
        self.assertIn("$B$13:$B$19", graf._charts[1].series[0].val.numRef.f)
        texto = " ".join(str(cell.value or "") for row in self.livro["Leia primeiro"] for cell in row)
        for trecho in ("1.099", "deduplicação incompletas", "Não informado", "não independente",
                       "retratos estáticos", "2026 é parcial"):
            self.assertIn(trecho, texto)
        self.assertNotIn("Revisor", [c.value for c in self.livro["Referências"][1]])
        self.assertNotIn("Alerta de qualidade", [c.value for c in self.livro["Referências"][1]])
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())
            self.assertIn("xl/charts/chart1.xml", arquivo.namelist())
            self.assertIn("xl/charts/chart2.xml", arquivo.namelist())
            for arquivo_grafico in ("xl/charts/chart2.xml", "xl/charts/chart3.xml"):
                grafico = arquivo.read(arquivo_grafico).decode("utf-8")
                self.assertIn("parcial", grafico)
                self.assertIn("19 linhas", grafico)
                self.assertIn('showCatName val="0"', grafico)
                self.assertIn('showSerName val="0"', grafico)
        self.assertIn("qualidade reduzida", graf["F27"].value)
        self.assertIn("qualidade reduzida", graf["F54"].value)
        self.assertIn("Fonte: base técnica", graf["F27"].value)

    def test_panorama_nacional_por_ano_de_defesa(self):
        graf = self.livro["Panorama nacional"]
        anos = produto.anos_defesa_bdtd(produto.BDTD_NACIONAL)
        for linha, ano in enumerate(range(2007, 2027), 4):
            self.assertEqual(graf.cell(linha, 1).value, str(ano))
            self.assertEqual(graf.cell(linha, 2).value, anos[ano])
        self.assertEqual(graf["B25"].value, 1018)
        self.assertEqual(len(graf._charts), 1)
        self.assertEqual(graf._charts[0].x_axis.axPos, "b")
        self.assertEqual(graf._charts[0].x_axis.tickLblPos, "nextTo")
        self.assertIn("$B$4:$B$23", graf._charts[0].series[0].val.numRef.f)
        self.assertIn("Ano de defesa não equivale a ano de publicação", graf["D28"].value)
        self.assertIn("não representam toda a produção brasileira", graf["D28"].value)

    def test_recusa_sobrescrita_e_base_inconsistente(self):
        with self.assertRaises(FileExistsError):
            produto.gerar(produto.BASE, self.saida)
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            base = load_workbook(produto.BASE)
            triagem = base["Triagem"]
            ct = produto.cabecalhos(triagem)
            linha = next(n for n in range(2, triagem.max_row + 1)
                         if triagem.cell(n, ct["Decisão de elegibilidade"]).value == "Incluir")
            triagem.cell(linha, ct["Decisão de elegibilidade"]).value = "Pendente"
            base_alterada = pasta / "base.xlsx"
            base.save(base_alterada)
            base.close()
            saida = pasta / "saida.xlsx"
            with self.assertRaisesRegex(ValueError, "19 registros"):
                produto.gerar(base_alterada, saida)
            self.assertFalse(saida.exists())


if __name__ == "__main__":
    unittest.main()
