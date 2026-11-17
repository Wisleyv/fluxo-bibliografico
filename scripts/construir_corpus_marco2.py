"""Consolidação local conservadora; não coleta nem modifica decisões anteriores."""
import csv
import hashlib
import html
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit

from openpyxl import load_workbook
from scripts.preanalise_e_validacao_20261115 import texto_normalizado, cabecalhos
from scripts.conferir_amostra_por_regras_20261115 import titulo_normalizado
from scripts.preparar_piloto_20261115 import normalizar_doi
from scripts.conciliar_pares_confirmados_20261115 import pares_confirmados
from scripts.coletar_openalex_restrita_20261115 import validate_page, PARAMS

ROOT = Path(__file__).resolve().parents[1]
A = ROOT/'dados/analises'
OUT = A/'marco2'
NORMAL = ROOT/'dados/normalizados/registros_normalizados__20261108T205625-0300__828bdff7.csv'
ACADEMIC = {'article','book','book-chapter','conference-paper','dissertation','review'}
BASE_KIND = {'Artigo':'article','Tese':'dissertation','Dissertação':'dissertation',
             'Livro':'book','Capítulo de livro':'book-chapter','Trabalho em anais':'conference-paper'}
READINGS = {
 'b0560bbc': ('sustentado por leitura Marco 2', 'Resumo analisa os sentidos da docência reconstruídos por bolsistas de Pedagogia do PIBID; programa integra o objeto e a avaliação de impacto.'),
 '7ef41aa6': ('sustentado por leitura Marco 2', 'Resumo em português analisa documentos de 2007–2013 relativos ao PIBID e parceria na formação docente; programa é objeto da análise.'),
 'fe0699e5': ('sustentado por leitura Marco 2', 'Resumo investiga representações de participantes do subprojeto PIBID-Inglês da UEL; relação substantiva com participantes, sem converter resultado em efeito do PIBID.'),
 '3d810ada': ('pendente', 'Resumo descreve subprojeto A World of Englishes sem identificar explicitamente o PIBID; a recuperação pela fonte não basta para decidir pertinência.'),
 '2f5c7e30': ('pendente', 'Resumo investiga sentidos do futebol entre crianças; não esclarece relação substantiva com o programa. Não excluir pela falta de sigla.'),
 '06792f41': ('pendente', 'Campo de resumo é referência bibliográfica; menção incidental anterior não é exclusão nacional automática.'),
}


def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))


def tokens(value):
    return re.findall(r'[a-z0-9]+',texto_normalizado(html.unescape(str(value or ''))))


def authors(value):
    ts=tokens(value)
    return tuple(sorted(ts)) if ts and not re.search(r'\bet\s+al\b',str(value),re.I) else ()


def abstract_similarity(a,b):
    aa,bb=set(tokens(a)),set(tokens(b))
    if min(len(aa),len(bb))<30:
        return 0.0
    return len(aa & bb)/len(aa | bb)


def repo_key(url):
    p=urlsplit(str(url or ''))
    path=p.path.rstrip('/').lower()
    match=re.search(r'/(?:handle|jspui/handle)/(.+)',path)
    if match:
        return match[1]
    return ''


def same_type(a,b):
    return bool(a['kind'] and a['kind']==b['kind'] and a['kind'] in ACADEMIC)


def identity(a,b):
    """Título longo + autoria completa + tipo e evidência independente do título."""
    if not same_type(a,b):
        return 'pendente', 'Tipos distintos/ambíguos: título não permite fundir tese e artigo ou tipos não harmonizados.'
    if a['doi'] and b['doi'] and a['doi']!=b['doi']:
        return 'pendente', 'DOIs distintos: podem ser versões ou obras relacionadas; não fundir automaticamente.'
    title=bool(a['tn'] and a['tn']==b['tn'] and len(tokens(a['title']))>=6)
    au=bool(a['au'] and a['au']==b['au'])
    shared=a['repos'] & b['repos']
    sim=abstract_similarity(a['abstract'],b['abstract'])
    if title and au and (shared or sim>=0.90):
        return 'confirmada', 'Título longo, autoria completa, tipo compatível e '+('identificador de repositório coincidente.' if shared else f'resumos concordantes (Jaccard={sim:.4f}, mínimo 30 tokens distintos).')
    # Duas datas explicitamente de publicação; defesa nunca é usada como publicação.
    if title and au and a['year'] and a['year']==b['year'] and a['kind']!='dissertation':
        return 'confirmada', 'Título longo, autoria completa, tipo e ano de publicação concordantes; sem conflito de DOI.'
    return 'pendente', f'Corroboração insuficiente: título_longo={title}; autoria={au}; resumo_jaccard={sim:.4f}; repositório={bool(shared)}.'


