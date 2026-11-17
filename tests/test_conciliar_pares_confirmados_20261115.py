import hashlib
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from scripts import conciliar_pares_confirmados_20261115 as conciliacao
from scripts.preanalise_e_validacao_20261115 import cabecalhos


class ConciliacaoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pasta = tempfile.TemporaryDirectory()
        cls.saida = Path(cls.pasta.name) / "saida.xlsx"
        cls.hash_antes = hashlib.sha256(conciliacao.BASE.read_bytes()).hexdigest()
        conciliacao.integrar(conciliacao.BASE, cls.saida)
        cls.antes = load_workbook(conciliacao.BASE)
        cls.depois = load_workbook(cls.saida)

    @classmethod
    def tearDownClass(cls):
        cls.antes.close()
        cls.depois.close()
        cls.pasta.cleanup()

    def test_decisoes_e_preservacao(self):
        antes, depois = self.antes["Triagem"], self.depois["Triagem"]
        colunas = cabecalhos(antes)
        indices = conciliacao.indice_unico(antes, colunas["Código"], 1317)
        permitidos = {
            "2e073f75": {"Relação com PIBID", "Publicação em 2020–2026",
                         "Fontes das evidências", "Limitações e pendências"},
            "361dd6b1": {"Contexto de Goiás", "Evidência do contexto", "Limitações e pendências"},
            "5f5259e7": {"Contexto de Goiás", "Evidência do contexto", "Limitações e pendências"},
        }
        for codigo, par, campo, anterior, novo, _ in conciliacao.AJUSTES:
            self.assertEqual(antes.cell(indices[codigo], colunas[campo]).value, anterior)
            self.assertEqual(depois.cell(indices[codigo], colunas[campo]).value, novo)
            self.assertEqual(depois.cell(indices[par], colunas[campo]).value, novo)
        for codigo, numero in indices.items():
            for campo, coluna in colunas.items():
                if campo not in permitidos.get(codigo, set()):
                    self.assertEqual(antes.cell(numero, coluna).value, depois.cell(numero, coluna).value,
                                     f"{codigo}: {campo}")
        for nome in self.antes.sheetnames:
            if nome not in {"Triagem", "Limites da integração"}:
                self.assertEqual(list(self.antes[nome].values), list(self.depois[nome].values), nome)
            self.assertEqual(str(self.antes[nome].data_validations), str(self.depois[nome].data_validations))
        self.assertEqual(hashlib.sha256(conciliacao.BASE.read_bytes()).hexdigest(), self.hash_antes)
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())
        auditoria = self.depois["Conciliação pares confirmados"]
        self.assertEqual(auditoria.tables["ConciliacaoParesConfirmados"].ref, "A1:F5")
        self.assertEqual(auditoria.tables["ConciliacaoParesConfirmados"].autoFilter.ref, "A1:F5")
        formulas = lambda livro: {(s.title, c.coordinate, c.value) for s in livro for row in s for c in row if c.data_type == "f"}
        self.assertEqual(formulas(self.antes), formulas(self.depois))

    def test_recusa_material_divergente_e_sobrescrita(self):
        with self.assertRaises(FileExistsError):
            conciliacao.integrar(conciliacao.BASE, self.saida)
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            livro = load_workbook(conciliacao.BASE)
            triagem = livro["Triagem"]
            colunas = cabecalhos(triagem)
            indices = conciliacao.indice_unico(triagem, colunas["Código"], 1317)
            triagem.cell(indices["5dbf2cee"], colunas["Resumo"]).value = "Outro resumo"
            base, saida = pasta / "base.xlsx", pasta / "saida.xlsx"
            livro.save(base)
            livro.close()
            with self.assertRaisesRegex(ValueError, "Material ou identidade divergente"):
                conciliacao.integrar(base, saida)
            self.assertFalse(saida.exists())


if __name__ == "__main__":
    unittest.main()
