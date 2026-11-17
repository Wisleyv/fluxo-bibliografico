import csv
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

from scripts import integrar_lote_goias_20261115 as lote


class LoteGoiasTests(unittest.TestCase):
    def test_integra_lote_sem_excluir_por_ano_de_defesa(self):
        antes = lote.BASE.read_bytes()
        with tempfile.TemporaryDirectory() as pasta:
            saida = Path(pasta) / "integrada.xlsx"
            lote.integrar(lote.BASE, lote.DECISOES, saida)
            livro = load_workbook(saida)
            aba = livro["Triagem"]
            col = lote.cabecalhos(aba)
            indices = lote.indice_unico(aba, col["Código"], 1317)
            def obter(codigo, campo):
                return aba.cell(indices[codigo], col[campo]).value
            self.assertEqual(obter("fdfb1cc1", "Triagem de título e resumo"), "Pendente")
            self.assertEqual(obter("fdfb1cc1", "Publicação em 2020–2026"), "Só ano de defesa disponível")
            self.assertEqual(obter("fdfb1cc1", "Duplicidade"), "Duplicata confirmada")
            self.assertEqual(obter("b4cf1792", "Duplicidade"), "Duplicata confirmada")
            self.assertEqual(obter("def4bf15", "Triagem de título e resumo"), "Excluir")
            self.assertEqual(obter("def4bf15", "Motivo da exclusão"), "Fora do período")
            self.assertEqual(obter("def4bf15", "Decisão de elegibilidade"), "Pendente")
            self.assertEqual(obter("3d9f25bd", "Relação com PIBID"), "Menção incidental")
            self.assertEqual(obter("d6245c9f", "Contexto de Goiás"), "Incerto")
            self.assertEqual(livro["Lote prioritário GO"].max_row, 37)
            eixos = livro["Eixos de análise"]
            self.assertEqual(eixos.max_row, 379)
            self.assertEqual(eixos.tables["Eixos"].ref, "A1:K379")
            self.assertEqual(eixos.tables["Eixos"].autoFilter.ref, "A1:K379")
        self.assertEqual(lote.BASE.read_bytes(), antes)

    def test_rejeita_decisoes_duplicadas(self):
        with lote.DECISOES.open(encoding="utf-8", newline="") as f:
            leitor = csv.DictReader(f)
            campos = leitor.fieldnames
            dados = list(leitor)
        dados[1]["codigo"] = dados[0]["codigo"]
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "invalido.csv"
            with arquivo.open("w", encoding="utf-8", newline="") as f:
                escritor = csv.DictWriter(f, fieldnames=campos)
                escritor.writeheader()
                escritor.writerows(dados)
            with self.assertRaisesRegex(ValueError, "Código repetido"):
                lote.ler_decisoes(arquivo)

    def test_nao_sobrescreve(self):
        with tempfile.TemporaryDirectory() as pasta:
            saida = Path(pasta) / "existente.xlsx"
            saida.write_bytes(b"preservar")
            with self.assertRaises(FileExistsError):
                lote.integrar(lote.BASE, lote.DECISOES, saida)
            self.assertEqual(saida.read_bytes(), b"preservar")


if __name__ == "__main__":
    unittest.main()