def publication(dates, years):
    valid=[d for d in dates if '2007-01-01'<=d<='2026-11-08']
    bad=[d for d in dates if not '2007-01-01'<=d<='2026-11-08']
    if valid and not bad:
        return 'no período', 'data completa arquivada'
    if valid and bad:
        return 'conflito temporal', 'datas completas em lados diferentes do corte'
    if bad:
        return 'fora do período', 'data completa fora do corte'
    yy={int(y) for y in years if str(y).isdigit()}
    if yy and all(2007<=y<=2025 for y in yy):
        return 'no período', 'ano explícito de publicação anterior a 2026'
    return 'pendente', 'sem publicação comprovada no corte; defesa não substitui publicação nacional'


def dump(name, rows, fields):
    with (OUT/name).open('x',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


def main():
    if OUT.exists():
        raise FileExistsError('Rodada existente; não será sobrescrita.')
    csv.field_size_limit(2**30)
    inputs=[A/'triagem_criterio_defesa_20261115.xlsx', A/'openalex_busca_restrita_20261115.csv',
            A/'marco1/Pares auditados.csv', A/'marco1/Exclusivos observados complementares.csv',
            A/'openalex_busca_restrita_auditoria_20261115.json',NORMAL]
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    w=load_workbook(inputs[0],data_only=True)
    sh=w['Triagem']; vals=iter(sh.values); headers=next(vals)
    base={v[0]:dict(zip(headers,v)) for v in vals if v[0]}
    hist=pares_confirmados(w,sh,cabecalhos(sh),{c:i for i,c in enumerate(base,2)})
    w.close()
    # Lê a geração normalizada vigente uma vez para recuperar UUID, execução e bruto.
    normalized={}
    with NORMAL.open(encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f):
            c=r['record_id'][:8]
            if c in base:
                if c in normalized:
                    raise ValueError('Prefixo de UUID duplicado.')
                normalized[c]=r
    if set(normalized)!=set(base):
        raise ValueError('Faltam registros normalizados para a proveniência.')
    oa={r['openalex_id']:r for r in read(inputs[1])}
    audit=json.loads(inputs[4].read_text(encoding='utf8'))
    pages=sorted((ROOT/'dados/brutos/openalex/busca-restrita-20261115').glob('pagina_*.json'))
    assert len(pages)==125 and len(oa)==12431 and len(base)==1317
    cursor='*'; seen=set(); raw={}
    for p in pages:
        data=p.read_bytes()
        assert hashlib.sha256(data).hexdigest()==audit['page_sha256'][p.name]
        page=json.loads(data)
        assert page['request_parameters']==PARAMS
        cursor=validate_page(page,cursor,seen)
        for item in page['response']['results']:
            urls=[loc.get('landing_page_url') for loc in item.get('locations',[])]
            countries=sorted({country for a in item.get('authorships',[]) for country in a.get('countries',[])})
            raw[item['id']]={'repos':{repo_key(u) for u in urls if repo_key(u)},'countries':countries,
                             'collected':page['retrieved_at']}
    assert cursor is None and seen==set(oa)
    records={}
    for id,r in oa.items():
        records[id]={'node':id,'source':'OpenAlex','title':r['titulo'],'tn':titulo_normalizado(r['titulo']),
                     'author':r['autores'],'au':authors(r['autores']),'abstract':r['resumo'],
                     'kind':r['tipo'],'doi':normalizar_doi(r['doi']),'year':r['ano_publicacao'],
                     'date':r['data_publicacao'],'repos':raw[id]['repos'],'base_code':'',
                     'countries':raw[id]['countries'],'theme':'', 'theme_note':'',
                     'raw_file':str((pages[0].parent/r['pagina_origem']).relative_to(ROOT)),
                     'record_id':id,'source_id':id,'run_id':'busca-restrita-20261115',
                     'collected':raw[id]['collected'],'original_type':r['tipo'],
                     'goias':'','defense':''}
    for c,r in base.items():
        n=normalized[c]
        theme='sustentado por leitura anterior' if r['Relação com PIBID'] in ('Tema central do estudo','Relação substantiva com PIBID') else 'pendente'
        note='Relação com PIBID na base técnica: '+str(r['Relação com PIBID'])+'; decisão regional não é elegibilidade nacional.'
        if c in READINGS: theme,note=READINGS[c]
        id='BASE:'+c
        records[id]={'node':id,'source':r['Fonte'],'title':r['Título'],'tn':titulo_normalizado(r['Título']),
                     'author':r['Autoria'] or '','au':authors(r['Autoria']),'abstract':r['Resumo'] or '',
                     'kind':BASE_KIND.get(r['Tipo de produção'],''),'doi':normalizar_doi(r['DOI']),
                     'year':str(r['Ano de publicação'] or ''),'date':'',
                     'repos':{repo_key(r['Link da fonte'])} if repo_key(r['Link da fonte']) else set(),
                     'base_code':c,'countries':[],'theme':theme,'theme_note':note,
                     'raw_file':n['raw_file'],'record_id':n['record_id'],'source_id':n['source_record_id'],
                     'run_id':n['source_run_id'],'collected':n['collected_at'],
                     'original_type':r['Tipo de produção'],'goias':str(r['Contexto de Goiás'] or '')+'; '+str(r['Afiliação em Goiás'] or ''),
                     'defense':str(r['Ano de defesa'] or '')}
    parent={id:id for id in records}
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]];x=parent[x]
        return x
    def union(a,b):
        a,b=find(a),find(b)
        parent[max(a,b)]=min(a,b)
    edges=[]
    def edge(a,b,status,reason,origin):
        edges.append({'registro_a':a,'registro_b':b,'decisao':status,'fundamento':reason,'origem':origin})
        if status=='confirmada':union(a,b)
    for a,b in sorted(hist):edge('BASE:'+a,'BASE:'+b,'confirmada','Par histórico confirmado preservado.','histórico 40')
    old=read(inputs[2])
    for p in old:
        a='BASE:'+p['codigo_base'];b=p['openalex_id']
        if p['decisao_marco1']=='mesma obra confirmada':
            edge(a,b,'confirmada',p['fundamento'],'Marco 1 confirmado')
        else:
            status,reason=identity(records[a],records[b])
            edge(a,b,status,reason,'Marco 1 inconclusivo')
    # Compara títulos exatos entre todos os controles e dentro do OpenAlex.
    # Indexação por título evita produto cartesiano; DOI sozinho não basta.
    by_title=defaultdict(list)
    for id,r in records.items():
        if r['tn']:by_title[r['tn']].append(id)
    previous={tuple(sorted((r['registro_a'],r['registro_b']))) for r in edges}
    for title,ids in sorted(by_title.items()):
        if len(ids)<2:continue
        for i,a in enumerate(ids):
            for b in ids[i+1:]:
                key=tuple(sorted((a,b)))
                if key in previous:continue
                previous.add(key)
                status,reason=identity(records[a],records[b])
                edge(a,b,status,reason,'Título exato adicional')
    # DOI idêntico só é unido com título/autoria/tipo corroborantes.
    by_doi=defaultdict(list)
    for id,r in records.items():
        if r['doi']:by_doi[r['doi']].append(id)
    for doi,ids in by_doi.items():
        for i,a in enumerate(ids):
            for b in ids[i+1:]:
                key=tuple(sorted((a,b)))
                if key in previous:continue
                previous.add(key);status,reason=identity(records[a],records[b])
                edge(a,b,status,reason,'DOI adicional')
    groups=defaultdict(list)
    for id in records:groups[find(id)].append(id)
    unresolved_nodes=set()
    for e in edges:
        # Relações absorvidas por evidência confirmada deixam de ser pendência de identidade.
        e['efeito_residual']='absorvida por identidade confirmada' if find(e['registro_a'])==find(e['registro_b']) else 'pode alterar contagem' if e['decisao']=='pendente' else 'sem pendência'
        if e['efeito_residual']=='pode alterar contagem':unresolved_nodes.update((e['registro_a'],e['registro_b']))
    units=[]; provenance=[]; pending=[]
    for root,ids in sorted(groups.items()):
        rr=[records[id] for id in sorted(ids)]
        uid='M2-'+hashlib.sha256('|'.join(sorted(ids)).encode()).hexdigest()[:16]
        dates=sorted({r['date'] for r in rr if r['date']}); years=sorted({r['year'] for r in rr if r['year']})
        when,why=publication(dates,years)
        kind=sorted({r['kind'] for r in rr if r['kind']})
        academic=bool(kind) and all(k in ACADEMIC for k in kind)
        supported=[r for r in rr if r['theme'].startswith('sustentado')]
        title_signal=any(re.search(r'\bpibid\b',r['tn']) or 'programa institucional de bolsa de iniciacao a docencia' in r['tn'] for r in rr)
        theme='sustentado por leitura' if supported else 'sinal no título; triagem pendente' if title_signal else 'triagem temática pendente'
        ident=any(id in unresolved_nodes for id in ids)
        # Não incluir sinal literal isolado como pertinência final.
        core=when=='no período' and academic and bool(supported)
        proposal=when=='no período' and academic and (bool(supported) or title_signal)
        countries=sorted({c for r in rr for c in r['countries']})
        unit={'obra_id':uid,'estado':'provisório; definição nacional em aberto',
              'suporte_tematico':theme,'suporte_documental':'compatível com escopo' if academic else 'tipo pendente',
              'suporte_temporal':when,'evidencia_temporal':why,'datas_publicacao':';'.join(dates),
              'anos_publicacao':';'.join(years),'divergencia_ano':int(len(set(years))>1),
              'ano_defesa':';'.join(sorted({r['defense'] for r in rr if r['defense']})),
              'titulo':next((r['title'] for r in rr if r['source']=='OpenAlex'),rr[0]['title']),
              'autoria':next((r['author'] for r in rr if r['source']=='OpenAlex'),rr[0]['author']),
              'tipos':';'.join(kind),'dois':';'.join(sorted({r['doi'] for r in rr if r['doi']})),
              'fontes':';'.join(sorted({r['source'] for r in rr})),
              'ids_openalex':';'.join(sorted(id for id in ids if id in oa)),
              'codigos_base':';'.join(sorted(r['base_code'] for r in rr if r['base_code'])),
              'registros_origem':len(ids),'nucleo_com_evidencia_temática':int(core),
              'candidato_pre_corpus':int(proposal),'identidade_residual':int(ident),
              'paises_afiliacao_openalex':';'.join(countries),
              'nacionalidade':'pendente de definição; BR disponível' if 'BR' in countries else 'pendente de definição; sem BR explícito ou sem afiliação',
              'complementar_sem_openalex':int(not any(id in oa for id in ids))}
        units.append(unit)
        for r in rr:
            provenance.append({'obra_id':uid,'registro':r['node'],'fonte':r['source'],
                               'record_id':r['record_id'],'source_record_id':r['source_id'],
                               'source_run_id':r['run_id'],'raw_file':r['raw_file'],
                               'coletado_em':r['collected'],'data_publicacao_original':r['date'],
                               'ano_publicacao_original':r['year'],'ano_defesa_original':r['defense'],
                               'tipo_original':r['original_type'],'titulo_original':r['title'],
                               'autoria_original':r['author'],'doi_original_normalizado':r['doi'],
                               'tema_previo':r['theme'],'evidencia_tema':r['theme_note'],
                               'vinculo_goias_previo':r['goias']})
        reasons=['definir produção brasileira']
        if ident:reasons.append('identidade pode reduzir contagem')
        if when!='no período':reasons.append('publicação no corte não comprovada')
        if not academic:reasons.append('decidir natureza acadêmica do tipo')
        if not supported:reasons.append('confirmar pertinência substantiva; sinal não basta')
        if len(set(years))>1:reasons.append('anos de publicação divergentes; não escolher silenciosamente')
        pending.append({'obra_id':uid,'prioridade':1 if ident or core or unit['divergencia_ano'] else 2 if proposal else 3,
                        'pendencias':';'.join(reasons),'fontes':unit['fontes'],'codigos_base':unit['codigos_base'],
                        'ids_openalex':unit['ids_openalex'],'registros_origem':len(ids),
                        'efeito':'inclusão nacional; '+('contagem única; ' if ident else '')+('revisão Goiás: avaliar sinais e defesa separadamente' if unit['codigos_base'] else 'não inferir Goiás da ausência de sinais')})
    # Amostra reproduzível para conferência, sem estimativa de acurácia.
    rng=random.Random(20261115)
    buckets=defaultdict(list)
    for u in units:
        bucket='núcleo com leitura' if u['nucleo_com_evidencia_temática'] else 'sinal no título' if u['candidato_pre_corpus'] else 'demais pendentes'
        buckets[bucket].append(u)
    sample=[]
    for bucket,items in sorted(buckets.items()):
        for u in rng.sample(items,min(10,len(items))):
            id=(u['ids_openalex'].split(';')[0] if u['ids_openalex'] else 'BASE:'+u['codigos_base'].split(';')[0])
            r=records[id]
            sample.append({'obra_id':u['obra_id'],'estrato':bucket,'titulo':r['title'],
                           'tipo':r['original_type'],'resumo':r['abstract'],
                           'suporte_temporal':u['suporte_temporal'],'raw_file':r['raw_file']})
    OUT.mkdir()
    dump('Registro de unidades.csv',units,list(units[0]))
    dump('Pre corpus tematico.csv',[u for u in units if u['candidato_pre_corpus']],list(units[0]))
    dump('Corpus nacional provisorio.csv',[u for u in units if u['nucleo_com_evidencia_temática']],list(units[0]))
    dump('Obras complementares incorporadas provisoriamente.csv',[u for u in units if u['complementar_sem_openalex'] and u['nucleo_com_evidencia_temática']],list(units[0]))
    dump('Proveniencia.csv',provenance,list(provenance[0]))
    dump('Conciliacao de identidades.csv',edges,list(edges[0]))
    dump('Pendencias residuais.csv',pending,list(pending[0]))
    dump('Amostra para conferencia.csv',sample,list(sample[0]))
    coverage=[]
    for f in sorted({r['source'] for r in records.values()}):
        pp=[p for p in provenance if p['fonte']==f]
        ids={p['obra_id'] for p in pp};uu=[u for u in units if u['obra_id'] in ids]
        coverage.append({'fonte':f,'registros':len(pp),'unidades_sustentadas_por_identidade':len(ids),
                         'unidades_com_openalex':sum(bool(u['ids_openalex']) for u in uu),
                         'unidades_sem_openalex':sum(not bool(u['ids_openalex']) for u in uu),
                         'nucleo_com_leitura':sum(u['nucleo_com_evidencia_temática'] for u in uu),
                         'pre_corpus':sum(u['candidato_pre_corpus'] for u in uu)})
    dump('Cobertura atualizada.csv',coverage,list(coverage[0]))
    assert len(provenance)==len(records)==13748
    assert sum(u['registros_origem'] for u in units)==13748
    assert len({p['registro'] for p in provenance})==13748
    assert all((ROOT/p['raw_file']).exists() for p in provenance)
    assert sum(c['registros'] for c in coverage)==13748
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    result={'inputs_sha256':hashes,'registros':len(records),'registros_openalex':len(oa),'linhas_base':len(base),
            'unidades':len(units),'reducoes_por_identidade':len(records)-len(units),
            'pares':dict(Counter((e['origem']+' / '+e['decisao']) for e in edges)),
            'pares_residuais':sum(e['efeito_residual']=='pode alterar contagem' for e in edges),
            'pre_corpus':sum(u['candidato_pre_corpus'] for u in units),
            'nucleo_com_leitura':sum(u['nucleo_com_evidencia_temática'] for u in units),
            'complementares_nucleo':sum(u['complementar_sem_openalex'] and u['nucleo_com_evidencia_temática'] for u in units),
            'unidades_so_complementares':sum(u['complementar_sem_openalex'] for u in units),
            'anos_divergentes':sum(u['divergencia_ano'] for u in units),
            'temporal':dict(Counter(u['suporte_temporal'] for u in units)),
            'amostra':len(sample),'checagens':'IDs, hashes, 125 páginas, cursores, datas, proveniência, soma registros e cobertura reconciliados.'}
    (OUT/'Auditoria.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
