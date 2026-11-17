import csv
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from openpyxl import load_workbook

from scripts import consolidar_portal_prioritario_20261115 as lote


class ConsolidarPortalPrioritarioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pasta = tempfile.TemporaryDirectory()
        cls.saida = Path(cls.pasta.name) / "saida.xlsx"
        lote.integrar(lote.BASE, lote.CAMPOS, lote.EXTRACOES, lote.METADADOS, lote.BRUTOS, cls.saida)
        cls.antes = load_workbook(lote.BASE)
        cls.depois = load_workbook(cls.saida)

    @classmethod
    def tearDownClass(cls):
        cls.antes.close()
        cls.depois.close()
        cls.pasta.cleanup()

    def test_decisoes_e_eixos(self):
        triagem = self.depois["Triagem"]
        ct = lote.cabecalhos(triagem)
        registros = {r[ct["Código"] - 1]: r for r in list(triagem.values)[1:]}
        self.assertEqual(Counter(r[ct["Decisão de elegibilidade"] - 1] for r in registros.values()),
                         {"Incluir": 19, "Excluir": 199, "Pendente": 247, "Não iniciada": 852})
        for codigo in set(lote.RESUMOS) - set(lote.INCERTOS):
            linha = registros[codigo]
            self.assertEqual(linha[ct["Decisão de elegibilidade"] - 1], "Incluir")
            self.assertEqual(linha[ct["Duplicidade"] - 1], "Não verificada")
            self.assertIn("não comprova o conteúdo exibido no corte", linha[ct["Limitações e pendências"] - 1])
        for codigo in lote.INCERTOS:
            linha = registros[codigo]
            self.assertEqual(linha[ct["Decisão de elegibilidade"] - 1], "Pendente")
            self.assertIn("Incerteza temática", linha[ct["Limitações e pendências"] - 1])
        self.assertIn("dd5b9244", registros["4a213f79"][ct["Limitações e pendências"] - 1])
        incluidos = {c for c, r in registros.items() if r[ct["Decisão de elegibilidade"] - 1] == "Incluir"}
        eixos = self.depois["Eixos de análise"]
        ce = lote.cabecalhos(eixos)
        estados = Counter(r[ce["Estado"] - 1] for r in list(eixos.values)[1:]
                          if r[ce["Código"] - 1] in incluidos)
        self.assertEqual(estados, {"Presente": 23, "Não informado": 23, "Não verificável": 11})
        self.assertEqual(self.depois["Portal prioritário"].max_row, 11)

    def test_preservacao_e_integridade(self):
        ct = lote.cabecalhos(self.antes["Triagem"])
        for antes, depois in zip(list(self.antes["Triagem"].values)[1:],
                                 list(self.depois["Triagem"].values)[1:]):
            codigo = antes[ct["Código"] - 1]
            for campo, numero in ct.items():
                if codigo in lote.RESUMOS and campo == "Limitações e pendências":
                    continue
                if codigo in set(lote.RESUMOS) - set(lote.INCERTOS) and campo == "Decisão de elegibilidade":
                    continue
                self.assertEqual(antes[numero - 1], depois[numero - 1], (codigo, campo))
        ce = lote.cabecalhos(self.antes["Eixos de análise"])
        chaves = {(item["codigo"], lote.EIXOS_CODIGO[item["eixo"]])
                  for item in lote.ler_extracoes(lote.EXTRACOES)}
        for antes, depois in zip(list(self.antes["Eixos de análise"].values)[1:],
                                 list(self.depois["Eixos de análise"].values)[1:]):
            chave = (antes[ce["Código"] - 1], antes[ce["Eixo"] - 1])
            if chave not in chaves:
                self.assertEqual(antes, depois, chave)
            else:
                self.assertEqual(antes[:3], depois[:3], chave)
                self.assertIn("não independente", depois[ce["Limites da evidência"] - 1])
        for nome in self.antes.sheetnames:
            a, d = self.antes[nome], self.depois[nome]
            if nome not in {"Triagem", "Eixos de análise", "Limites da integração"}:
                self.assertEqual(list(a.values), list(d.values), nome)
            self.assertEqual(str(a.data_validations), str(d.data_validations), nome)
            self.assertEqual({t.name: (t.ref, t.autoFilter.ref if t.autoFilter else None) for t in a.tables.values()},
                             {t.name: (t.ref, t.autoFilter.ref if t.autoFilter else None) for t in d.tables.values()}, nome)
        formulas = lambda livro: {(s.title, c.coordinate, c.value) for s in livro
                                  for row in s for c in row if c.data_type == "f"}
        self.assertEqual(formulas(self.antes), formulas(self.depois))
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())

    def test_recusa_sobrescrita_e_conflitos(self):
        with self.assertRaises(FileExistsError):
            lote.integrar(lote.BASE, lote.CAMPOS, lote.EXTRACOES, lote.METADADOS, lote.BRUTOS, self.saida)
        with tempfile.TemporaryDirectory() as pasta:
            pasta = Path(pasta)
            itens = lote.ler_extracoes(lote.EXTRACOES)
            itens[0]["trecho"] = "trecho inexistente no resumo"
            csv_alterado = pasta / "extracoes.csv"
            with csv_alterado.open("w", encoding="utf-8", newline="") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=itens[0].keys())
                escritor.writeheader()
                escritor.writerows(itens)
            saida = pasta / "saida.xlsx"
            with self.assertRaisesRegex(ValueError, "Trecho não localizado"):
                lote.integrar(lote.BASE, lote.CAMPOS, csv_alterado, lote.METADADOS, lote.BRUTOS, saida)
            self.assertFalse(saida.exists())

            livro = load_workbook(lote.BASE)
            triagem = livro["Triagem"]
            ct = lote.cabecalhos(triagem)
            numero = next(n for n in range(2, triagem.max_row + 1)
                          if triagem.cell(n, ct["Código"]).value == "05cbfe1e")
            triagem.cell(numero, ct["Decisão de elegibilidade"]).value = "Excluir"
            base = pasta / "base.xlsx"
            livro.save(base)
            livro.close()
            with self.assertRaisesRegex(ValueError, "Estado ou resumo divergente"):
                lote.integrar(base, lote.CAMPOS, lote.EXTRACOES, lote.METADADOS, lote.BRUTOS, saida)
            self.assertFalse(saida.exists())


if __name__ == "__main__":
    unittest.main()
