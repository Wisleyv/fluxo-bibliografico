import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

from scripts import conferir_amostra_por_regras_20261115 as conferencia


class ConferenciaTests(unittest.TestCase):
    def test_detecta_campos_que_podem_nao_ser_resumos(self):
        self.assertEqual(conferencia.tipo_resumo(None), "Campo vazio")
        self.assertEqual(conferencia.tipo_resumo("Orientador: Alguém"), "Possível informação de orientação")
        self.assertEqual(conferencia.tipo_resumo("Dissertação (mestrado) — Universidade, 2024."),
                         "Possível referência bibliográfica")
        self.assertEqual(conferencia.tipo_resumo("A pesquisa analisou os dados."),
                         "Texto preenchido; conteúdo não verificado por regra")

    def test_avanco_exige_todos_os_criterios_declarados(self):
        linha = {
            "Triagem da autoavaliação": "Avançar para avaliação",
            "Relação com PIBID": "Relação substantiva com PIBID",
            "Contexto de Goiás": "Incerto",
            "Afiliação em Goiás": "Sim",
            "Publicação em 2020–2026": "Publicação 2020–2026 confirmada",
            "Produção acadêmica": "Sim",
        }
        self.assertEqual(conferencia.coerencia_triagem(linha), "Requisitos declarados compatíveis")
        linha["Publicação em 2020–2026"] = "Incerto"
        self.assertEqual(conferencia.coerencia_triagem(linha), "Requisitos declarados incompatíveis")

    def test_saida_preserva_fontes_e_detecta_divergencias_conhecidas(self):
        entradas = [conferencia.CEGA, conferencia.AUTO, conferencia.BASE]
        antes = [p.read_bytes() for p in entradas]
        with tempfile.TemporaryDirectory() as pasta:
            saida = Path(pasta) / "conferencia.xlsx"
            conferencia.gerar(*entradas, saida)
            livro = load_workbook(saida)
            self.assertEqual(livro["Conferência por registro"].max_row, 61)
            alertas = list(livro["Alertas"].values)[1:]
            encontrados = {(r[0], r[1]) for r in alertas}
            for codigo in ("06792f41", "c3920958", "5dbf2cee"):
                self.assertIn((codigo, "Período entre versões"), encontrados)
            self.assertIn(("796dae04", "Diferença na integração"), encontrados)
            self.assertIn(("46baf45a", "Inconsistência previamente documentada"), encontrados)
            self.assertIn(("83224e28", "DOI repetido"), encontrados)
            self.assertEqual(len([r for r in alertas if r[1] == "Inconsistência lógica"]), 0)
            self.assertIn("não é análise independente", livro["Limites e regras"]["A1"].value)
        self.assertEqual([p.read_bytes() for p in entradas], antes)

    def test_recusa_sobrescrita(self):
        with tempfile.TemporaryDirectory() as pasta:
            saida = Path(pasta) / "existe.xlsx"
            saida.write_bytes(b"preservar")
            with self.assertRaises(FileExistsError):
                conferencia.gerar(conferencia.CEGA, conferencia.AUTO, conferencia.BASE, saida)
            self.assertEqual(saida.read_bytes(), b"preservar")


if __name__ == "__main__":
    unittest.main()
