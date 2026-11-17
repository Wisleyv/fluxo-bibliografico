"""Mede sobreposição local; não coleta, não altera triagem nem decide elegibilidade."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from openpyxl import load_workbook
from scripts.conferir_identidades_openalex_20261115 import SAME, REVIEW, TITLE_ONLY
from scripts.conciliar_pares_confirmados_20261115 import pares_confirmados
from scripts.preanalise_e_validacao_20261115 import cabecalhos
from scripts.preparar_piloto_20261115 import normalizar_doi
from scripts.normalize_collection import _parse_ris

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / 'dados/analises'
OUT = A / 'marco1'
BASE = A / 'triagem_criterio_defesa_20261115.xlsx'
FOUND = 'mesma obra confirmada'
PENDING = 'candidato em revisão'
ABSENT = 'não recuperado no OpenAlex'
UNKNOWN = 'não verificável'
CATEGORIES = (FOUND, PENDING, ABSENT, UNKNOWN)

# Notas de conferência individual, com comparação dos campos arquivados.
NOTES = {
 '220d5042': 'Sufixo Junior omitido no OpenAlex; DOI, título, ano e segundo autor concordam.',
 '91146316': 'Autoria OpenAlex truncada em María de Fátima; DOI, título, ano, fascículo 53 e páginas 149–167 sustentam identidade; não corrigir autoria.',
 '8558b71c': 'Título CAPES sem subtítulo; DOI, dois autores, ano e volume 28(2) concordam.',
 '25b844fb': 'CAPES omite subtítulo; Marcela Amaral abreviada no OpenAlex; DOI, primeira autora, ano e volume 11(2) sustentam identidade.',
 '320aed50': 'Título inglês traduz o título português; DOI, autora, ano e páginas 148–174 concordam.',
 '64b40852': 'Título SciELO tem professor redundante ao final; DOI, três autores, ano e volume 103(265) concordam.',
 '2511e505': 'Título SciELO tem XXI redundante ao final; DOI, autores, ano e volume 37(75) concordam.',
 'e2fdf173': 'Título inglês traduz o português; nomes expandidos compatíveis; DOI, ano e periódico concordam.',
 '89d30495': 'Título inglês/português equivalentes; DOI, seis autores compatíveis, ano e volume 35(1) concordam.',
 '5c2ab78c': 'Título inglês traduz o português; DOI e Agnaldo Arroio concordam; Santos/Santos-Ebinuma compatível. Ano 2015 na origem versus 2014 no OpenAlex permanece conflito temporal, sem mudança dos anos.',
 '8819ba66': 'Variação Val/Alves e Maria Souza abreviada; DOI, título, ano e Cláudio Pires Viana concordam; afiliações já arquivadas na base registram Valdirene Alves de Oliveira e Maria Souza.',
 '4348c88f': 'DOI atípico 10.5216/10.5216 não é âncora suficiente. Título/ano e vários nomes coincidem; OpenAlex localiza repositório LA Referencia/UFG, sem link de origem na base que confirme identidade. Mantido para conferência bibliográfica; não declarado obra distinta.',
}


def read(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write(name, rows, fields=None):
    with (OUT / name).open('x', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def classify(found, pending, identifiable):
    if found:
        return FOUND
    if pending:
        return PENDING
    return ABSENT if identifiable else UNKNOWN


def metrics(rows):
    c = Counter(r['categoria'] for r in rows)
    d = c[FOUND] + c[ABSENT]
    return {'total_origem': len(rows), **{k: c[k] for k in CATEGORIES},
            'numerador_confirmado': c[FOUND], 'denominador_verificavel': d,
            'cobertura_verificavel_pct': round(100*c[FOUND]/d, 4) if d else '',
            'confirmado_sobre_total_pct': round(100*c[FOUND]/len(rows), 4) if rows else '',
            'revisao_excluida_denominador': c[PENDING],
            'nao_verificavel_excluido_denominador': c[UNKNOWN]}


def period(year):
    if not year:
        return 'sem ano'
    return '2007–2019' if 2007 <= int(year) <= 2019 else '2020–2026' if 2020 <= int(year) <= 2026 else 'fora de 2007–2026'


def main():
    if OUT.exists():
        raise FileExistsError('Diretório de resultados já existe; preservar a rodada.')
    inputs = [BASE, A/'openalex_busca_restrita_20261115.csv',
              A/'openalex_identidades_conferidas_20261115.csv',
              A/'openalex_correspondencias_candidatas_20261115.csv']
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    csv.field_size_limit(2**30)
    w = load_workbook(BASE, data_only=True)
    s = w['Triagem']
    values = iter(s.values)
    header = next(values)
    rows = [dict(zip(header, v)) for v in values if v[0]]
    base = {r['Código']: r for r in rows}
    historical = pares_confirmados(w, s, cabecalhos(s), {r['Código']: n for n,r in enumerate(rows,2)})
    w.close()
    works = {r['openalex_id']:r for r in read(inputs[1])}
    old = read(inputs[2])
    candidates = read(inputs[3])
    assert len(base) == len(rows) == 1317 and len(works) == 12431
    assert len(old) == len(candidates) == 689
    assert {(p['openalex_id'],p['codigo_base']) for p in old} == {(p['openalex_id'],p['codigo_base']) for p in candidates}
    assert Counter(r['classificacao'] for r in old) == {SAME:116, REVIEW:52, TITLE_ONLY:521}
    # Localização dos RIS originais por DOI, sem reescrever metadados.
    ris = defaultdict(list)
    for folder in ('portal-capes','scielo'):
        for path in sorted((ROOT/'dados/brutos'/folder).glob('*.ris')):
            for record, _ in _parse_ris(path):
                doi = normalizar_doi(' '.join(record.get('DO', [])))
                if doi:
                    ris[doi].append((path, record))
    decisions = []
    for p in old:
        assert p['codigo_base'] in base and p['openalex_id'] in works
        q = dict(p)
        q['classe_anterior'] = q.pop('classificacao')
        q['decisao_marco1'] = FOUND if q['classe_anterior'] == SAME else PENDING
        q['fundamento'] = 'Correspondência estrita sustentada anteriormente; reaproveitada.' if q['classe_anterior'] == SAME else 'Título isolado não estabelece identidade; candidato preservado para revisão.'
        q['ris_origem'] = ''
        q['pagina_openalex'] = works[p['openalex_id']]['pagina_origem']
        if q['classe_anterior'] == REVIEW:
            code = p['codigo_base']
            # Todos os 52 foram conferidos nesta rodada; apenas 4348c88f fica inconclusivo.
            assert p['doi_igual'] == '1' and p['tipo_artigo_igual'] == '1'
            records = ris[normalizar_doi(p['doi_base'])]
            assert records, f'RIS ausente para {code}'
            q['ris_origem'] = ';'.join(sorted({str(path.relative_to(ROOT)) for path,_ in records}))
            q['fundamento'] = NOTES.get(code, 'DOI, título, ano e tipo concordantes; autoria individualmente conferida: nomes expandidos/abreviados, partículas, et al. ou sufixos compatíveis. Nenhum conflito que indique outra obra; não se corrigem autores.')
            q['decisao_marco1'] = PENDING if code == '4348c88f' else FOUND
        decisions.append(q)
    # Componentes de identidade: só pares históricos confirmados e correspondências aceitas.
    parent = {c:c for c in base}
    def find(c):
        while parent[c] != c:
            parent[c] = parent[parent[c]]
            c = parent[c]
        return c
    def union(a,b):
        a,b = find(a),find(b)
        parent[max(a,b)] = min(a,b)
    for a,b in historical:
        union(a,b)
    by_oa = defaultdict(list)
    for p in decisions:
        if p['decisao_marco1'] == FOUND:
            by_oa[p['openalex_id']].append(p['codigo_base'])
    for codes in by_oa.values():
        for c in codes[1:]:
            union(codes[0],c)
    groups = defaultdict(list)
    for code in base:
        groups[find(code)].append(code)
    confirmed = defaultdict(set)
    pending = defaultdict(set)
    for p in decisions:
        target = confirmed if p['decisao_marco1'] == FOUND else pending
        target[find(p['codigo_base'])].add(p['openalex_id'])
    detail = []
    for r in rows:
        code = r['Código']; group = find(code)
        year = r['Ano de publicação'] or r['Ano de defesa'] or ''
        basis = 'publicação' if r['Ano de publicação'] else 'defesa' if r['Ano de defesa'] else 'ausente'
        identifiable = bool(r['Título'] and (r['Autoria'] or r['DOI']))
        status = classify(confirmed[group], pending[group], identifiable)
        detail.append({'codigo_base':code, 'grupo_identidade_observada':group,
                       'fonte':r['Fonte'], 'tipo_documental':r['Tipo de produção'] or 'não informado',
                       'base_temporal':basis, 'ano':str(year), 'periodo':period(year),
                       'categoria':status, 'ids_confirmados':';'.join(sorted(confirmed[group])),
                       'ids_candidatos_nao_resolvidos':';'.join(sorted(pending[group])),
                       'titulo':r['Título'], 'autoria':r['Autoria'] or '', 'doi':r['DOI'] or '',
                       'limite':'Correspondência na busca arquivada; classe por linha, sem elegibilidade.' if status==FOUND else
                           'Candidato pendente; não tratado como ausência.' if status==PENDING else
                           'Sem candidato pelos identificadores e título normalizado nas tabelas locais; ausência no snapshot recuperado, não no índice completo.' if status==ABSENT else
                           'Metadados insuficientes para a regra de comparação.'})
    matrices=[]
    dimensions = [(),('fonte',),('fonte','base_temporal','periodo','tipo_documental'),('fonte','base_temporal','ano','tipo_documental')]
    for dims in dimensions:
        buckets=defaultdict(list)
        for r in detail:
            buckets[tuple(r[d] for d in dims)].append(r)
        for key, records in sorted(buckets.items()):
            matrices.append({'nivel':'+'.join(dims) or 'total',
                             **{d:(key[dims.index(d)] if d in dims else 'todos') for d in ('fonte','base_temporal','periodo','ano','tipo_documental')}, **metrics(records)})
    # Grupos só com evidência confirmada; título isolado não faz fusão.
    units=[]
    lookup={r['codigo_base']:r for r in detail}
    for group,codes in sorted(groups.items()):
        cats={lookup[c]['categoria'] for c in codes}
        status=classify(confirmed[group],pending[group], all(lookup[c]['categoria']!=UNKNOWN for c in codes))
        units.append({'grupo_identidade_observada':group, 'codigos_base':';'.join(sorted(codes)),
                      'fontes':';'.join(sorted({base[c]['Fonte'] for c in codes})),
                      'linhas_origem':len(codes), 'categoria':status,
                      'ids_confirmados':';'.join(sorted(confirmed[group])),
                      'titulo_representante':base[min(codes)]['Título'],
                      'limite':'Unidade provisória: agrupamento apenas por identidades sustentadas, sem deduplicação exaustiva.'})
    overlaps=[]
    sources=sorted({r['Fonte'] for r in rows})
    for i,a in enumerate(sources):
        for b in sources[i+1:]:
            gs=[u for u in units if a in u['fontes'].split(';') and b in u['fontes'].split(';')]
            overlaps.append({'fonte_a':a,'fonte_b':b,'grupos_confirmados_compartilhados':len(gs),
                             'grupos_com_openalex':sum(u['categoria']==FOUND for u in gs),
                             'grupos_sem_confirmacao_openalex':sum(u['categoria']!=FOUND for u in gs)})
    OUT.mkdir()
    write('Pares auditados.csv', decisions)
    write('Revisao dos 52 pares.csv',[p for p in decisions if p['classe_anterior']==REVIEW])
    write('Registros de controle classificados.csv',detail)
    write('Matriz de cobertura.csv',matrices)
    write('Unidades e sobreposicao.csv',units)
    write('Sobreposicao entre fontes.csv',overlaps)
    exclusive=[u for u in units if u['categoria']==ABSENT]
    write('Exclusivos observados complementares.csv',exclusive, list(units[0]))
    assert len(detail)==sum(Counter(r['categoria'] for r in detail).values())==1317
    assert sum(u['linhas_origem'] for u in units)==1317
    assert all(sum(p[k] for k in CATEGORIES)==p['total_origem'] for p in matrices)
    for dims in dimensions[1:]:
        assert sum(m['total_origem'] for m in matrices if m['nivel']=='+'.join(dims))==1317
    assert all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==value for name,value in hashes.items())
    review=[p for p in decisions if p['classe_anterior']==REVIEW]
    audit={'input_sha256':hashes,'linhas_controle':len(detail),'pares_historicos_reaproveitados':len(historical),
           'pares_openalex_anteriores':116, 'revisao_52':dict(Counter(p['decisao_marco1'] for p in review)),
           'pares_apos_revisao':dict(Counter(p['decisao_marco1'] for p in decisions)),
           'controle_por_categoria':metrics(detail),'unidades_provisorias':len(units),
           'exclusivos_observados_grupos_provisorios':len(exclusive),
           'exclusivos_observados_linhas':sum(u['linhas_origem'] for u in exclusive),
           'fontes':{f:metrics([r for r in detail if r['fonte']==f]) for f in sources},
           'checks':{'1317_linhas_reconciliadas':True,'estratos_reconciliados':True,'entradas_inalteradas':True,'40_pares_historicos_conferidos':True}}
    with (OUT/'Auditoria.json').open('x',encoding='utf8') as f:
        json.dump(audit,f,ensure_ascii=False,indent=2)
    print(json.dumps(audit,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
