import hashlib
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from scripts import integrar_catalogo_lote4_20261115 as leitura
from scripts import integrar_catalogo_lote5_20261115 as lote


class CatalogoLote5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pasta = tempfile.TemporaryDirectory()
        cls.saida = Path(cls.pasta.name) / "saida.xlsx"
        cls.hash_antes = hashlib.sha256(lote.BASE.read_bytes()).hexdigest()
        lote.integrar(lote.BASE, lote.DECISOES, lote.BRUTO, cls.saida)
        cls.antes = load_workbook(lote.BASE)
        cls.depois = load_workbook(cls.saida)
        cls.col = leitura.cabecalhos(cls.antes["Triagem"])
        cls.indices = leitura.indice_unico(cls.antes["Triagem"], cls.col["Código"], 1317)

    @classmethod
    def tearDownClass(cls):
        cls.antes.close()
        cls.depois.close()
        cls.pasta.cleanup()

    def valor(self, codigo, campo):
        return self.depois["Triagem"].cell(self.indices[codigo], self.col[campo]).value

    def test_decisoes_e_cobertura_do_inventario(self):
        lidos = set()
        nomes = (*leitura.ANTERIORES, "CAPES bilíngue lote 4", "CAPES bilíngue lote 5")
        for nome in nomes:
            for linha in list(self.depois[nome].values)[1:]:
                self.assertNotIn(linha[0], lidos)
                lidos.add(linha[0])
        inventario = {r[0] for r in list(self.depois["Inventário inglês CAPES"].values)[1:]}
        self.assertEqual(len(lidos), 76)
        self.assertEqual(inventario - lidos, set(lote.SEM_RESUMO))
        for codigo in lote.SEM_RESUMO:
            numero = self.indices[codigo]
            self.assertEqual(list(self.antes["Triagem"].values)[numero - 1],
                             list(self.depois["Triagem"].values)[numero - 1])
            self.assertEqual(self.valor(codigo, "Qualidade documental do resumo"), lote.REDUZIDA)
        self.assertEqual(self.valor("763c469e", "Triagem de título e resumo"), "Excluir")
        self.assertIn("reversível", self.valor("763c469e", "Limitações e pendências"))
        self.assertEqual(self.valor("54a94a85", "Relação com PIBID"), "Incerto")
        self.assertIn("dois programas", self.valor("3131a854", "Limitações e pendências"))
        eixo = self.depois["Eixos de análise"]
        ce = leitura.cabecalhos(eixo)
        por_codigo = {}
        for linha in list(eixo.values)[1:]:
            por_codigo.setdefault(linha[ce["Código"] - 1], []).append(linha[ce["Estado"] - 1])
        self.assertNotIn("763c469e", por_codigo)
        self.assertEqual(por_codigo["54a94a85"], ["Não verificável"] * 3)
        self.assertEqual(por_codigo["75588769"], ["Presente"] * 3)

    def test_preservacao_e_integridade(self):
        antigos, atuais = self.antes["Triagem"], self.depois["Triagem"]
        codigos = {x["codigo"] for x in leitura.ler_decisoes(lote.DECISOES, 10)}
        permitidos = {"Relação com PIBID", "Contexto de Goiás", "Decisão de elegibilidade",
                      "Triagem de título e resumo", "Motivo da exclusão", "Evidência do contexto",
                      "Fontes das evidências", "Material consultado", "Limitações e pendências",
                      "Observações", "Revisor", "Data da triagem"}
        for codigo, numero in self.indices.items():
            for campo, coluna in self.col.items():
                if codigo not in codigos or campo not in permitidos:
                    self.assertEqual(antigos.cell(numero, coluna).value, atuais.cell(numero, coluna).value,
                                     f"{codigo}: {campo}")
        for nome in self.antes.sheetnames:
            if nome not in {"Triagem", "Eixos de análise", "Limites da integração"}:
                self.assertEqual(list(self.antes[nome].values), list(self.depois[nome].values), nome)
            if nome != "Eixos de análise":
                self.assertEqual(str(self.antes[nome].data_validations), str(self.depois[nome].data_validations))
        antigo, novo = self.antes["Eixos de análise"], self.depois["Eixos de análise"]
        self.assertEqual(list(antigo.values), list(novo.values)[:antigo.max_row])
        self.assertEqual(novo.max_row, antigo.max_row + 27)
        self.assertEqual(novo.tables["Eixos"].ref, f"A1:K{novo.max_row}")
        self.assertEqual(novo.tables["Eixos"].autoFilter.ref, novo.tables["Eixos"].ref)
        self.assertEqual(str(novo.data_validations.dataValidation[0].sqref), f"D2:D{novo.max_row}")
        tabela = self.depois["CAPES bilíngue lote 5"].tables["CAPESBilingueLote5"]
        self.assertEqual(tabela.ref, "A1:I11")
        self.assertEqual(tabela.autoFilter.ref, tabela.ref)
        formulas = lambda livro: {(s.title, c.coordinate, c.value) for s in livro for row in s for c in row if c.data_type == "f"}
        self.assertEqual(formulas(self.antes), formulas(self.depois))
        self.assertEqual(hashlib.sha256(lote.BASE.read_bytes()).hexdigest(), self.hash_antes)
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())

    def test_recusa_sobrescrita_e_resumo_indisponivel_divergente(self):
        with self.assertRaises(FileExistsError):
            lote.integrar(lote.BASE, lote.DECISOES, lote.BRUTO, self.saida)
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            livro = load_workbook(lote.BASE)
            livro["Triagem"].cell(self.indices["53af6244"], self.col["Resumo"]).value = "Outro conteúdo"
            base, saida = pasta / "base.xlsx", pasta / "saida.xlsx"
            livro.save(base)
            livro.close()
            with self.assertRaisesRegex(ValueError, "Estado do resumo indisponível divergente"):
                lote.integrar(base, lote.DECISOES, lote.BRUTO, saida)
            self.assertFalse(saida.exists())


if __name__ == "__main__":
    unittest.main()
