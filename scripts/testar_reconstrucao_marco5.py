"""Extrai o pacote em diretório novo e reconstrói produtos finais sem rede."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from openpyxl import load_workbook
from scripts.entregar_marco5 import ROOT, OUT, BOOK, M4, MANIFEST, digest, read


def workbook_signature(path):
    result={}
    values=load_workbook(path,data_only=True,read_only=True)
    for s in values:
        h=hashlib.sha256()
        for row in s.iter_rows(values_only=True):h.update((json.dumps(row,ensure_ascii=False,default=str)+'\n').encode('utf8'))
        result[s.title]=h.hexdigest()
    values.close()
    return result


def main():
    source=OUT/'Pacote reproduzivel PIBID.zip'
    expected={p.name:digest(p) for p in M4.glob('*.csv') if not MANIFEST or p.name!='Inventario de produtos.csv'}
    workbook_expected=workbook_signature(BOOK)
    matrix_expected=workbook_signature(OUT/'Matriz de cobertura e sobreposicao.xlsx')
    tmp=Path(tempfile.mkdtemp(prefix='pibid-m5-recon-')).resolve()
    assert tmp.parent==Path(tempfile.gettempdir()).resolve() and tmp.name.startswith('pibid-m5-recon-')
    commands=[
        [sys.executable,'-m','scripts.produzir_indicadores_marco4','--atualizar'],
        [sys.executable,'-m','scripts.documentar_conferencias_marco4','--atualizar'],
        [sys.executable,'-m','scripts.verificar_marco4','--atualizar'],
        [sys.executable,'-m','scripts.entregar_marco5','preparar'],
        ['powershell','-NoProfile','-File','scripts/conferir_excel_marco5.ps1'],
        [sys.executable,'-m','scripts.entregar_marco5','verificar'],
        [sys.executable,'-m','unittest','discover','-s','tests','-p','test_*marco*.py'],
    ]
    if MANIFEST:
        relative_manifest=str(MANIFEST.relative_to(ROOT))
        options=['--manifesto',relative_manifest]
        commands=[
            [sys.executable,'-X','utf8','-m','scripts.recalcular_cobertura_capes_20261116','--recalcular','--atualizar'],
            [sys.executable,'-X','utf8','-m','scripts.entregar_marco5','preparar']+options,
            ['powershell','-NoProfile','-File','scripts/conferir_excel_marco5.ps1','-Manifesto',relative_manifest],
            [sys.executable,'-X','utf8','-m','scripts.entregar_marco5','verificar']+options,
        ]
        commands += [[sys.executable,'-m','unittest','discover','-s','tests','-p',pattern] for pattern in ['test_*marco*.py','test_indicadores_capes_20261116.py','test_delta_capes_20261116.py','test_entrega_capes_20261116.py']]
    logs=[];ok=False
    try:
        with zipfile.ZipFile(source) as z:
            # A extração só aceita membros contidos na raiz temporária.
            for name in z.namelist():assert (tmp/name).resolve().is_relative_to(tmp),name
            z.extractall(tmp)
        manifest=read(tmp/OUT.relative_to(ROOT)/'Inventario.csv')
        assert all(digest(tmp/r['caminho'])==r['sha256'] for r in manifest)
        for cmd in commands:
            proc=subprocess.run(cmd,cwd=tmp,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf8',errors='replace')
            logs.append({'comando':' '.join(cmd).replace(sys.executable,'python'),'codigo_saida':proc.returncode,'saida':proc.stdout})
            print(logs[-1]['comando']+': '+str(proc.returncode),flush=True)
            if proc.returncode:raise RuntimeError(proc.stdout)
        different=[name for name,sha in expected.items() if digest(tmp/M4.relative_to(ROOT)/name)!=sha]
        # O inventário inclui código/resultados; caminhos relativos devem ser idênticos.
        assert not different,different
        assert workbook_signature(tmp/OUT.relative_to(ROOT)/'Planilha final PIBID.xlsx')==workbook_expected,'Valores das planilhas divergentes'
        assert workbook_signature(tmp/OUT.relative_to(ROOT)/'Matriz de cobertura e sobreposicao.xlsx')==matrix_expected,'Matriz divergente'
        result={'estado':'OK','arquivo_testado_sha256':digest(source),'arquivos_extraidos_conferidos':len(manifest),
                'comandos_sem_rede':len(commands),'tabelas_csv_marco4_identicas':len(expected),
                'planilha_final':'Valores de todas as abas idênticos após geração e recálculo nativo',
                'matriz':'Valores de todas as abas idênticos',
                'graficos':'Seis gráficos nativos reconstruídos, exportados e verificados estruturalmente; revisão visual original registrada em Conferencia visual.csv',
                'alcance':'Reconstrução desde corpora e decisões congelados; não nova coleta ou validação científica independente',
                'logs':logs}
        (OUT/'Teste de reconstrucao.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
        ok=True
        print('Reconstrução integral dos indicadores e produtos finais: OK',flush=True)
    finally:
        if ok:
            assert tmp.parent==Path(tempfile.gettempdir()).resolve() and tmp.name.startswith('pibid-m5-recon-')
            shutil.rmtree(tmp)
        else:print('Diretório preservado para diagnóstico: '+str(tmp),flush=True)


if __name__=='__main__':main()
