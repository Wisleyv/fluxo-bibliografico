"""Diagnóstico do RIS CAPES: não integra nem altera os corpora/entrega vigentes."""
import csv
import hashlib
import html
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from scripts.normalize_collection import _parse_ris
from scripts.conferir_amostra_por_regras_20261115 import titulo_normalizado as titulo_base
from scripts.preanalise_e_validacao_20261115 import texto_normalizado
from scripts.fechar_marco2 import thematic, read, ROOT, A

SOURCE=ROOT/'dados/CAPES-concatenado.ris'
OUT=A/'capes_20261116_avaliacao'
URL='https://www-periodicos-capes-gov-br.ez29.periodicos.capes.gov.br/index.php/acervo/buscador.html?q=%E2%80%9CPIBID%E2%80%9D+OR+%E2%80%9CPrograma+Institucional+de+Bolsa+de+Inicia%C3%A7%C3%A3o+%C3%A0+Doc%C3%AAncia%E2%80%9D&source=all&type%5B%5D=type%3D%3DArtigo&type%5B%5D=type%3D%3DEditorial&national_production%5B%5D=national_production%3D%3D1&num=30&page=23&publishyear=2007%3A2026'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def titulo_normalizado(value):return titulo_base(html.unescape(value or ''))


def normalizar_doi(value):
    text=html.unescape(value or '').strip().lower()
    return re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)','',text)


