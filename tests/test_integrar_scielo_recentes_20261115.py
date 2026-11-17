import csv
import hashlib
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from openpyxl import Workbook, load_workbook

from scripts import integrar_scielo_recentes_20261115 as lote


class LoteScieloTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporario = tempfile.TemporaryDirectory()
        cls.saida = Path(cls.temporario.name) / "saida.xlsx"
        cls.hash_antes = hashlib.sha256(lote.BASE.read_bytes()).hexdigest()
        lote.integrar(lote.BASE, lote.DECISOES, lote.PARES, lote.METADADOS, lote.COMPLEMENTO, cls.saida)
        cls.antes = load_workbook(lote.BASE)
        cls.depois = load_workbook(cls.saida)

    @classmethod
    def tearDownClass(cls):
        cls.antes.close()
        cls.depois.close()
        cls.temporario.cleanup()

    def obter(self, codigo, campo):
        aba = self.depois["Triagem"]
        col = lote.cabecalhos(aba)
        indices = lote.indice_unico(aba, col["Código"], 1317)
        return aba.cell(indices[codigo], col[campo]).value

    def test_artigo_de_anapolis_tem_duas_evidencias_distintas(self):
        self.assertEqual(self.obter("910fa3c6", "Contexto de Goiás"), "Pesquisa realizada em Goiás")
        self.assertEqual(self.obter("910fa3c6", "Afiliação em Goiás"), "Sim")
        self.assertEqual(self.obter("910fa3c6", "Triagem de título e resumo"), "Avançar para avaliação")
        self.assertEqual(self.obter("910fa3c6", "Decisão de elegibilidade"), "Pendente")
        self.assertIn("Anápolis", self.obter("910fa3c6", "Evidência do contexto"))
        self.assertIn("Universidade Estadual de Goiás", self.obter("910fa3c6", "Evidência da afiliação"))

    def test_nenhuma_ausencia_de_afiliacao_ou_data_gera_exclusao(self):
        self.assertEqual(self.obter("4264db79", "Publicação em 2020–2026"), "Incerto")
        self.assertEqual(self.obter("cee52e9a", "Publicação em 2020–2026"), "Incerto")
        self.assertEqual(self.obter("cee52e9a", "Triagem de título e resumo"), "Pendente")
        self.assertEqual(self.obter("ec62cd2a", "Afiliação em Goiás"), "Incerto")
        self.assertIn("Universidade Estadual", self.obter("ec62cd2a", "Afiliações de autoria"))

    def test_pares_confirmados_e_grupo_ambiguo_preservado(self):
        self.assertEqual(self.obter("2d5e8833", "Duplicidade"), "Duplicata confirmada")
        self.assertEqual(self.obter("59b0d9e7", "Duplicidade"), "Duplicata confirmada")
        self.assertEqual(self.obter("ca80f876", "Duplicidade"), "Duplicata confirmada")
        self.assertEqual(self.obter("b577aa7f", "Duplicidade"), "Duplicata confirmada")
        self.assertEqual(self.obter("f2e72aea", "Duplicidade"), "Não verificada")
        self.assertIsNone(self.obter("2d5e8833", "Código do registro principal"))

    def test_preserva_entrada_e_conteudos_fora_do_escopo(self):
        self.assertEqual(hashlib.sha256(lote.BASE.read_bytes()).hexdigest(), self.hash_antes)
        antes, depois = self.antes["Triagem"], self.depois["Triagem"]
        col = lote.cabecalhos(antes)
        lidos = {r["codigo"] for r in lote.ler_csv(lote.DECISOES, ["codigo", "pibid", "contexto", "afiliacao", "triagem", "eixos", "evidencia", "limites"], 28)}
        pares = {r[k] for r in lote.ler_csv(lote.PARES, ["codigo_1", "codigo_2"], 23) for k in ("codigo_1", "codigo_2")}
        campos_lote = {col[campo] for campo in (
            "Relação com PIBID", "Contexto de Goiás", "Afiliação em Goiás", "Triagem de título e resumo",
            "Produção acadêmica", "Decisão de elegibilidade", "Afiliações de autoria",
            "Evidência do contexto", "Evidência da afiliação", "Fontes das evidências", "Material consultado",
            "Limitações e pendências", "Observações", "Revisor", "Data da triagem",
        )}
        for numero in range(1, antes.max_row + 1):
            codigo = antes.cell(numero, col["Código"]).value
            for coluna in range(1, antes.max_column + 1):
                if codigo in lidos and coluna in campos_lote:
                    continue
                if codigo in pares and coluna in {col["Duplicidade"], col["Observações"]}:
                    continue
                self.assertEqual(antes.cell(numero, coluna).value, depois.cell(numero, coluna).value, (codigo, coluna))
        for nome in self.antes.sheetnames:
            if nome in {"Triagem", "Eixos de análise", "Limites da integração"}:
                continue
            self.assertEqual(list(self.antes[nome].values), list(self.depois[nome].values), nome)
        originais = list(self.antes["Eixos de análise"].values)
        self.assertEqual(originais, list(self.depois["Eixos de análise"].values)[:len(originais)])

    def test_estrutura_e_integridade(self):
        with ZipFile(self.saida) as arquivo:
            self.assertIsNone(arquivo.testzip())
        eixos = self.depois["Eixos de análise"]
        self.assertEqual(eixos.max_row, self.antes["Eixos de análise"].max_row + 84)
        self.assertEqual(eixos.tables["Eixos"].ref, f"A1:K{eixos.max_row}")
        self.assertEqual(eixos.tables["Eixos"].autoFilter.ref, f"A1:K{eixos.max_row}")
        self.assertEqual(str(eixos.data_validations.dataValidation[0].sqref), f"D2:D{eixos.max_row}")
        self.assertEqual(self.depois["Lote SciELO recente"].max_row, 29)
        self.assertEqual(self.depois["Pares recentes conferidos"].max_row, 24)
        for nome in self.antes.sheetnames:
            if nome == "Eixos de análise":
                continue
            self.assertEqual(str(self.antes[nome].data_validations), str(self.depois[nome].data_validations))
        formulas_antes = {(s.title, c.coordinate, c.value) for s in self.antes for linha in s for c in linha if c.data_type == "f"}
        formulas_depois = {(s.title, c.coordinate, c.value) for s in self.depois for linha in s for c in linha if c.data_type == "f"}
        self.assertEqual(formulas_antes, formulas_depois)

    def test_recusa_avanco_sem_data_confirmada(self):
        with lote.DECISOES.open(encoding="utf-8", newline="") as arquivo:
            leitor = csv.DictReader(arquivo)
            campos, linhas = leitor.fieldnames, list(leitor)
        linha = next(x for x in linhas if x["codigo"] == "4264db79")
        linha.update(contexto="G", triagem="A")
        with tempfile.TemporaryDirectory() as pasta:
            invalido = Path(pasta) / "decisoes.csv"
            with invalido.open("w", encoding="utf-8", newline="") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=campos)
                escritor.writeheader()
                escritor.writerows(linhas)
            with self.assertRaisesRegex(ValueError, "Avanço sem requisitos"):
                lote.integrar(lote.BASE, invalido, lote.PARES, lote.METADADOS, lote.COMPLEMENTO, Path(pasta) / "saida.xlsx")

    def test_recusa_grupo_maior(self):
        with lote.PARES.open(encoding="utf-8", newline="") as arquivo:
            linhas = list(csv.DictReader(arquivo))
        linhas[0] = {"codigo_1": "f2e72aea", "codigo_2": "14bf350a"}
        with tempfile.TemporaryDirectory() as pasta:
            invalido = Path(pasta) / "pares.csv"
            with invalido.open("w", encoding="utf-8", newline="") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=["codigo_1", "codigo_2"])
                escritor.writeheader()
                escritor.writerows(linhas)
            with self.assertRaisesRegex(ValueError, "Grupo maior"):
                lote.integrar(lote.BASE, lote.DECISOES, invalido, lote.METADADOS, lote.COMPLEMENTO, Path(pasta) / "saida.xlsx")

    def test_recusa_identificador_composto_sem_handle(self):
        aba = Workbook().active
        aba.append(list(lote.IDENTIDADE))
        valores = ["Título", "Autoria", "Tese", 2023, "Instituição",
                   "Referência||https://repositorio.example/pagina||https://doi.org/10.1/teste"]
        aba.append(valores)
        aba.append(valores)
        with self.assertRaisesRegex(ValueError, "Identificadores compostos inválidos"):
            lote.validar_par_com_identificador(aba, lote.cabecalhos(aba), 2, 3, "a", "b")

    def test_nao_sobrescreve(self):
        with self.assertRaises(FileExistsError):
            lote.integrar(lote.BASE, lote.DECISOES, lote.PARES, lote.METADADOS, lote.COMPLEMENTO, self.saida)


if __name__ == "__main__":
    unittest.main()
