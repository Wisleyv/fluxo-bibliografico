import unittest

from scripts.conferir_identidades_openalex_20261115 import SAME, REVIEW, TITLE_ONLY, assess


class IdentityTest(unittest.TestCase):
    def setUp(self):
        self.base = {
            "Código": "1", "Fonte": "SciELO", "DOI": "10.1/abc",
            "Link OpenAlex": "", "Título": "Formação docente", "Ano de publicação": "2021",
            "Tipo de produção": "Artigo", "Autoria": "Silva, Ana | Souza, Maria",
        }
        self.work = {
            "openalex_id": "https://openalex.org/W1", "doi": "https://doi.org/10.1/ABC",
            "titulo": "Formacao docente", "data_publicacao": "2021-08-01",
            "tipo": "article", "autores": "Ana Silva; Maria Souza",
        }

    def test_exact_doi_and_compatible_bibliography(self):
        self.assertEqual(assess(self.base, self.work)["classificacao"], SAME)

    def test_disagreement_and_missing_data_do_not_confirm(self):
        for field, value in (("autores", "Ana Souza; Maria Silva"), ("autores", ""),
                             ("data_publicacao", "2020-01-01"), ("tipo", "dissertation")):
            with self.subTest(field=field, value=value):
                work = {**self.work, field: value}
                self.assertEqual(assess(self.base, work)["classificacao"], REVIEW)
        work = {**self.work, "doi": ""}
        self.assertEqual(assess(self.base, work)["classificacao"], TITLE_ONLY)


if __name__ == "__main__":
    unittest.main()
