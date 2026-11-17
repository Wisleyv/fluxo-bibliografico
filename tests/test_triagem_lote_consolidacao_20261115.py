import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from scripts import triagem_lote_consolidacao_20261115 as lote


class TriagemLoteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pasta = tempfile.TemporaryDirectory()
        cls.saida = Path(cls.pasta.name) / "saida.xlsx"
        lote.integrar(lote.BASE, lote.BRUTO, lote.UNB, cls.saida)
        cls.antes = load_workbook(lote.BASE)
        cls.depois = load_workbook(cls.saida)
        cls.col = lote.cabecalhos(cls.antes["Triagem"])
        cls.indices = lote.indice_unico(cls.antes["Triagem"], cls.col["Código"], 1317)

    @classmethod
    def tearDownClass(cls):
        cls.antes.close()
        cls.depois.close()
        cls.pasta.cleanup()

    def valor(self, codigo, campo):
        return self.depois["Triagem"].cell(self.indices[codigo], self.col[campo]).value

    def test_decisoes_e_data(self):
        audit = list(self.depois["Priorização lote"].values)
        self.assertEqual(len(audit), 1197)
        novas = {r[0] for r in audit[1:] if r[3] == "Excluir"}
        self.assertEqual(len(novas), 89)
        for codigo in lote.ADICIONAIS:
            self.assertIn(codigo, novas)
            self.assertEqual(self.valor(codigo, "Relação com PIBID"), "Menção incidental")
            self.assertEqual(self.valor(codigo, "Motivo da exclusão"), "Sem relação substantiva com PIBID")
        for codigo in lote.PAR_UNB:
            self.assertIsNone(self.valor(codigo, "Ano de publicação"))
            self.assertEqual(self.valor(codigo, "Publicação em 2020–2026"), "Incerto")
            self.assertEqual(self.valor(codigo, "Triagem de título e resumo"), "Pendente")
            self.assertIsNone(self.valor(codigo, "Motivo da exclusão"))
            self.assertEqual(self.valor(codigo, "Decisão de elegibilidade"), "Pendente")
        self.assertEqual(self.valor("95dee571", "Decisão de elegibilidade"), "Incluir")
        self.assertEqual(
            lote.categoria("Só ano de defesa disponível", "Incerto", "Incerto", "Incerto", "Pendente", "Pendente"),
            "Período e vínculo GO não estabelecidos",
        )

    def test_preservacao_e_integridade(self):
        antes, depois = self.antes["Triagem"], self.depois["Triagem"]
        audit = list(self.depois["Priorização lote"].values)[1:]
        novos = {r[0] for r in audit if r[3] == "Excluir"}
        comuns = {"Decisão de elegibilidade", "Limitações e pendências", "Observações"}
        adicionais = {"Relação com PIBID", "Triagem de título e resumo", "Motivo da exclusão",
                      "Fontes das evidências", "Material consultado", "Revisor", "Data da triagem"}
        temporal = {"Ano de publicação", "Publicação em 2020–2026", "Triagem de título e resumo",
                    "Motivo da exclusão", "Limitações e pendências", "Observações"}
        for codigo, numero in self.indices.items():
            permitidos = (comuns if codigo in novos else set()).copy()
            if codigo in lote.ADICIONAIS:
                permitidos |= adicionais
            if codigo in lote.PAR_UNB:
                permitidos |= temporal
            for campo, coluna in self.col.items():
                if campo not in permitidos:
                    self.assertEqual(antes.cell(numero, coluna).value, depois.cell(numero, coluna).value,
                                     f"{codigo}: {campo}")
        for nome in self.antes.sheetnames:
            if nome not in {"Triagem", "Limites da integração"}:
                self.assertEqual(list(self.antes[nome].values), list(self.depois[nome].values), nome)
            self.assertEqual(str(self.antes[nome].data_validations), str(self.depois[nome].data_validations))
        tabela = self.depois["Priorização lote"].tables["PriorizacaoLote"]
        self.assertEqual(tabela.ref, "A1:K1197")
        self.assertEqual(tabela.autoFilter.ref, tabela.ref)
        formulas = lambda livro: {(s.title, c.coordinate, c.value) for s in livro
                                  for row in s for c in row if c.data_type == "f"}
        self.assertEqual(formulas(self.antes), formulas(self.depois))
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())

    def test_recusa_sobrescrita_e_conflito(self):
        with self.assertRaises(FileExistsError):
            lote.integrar(lote.BASE, lote.BRUTO, lote.UNB, self.saida)
        with tempfile.TemporaryDirectory() as pasta:
            base, saida = Path(pasta) / "base.xlsx", Path(pasta) / "saida.xlsx"
            livro = load_workbook(lote.BASE)
            livro["Triagem"].cell(self.indices["6af837ea"], self.col["Resumo"]).value = "Conteúdo divergente"
            livro.save(base)
            livro.close()
            with self.assertRaises(ValueError):
                lote.integrar(base, lote.BRUTO, lote.UNB, saida)
            self.assertFalse(saida.exists())


if __name__ == "__main__":
    unittest.main()
