import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from scripts.entregar_marco5 import delivery_counts
from scripts.produzir_indicadores_marco4 import ROOT


class IncrementalDeliveryTests(unittest.TestCase):
    def counts(self,n,g,matched,num,common_num,common_den):
        data={'Corpus nacional.csv':[None]*n,'Corpus goiano.csv':[None]*g,
              'Correspondencia Goias Brasil.csv':[{'incluida_no_nacional':'Sim'}]*matched+[{'incluida_no_nacional':'Não'}]*(g-matched),
              'Participacao e contexto Goias.csv':[{'numerador':str(num)}],
              'Participacao periodo comum.csv':[{'obras_com_afiliacao_goiana_identificada':str(common_num),'obras_nacionais':str(common_den)}]}
        with patch('scripts.entregar_marco5.read',side_effect=lambda p:data[p.name]):return delivery_counts()

    def test_legacy_counts_are_still_supported(self):
        self.assertEqual(self.counts(7780,97,78,196,67,3459),(7780,97,7799,196,67,3459))

    def test_incremental_denominator_and_union_follow_inputs(self):
        self.assertEqual(self.counts(7779,97,78,196,67,3459),(7779,97,7798,196,67,3459))

    def test_regional_membership_does_not_promote_outside_national(self):
        self.assertEqual(self.counts(2,2,1,1,1,2),(2,2,3,1,1,2))

    def import_with_manifest(self,destination):
        data={'diretorio_nacional':'dados/analises/integracao_capes_20261116/elegibilidade',
              'diretorio_regional':'dados/analises/integracao_capes_20261116/elegibilidade',
              'diretorio_indicadores_proposto':'dados/analises/integracao_capes_20261116/indicadores',
              'diretorio_entrega_proposto':destination}
        f=tempfile.NamedTemporaryFile(mode='w',encoding='utf8',suffix='.json',delete=False)
        json.dump(data,f);f.close();self.addCleanup(Path(f.name).unlink)
        return subprocess.run([sys.executable,'-c','from scripts.entregar_marco5 import OUT; print(OUT)','--manifesto',f.name],cwd=ROOT,capture_output=True,text=True)

    def test_old_delivery_cannot_be_manifest_destination(self):
        self.assertNotEqual(self.import_with_manifest('dados/entregas/marco5').returncode,0)

    def test_destination_outside_delivery_tree_is_rejected(self):
        self.assertNotEqual(self.import_with_manifest('dados/analises/ensaio_manifesto_entrega').returncode,0)

    def test_import_configures_destination_without_creating_it(self):
        target=ROOT/'dados/entregas/ensaio_manifesto_entrega'
        self.assertFalse(target.exists())
        self.assertEqual(self.import_with_manifest(str(target)).returncode,0)
        self.assertFalse(target.exists())


if __name__=='__main__':unittest.main()
