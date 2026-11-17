import unittest

from scripts.priorizar_openalex_goias_20261115 import publication_band


class PublicationBandTest(unittest.TestCase):
    def test_bands_do_not_claim_eligibility(self):
        self.assertEqual(publication_band("2020-01-01"), "2020–2025")
        self.assertEqual(publication_band("2025-12-31"), "2020–2025")
        self.assertIn("não comprovada", publication_band("2026-01-01"))
        self.assertIn("não excluir", publication_band("2019-12-31"))


if __name__ == "__main__":
    unittest.main()
