import unittest
from scripts.construir_corpus_marco2 import identity, publication, repo_key


class CorpusTests(unittest.TestCase):
    def record(self, **kwargs):
        r={'kind':'article','doi':'','tn':'a formação de professores no contexto do pibid',
           'title':'A formação de professores no contexto do PIBID', 'au':('ana','silva'),
           'repos':set(),'abstract':'','year':'2020'}
        r.update(kwargs)
        return r

    def test_title_does_not_merge_thesis_and_article(self):
        self.assertEqual(identity(self.record(),self.record(kind='dissertation'))[0],'pendente')

    def test_conflicting_doi_blocks_merge(self):
        self.assertEqual(identity(self.record(doi='10.1/a'),self.record(doi='10.1/b'))[0],'pendente')

    def test_thesis_needs_evidence_beyond_title_author(self):
        a=self.record(kind='dissertation')
        self.assertEqual(identity(a,a)[0],'pendente')
        b={**a,'repos':{'123/45'}}
        self.assertEqual(identity(b,b)[0],'confirmada')

    def test_absent_publication_and_partial_2026_stay_pending(self):
        self.assertEqual(publication([],[])[0],'pendente')
        self.assertEqual(publication([],['2026'])[0],'pendente')
        self.assertEqual(publication([],['2024'])[0],'no período')

    def test_cutoff_and_conflict(self):
        self.assertEqual(publication(['2026-11-08'],['2026'])[0],'no período')
        self.assertEqual(publication(['2026-11-09'],['2026'])[0],'fora do período')
        self.assertEqual(publication(['2026-11-08','2026-11-09'],['2026'])[0],'conflito temporal')

    def test_handle_identity(self):
        self.assertEqual(repo_key('http://repo/x/handle/123/456'), '123/456')
        self.assertEqual(repo_key('https://repo/jspui/handle/123/456/'), '123/456')
        self.assertEqual(repo_key('https://doi.org/10.1/test'), '')


if __name__=='__main__':unittest.main()
