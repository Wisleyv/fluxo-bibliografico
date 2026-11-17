"""Etapa 4: delta de elegibilidade/metadados, sem nova coleta ou indicadores."""
import copy
import html
import json
import re
import sys
from collections import Counter, defaultdict
from scripts.avaliar_capes_20261116 import A, ROOT, read, sha, titulo_normalizado, normalizar_doi
from scripts.conciliar_capes_20261116 import MASTER, MERGED
from scripts.entregar_marco5 import save_csv
from scripts.fechar_marco2 import thematic
from scripts.executar_marco3 import GEO, institution_signal, texto_normalizado

BASE=A/'integracao_capes_20261116/conciliacao'
OUT=A/'integracao_capes_20261116/elegibilidade'


def values(text):return set(filter(None,(text or '').split(';')))


def author_tokens(text):
    return Counter(re.findall(r'\w+',texto_normalizado(html.unescape(text or ''))))


def assess_existing(unit, records):
    """Recuperação em uma fonte não promove/rebaixa elegibilidade por si só."""
    new_support=[]
    old_title_state=thematic(unit['titulo'],'')[0]
    for r in records:
        state,rule,excerpt=thematic(html.unescape(r['titulo']),'')
        if state=='incluir' and old_title_state!='incluir':
            new_support.append((r['registro_capes'],rule,excerpt))
    if unit['decisao']=='incluída':reason='Inclusão anterior preservada; identidade conciliada. Não rebaixar por título abreviado ou falta de resumo no RIS.'
    elif unit['decisao']=='elegível com identidade pendente':reason='Critérios nacionais já sustentados; nova recuperação não resolve a relação de identidade residual entre componentes.'
    else:reason='Manter pendência: novo RIS sem resumo/conteúdo substantivo adicional; recuperação e rótulo documental não bastam para resolver tema ou natureza acadêmica.'
    return unit['decisao'],reason,new_support


def assess_provisional(record):
    theme,rule,excerpt=thematic(html.unescape(record['titulo']),'')
    year=record['ano_publicacao_ris']
    temporal='Sim' if year.isdigit() and 2007<=int(year)<=2025 else 'Incerto'
    academic=record['tipo_original'].lower()=='article' and bool(record['veiculo'] and record['autoria_original'])
    state='elegível com identidade pendente' if theme=='incluir' and temporal=='Sim' and academic else 'pendente'
    reasons=['identidade não sustentada; componente provisório, não contar como obra confirmada']
    if theme!='incluir':reasons.append('pertinência temática insuficientemente sustentada pelo título; sem resumo no RIS')
    if temporal!='Sim':reasons.append('ano 2026 sem dia/mês; não demonstra publicação até 08/11/2026')
    if not academic:reasons.append('natureza acadêmica requer suporte adicional')
    return state,theme,temporal,academic,'; '.join(reasons),rule,excerpt


