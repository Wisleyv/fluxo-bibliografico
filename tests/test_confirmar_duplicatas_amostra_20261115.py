import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

from scripts import confirmar_duplicatas_amostra_20261115 as duplicatas


class DuplicatasTests(unittest.TestCase):
    def test_confirmacao_preserva_base_e_nao_escolhe_principal(self):
        anterior = duplicatas.BASE.read_bytes()
        with tempfile.TemporaryDirectory() as pasta:
            saida = Path(pasta) / "base.xlsx"
            duplicatas.confirmar(duplicatas.BASE, saida)
            livro = load_workbook(saida)
            triagem = livro["Triagem"]
            col = duplicatas.cabecalhos(triagem)
            linhas = duplicatas.indice_unico(triagem, col["Código"], 1317)
            for codigo in (c for par in duplicatas.PARES for c in par):
                n = linhas[codigo]
                self.assertEqual(triagem.cell(n, col["Duplicidade"]).value, "Duplicata confirmada")
                self.assertIsNone(triagem.cell(n, col["Código do registro principal"]).value)
            self.assertEqual(livro["Duplicatas conferidas"].max_row, 5)
        self.assertEqual(duplicatas.BASE.read_bytes(), anterior)

    def test_par_com_dados_divergentes_nao_e_confirmado(self):
        with tempfile.TemporaryDirectory() as pasta:
            saida = Path(pasta) / "invalida.xlsx"
            with self.assertRaisesRegex(ValueError, "Dados diferentes"):
                duplicatas.confirmar(duplicatas.BASE, saida, (("dca33e23", "5dbf2cee"),))
            self.assertFalse(saida.exists())

    def test_nao_sobrescreve(self):
        with tempfile.TemporaryDirectory() as pasta:
            saida = Path(pasta) / "existente.xlsx"
            saida.write_bytes(b"preservar")
            with self.assertRaises(FileExistsError):
                duplicatas.confirmar(duplicatas.BASE, saida)
            self.assertEqual(saida.read_bytes(), b"preservar")


if __name__ == "__main__":
    unittest.main()
