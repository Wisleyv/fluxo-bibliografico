import unittest
from scripts.medir_cobertura_marco1 import (
    classify, metrics, period, FOUND, PENDING, ABSENT, UNKNOWN,
)


class CoverageTests(unittest.TestCase):
    def test_unresolved_is_not_absent_and_confirmed_has_precedence(self):
        self.assertEqual(classify(set(), {'W1'}, True), PENDING)
        self.assertEqual(classify({'W1'}, {'W2'}, True), FOUND)
        self.assertEqual(classify(set(), set(), False), UNKNOWN)
        self.assertEqual(classify(set(), set(), True), ABSENT)

    def test_denominator_excludes_uncertainty_and_handles_empty(self):
        result = metrics([{'categoria': x} for x in [FOUND, ABSENT, PENDING, UNKNOWN]])
        self.assertEqual(result['numerador_confirmado'], 1)
        self.assertEqual(result['denominador_verificavel'], 2)
        self.assertEqual(result['cobertura_verificavel_pct'], 50)
        self.assertEqual(result['confirmado_sobre_total_pct'], 25)
        self.assertEqual(metrics([{'categoria': PENDING}])['cobertura_verificavel_pct'], '')

    def test_period_boundaries(self):
        self.assertEqual(period('2007'), '2007–2019')
        self.assertEqual(period('2020'), '2020–2026')
        self.assertEqual(period('2026'), '2020–2026')
        self.assertEqual(period('2027'), 'fora de 2007–2026')
        self.assertEqual(period(''), 'sem ano')


if __name__ == '__main__':
    unittest.main()
