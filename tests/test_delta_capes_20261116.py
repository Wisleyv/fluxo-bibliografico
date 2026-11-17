import unittest
from scripts.avaliar_delta_capes_20261116 import assess_existing, assess_provisional, author_tokens


class EligibilityDeltaTests(unittest.TestCase):
    def test_shortened_title_does_not_erase_previous_inclusion(self):
        state,_,_=assess_existing({'titulo':'PIBID e formação docente','decisao':'incluída'},[{'registro_capes':'R1','titulo':'PIBID'}])
        self.assertEqual(state,'incluída')

    def test_editorial_label_or_retrieval_does_not_prove_theme(self):
        state,_,support=assess_existing({'titulo':'Editorial','decisao':'pendente'},[{'registro_capes':'R1','titulo':'Editorial'}])
        self.assertEqual(state,'pendente');self.assertEqual(support,[])

    def test_new_substantive_title_is_flagged_for_review_not_silent_promotion(self):
        state,_,support=assess_existing({'titulo':'Uma atividade','decisao':'pendente'},[{'registro_capes':'R1','titulo':'PIBID e formação docente'}])
        self.assertEqual(state,'pendente');self.assertEqual(len(support),1)

    def record(self,title,year):
        return {'titulo':title,'ano_publicacao_ris':year,'tipo_original':'article','veiculo':'Revista de Educação','autoria_original':'Pessoa Silva'}

    def test_year_2026_alone_does_not_demonstrate_cutoff(self):
        state,_,time,*_=assess_provisional(self.record('PIBID e formação docente','2026'))
        self.assertEqual(state,'pendente');self.assertEqual(time,'Incerto')

    def test_generic_title_is_pending_instead_of_excluded(self):
        state,theme,*_=assess_provisional(self.record('Educação ambiental escolar','2018'))
        self.assertEqual(state,'pendente');self.assertEqual(theme,'pendente')

    def test_positive_eligibility_without_identity_stays_outside_corpus(self):
        state,*_=assess_provisional(self.record('PIBID e formação docente','2025'))
        self.assertEqual(state,'elegível com identidade pendente');self.assertNotEqual(state,'incluída')

    def test_author_order_is_not_new_authorship_but_missing_person_is_visible(self):
        self.assertEqual(author_tokens('Silva, Pessoa | Souza, Maria'),author_tokens('Pessoa Silva; Maria Souza'))
        self.assertNotEqual(author_tokens('Pessoa Silva'),author_tokens('Pessoa Silva; Maria Souza'))


if __name__=='__main__':unittest.main()
