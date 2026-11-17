"""Revisão regional local com decisões por componente e extração rastreável."""
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from openpyxl import load_workbook
from scripts.fechar_marco2 import A, ROOT, read, thematic
from scripts.preanalise_e_validacao_20261115 import texto_normalizado

OUT=A/'marco3'
M2=A/'marco2_fechamento'
BASE=A/'triagem_criterio_defesa_20261115.xlsx'
IES=r'universidade federal de goias|universidade estadual de goias|instituto federal goiano|instituto federal de goias|instituto federal de educacao ciencia e tecnologia goiano|instituto federal de educacao ciencia e tecnologia de goias|catolica de goias|universidade federal de jatai|universidade federal de catalao|universidade de rio verde|unievangelica'
GEO=r'\bgoias\b|\bgoian[oa]s?\b|\bgoiania\b|\banapolis\b|\bjatai\b|\bcatalao\b|\bmorrinhos\b|\burutai\b|'+IES


def institution_signal(value):
    text=re.sub(r'\W+',' ',texto_normalizado(value or '')).strip()
    return bool(re.search(IES,text))


def write(name,rows,fields=None):
    with (OUT/name).open('w' if '--atualizar' in sys.argv else 'x',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)


def period(publication_years,dates,defense,thesis):
    if any('2020-01-01'<=d<='2026-11-08' for d in dates):return 'Sim','publicação completa'
    if any(y.isdigit() and 2020<=int(y)<=2025 for y in publication_years):return 'Sim','ano de publicação'
    if thesis and any(y.isdigit() and 2020<=int(y)<=2026 for y in defense):return 'Sim','defesa alternativa; 2026 só ano = evidência limitada'
    # Publicação antiga não invalida defesa alternativa ainda desconhecida.
    if publication_years and all(y.isdigit() and int(y)<2020 for y in publication_years) and not thesis:return 'Não','publicação anterior a 2020'
    if thesis and defense and publication_years and all(y.isdigit() and int(y)<2020 for y in defense|publication_years):return 'Não','publicação e defesa explicitamente anteriores a 2020'
    return 'Incerto','evidência temporal regional insuficiente'


