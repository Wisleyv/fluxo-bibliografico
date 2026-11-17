import json
import tempfile
import unittest
from pathlib import Path
from scripts.produzir_indicadores_marco4 import run_paths, ROOT
from scripts.recalcular_cobertura_capes_20261116 import classify, coverage, period, SAME, REVIEW, MISSING, UNVERIFIABLE


class IntegrationIndicatorTests(unittest.TestCase):
    def row(self,year='2025',candidate=''):
        return {'ano_publicacao_ris':year,'obras_candidatas':candidate}

    def test_nominal_id_does_not_resolve_conflicting_identity(self):
        self.assertEqual(classify(self.row(candidate='old-work'),False,True),REVIEW)

    def test_alias_can_link_work_even_without_same_nominal_id(self):
        self.assertEqual(classify(self.row(),True,True),SAME)

    def test_control_without_openalex_is_not_confirmed_overlap(self):
        self.assertEqual(classify(self.row(),True,False),MISSING)

    def test_2026_without_verified_date_is_not_counted_as_absence(self):
        self.assertEqual(classify(self.row(year='2026'),False,False),UNVERIFIABLE)
        self.assertEqual(classify(self.row(year='2026'),True,False),UNVERIFIABLE)

    def test_review_and_unknown_are_excluded_from_denominator(self):
        r=coverage([{'classe_cobertura':c} for c in [SAME,SAME,REVIEW,MISSING,UNVERIFIABLE]])
        self.assertEqual(r['denominador_verificavel'],3)
        self.assertAlmostEqual(r['fracao_confirmada_verificavel_pct'],200/3)

    def test_no_verifiable_records_has_no_fabricated_percentage(self):
        self.assertEqual(coverage([{'classe_cobertura':REVIEW}])['fracao_confirmada_verificavel_pct'],'')

    def test_year_disagreement_within_period_does_not_double_count(self):
        self.assertEqual(period('2011;2012'),'2007–2019')
        self.assertEqual(period('2022;2025'),'2020–2026')
        self.assertEqual(period('2019;2020'),'período divergente/não informado')

    def manifest(self,target):
        f=tempfile.NamedTemporaryFile(mode='w',encoding='utf8',suffix='.json',delete=False)
        json.dump({'diretorio_nacional':'dados/analises/integracao_capes_20261116/elegibilidade',
                   'diretorio_regional':'dados/analises/integracao_capes_20261116/elegibilidade',
                   'diretorio_indicadores_proposto':target},f)
        f.close();self.addCleanup(Path(f.name).unlink);return f.name

    def test_manifest_does_not_overwrite_historical_indicators(self):
        with self.assertRaises(AssertionError):run_paths(self.manifest('dados/analises/marco4'))

    def test_manifest_does_not_overwrite_corpus_inputs(self):
        with self.assertRaises(AssertionError):run_paths(self.manifest('dados/analises/integracao_capes_20261116/elegibilidade'))

    def test_manifest_keeps_output_in_the_project(self):
        _,_,paths=run_paths(self.manifest('dados/analises/integracao_capes_20261116/indicadores'))
        self.assertTrue(paths['diretorio_indicadores_proposto'].is_relative_to(ROOT.resolve()))


if __name__=='__main__':unittest.main()
