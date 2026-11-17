"""Integra a conferência amostral explícita aos produtos gerados nesta rodada."""
import csv
import json
from collections import Counter
from scripts.construir_corpus_marco2 import OUT, read


def save(name, rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    audit=json.loads((OUT/'Auditoria.json').read_text(encoding='utf8'))
    if 'conferencia_integrada' in audit:
        raise FileExistsError('Conferência já integrada; preservar produtos.')
    units=read(OUT/'Registro de unidades.csv')
    reviewed=read(OUT/'Conferencia amostral.csv')
    sample=read(OUT/'Amostra para conferencia.csv')
    assert len(reviewed)==len(sample)==30
    assert {r['obra_id'] for r in sample}=={r['obra_id'] for r in reviewed}
    ledger={r['obra_id']:r for r in reviewed}
    for u in units:
        r=ledger.get(u['obra_id'])
        u['evidencia_leitura_amostral']=r['justificativa'] if r else ''
        if r and r['resultado_conferencia']=='pertinência sustentada no material amostral':
            u['suporte_tematico']='sustentado por leitura amostral Marco 2'
            if u['suporte_temporal']=='no período' and u['suporte_documental']=='compatível com escopo':
                u['nucleo_com_evidencia_temática']='1';u['candidato_pre_corpus']='1'
    save('Registro de unidades.csv',units)
    save('Corpus nacional provisorio.csv',[u for u in units if str(u['nucleo_com_evidencia_temática'])=='1'])
    save('Pre corpus tematico.csv',[u for u in units if str(u['candidato_pre_corpus'])=='1'])
    save('Obras complementares incorporadas provisoriamente.csv',[
        u for u in units if u['complementar_sem_openalex']=='1' and u['nucleo_com_evidencia_temática']=='1'])
    pending=read(OUT/'Pendencias residuais.csv')
    index={u['obra_id']:u for u in units}
    for p in pending:
        u=index[p['obra_id']]
        if u['suporte_tematico']=='sustentado por leitura amostral Marco 2':
            p['pendencias']=';'.join(v for v in p['pendencias'].split(';') if v!='confirmar pertinência substantiva' and v.strip()!='sinal não basta')
            p['prioridade']='1'
    save('Pendencias residuais.csv',pending)
    coverage=read(OUT/'Cobertura atualizada.csv')
    prov=read(OUT/'Proveniencia.csv')
    for c in coverage:
        ids={p['obra_id'] for p in prov if p['fonte']==c['fonte']}
        c['nucleo_com_leitura']=sum(index[k]['nucleo_com_evidencia_temática']=='1' for k in ids)
        c['pre_corpus']=sum(index[k]['candidato_pre_corpus']=='1' for k in ids)
    save('Cobertura atualizada.csv',coverage)
    audit['conferencia_integrada']=dict(Counter(r['resultado_conferencia'] for r in reviewed))
    audit['nucleo_antes_conferencia']=audit['nucleo_com_leitura']
    audit['pre_corpus_antes_conferencia']=audit['pre_corpus']
    audit['nucleo_com_leitura']=sum(u['nucleo_com_evidencia_temática']=='1' for u in units)
    audit['pre_corpus']=sum(u['candidato_pre_corpus']=='1' for u in units)
    audit['complementares_nucleo']=sum(u['complementar_sem_openalex']=='1' and u['nucleo_com_evidencia_temática']=='1' for u in units)
    (OUT/'Auditoria.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in audit.items() if k not in ('inputs_sha256',)},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
