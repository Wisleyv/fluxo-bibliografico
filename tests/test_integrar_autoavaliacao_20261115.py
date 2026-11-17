import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

from scripts import integrar_autoavaliacao_20261115 as integracao


class IntegracaoTests(unittest.TestCase):
    def test_integracao_preserva_base_e_sinaliza_limites(self):
        base_antes = integracao.BASE.read_bytes()
        amostra_antes = integracao.AMOSTRA.read_bytes()
        with tempfile.TemporaryDirectory() as pasta:
            saida = Path(pasta) / "integrada.xlsx"
            integracao.integrar(integracao.BASE, integracao.AMOSTRA, saida)
            livro = load_workbook(saida)
            triagem = livro["Triagem"]
            col = integracao.cabecalhos(triagem)
            linhas = integracao.indice_unico(triagem, col["Código"], 1317)
            def obter(codigo, campo):
                return triagem.cell(linhas[codigo], col[campo]).value
            self.assertEqual(obter("796dae04", "Contexto de Goiás"), "Incerto")
            self.assertEqual(obter("796dae04", "Afiliação em Goiás"), "Sim")
            self.assertEqual(obter("796dae04", "Triagem de título e resumo"), "Avançar para avaliação")
            self.assertEqual(obter("06792f41", "Ano de publicação"), 2024)
            self.assertEqual(obter("c3920958", "Publicação em 2020–2026"), "Incerto")
            for codigo in ("83224e28", "387c5254"):
                self.assertEqual(obter(codigo, "Duplicidade"), "Duplicata confirmada")
                self.assertEqual(obter(codigo, "Decisão de elegibilidade"), "Pendente")
                self.assertIsNone(obter(codigo, "Código do registro principal"))
            eixos = livro["Eixos de análise"]
            self.assertEqual(eixos.max_row, 271)
            self.assertEqual(eixos.tables["Eixos"].ref, "A1:K271")
            self.assertEqual(eixos.tables["Eixos"].autoFilter.ref, "A1:K271")
            self.assertEqual(str(eixos.data_validations.dataValidation[0].sqref), "D2:D271")
            self.assertEqual(sum(r[3].value is not None for r in list(eixos.rows)[1:]), 189)
            self.assertIn("NÃO é validação independente", livro["Limites da integração"]["A2"].value)
            auditoria = list(livro["Alterações da amostra"].values)
            self.assertTrue(any(r[0] == "796dae04" and r[1] == "Contexto de Goiás"
                                and r[2] == r[4] != r[3] for r in auditoria[1:]))
        self.assertEqual(integracao.BASE.read_bytes(), base_antes)
        self.assertEqual(integracao.AMOSTRA.read_bytes(), amostra_antes)

    def test_nao_sobrescreve_saida(self):
        with tempfile.TemporaryDirectory() as pasta:
            saida = Path(pasta) / "existente.xlsx"
            saida.write_bytes(b"preservar")
            with self.assertRaises(FileExistsError):
                integracao.integrar(integracao.BASE, integracao.AMOSTRA, saida)
            self.assertEqual(saida.read_bytes(), b"preservar")


if __name__ == "__main__":
    unittest.main()
