import unittest

from scripts.preanalise_e_validacao_20261115 import (
    PADRAO_GO,
    criar_formulario,
    distribuir,
    periodo,
    reconstruir_resumo,
    sinal,
)


class PreanaliseTests(unittest.TestCase):
    def test_periodo_preserva_ano_de_defesa_e_data_de_corte(self):
        self.assertEqual(periodo(None, 2024), "Só ano de defesa disponível")
        self.assertEqual(periodo(2019, None), "Publicação fora de 2020–2026")
        self.assertEqual(periodo(2020, None), "Publicação 2020–2026 confirmada")
        self.assertEqual(periodo(2025, None), "Publicação 2020–2026 confirmada")
        self.assertEqual(periodo(2026, None), "Incerto")
        self.assertEqual(periodo(None, None), "Ano ausente")
        with self.assertRaises(ValueError):
            periodo("2024-01", None)

    def test_sinal_geografico_nao_e_decisao(self):
        campos = {"Título": "Escola Norte Goiano em Araguaína", "Resumo": "Goiás", "Outro": "Goiânia"}
        self.assertEqual(sinal(campos, PADRAO_GO), ["Título", "Resumo"])

    def test_resumo_reconstruido_rejeita_lacuna_ou_posicao_repetida(self):
        self.assertEqual(reconstruir_resumo({"ensino": [0, 2], "e": [1]}), "ensino e ensino")
        with self.assertRaises(ValueError):
            reconstruir_resumo({"a": [0], "b": [2]})
        with self.assertRaises(ValueError):
            reconstruir_resumo({"a": [0], "b": [0]})

    def test_alocacao_garante_estratos_e_nao_excede_populacao(self):
        grupos = {"a": list(range(100)), "b": [1, 2], "c": [1]}
        resultado = distribuir(grupos, 8)
        self.assertEqual(resultado, {"a": 6, "b": 1, "c": 1})
        with self.assertRaises(ValueError):
            distribuir(grupos, 2)
        with self.assertRaises(ValueError):
            distribuir(grupos, 104)

    def test_formulario_nao_expoe_decisoes_e_trata_texto_como_texto(self):
        registro = {
            "Código": "abc", "Fonte": "BDTD", "Tipo de produção": "Tese",
            "Título": "=1+1", "Autoria": "Pessoa", "Ano de publicação": None,
            "Ano de defesa": 2024, "Resumo": "Resumo original",
            "Palavras-chave": None, "Instituição associada": None,
            "Afiliações de autoria": None, "DOI": None, "Link da fonte": None,
            "Link OpenAlex": None, "Decisão de elegibilidade": "Incluir",
        }
        aba = criar_formulario([registro], {})["Avaliação independente"]
        self.assertEqual(aba["D2"].value, "=1+1")
        self.assertEqual(aba["D2"].data_type, "s")
        self.assertTrue(all(aba.cell(2, coluna).value is None for coluna in range(16, 29)))


if __name__ == "__main__":
    unittest.main()
