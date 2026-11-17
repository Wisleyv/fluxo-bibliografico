import hashlib
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from scripts import conciliar_fontes_catalogo_bdtd_20261115 as lote


class ConciliarFontesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pasta = tempfile.TemporaryDirectory()
        cls.saida = Path(cls.pasta.name) / "saida.xlsx"
        cls.hash_antes = hashlib.sha256(lote.BASE.read_bytes()).hexdigest()
        lote.integrar(lote.BASE, lote.BRUTO, cls.saida)
        cls.antes = load_workbook(lote.BASE)
        cls.depois = load_workbook(cls.saida)
        cls.col = lote.cabecalhos(cls.antes["Triagem"])
        cls.indices = lote.indice_unico(cls.antes["Triagem"], cls.col["Código"], 1317)

    @classmethod
    def tearDownClass(cls):
        cls.antes.close()
        cls.depois.close()
        cls.pasta.cleanup()

    def test_reaproveitamento_e_candidatos(self):
        triagem = self.depois["Triagem"]
        eixos = self.depois["Eixos de análise"]
        ce = lote.cabecalhos(eixos)
        for codigo, origem in lote.PARES_REAPROVEITADOS.items():
            linha = self.indices[codigo]
            valor = lambda campo: triagem.cell(linha, self.col[campo]).value
            self.assertEqual(valor("Relação com PIBID"), "Tema central do estudo")
            self.assertEqual(valor("Contexto de Goiás"), "Sem evidência de contexto goiano")
            self.assertEqual(valor("Decisão de elegibilidade"), "Pendente")
            self.assertEqual(valor("Duplicidade"), "Não verificada")
            self.assertIn(origem, valor("Fontes das evidências"))
            estados = tuple(r[ce["Estado"] - 1] for r in list(eixos.values)[1:] if r[0] == codigo)
            self.assertEqual(estados, lote.ESTADOS_ESPERADOS[origem])
        auditoria = list(self.depois["Comparação entre fontes"].values)
        self.assertEqual(len(auditoria), 39)
        self.assertEqual(sum(r[3] == "Catálogo CAPES" for r in auditoria[1:]), 36)
        self.assertEqual(sum("não deduplicar" in r[-1] for r in auditoria[1:]), 2)
        self.assertEqual(sum("reaproveitada" in r[-1] for r in auditoria[1:]), 3)

    def test_preservacao_e_integridade(self):
        antes, depois = self.antes["Triagem"], self.depois["Triagem"]
        permitidos = {
            "Relação com PIBID", "Contexto de Goiás", "Decisão de elegibilidade",
            "Evidência do contexto", "Fontes das evidências", "Material consultado",
            "Limitações e pendências", "Observações", "Revisor", "Data da triagem",
        }
        for codigo, numero in self.indices.items():
            for campo, coluna in self.col.items():
                if codigo not in lote.PARES_REAPROVEITADOS or campo not in permitidos:
                    self.assertEqual(antes.cell(numero, coluna).value, depois.cell(numero, coluna).value,
                                     f"{codigo}: {campo}")
        for nome in self.antes.sheetnames:
            if nome not in {"Triagem", "Eixos de análise", "Limites da integração"}:
                self.assertEqual(list(self.antes[nome].values), list(self.depois[nome].values), nome)
            if nome != "Eixos de análise":
                self.assertEqual(str(self.antes[nome].data_validations), str(self.depois[nome].data_validations))
        antigo, novo = self.antes["Eixos de análise"], self.depois["Eixos de análise"]
        self.assertEqual(list(antigo.values), list(novo.values)[:antigo.max_row])
        self.assertEqual(novo.max_row, antigo.max_row + 9)
        self.assertEqual(novo.tables["Eixos"].ref, f"A1:K{novo.max_row}")
        self.assertEqual(novo.tables["Eixos"].autoFilter.ref, novo.tables["Eixos"].ref)
        self.assertEqual(str(novo.data_validations.dataValidation[0].sqref), f"D2:D{novo.max_row}")
        tabela = self.depois["Comparação entre fontes"].tables["ComparacaoEntreFontes"]
        self.assertEqual(tabela.ref, "A1:K39")
        self.assertEqual(tabela.autoFilter.ref, tabela.ref)
        formulas = lambda livro: {(s.title, c.coordinate, c.value) for s in livro
                                  for row in s for c in row if c.data_type == "f"}
        self.assertEqual(formulas(self.antes), formulas(self.depois))
        self.assertEqual(hashlib.sha256(lote.BASE.read_bytes()).hexdigest(), self.hash_antes)
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())

    def test_recusa_sobrescrita_e_divergencias(self):
        with self.assertRaises(FileExistsError):
            lote.integrar(lote.BASE, lote.BRUTO, self.saida)
        for codigo, campo, valor, mensagem in (
            ("417d0d90", "Resumo", "Resumo divergente", "Material ou metadados divergentes"),
            ("417d0d90", "Revisor", "Avaliação anterior", "Estado anterior divergente"),
            ("417d0d90", "Título", "Título divergente", "Títulos divergentes"),
        ):
            with self.subTest(campo=campo), tempfile.TemporaryDirectory() as pasta:
                base, saida = Path(pasta) / "base.xlsx", Path(pasta) / "saida.xlsx"
                livro = load_workbook(lote.BASE)
                livro["Triagem"].cell(self.indices[codigo], self.col[campo]).value = valor
                livro.save(base)
                livro.close()
                with self.assertRaisesRegex(ValueError, mensagem):
                    lote.integrar(base, lote.BRUTO, saida)
                self.assertFalse(saida.exists())


if __name__ == "__main__":
    unittest.main()