def main():
    if OUT.exists() and '--atualizar' not in sys.argv:raise FileExistsError('Rodada existente; preservar.')
    inputs=[BASE,M2/'Registro de decisoes.csv',M2/'Proveniencia.csv',M2/'Estado de todas as relacoes.csv',A/'openalex_busca_restrita_20261115.csv',A/'openalex_prioridade_goias_20261115.csv']
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    w=load_workbook(BASE,read_only=True,data_only=True);it=iter(w['Triagem'].values);h=next(it)
    base={v[0]:dict(zip(h,v)) for v in it if v[0]}
    eh=iter(w['Eixos de análise'].values);headers=next(eh);history=[dict(zip(headers,v)) for v in eh if v[0]];w.close()
    oa={r['openalex_id']:r for r in read(inputs[4])}
    units={r['obra_id']:r for r in read(inputs[1])};prov=read(inputs[2]);rels=read(inputs[3])
    bynode={r['registro']:r['obra_id'] for r in prov};byunit=defaultdict(list)
    for p in prov:byunit[p['obra_id']].append(p)
    queues=defaultdict(set)
    def add(node,queue):queues[bynode[node]].add(queue)
    defense_codes=[]
    for c,b in base.items():
        add('BASE:'+c,'base técnica e fontes complementares')
        if b['Decisão de elegibilidade']=='Incluir':add('BASE:'+c,'19 inclusões históricas')
        d=str(b['Ano de defesa'] or '')
        if b['Tipo de produção'] in ('Tese','Dissertação') and d.isdigit() and 2020<=int(d)<=2026:
            add('BASE:'+c,'417 linhas por defesa');defense_codes.append(c)
    geo_prior=read(inputs[5]);hundred=[]
    for r in geo_prior:
        if '2020-01-01'<=r['data_publicacao']<='2026-11-08':add(r['openalex_id'],'100 OpenAlex sinalizados');hundred.append(r['openalex_id'])
    # Complementação interna por IES/contextos: só arquivos existentes, sem novas buscas.
    for id,r in oa.items():
        if re.search(GEO,texto_normalizado(r['titulo']+' '+r['resumo']+' '+r['instituicoes'])):
            add(id,'varredura local por IES/contextos')
    assert len(defense_codes)==417 and len(hundred)==100
    materials=[];draft=[];hist_eixos=[]
    for gid,q in sorted(queues.items()):
        u=units[gid];pp=byunit[gid]
        bs=[base[p['registro'][5:]] for p in pp if p['registro'].startswith('BASE:')]
        os=[oa[p['registro']] for p in pp if p['registro'] in oa]
        years={p['ano_publicacao_original'] for p in pp if p['ano_publicacao_original']}
        dates={p['data_publicacao_original'] for p in pp if p['data_publicacao_original']}
        defense={p['ano_defesa_original'] for p in pp if p['ano_defesa_original']}
        thesis=any(p['tipo_original'] in ('Tese','Dissertação','dissertation') for p in pp)
        temporal,why=period(years,dates,defense,thesis)
        affiliation=[o['instituicoes'] for o in os if institution_signal(o['instituicoes'])]
        affiliation += [str(b['Evidência da afiliação'] or '') for b in bs if b['Afiliação em Goiás']=='Sim']
        context=[str(b['Evidência do contexto'] or '') for b in bs if b['Contexto de Goiás']=='Pesquisa realizada em Goiás']
        historical=any(b['Decisão de elegibilidade']=='Incluir' for b in bs)
        hist_theme=any(b['Relação com PIBID'] in ('Tema central do estudo','Relação substantiva com PIBID') for b in bs)
        thematic_yes=u['criterio_tema']!='insuficiente' or hist_theme
        academic=bool(u['tipos_sustentados']) or historical
        texts=[]
        for p in pp:
            node=p['registro']
            abstract=oa[node]['resumo'] if node in oa else (base[node[5:]]['Resumo'] or '')
            title=oa[node]['titulo'] if node in oa else base[node[5:]]['Título']
            texts.append((node,title,abstract,p['raw_file']))
            materials.append({'obra_id':gid,'registro':node,'titulo':title,'resumo':abstract,'raw_file':p['raw_file'],
                              'afiliacoes':oa[node]['instituicoes'] if node in oa else str(base[node[5:]]['Afiliações de autoria'] or ''),
                              'filas':';'.join(sorted(q))})
        # Sinais de contexto somente priorizam; a confirmação é por leitura registrada.
        context_signal=any(re.search(GEO,texto_normalizado(t+' '+a)) for _,t,a,_ in texts)
        historical_exclusion=[b['Motivo da exclusão'] for b in bs if b['Decisão de elegibilidade']=='Excluir']
        state='Excluir' if temporal=='Não' else 'Pendente'
        reason=why if state=='Excluir' else 'Verificar evidências regionais'
        potential=temporal=='Sim' and thematic_yes and academic and (historical or affiliation or context or context_signal)
        draft.append({'obra_id':gid,'titulo':u['titulo'],'filas':';'.join(sorted(q)),
                      'tema_sustentado':int(thematic_yes),'academico_sustentado':int(academic),
                      'periodo':temporal,'criterio_temporal':why,'anos_publicacao':';'.join(sorted(years)),
                      'datas_publicacao':';'.join(sorted(dates)),'anos_defesa':';'.join(sorted(defense)),
                      'afiliacao_goias':'Sim' if affiliation else 'Não identificada no material',
                      'evidencia_afiliacao':' | '.join(affiliation),
                      'contexto_goias':'Sim' if context else 'A verificar' if context_signal else 'Não identificado no material',
                      'evidencia_contexto':' | '.join(context),'historico_incluido':int(historical),
                      'exclusoes_historicas':';'.join(str(v or '') for v in historical_exclusion),
                      'potencial_inclusao':int(bool(potential)),'decisao':state,'justificativa':reason,
                      'codigos_base':u['codigos_base'],'ids_openalex':u['ids_openalex'],
                      'estado_nacional':u['decisao']})
        for b in bs:
            if b['Decisão de elegibilidade']=='Incluir':
                for e in history:
                    if e['Código']==b['Código'] and e['Estado']:
                        hist_eixos.append({'obra_id':gid,**{k:str(v or '') for k,v in e.items()}})
    OUT.mkdir(exist_ok=True)
    write('Triagem regional inicial.csv',draft)
    write('Materiais locais.csv',materials)
    write('Eixos historicos reaproveitaveis.csv',hist_eixos)
    write('Revisao individual prioritaria.csv',[r for r in draft if r['potencial_inclusao']],list(draft[0]))
    pr=[p for p in prov if p['obra_id'] in queues];write('Proveniencia.csv',pr)
    overlaps=Counter()
    for q in queues.values():
        for a in q:
            for b in q:
                if a<=b:overlaps[(a,b)]+=1
    write('Sobreposicao das filas.csv',[{'fila_a':a,'fila_b':b,'obras_compartilhadas':n} for (a,b),n in sorted(overlaps.items())])
    assert len(draft)==len({r['obra_id'] for r in draft})
    assert all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==v for n,v in hashes.items())
    audit={'unidades_regionais':len(draft),'registros_origem':len(pr),'potenciais':sum(r['potencial_inclusao'] for r in draft),
           'historicas':sum(r['historico_incluido'] for r in draft),'periodo':dict(Counter(r['periodo'] for r in draft)),
           'filas':dict(Counter(f for q in queues.values() for f in q)), 'hashes_entradas':hashes}
    (OUT/'Auditoria inicial.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(audit,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
