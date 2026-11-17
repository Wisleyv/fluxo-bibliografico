import unittest
from scripts.executar_marco3 import period, institution_signal
from scripts.fechar_marco3 import quote_for


class RegionalRulesTests(unittest.TestCase):
    def test_old_defense_alone_cannot_exclude_unknown_publication(self):
        self.assertEqual(period(set(), set(), {'2015'}, True)[0], 'Incerto')

    def test_alternative_defense_does_not_replace_publication(self):
        self.assertEqual(period({'2019'}, set(), {'2021'}, True)[0], 'Sim')
        self.assertEqual(period({'2019'}, set(), set(), False)[0], 'Não')

    def test_two_old_dates_support_exclusion(self):
        self.assertEqual(period({'2019'}, set(), {'2018'}, True)[0], 'Não')

    def test_cutoff_and_incomplete_year(self):
        self.assertEqual(period({'2026'}, {'2026-11-08'}, set(), False)[0], 'Sim')
        self.assertEqual(period({'2026'}, {'2026-11-09'}, set(), False)[0], 'Incerto')
        self.assertEqual(period({'2026'}, set(), set(), False)[0], 'Incerto')

    def test_geographic_name_is_not_institutional_affiliation(self):
        self.assertFalse(institution_signal('Escola Norte Goiano, Araguaína, Tocantins'))
        self.assertTrue(institution_signal('Instituto Federal de Educação, Ciência e Tecnologia de Goiás'))

    def test_evidence_locator_returns_exact_archived_span(self):
        abstract='Objetivo geral. Os resultados indicam aprendizagem da docência no PIBID.'
        hit=quote_for([{'resumo':abstract,'registro':'local','raw_file':'arquivo'}], 0)
        self.assertIsNotNone(hit)
        self.assertEqual(abstract[hit[4]:hit[5]].strip(), hit[2])
        self.assertIsNone(quote_for([{'resumo':'','registro':'local','raw_file':'arquivo'}], 0))


if __name__=='__main__':
    unittest.main()
