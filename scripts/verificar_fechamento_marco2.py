"""Confere produtos persistidos e reconcilia unidades, sem alterar entradas."""
import csv
import hashlib
import json
from collections import Counter
from scripts.fechar_marco2 import OUT, ROOT, A, read


def main():
    audit=json.loads((OUT/'Auditoria.json').read_text(encoding='utf8'))
    rows=read(OUT/'Registro de decisoes.csv');core=read(OUT/'Corpus nacional.csv')
    prov=read(OUT/'Proveniencia.csv');pending=read(OUT/'Pendencias residuais.csv')
    index={r['obra_id']:r for r in rows}
    assert len(rows)==len(index)==13222
    assert len(prov)==13748==len({r['registro'] for r in prov})
    counts=Counter(r['obra_id'] for r in prov)
    assert all(counts[k]==int(r['registros_origem']) for k,r in index.items())
    assert len(core)==7780 and all(r['decisao']=='incluída' and not r['pendencias'] for r in core)
    assert len(pending)==5442 and {r['obra_id'] for r in pending}.isdisjoint(r['obra_id'] for r in core)
    assert set(index)=={r['obra_id'] for r in core+pending}
    assert sum(int(r['unidades_nucleo_anterior']) for r in core)==138
    assert all((ROOT/r['raw_file']).exists() for r in prov)
    assert all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h for name,h in audit['hashes_entradas'].items())
    coverage=read(OUT/'Cobertura atualizada.csv')
    assert sum(int(r['registros']) for r in coverage)==13748
    assert len(read(OUT/'Candidatos por defesa para Marco 3.csv'))==417
    sample=read(OUT/'Amostra de conferencia de regras.csv')
    assert len(sample)==42==len({r['obra_id'] for r in sample})
    checked=[]
    for r in sample:
        checked.append({'obra_id':r['obra_id'],'estado':r['decisao'],'criterio_tema':r['criterio_tema'],
                        'conferencia':'evidência selecionada compatível com regra temática; identidade preservada em separado' if r['decisao']!='pendente' else 'pendência explicitada; ausência de evidência não virou exclusão',
                        'limite':'Conferência de título/trecho e estado; não é validação independente ou leitura integral.'})
    path=OUT/'Conferencia da amostra de regras.csv'
    if not path.exists():
        with path.open('x',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(checked[0]));w.writeheader();w.writerows(checked)
    by_node={p['registro']:p['obra_id'] for p in prov}
    regional=[]
    for r in read(A/'openalex_prioridade_goias_20261115.csv'):
        if '2020-01-01'<=r['data_publicacao']<='2026-11-08':
            u=index[by_node[r['openalex_id']]]
            regional.append({'openalex_id':r['openalex_id'],'obra_id':u['obra_id'],'titulo':r['titulo'],
                             'data_publicacao':r['data_publicacao'],'decisao_nacional':u['decisao'],
                             'sinais_geograficos':r['sinais_goias_texto_campos']+';'+r['sinal_goias_instituicoes'],
                             'limite':'Sinal para revisão; não confirma contexto/afiliação em Goiás e não esgota candidatos regionais.'})
    assert len(regional)==100
    path=OUT/'Candidatos OpenAlex sinalizados para Marco 3.csv'
    if not path.exists():
        with path.open('x',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(regional[0]));w.writeheader();w.writerows(regional)
    print(json.dumps({'registros':len(prov),'unidades':len(rows),'incluidas':len(core),'pendentes':len(pending),
                      'amostra':dict(Counter(r['decisao'] for r in sample)),
                      'cheques':'partição, contagens, 138 anteriores, 417 defesas, caminhos e hashes OK'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
