import hashlib
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from scripts import integrar_pares_pendentes_20261115 as lote


class ParesPendentesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporario = tempfile.TemporaryDirectory()
        cls.saida = Path(cls.temporario.name) / "saida.xlsx"
        cls.hash_antes = hashlib.sha256(lote.BASE.read_bytes()).hexdigest()
        lote.integrar(lote.BASE, lote.DECISOES, cls.saida)
        cls.antes = load_workbook(lote.BASE)
        cls.depois = load_workbook(cls.saida)
        cls.col = lote.cabecalhos(cls.depois["Triagem"])
        cls.indices = lote.indice_unico(cls.depois["Triagem"], cls.col["Código"], 1317)

    @classmethod
    def tearDownClass(cls):
        cls.antes.close()
        cls.depois.close()
        cls.temporario.cleanup()

    def obter(self, codigo, campo):
        return self.depois["Triagem"].cell(self.indices[codigo], self.col[campo]).value

    def test_leitura_nao_equivale_a_exclusao_ou_elegibilidade_final(self):
        for codigo in ("0cb51afe", "1db64a11", "64235f11", "9b8e6ce0", "8d98ed7d", "2bc47990"):
            self.assertEqual(self.obter(codigo, "Relação com PIBID"), "Tema central do estudo")
        for codigo in ("a3e7321c", "69c845eb", "c71706a2", "9a81aa29"):
            self.assertEqual(self.obter(codigo, "Relação com PIBID"), "Incerto")
        for codigo in ("0cb51afe", "1db64a11", "a3e7321c", "69c845eb", "c71706a2", "9a81aa29"):
            self.assertEqual(self.obter(codigo, "Triagem de título e resumo"), "Pendente")
            self.assertEqual(self.obter(codigo, "Decisão de elegibilidade"), "Pendente")
            self.assertIsNone(self.obter(codigo, "Ano de publicação"))
        self.assertEqual(self.obter("a3e7321c", "Contexto de Goiás"), "Incerto")
        self.assertEqual(self.obter("c71706a2", "Contexto de Goiás"), "Sem evidência de contexto goiano")
        self.assertIn("não se atribuem essas trajetórias ao programa", self.obter("c71706a2", "Limitações e pendências"))

    def test_eixos_refletem_evidencia_e_incerteza(self):
        aba = self.depois["Eixos de análise"]
        col = lote.cabecalhos(aba)
        estados = {}
        for linha in aba.iter_rows(min_row=2, values_only=True):
            estados[(linha[col["Código"] - 1], linha[col["Eixo"] - 1])] = linha[col["Estado"] - 1]
        nomes = list(lote.EIXOS.values())
        for codigo, esperado in (("0cb51afe", ["Não verificável", "Presente", "Não informado"]),
                                 ("8d98ed7d", ["Presente", "Presente", "Presente"]),
                                 ("c71706a2", ["Não verificável"] * 3)):
            self.assertEqual([estados[(codigo, eixo)] for eixo in nomes], esperado)

    def test_rejeita_material_diferente_e_registro_ja_revisado(self):
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            for campo, valor in (("Resumo", "Diferente"), ("Palavras-chave", "Diferente"),
                                 ("Revisor", "Revisão anterior")):
                livro = load_workbook(lote.BASE)
                aba = livro["Triagem"]
                aba.cell(self.indices["1db64a11"], self.col[campo]).value = valor
                base = pasta / f"{campo}.xlsx"
                saida = pasta / f"saida-{campo}.xlsx"
                livro.save(base)
                livro.close()
                with self.assertRaises(ValueError):
                    lote.integrar(base, lote.DECISOES, saida)
                self.assertFalse(saida.exists())

    def test_preserva_entrada_e_conteudo_fora_do_lote(self):
        self.assertEqual(hashlib.sha256(lote.BASE.read_bytes()).hexdigest(), self.hash_antes)
        antes, depois = self.antes["Triagem"], self.depois["Triagem"]
        codigos = {r[0] for r in list(self.depois["Pares pendentes lidos"].values)[1:]}
        self.assertEqual(len(codigos), 38)
        campos = {self.col[nome] for nome in (
            "Relação com PIBID", "Contexto de Goiás", "Decisão de elegibilidade", "Evidência do contexto",
            "Fontes das evidências", "Material consultado", "Limitações e pendências",
            "Observações", "Revisor", "Data da triagem",
        )}
        for numero in range(1, antes.max_row + 1):
            codigo = antes.cell(numero, self.col["Código"]).value
            for coluna in range(1, antes.max_column + 1):
                if codigo in codigos and coluna in campos:
                    continue
                self.assertEqual(antes.cell(numero, coluna).value, depois.cell(numero, coluna).value, (codigo, coluna))
        for nome in self.antes.sheetnames:
            if nome not in {"Triagem", "Eixos de análise", "Limites da integração"}:
                self.assertEqual(list(self.antes[nome].values), list(self.depois[nome].values), nome)
        anteriores = list(self.antes["Eixos de análise"].values)
        self.assertEqual(anteriores, list(self.depois["Eixos de análise"].values)[:len(anteriores)])

    def test_estrutura_e_integridade(self):
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())
        self.assertEqual(self.depois["Pares pendentes lidos"].max_row, 39)
        eixos = self.depois["Eixos de análise"]
        self.assertEqual(eixos.max_row, self.antes["Eixos de análise"].max_row + 114)
        self.assertEqual(eixos.tables["Eixos"].ref, f"A1:K{eixos.max_row}")
        self.assertEqual(eixos.tables["Eixos"].autoFilter.ref, f"A1:K{eixos.max_row}")
        self.assertEqual(str(eixos.data_validations.dataValidation[0].sqref), f"D2:D{eixos.max_row}")
        for nome in self.antes.sheetnames:
            if nome != "Eixos de análise":
                self.assertEqual(str(self.antes[nome].data_validations), str(self.depois[nome].data_validations))
        formulas_antes = {(s.title, c.coordinate, c.value) for s in self.antes for linha in s for c in linha if c.data_type == "f"}
        formulas_depois = {(s.title, c.coordinate, c.value) for s in self.depois for linha in s for c in linha if c.data_type == "f"}
        self.assertEqual(formulas_antes, formulas_depois)

    def test_nao_sobrescreve(self):
        with self.assertRaises(FileExistsError):
            lote.integrar(lote.BASE, lote.DECISOES, self.saida)


if __name__ == "__main__":
    unittest.main()
