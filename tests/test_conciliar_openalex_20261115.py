import unittest

from scripts.conciliar_openalex_20261115 import find_pairs, make_signals


class ConciliationTest(unittest.TestCase):
    def test_candidate_evidence_and_different_document_types_are_preserved(self):
        work = {
            "openalex_id": "https://openalex.org/W1", "titulo": "Formação docente no PIBID",
            "tipo": "article", "data_publicacao": "2021-01-01",
            "doi": "https://doi.org/10.1234/abc",
        }
        base = [
            {"Código": "a", "Fonte": "SciELO", "DOI": "10.1234/ABC",
             "Título": "Formacao docente no PIBID", "Link OpenAlex": "",
             "Tipo de produção": "Artigo", "Ano de publicação": "2021", "Ano de defesa": ""},
            {"Código": "b", "Fonte": "BDTD", "DOI": "", "Título": "Formação docente no PIBID",
             "Link OpenAlex": "", "Tipo de produção": "Tese",
             "Ano de publicação": "", "Ano de defesa": "2020"},
            {"Código": "c", "Fonte": "BDTD", "DOI": "", "Título": "Outro",
             "Link OpenAlex": "", "Tipo de produção": "Tese",
             "Ano de publicação": "", "Ano de defesa": ""},
        ]
        pairs = find_pairs([work], base)
        self.assertEqual([p["codigo_base"] for p in pairs], ["a", "b"])
        self.assertEqual(pairs[0]["sinais_correspondencia"], "doi; titulo")
        self.assertEqual(pairs[1]["sinais_correspondencia"], "titulo")
        self.assertEqual(pairs[1]["tipo_base"], "Tese")
        self.assertEqual(pairs[1]["tipo_openalex"], "article")

    def test_geographical_signal_is_not_an_exclusion(self):
        work = {
            "openalex_id": "W", "titulo": "PIBID no Brasil", "resumo": "",
            "palavras_chave": "", "instituicoes": "", "tipo": "article",
            "data_publicacao": "2022-01-01", "doi": "", "pagina_origem": "pagina_0001.json",
        }
        signal = make_signals(work, 0)
        self.assertEqual(signal["sinais_pibid_campos"], "título")
        self.assertEqual(signal["sinais_goias_texto_campos"], "")
        self.assertEqual(signal["sinal_goias_instituicoes"], "")


if __name__ == "__main__":
    unittest.main()
