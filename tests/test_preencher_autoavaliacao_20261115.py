import csv
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

from scripts import preencher_autoavaliacao_20261115 as modulo


class AutoavaliacaoTests(unittest.TestCase):
    def test_preenchimento_preserva_base_e_estrutura(self):
        antes = modulo.BASE.read_bytes()
        with tempfile.TemporaryDirectory() as pasta:
            saida = Path(pasta) / "autoavaliacao.xlsx"
            modulo.preencher(modulo.BASE, modulo.DECISOES, saida)
            livro = load_workbook(saida)
            aba = livro["Autoavaliação"]
            self.assertEqual(len(aba.tables), 1)
            self.assertEqual(len(aba.data_validations.dataValidation), 9)
            self.assertEqual(aba.max_row, 61)
            self.assertTrue(all(aba.cell(r, c).value for r in range(2, 62) for c in range(16, 29)))
            por_codigo = {aba.cell(r, 1).value: r for r in range(2, 62)}
            self.assertEqual(aba.cell(por_codigo["06792f41"], 6).value, 2024)
            self.assertEqual(aba.cell(por_codigo["06792f41"], 8).value, "Não")
            self.assertEqual(aba.cell(por_codigo["5dbf2cee"], 19).value, "Incerto")
            self.assertEqual(aba.cell(por_codigo["c3920958"], 19).value, "Incerto")
            self.assertIn("não independente", aba.cell(2, 28).value)
            self.assertIn("NÃO é validação independente", livro["Instruções"].cell(1, 1).value)
            self.assertTrue(all(c.data_type != "f" for row in aba for c in row))
        self.assertEqual(modulo.BASE.read_bytes(), antes)

    def test_rejeita_avanco_sem_data_confirmada(self):
        with modulo.DECISOES.open(encoding="utf-8", newline="") as entrada:
            leitor = csv.DictReader(entrada)
            campos = leitor.fieldnames
            dados = list(leitor)
        dados[0]["triagem"] = "A"
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "invalido.csv"
            with arquivo.open("w", encoding="utf-8", newline="") as saida:
                escritor = csv.DictWriter(saida, fieldnames=campos)
                escritor.writeheader()
                escritor.writerows(dados)
            with self.assertRaisesRegex(ValueError, "Avanço sem requisitos"):
                modulo.ler_decisoes(arquivo)

    def test_nao_sobrescreve_saida(self):
        with tempfile.TemporaryDirectory() as pasta:
            saida = Path(pasta) / "existente.xlsx"
            saida.write_bytes(b"preservar")
            with self.assertRaises(FileExistsError):
                modulo.preencher(modulo.BASE, modulo.DECISOES, saida)
            self.assertEqual(saida.read_bytes(), b"preservar")


if __name__ == "__main__":
    unittest.main()
