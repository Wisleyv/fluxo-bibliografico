import unittest
from scripts.produzir_indicadores_marco4 import documentary_type, valid_author, affiliation_state, author_key


class IndicatorRulesTests(unittest.TestCase):
    def test_translated_type_labels_do_not_double_count(self):
        self.assertEqual(documentary_type('Artigo;article'),'artigo')
        self.assertEqual(documentary_type('Tese;dissertation'),'tese')
        self.assertEqual(documentary_type('Dissertação;dissertation'),'dissertação')

    def test_unspecified_degree_is_not_invented(self):
        self.assertEqual(documentary_type('dissertation'),'tese/dissertação sem grau discriminado')

    def test_different_documentary_types_remain_visible(self):
        self.assertEqual(documentary_type('article;book-chapter'),'artigo; capítulo')

    def test_institution_label_does_not_become_person(self):
        self.assertFalse(valid_author('Universidade Federal de Goiás'))
        self.assertTrue(valid_author('Maria de Souza'))

    def test_affiliation_absence_does_not_become_non_goias(self):
        self.assertEqual(affiliation_state([{'institutions':[]}]),'desconhecida')
        self.assertEqual(affiliation_state([{'institutions':[{'id':'I1'}]},{}]),'parcial')
        self.assertEqual(affiliation_state([{'raw_affiliation_strings':['Instituição sem ID']}]),'parcial')

    def test_known_affiliation_requires_all_authors_mapped(self):
        self.assertEqual(affiliation_state([{'institutions':[{'id':'I1'}]}]),'conhecida')
        self.assertEqual(affiliation_state([{'institutions':[{'id':'I1'}]}],flagged=True),'parcial')

    def test_unique_orcid_is_propagated_but_conflict_is_not_merged(self):
        a={'author':{'id':'A1','display_name':'Pessoa'}}
        self.assertEqual(author_key(a,{'A1':'ORCID1'})[0],'ORCID1')
        self.assertEqual(author_key(a,{'A1':'ORCID1'},{'A1'})[0],'A1')


if __name__=='__main__':unittest.main()
