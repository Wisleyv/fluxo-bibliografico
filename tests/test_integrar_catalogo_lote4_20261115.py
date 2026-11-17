import csv
import hashlib
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from scripts import integrar_catalogo_lote4_20261115 as lote


class CatalogoLote4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pasta = tempfile.TemporaryDirectory()
        cls.saida = Path(cls.pasta.name) / "saida.xlsx"
        cls.hash_antes = hashlib.sha256(lote.BASE.read_bytes()).hexdigest()
        lote.integrar(lote.BASE, lote.DECISOES, lote.BRUTO, cls.saida)
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

    def test_decisoes_e_eixos(self):
        for codigo in ("1235abfa", "613e44cb", "335fb704", "e7ac9998", "602efe78", "4a91a186"):
            self.assertEqual(self.valor(codigo, "Relação com PIBID"), "Incerto")
            self.assertEqual(self.valor(codigo, "Triagem de título e resumo"), "Pendente")
        self.assertEqual(self.valor("4528a40d", "Relação com PIBID"), "Menção incidental")
        self.assertEqual(self.valor("4528a40d", "Triagem de título e resumo"), "Excluir")
        self.assertEqual(self.valor("4528a40d", "Motivo da exclusão"), "Sem relação substantiva com PIBID")
        self.assertIn("reversível", self.valor("4528a40d", "Limitações e pendências"))
        self.assertIn("não comprova participação de comunidades", self.valor("159d6d08", "Limitações e pendências"))
        eixo = self.depois["Eixos de análise"]
        ce = lote.cabecalhos(eixo)
        por_codigo = {}
        for linha in list(eixo.values)[1:]:
            por_codigo.setdefault(linha[ce["Código"] - 1], []).append(linha[ce["Estado"] - 1])
        self.assertNotIn("4528a40d", por_codigo)
        self.assertEqual(por_codigo["335fb704"], ["Não verificável"] * 3)
        self.assertEqual(por_codigo["bf965aec"], ["Presente", "Não informado", "Presente"])
        self.assertEqual(por_codigo["55972834"], ["Não informado"] * 3)
        for item in lote.ler_decisoes(lote.DECISOES):
            codigo = item["codigo"]
            self.assertEqual(self.valor(codigo, "Decisão de elegibilidade"), "Pendente")
            self.assertEqual(self.valor(codigo, "Afiliação em Goiás"), "Incerto")
            self.assertIsNone(self.valor(codigo, "Ano de publicação"))

    def test_preservacao_e_integridade(self):
        antes, depois = self.antes["Triagem"], self.depois["Triagem"]
        codigos = {x["codigo"] for x in lote.ler_decisoes(lote.DECISOES)}
        permitidos = {"Relação com PIBID", "Contexto de Goiás", "Decisão de elegibilidade",
                      "Triagem de título e resumo", "Motivo da exclusão", "Evidência do contexto",
                      "Fontes das evidências", "Material consultado", "Limitações e pendências",
                      "Observações", "Revisor", "Data da triagem"}
        for codigo, numero in self.indices.items():
            for campo, coluna in self.col.items():
                if codigo not in codigos or campo not in permitidos:
                    self.assertEqual(antes.cell(numero, coluna).value, depois.cell(numero, coluna).value,
                                     f"{codigo}: {campo}")
        for nome in self.antes.sheetnames:
            if nome not in {"Triagem", "Eixos de análise", "Limites da integração"}:
                self.assertEqual(list(self.antes[nome].values), list(self.depois[nome].values), nome)
            if nome != "Eixos de análise":
                self.assertEqual(str(self.antes[nome].data_validations), str(self.depois[nome].data_validations))
        antigo, novo = self.antes["Eixos de análise"], self.depois["Eixos de análise"]
        self.assertEqual(list(antigo.values), list(novo.values)[:antigo.max_row])
        self.assertEqual(novo.max_row, antigo.max_row + 51)
        self.assertEqual(novo.tables["Eixos"].ref, f"A1:K{novo.max_row}")
        self.assertEqual(novo.tables["Eixos"].autoFilter.ref, novo.tables["Eixos"].ref)
        self.assertEqual(str(novo.data_validations.dataValidation[0].sqref), f"D2:D{novo.max_row}")
        tabela = self.depois[lote.ABA].tables["CAPESBilingueLote4"]
        self.assertEqual(tabela.ref, "A1:I19")
        self.assertEqual(tabela.autoFilter.ref, tabela.ref)
        formulas = lambda livro: {(s.title, c.coordinate, c.value) for s in livro for row in s for c in row if c.data_type == "f"}
        self.assertEqual(formulas(self.antes), formulas(self.depois))
        self.assertEqual(hashlib.sha256(lote.BASE.read_bytes()).hexdigest(), self.hash_antes)
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())

    def test_recusa_sobrescrita_selecao_e_estado_divergente(self):
        with self.assertRaises(FileExistsError):
            lote.integrar(lote.BASE, lote.DECISOES, lote.BRUTO, self.saida)
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            livro = load_workbook(lote.BASE)
            livro["Triagem"].cell(self.indices["85898bee"], self.col["Revisor"]).value = "Avaliação anterior"
            base, saida = pasta / "base.xlsx", pasta / "saida.xlsx"
            livro.save(base)
            livro.close()
            with self.assertRaisesRegex(ValueError, "Estado anterior"):
                lote.integrar(base, lote.DECISOES, lote.BRUTO, saida)
            self.assertFalse(saida.exists())
            itens = lote.ler_decisoes(lote.DECISOES)
            itens[0], itens[1] = itens[1], itens[0]
            alterado = pasta / "decisoes.csv"
            with alterado.open("w", encoding="utf-8", newline="") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=itens[0].keys())
                escritor.writeheader()
                escritor.writerows(itens)
            with self.assertRaisesRegex(ValueError, "Seleção ou histórico"):
                lote.integrar(lote.BASE, alterado, lote.BRUTO, saida)
            self.assertFalse(saida.exists())


if __name__ == "__main__":
    unittest.main()