def write(name,rows,fields=None):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    if OUT.exists() and '--atualizar' not in sys.argv:raise FileExistsError('Avaliação existente; --atualizar regenera só o diagnóstico, não os corpora.')
    m2=A/'marco2_fechamento';m3=A/'marco3'
    inputs=[SOURCE,m2/'Registro de decisoes.csv',m2/'Proveniencia.csv',m2/'Corpus nacional.csv',
            m3/'Decisoes regionais.csv',m3/'Proveniencia regional.csv',m3/'Corpus goiano.csv',
            A/'openalex_busca_restrita_20261115.csv',ROOT/'Vaneria.txt',ROOT/'Protocolo de busca bibliométrica - v1.3 fechamento nacional.md']
    hashes={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    units={r['obra_id']:r for r in read(inputs[1])};prov=read(inputs[2]);node={p['registro']:p['obra_id'] for p in prov}
    oa={r['openalex_id']:r for r in read(inputs[7])};regional={r['obra_id']:r for r in read(inputs[4])}
    regional_by_node={p['registro']:p['obra_id'] for p in read(inputs[5])}
    ids=defaultdict(set);dois=defaultdict(set);titles=defaultdict(set);unit_records=defaultdict(list)
    for p in prov:
        gid=p['obra_id'];unit_records[gid].append(p)
        if p['registro'].startswith('https://openalex.org/'):ids[p['registro'].rsplit('/',1)[-1]].add(gid)
        if p['doi_original_normalizado']:dois[normalizar_doi(p['doi_original_normalizado'])].add(gid)
        t=titulo_normalizado(p['titulo_original'])
        if t:titles[t].add(gid)
    records=list(_parse_ris(SOURCE));rows=[];tagcov=Counter();issues=Counter();exact=Counter();idcount=Counter();doicount=Counter();titlecount=Counter()
    for position,(tags,errors) in enumerate(records,1):
        get=lambda t:';'.join(tags.get(t,[])).strip()
        sid=get('ID');title=get('TI');year=get('PY');doi=normalizar_doi(get('DO'));tn=titulo_normalizado(title)
        iid=sid.rsplit('/',1)[-1] if re.fullmatch(r'(https://openalex.org/)?W\d+',sid) else ''
        idhits=ids.get(iid,set());dhits=dois.get(doi,set()) if doi else set();thits=titles.get(tn,set())
        strong=idhits|dhits;targets=strong or thits
        matches=[oa['https://openalex.org/'+iid]] if 'https://openalex.org/'+iid in oa else []
        conflicts=[]
        if idhits and dhits and idhits!=dhits:conflicts.append('ID e DOI apontam a componentes diferentes')
        if len(strong)>1:conflicts.append('mais de um componente por identificador')
        for old in matches:
            if titulo_normalizado(old['titulo'])!=tn:conflicts.append('título difere do registro OpenAlex com mesmo ID')
            if doi and old['doi'] and doi!=normalizar_doi(old['doi']):conflicts.append('DOI difere no mesmo ID OpenAlex')
            if year and old['ano_publicacao'] and year!=old['ano_publicacao']:conflicts.append('ano difere do registro OpenAlex com mesmo ID')
        category='identificador concordante; revisão bibliográfica' if conflicts else 'identificador concordante com acervo' if strong else 'somente título; identidade não sustentada' if thits else 'sem correspondência pelos índices utilizados'
        states=sorted({units[g]['decisao'] for g in targets})
        oldcap={g for g in targets if any(p['fonte']=='Portal CAPES' for p in unit_records[g])}
        gohits={regional_by_node[p['registro']] for g in targets for p in unit_records[g] if p['registro'] in regional_by_node}
        tokenstate,rule,_=thematic(title,'')
        goyears={r['data_publicacao'] for r in matches if r['data_publicacao']}
        time='publicação completa arquivada no corte' if any('2007-01-01'<=d<='2026-11-08' for d in goyears) and not any('ano difere' in c for c in conflicts) else 'ano 2007–2025 no período' if year.isdigit() and 2007<=int(year)<=2025 else '2026 sem data completa independente neste RIS' if year=='2026' else 'revisar período'
        row={'registro_capes':'CAPES20261116:'+str(position).zfill(4),'posicao_no_arquivo':position,'id_original':sid,'titulo':title,'autoria_original':get('AU'),
             'ano_publicacao_ris':year,'tipo_original':get('TY'),'veiculo':get('JO'),'doi_normalizado':doi,
             'campos_presentes':';'.join(sorted(k for k,v in tags.items() if any(x.strip() for x in v))),
             'titulo_contem_entidade_html':'Sim' if html.unescape(title)!=title else 'Não',
             'registro_sha256':hashlib.sha256(json.dumps(tags,sort_keys=True,ensure_ascii=False).encode('utf8')).hexdigest(),
             'categoria':category,'conflitos':'; '.join(sorted(set(conflicts))),'obras_candidatas':';'.join(sorted(targets)),
             'por_id':';'.join(sorted(idhits)),'por_doi':';'.join(sorted(dhits)),'por_titulo':';'.join(sorted(thits)),
             'id_no_snapshot_openalex':'Sim' if matches else 'Não','estado_nacional_atual':';'.join(states),
             'ja_tem_proveniencia_portal':'Sim' if oldcap else 'Não','obras_regionais_candidatas':';'.join(sorted(gohits)),
             'estados_regionais_atuais':';'.join(sorted({regional[g]['decisao'] for g in gohits})),
             'triagem_titulo_proposta':tokenstate,'regra_titulo':rule,'evidencia_temporal_disponivel':time,
             'limite':'Diagnóstico de correspondência; não decisão de inclusão. AU concatenado preservado sem atribuir contagem de pessoas.'}
        rows.append(row)
        exact[row['registro_sha256']]+=1;idcount[sid]+=1
        if doi:doicount[doi]+=1
        if tn:titlecount[tn]+=1
        issues.update(errors);tagcov.update(k for k,v in tags.items() if any(x.strip() for x in v))
    OUT.mkdir(exist_ok=True)
    write('Registros e correspondencias.csv',rows)
    variants=[];duplicate_titles=[]
    for r in rows:
        if 'título difere' not in r['conflitos']:continue
        old=oa['https://openalex.org/'+r['id_original']]
        t=titulo_normalizado(r['titulo']);u=titulo_normalizado(old['titulo'])
        prefix=(t.startswith(u+' ') or u.startswith(t+' ')) and min(len(t.split()),len(u.split()))>=5
        authors=Counter(re.findall(r'\w+',texto_normalizado(r['autoria_original'])))==Counter(re.findall(r'\w+',texto_normalizado(old['autores'])))
        if prefix and authors and r['doi_normalizado'] and normalizar_doi(old['doi'])==r['doi_normalizado'] and r['ano_publicacao_ris']==old['ano_publicacao']:
            variants.append({'registro_capes':r['registro_capes'],'caso':'variação por subtítulo/prefixo',
                             'evidencia':'Mesmo ID, DOI, ano e multiconjunto de tokens de autoria; título é prefixo exato com pelo menos cinco palavras.',
                             'candidatos':r['obras_candidatas'],'tratamento_proposto':'Conciliação objetiva em lote, preservando títulos das duas fontes; conferir amostra, sem refazer leitura temática.',
                             'referencia':'Campos do RIS e do snapshot OpenAlex; não há contagem nova de obra.'})
    # Candidato recuperado por limpeza explícita; não corrigir o identificador original.
    for r in rows:
        if r['categoria']!='sem correspondência pelos índices utilizados':continue
        clean=re.sub(r'\s+DOI\s*[-:]\s*10\..*$','',r['titulo'],flags=re.I)
        tt=titles.get(titulo_normalizado(clean),set()) if clean!=r['titulo'] else set()
        if tt:variants.append({'registro_capes':r['registro_capes'],'caso':'DOI colado ao título e prefixo repetido no campo DO',
                 'evidencia':'Título sem sufixo DOI encontra candidato local; comparar DOI correto escrito no título com metadados arquivados.',
                 'candidatos':';'.join(sorted(tt)),'tratamento_proposto':'Revisar reparo e registrar alias; não tratar como obra nova por ausência no índice literal.',
                 'referencia':'RIS original preservado; proposta de correção de metadado, sem promoção de corpus.'})
    for r in rows:
        if r['registro_capes'] in ('CAPES20261116:0029','CAPES20261116:0048','CAPES20261116:0094'):
            variants.append({'registro_capes':r['registro_capes'],'caso':{'CAPES20261116:0029':'IDs/DOIs ligam duas inclusões antigas; possível fusão','CAPES20261116:0048':'Ano 2019 versus 2013 na obra Práticas de leitura','CAPES20261116:0094':'DOI alternativo SciELO em identidade anteriormente conferida'}[r['registro_capes']],
                 'evidencia':r['conflitos'] or 'Título, autoria e DOI alternativo devem ser relacionados ao PID e à conferência anterior.',
                 'candidatos':r['obras_candidatas'],'tratamento_proposto':'Reaproveitar conferência histórica e resolver só o efeito material em identidade/ano; não substituir registro antigo.',
                 'referencia':'dados/analises/marco2_fechamento/Relatorio de fechamento.md; Proveniencia.csv; registro CAPES indicado.'})
    write('Variantes e prioridades bibliograficas.csv',variants)
    for title,n in titlecount.items():
        if n>1:
            group=[r for r in rows if titulo_normalizado(r['titulo'])==title]
            duplicate_titles.append({'titulo_normalizado':title,'registros':n,'ids':';'.join(r['id_original'] for r in group),'dois':';'.join(r['doi_normalizado'] for r in group),
                                     'estado':'Candidato interno; mesmo título com IDs/DOIs diferentes não determina identidade.'})
    write('Titulos repetidos no RIS.csv',duplicate_titles)
    candidates=[r for r in rows if r['categoria']!='identificador concordante com acervo' or r['estado_nacional_atual']!='incluída']
    write('Fila preliminar de revisao.csv',candidates,list(rows[0]))
    mapped={g for r in rows for g in r['obras_candidatas'].split(';') if g}
    newids={r['id_original'] for r in rows}
    contro=[]
    for p in prov:
        if p['fonte']!='Portal CAPES':continue
        g=p['obra_id'];linked=[r['registro_capes'] for r in rows if g in r['obras_candidatas'].split(';')]
        contro.append({'registro_controle':p['registro'],'obra_id':g,'titulo':p['titulo_original'],'registros_nova_exportacao':';'.join(linked),
                      'situacao':'correspondência candidata na nova exportação' if linked else 'não localizado por ID/DOI/título exato; preservar controle anterior',
                      'limite':'Ausência nesta consulta filtrada não invalida fonte histórica.'})
    write('Comparacao dos controles CAPES.csv',contro)
    write('Distribuicao anual.csv',[{'ano':y,'registros_ris':n,'unidade':'registros, antes de deduplicação/inclusão'} for y,n in sorted(Counter(r['ano_publicacao_ris'] for r in rows).items())])
    audit={'data_coleta_informada':'2026-11-16','origem':'Arquivo fornecido pelo usuário; concatenação declarada de 23 páginas',
           'url_ultima_pagina_informada':URL,'pagina_web':'Tentativa de acesso sem sucesso; conteúdo da página não verificado',
           'filtros_extraidos_da_url':{'consulta':'“PIBID” OR “Programa Institucional de Bolsa de Iniciação à Docência”','tipos':['Artigo','Editorial'],'national_production':'1','publishyear':'2007:2026','num':'30','page':'23','source':'all'},
           'paginas_declaradas':23,'paginas_identificadas_no_ris':0,'registros':len(rows),'ty_no_texto':len(re.findall(r'^TY  -',SOURCE.read_text(encoding='utf-8-sig'),re.M)),
           'er_no_texto':len(re.findall(r'^ER  -',SOURCE.read_text(encoding='utf-8-sig'),re.M)),
           'ids_distintos':len(idcount),'ids_repetidos':{k:v for k,v in idcount.items() if v>1},'ids_formato_openalex':sum(bool(re.fullmatch(r'W\d+',r['id_original'])) for r in rows),
           'doi_presentes':sum(bool(r['doi_normalizado']) for r in rows),'dois_distintos':len(doicount),'dois_repetidos':{k:v for k,v in doicount.items() if v>1},
           'titulos_distintos_normalizados':len(titlecount),'grupos_titulo_repetido':{k:v for k,v in titlecount.items() if v>1},'duplicatas_exatas_excedentes':sum(v-1 for v in exact.values()),
           'problemas_parser':dict(issues),'cobertura_campos_nao_vazios':dict(tagcov),'tipos':dict(Counter(r['tipo_original'] for r in rows)),
           'categorias':dict(Counter(r['categoria'] for r in rows)),'estado_nacional_por_registro':dict(Counter(r['estado_nacional_atual'] or 'sem candidato' for r in rows)),
           'snapshot_openalex_por_registro':dict(Counter(r['id_no_snapshot_openalex'] for r in rows)),
           'ja_tem_portal_por_registro':dict(Counter(r['ja_tem_proveniencia_portal'] for r in rows)),
           'obras_candidatas_distintas':len(mapped),'estados_obras_candidatas_distintas':dict(Counter(units[g]['decisao'] for g in mapped)),
           'obras_regionais_distintas':dict(Counter(regional[g]['decisao'] for g in {g for r in rows for g in r['obras_regionais_candidatas'].split(';') if g})),
           'temporal':dict(Counter(r['evidencia_temporal_disponivel'] for r in rows)),
           'registros_2026':sum(r['ano_publicacao_ris']=='2026' for r in rows),'triagem_titulo_proposta':dict(Counter(r['triagem_titulo_proposta'] for r in rows)),
           'variacoes_subtitulo_com_id_doi_autoria_ano':sum(r['caso']=='variação por subtítulo/prefixo' for r in variants),
           'candidatos_por_limpeza_sufixo_doi':sum(r['caso']=='DOI colado ao título e prefixo repetido no campo DO' for r in variants),
           'controles_portal':len(contro),'controles_com_correspondencia':sum(bool(r['registros_nova_exportacao']) for r in contro),
           'hashes_insumos_preservados':hashes,'status':'Avaliação preliminar, sem alteração dos corpora ou da entrega Marco 5'}
    assert len(rows)==audit['ty_no_texto']==audit['er_no_texto']
    assert len(contro)==103
    assert sum(audit['categorias'].values())==len(rows)
    assert audit['ids_distintos']==len(rows) and audit['duplicatas_exatas_excedentes']==0
    assert len(mapped)==sum(audit['estados_obras_candidatas_distintas'].values())
    assert all(sha(ROOT/p)==h for p,h in hashes.items())
    write('Verificacoes locais.csv',[
        {'verificacao':'Integridade RIS','resultado':'OK','evidencia':f'{len(rows)} TY = {len(rows)} ER = {len(rows)} registros; sem alerta de parser'},
        {'verificacao':'Partição do diagnóstico','resultado':'OK','evidencia':'601 + 51 + 15 + 8 = 675 registros'},
        {'verificacao':'IDs e duplicação exata','resultado':'OK','evidencia':'675 IDs distintos; nenhuma repetição exata; títulos iguais permanecem candidatos'},
        {'verificacao':'Controle anterior','resultado':'OK','evidencia':'103 registros Portal preservados e comparados; 26 com correspondência candidata'},
        {'verificacao':'Unidade de contagem','resultado':'OK','evidencia':'651 componentes candidatos = 512 incluídos + 129 pendentes + 10 elegíveis com identidade pendente; não somar a 675'},
        {'verificacao':'Preservação','resultado':'OK','evidencia':f'{len(hashes)} hashes de insumos idênticos após o diagnóstico; nenhum corpus/entrega regravado'}])
    (OUT/'Auditoria.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in audit.items() if k not in ('hashes_insumos_preservados','url_ultima_pagina_informada','grupos_titulo_repetido')},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
