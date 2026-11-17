"""Conferir primeira execução isolada dos indicadores, sem copiar os insumos."""
import json
import shutil
import subprocess
import sys
import uuid
from scripts.avaliar_capes_20261116 import A,ROOT,sha


def main():
    base=A/'integracao_capes_20261116';out=base/'indicadores'
    tag='teste_manifesto_'+uuid.uuid4().hex
    target=base/tag;manifest=base/(tag+'.json')
    data=json.loads((base/'elegibilidade/Manifesto de execucao.json').read_text(encoding='utf8'))
    data['diretorio_indicadores_proposto']=str(target.relative_to(ROOT))
    manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
    logs=[];success=False
    try:
        for module in ('produzir_indicadores_marco4','documentar_conferencias_marco4','verificar_marco4'):
            args=[sys.executable,'-X','utf8','-m','scripts.'+module,'--manifesto',str(manifest)]
            p=subprocess.run(args,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf8',errors='replace')
            logs.append({'modulo':module,'codigo_saida':p.returncode,'saida':p.stdout})
            assert p.returncode==0,p.stdout
            print(module+': OK',flush=True)
        csvs=[p for p in target.glob('*.csv') if p.name!='Inventario de produtos.csv']
        assert csvs
        assert all((out/p.name).is_file() and sha(p)==sha(out/p.name) for p in csvs),'Tabelas divergentes'
        result={'estado':'OK','primeira_execucao_sem_atualizar':True,'rede':'não utilizada',
                'tabelas_csv_identicas':len(csvs),'inventario':'Não comparado byte a byte: registra caminhos diferentes dos produtos temporários.',
                'alcance':'Reprodução dos indicadores e das evidências reaproveitadas por manifesto em saída nova; não é teste da futura entrega Excel.',
                'logs':logs}
        (out/'Teste de reproducao por manifesto.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
        success=True;print('Tabelas reproduzidas exatamente: '+str(len(csvs)),flush=True)
    finally:
        if success:
            assert target.resolve().parent==base.resolve() and target.name.startswith('teste_manifesto_')
            shutil.rmtree(target)
            assert manifest.resolve().parent==base.resolve() and manifest.name.startswith('teste_manifesto_')
            manifest.unlink()
        else:print('Arquivos preservados para diagnóstico: '+str(target),flush=True)


if __name__=='__main__':main()
