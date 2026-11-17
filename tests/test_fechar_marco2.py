import unittest
from scripts.fechar_marco2 import thematic


class ClosingTests(unittest.TestCase):
    def test_bare_acronym_is_not_inclusion(self):
        self.assertEqual(thematic('PIBID','')[0],'pendente')

    def test_explicit_object_in_title_supports_inclusion(self):
        self.assertEqual(thematic('Aprendizagem da docência na experiência do PIBID','')[0],'incluir')

    def test_event_metadata_is_not_study_evidence(self):
        text='Enfoc Encontro de pesquisa e ensino do Programa Institucional de Bolsa de Iniciação à Docência PIBID apresenta atividades de pesquisa e ensino.'
        self.assertEqual(thematic('Recursos tecnológicos',text)[0],'pendente')

    def test_generic_program_goal_is_not_study_object(self):
        text='Um dos objetivos do Programa Institucional de Bolsa de Iniciação à Docência PIBID é a qualificação do licenciando por meio da pesquisa e formação.'
        self.assertEqual(thematic('Uma atividade',text)[0],'pendente')

    def test_abstract_can_support_without_acronym_in_title(self):
        text='Este artigo tem como objetivo analisar as ações e práticas de ensino desenvolvidas no contexto do PIBID em uma escola pública com professores em formação.'
        self.assertEqual(thematic('Uma atividade',text)[0],'incluir')

    def test_english_is_not_excluded(self):
        text='This study investigates the teaching practices developed by future teachers in the PIBID program within public schools and their learning experiences during initial teacher training.'
        self.assertEqual(thematic('Learning experiences',text)[0],'incluir')


if __name__=='__main__':unittest.main()