def main():
    if OUT.exists() and '--atualizar' not in sys.argv:raise FileExistsError('Etapa existente; --atualizar refaz somente os arquivos desta etapa.')
    paths=[BASE/n for n in ('Registro de decisoes.csv','Corpus nacional.csv','Proveniencia vinculada.csv','Registros CAPES integrados.csv','Pendencias CAPES.csv','Ponte de identidades.csv')]
    paths += [A/'marco3'/n for n in ('Decisoes regionais.csv','Corpus goiano.csv','Proveniencia regional.csv','Tres eixos.csv','Pendencias regionais.csv')]
    paths += [A/'openalex_busca_restrita_20261115.csv',ROOT/'dados/CAPES-concatenado.ris',ROOT/'Vaneria.txt',ROOT/'Protocolo de busca bibliométrica - v1.3 fechamento nacional.md']
    paths += [ROOT/'Protocolo de busca bibliométrica - v1.4 integração CAPES.md']
    hashes={str(p.relative_to(ROOT)):sha(p) for p in paths}
    assert sha(paths[12])==sha(ROOT/'dados/brutos/portal-capes/portal-capes__nacional-filtrado__20261116__RIS.ris')
    assert sha(paths[12])==json.loads((BASE.parent/'Manifesto.json').read_text(encoding='utf8'))['sha256_ris']
    original=read(paths[0]);units={r['obra_id']:dict(r) for r in original};prov=read(paths[2]);linked=read(paths[3]);unlinked=read(paths[4])
    oldprov=read(A/'marco2_fechamento/Proveniencia.csv')
    before=defaultdict(list)
    for p in oldprov:before[MASTER if p['obra_id']==MERGED else p['obra_id']].append(p)
    record_to_unit={r['registro_capes']:r['obra_id_confirmada'] for r in linked}
    touched=defaultdict(list)
    for r in linked:touched[r['obra_id_confirmada']].append(r)
    decisions=[];metadata=[];unseen_support=[]
    for gid,rr in sorted(touched.items()):
        u=units[gid];state,reason,support=assess_existing(u,rr)
        # A avaliação automática pode sinalizar evidência nova; não promovê-la silenciosamente.
        unseen_support += [{'obra_id':gid,'registro':node,'regra':rule,'trecho':excerpt} for node,rule,excerpt in support if u['decisao']!='incluída']
        decisions.append({'obra_id':gid,'unidade':'componente herdado','estado_antes':u['decisao'],'estado_depois':state,'tema_titulo_novo':'sinal adicional a examinar' if support else 'sem suporte positivo novo em relação ao título anterior',
                          'registros_capes':';'.join(r['registro_capes'] for r in rr),'decisao_delta':'preservar','fundamento':reason})
        known_dois={normalizar_doi(p['doi_original_normalizado']) for p in before[gid] if p['doi_original_normalizado']}
        for r in rr:
            diffs=[]
            if titulo_normalizado(r['titulo'])!=titulo_normalizado(u['titulo']):diffs.append('variante de título; original preservado')
            if r['ano_publicacao_ris'] and r['ano_publicacao_ris'] not in values(u['anos_publicacao']):diffs.append('ano discordante; preservar ano publicado anteriormente sustentado')
            if r['doi_normalizado'] and r['doi_normalizado'] not in known_dois:diffs.append('DOI adicional/divergente; vínculo de obra não valida automaticamente o DOI')
            if author_tokens(r['autoria_original'])!=author_tokens(u['autoria']):diffs.append('variante/lista de autoria; tokens diferentes não provam autores distintos nem autorizam substituir créditos')
            if not u['tipos_sustentados']:diffs.append('rótulo documental repetido não resolve suporte de conteúdo/natureza pendente')
            if diffs:metadata.append({'registro_capes':r['registro_capes'],'obra_id':gid,'campos':'; '.join(diffs),'titulo_capes':r['titulo'],'titulo_canonico_preservado':u['titulo'],
                                      'ano_capes':r['ano_publicacao_ris'],'anos_canonicos_preservados':u['anos_publicacao'],'doi_capes':r['doi_normalizado'],
                                      'acao':'Guardar na proveniência; não substituir metadado canônico sem evidência específica.',
                                      'excecao_documentada':'0048: publicação 2013, metadado CAPES 2019; 0134: DOI correto escrito no título e no snapshot, bruto com prefixo repetido preservado.'})
    assert not unseen_support,unseen_support
    provisionals=[];transfer=[];residual=[]
    for r in unlinked:
        gid='CAPES-PROVISORIO-'+r['registro_capes'][-4:]
        state,theme,temporal,academic,reason,rule,excerpt=assess_provisional(r)
        u={k:'' for k in original[0]}
        u.update(obra_id=gid,ids_anteriores=gid,decisao=state,titulo=html.unescape(r['titulo']),autoria=r['autoria_original'],fontes='Portal CAPES',registros_origem='1',
                 tipos_sustentados='article' if academic else '',tipos_sem_suporte='' if academic else r['tipo_original'],
                 criterio_tema=rule if theme=='incluir' else 'insuficiente',registro_evidencia=r['registro_capes'],trecho_evidencia=excerpt if theme=='incluir' else 'Sem resumo no RIS; recuperação não comprova pertinência.',
                 suporte_temporal='no período por ano 2007–2025' if temporal=='Sim' else 'insuficiente para corte em 08/11/2026',anos_publicacao=r['ano_publicacao_ris'],pendencias=reason,
                 interpretacao_nacional='escopo temático nacional aprovado; sem filtro geográfico; identidade provisória')
        units[gid]=u;provisionals.append(u)
        decisions.append({'obra_id':gid,'unidade':'componente novo provisório, não obra única confirmada','estado_antes':'registro sem destino de obra confirmado','estado_depois':state,
                          'tema_titulo_novo':theme,'registros_capes':r['registro_capes'],'decisao_delta':'fila provisória','fundamento':reason})
        p={k:'' for k in prov[0]};p.update(obra_id=gid,registro=r['registro_capes'],fonte='Portal CAPES',record_id=r['registro_capes'],source_record_id=r['id_original'],source_run_id='capes-nacional-filtrado-20261116',
             raw_file='dados/brutos/portal-capes/portal-capes__nacional-filtrado__20261116__RIS.ris',coletado_em='2026-11-16',ano_publicacao_original=r['ano_publicacao_ris'],tipo_original=r['tipo_original'],
             titulo_original=r['titulo'],autoria_original=r['autoria_original'],doi_original_normalizado=r['doi_normalizado'],evidencia_tema=reason,obra_id_antes_conciliacao='sem identidade confirmada')
        prov.append(p);record_to_unit[r['registro_capes']]=gid
        residual.append({**r,'componente_provisorio':gid,'estado_elegibilidade':state,'pendencia_elegibilidade':reason})
        oldyear=r['ano_publicacao_ris'].isdigit() and int(r['ano_publicacao_ris'])<2020
        transfer.append({'registro_capes':r['registro_capes'],'componente_provisorio':gid,'titulo':r['titulo'],'ano_publicacao':r['ano_publicacao_ris'],
                         'estado_regional_preliminar':'Fora do período regional por publicação' if oldyear else 'Pendente; não incorporar à revisão',
                         'vinculo_goias':'Não comprovado no material; não significa ausência','fundamento':'Artigo publicado antes de 2020; não converter em exclusão nacional.' if oldyear else reason+'; vínculo com Goiás não comprovado',
                         'limite':'Fila adicional de registros; não somar como obras únicas nem às 871 pendências anteriores.'})
    # Alertas de autoria permanecem ligados também ao componente candidato, sem mudar seus créditos.
    alerts=defaultdict(list)
    for r in unlinked:
        for target in values(r['obras_candidatas']):alerts[target].append(r['registro_capes']+': '+r['regra_integracao'])
    by=defaultdict(list)
    for p in prov:
        p['estado_identidade']='provisória; não contar como obra confirmada' if p['obra_id'].startswith('CAPES-PROVISORIO-') else 'herdada da conciliação; ver decisão da obra'
        p['doi_para_correspondencia']=p['doi_original_normalizado']
        p['ajuste_de_chave']=''
        if p['registro']=='CAPES20261116:0134':
            p['doi_para_correspondencia']='10.5752/p.2318-7344.2013v1n1p13';p['ajuste_de_chave']='Prefixo repetido corrigido só na chave comparativa; DOI literal confirmado no título e no snapshot W2141262701.'
        by[p['obra_id']].append(p)
    for gid,u in units.items():
        u['registros_origem']=str(len(by[gid]));u['fontes']=';'.join(sorted({p['fonte'] for p in by[gid]}))
        u['estado_identidade_integracao']='provisória' if gid.startswith('CAPES-PROVISORIO-') else 'componente herdado'
        u['alertas_integracao']=' | '.join(alerts[gid])
        u['anos_publicacao_observados']=';'.join(sorted({p['ano_publicacao_original'] for p in by[gid] if p['ano_publicacao_original']}))
    # Atualizar apenas proveniência e ponte da revisão regional, preservando decisões/eixos.
    region=read(paths[6]);rprov=read(paths[8]);axes=read(paths[9]);node_to_n={p['registro']:p['obra_id'] for p in prov}
    n_to_r=defaultdict(set)
    for r in region:
        r['obra_id_antes_integracao']=r['obra_id']
        if r['obra_id']==MERGED:r['obra_id']=MASTER
    for p in rprov:
        if p['obra_id']==MERGED:p['obra_id']=MASTER
        if p['registro'] in node_to_n:n_to_r[node_to_n[p['registro']]].add(p['obra_id'])
    assert all(len(gids)==1 for gids in n_to_r.values())
    regional_ids={r['obra_id'] for r in region};oa={r['openalex_id'].rsplit('/',1)[-1]:r for r in read(paths[11])}
    new_geo=[]
    for r in linked:
        if r['obra_id_confirmada'] in n_to_r:continue
        if re.search(GEO,texto_normalizado(r['titulo'])) or institution_signal(oa.get(r['id_original'],{}).get('instituicoes','')):new_geo.append(r['registro_capes'])
    assert not new_geo,('Sinal regional novo requer revisão',new_geo)
    prior_rnodes={p['registro'] for p in rprov};added=0
    for p in prov:
        if p['obra_id'] not in n_to_r or p['registro'] in prior_rnodes:continue
        q={k:p.get(k,'') for k in rprov[0]};q['obra_id']=next(iter(n_to_r[p['obra_id']]));rprov.append(q);prior_rnodes.add(q['registro']);added+=1
    rby=defaultdict(list)
    for p in rprov:rby[p['obra_id']].append(p)
    for r in region:
        r['registros_origem']=str(len(rby[r['obra_id']]))
        r['ids_openalex']=';'.join(sorted({p['registro'] for p in rby[r['obra_id']] if p['registro'].startswith('https://openalex.org/')}))
        r['componentes_nacionais']=';'.join(sorted({node_to_n[p['registro']] for p in rby[r['obra_id']] if p['registro'] in node_to_n}))
        r['anos_publicacao_observados']=';'.join(sorted({p['ano_publicacao_original'] for p in rby[r['obra_id']] if p['ano_publicacao_original']}))
    OUT.mkdir(exist_ok=True)
    save_csv(OUT/'Registro de decisoes.csv',list(units.values()))
    save_csv(OUT/'Corpus nacional.csv',[r for r in units.values() if r['decisao']=='incluída'])
    save_csv(OUT/'Proveniencia.csv',prov)
    save_csv(OUT/'Delta de elegibilidade.csv',decisions)
    save_csv(OUT/'Divergencias de metadados.csv',metadata)
    save_csv(OUT/'Componentes provisorios CAPES.csv',[units[r['obra_id']] for r in provisionals])
    save_csv(OUT/'Pendencias CAPES.csv',residual)
    save_csv(OUT/'Pendencias residuais nacionais.csv',[r for r in units.values() if r['decisao']!='incluída'])
    save_csv(OUT/'Decisoes regionais.csv',region);save_csv(OUT/'Corpus goiano.csv',[r for r in region if r['decisao']=='Incluir'])
    save_csv(OUT/'Proveniencia regional.csv',rprov);save_csv(OUT/'Tres eixos.csv',axes)
    save_csv(OUT/'Pendencias regionais.csv',[r for r in region if r['decisao']=='Pendente'])
    save_csv(OUT/'Fila de transferencia regional.csv',transfer)
    save_csv(OUT/'Ponte registro CAPES componente.csv',[{'registro':r,'obra_id':g,'estado_identidade':'provisória' if g.startswith('CAPES-PROVISORIO-') else 'conciliada'} for r,g in sorted(record_to_unit.items())])
    counts=Counter(u['decisao'] for u in units.values())
    assert len(prov)==14423 and len({p['registro'] for p in prov})==14423
    assert sum(int(u['registros_origem']) for u in units.values())==14423
    assert len(record_to_unit)==675 and len(units)==13231 and counts['incluída']==7779
    assert len(region)==len(regional_ids)==1529 and sum(r['decisao']=='Incluir' for r in region)==97
    assert sum(r['decisao']=='Pendente' for r in region)==871
    assert len(axes)==291 and Counter((r['obra_id'],r['eixo'],r['estado']) for r in axes)==Counter((r['obra_id'],r['eixo'],r['estado']) for r in read(paths[9]))
    assert all(sha(ROOT/p)==h for p,h in hashes.items())
    summary={'estado':'Etapa 4 concluída até o limite da evidência local; indicadores e entrega ainda não atualizados',
             'componentes_herdados_avaliados':len(touched),'estados_herdados':dict(Counter(units[g]['decisao'] for g in touched)),
             'promocoes_de_pendencias_a_inclusao':0,'novas_obras_confirmadas':0,'exclusoes_nacionais_novas':0,
             'componentes_provisorios_adicionados':10,'estados_provisorios':dict(Counter(r['decisao'] for r in provisionals)),
             'componentes_nacionais':len(units),'estados_nacionais':dict(counts),'registros_proveniencia':len(prov),
             'capes_registros_vinculados_a_identidade_conciliada':665,'capes_registros_identidade_provisoria':10,
             'corpus_goiano':97,'extracoes_eixos':291,'pendencias_regionais_preservadas':871,
             'registros_adicionais_proveniencia_regional':added,'registros_proveniencia_regional':len(rprov),
             'componentes_regionais_com_recuperacao_capes':len({r['obra_id_confirmada'] for r in linked if r['obra_id_confirmada'] in n_to_r}),
             'fila_regional_adicional':dict(Counter(r['estado_regional_preliminar'] for r in transfer)),
             'divergencias_metadados_registradas':len(metadata),'insumos_preservados_sha256':hashes}
    (OUT/'Verificacoes.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
    manifest={'etapa':'elegibilidade CAPES 20261116','coleta_capes':'2026-11-16','coleta_openalex':'2026-11-15','corte_publicacao':'2026-11-08',
              'diretorio_nacional':str(OUT.relative_to(ROOT)),'diretorio_regional':str(OUT.relative_to(ROOT)),
              'diretorio_indicadores_proposto':'dados/analises/integracao_capes_20261116/indicadores',
              'diretorio_entrega_proposto':'dados/entregas/marco5_capes_20261116',
              'estado':'Insumos prontos para recalcular indicadores; entrega anterior preservada',
              'protocolo_adendo':'Protocolo de busca bibliométrica - v1.4 integração CAPES.md'}
    (OUT/'Manifesto de execucao.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in summary.items() if k!='insumos_preservados_sha256'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
