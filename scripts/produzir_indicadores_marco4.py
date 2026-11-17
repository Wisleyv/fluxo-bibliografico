"""Indicadores dos corpora congelados; apenas arquivos locais, sem novas decisões de corpus."""
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from scripts.executar_marco3 import ROOT, A, M2, OUT as M3, read, institution_signal
from scripts.preanalise_e_validacao_20261115 import texto_normalizado

OUT=A/'marco4'


def run_paths(manifest_path):
    """Resolver uma rodada sem mudar os padrões ou os resultados históricos."""
    manifest_path=Path(manifest_path)
    if not manifest_path.is_absolute():manifest_path=ROOT/manifest_path
    data=json.loads(manifest_path.read_text(encoding='utf8'))
    resolved={k:(ROOT/data[k]).resolve() for k in ('diretorio_nacional','diretorio_regional','diretorio_indicadores_proposto')}
    assert all(p.is_relative_to(ROOT.resolve()) for p in resolved.values()),'Caminho fora do projeto'
    target=resolved['diretorio_indicadores_proposto']
    assert target not in (resolved['diretorio_nacional'],resolved['diretorio_regional'],(A/'marco4').resolve()),'Preservar fontes e indicadores históricos'
    return manifest_path,data,resolved


MANIFEST=None;RUN={}
if '--manifesto' in sys.argv:
    MANIFEST,RUN,paths=run_paths(sys.argv[sys.argv.index('--manifesto')+1])
    M2=paths['diretorio_nacional'];M3=paths['diretorio_regional'];OUT=paths['diretorio_indicadores_proposto']
MATERIALS=M3/'Materiais locais.csv'
if not MATERIALS.exists():MATERIALS=A/'marco3/Materiais locais.csv'
TYPE={'article':'artigo','Artigo':'artigo','book-chapter':'capítulo','conference-paper':'trabalho em anais',
      'dissertation':'tese/dissertação sem grau discriminado','Tese':'tese','Dissertação':'dissertação',
      'book':'livro','conference-abstract':'resumo em anais','preprint':'preprint','editorial':'editorial',
      'book-review':'resenha','report':'relatório'}
INSTITUTION_AUTHOR=r'^(?:universidade|university|instituto federal|departamento|department|faculdade|faculty|college|campus|escola)\b'


def split(value):return {x.strip() for x in (value or '').split(';') if x.strip()}


def documentary_type(value):
    raw=split(value);types={TYPE.get(t,t) for t in raw}
    if types&{'tese','dissertação'}:types.discard('tese/dissertação sem grau discriminado')
    return '; '.join(sorted(types)) if types else 'não documentado'


def valid_author(name):return bool(name and not re.search(INSTITUTION_AUTHOR,texto_normalizado(name)))


def author_key(a,aliases=None,conflicts=None):
    au=a.get('author') or {}; name=au.get('display_name') or a.get('raw_author_name') or ''
    aid=au.get('id')
    if aid and conflicts and aid in conflicts:return aid,name
    return (aliases or {}).get(aid) or au.get('orcid') or aid or 'nome:'+texto_normalizado(name),name


def affiliation_state(authorships, flagged=False):
    if not authorships:return 'desconhecida'
    mapped=[bool(a.get('institutions')) for a in authorships]
    evidence=[bool(a.get('institutions') or a.get('raw_affiliation_strings')) for a in authorships]
    if all(mapped) and not flagged:return 'conhecida'
    return 'parcial' if any(evidence) else 'desconhecida'


def save(name,rows,fields=None):
    with (OUT/name).open('w' if '--atualizar' in sys.argv else 'x',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    if OUT.exists() and '--atualizar' not in sys.argv:raise FileExistsError('Preservar rodada existente; usar --atualizar somente para reconstruir seus produtos.')
    inputs=[M2/'Corpus nacional.csv',M2/'Registro de decisoes.csv',M2/'Proveniencia.csv',
            M3/'Corpus goiano.csv',M3/'Decisoes regionais.csv',M3/'Proveniencia regional.csv',M3/'Tres eixos.csv',
            M3/'Pendencias regionais.csv',ROOT/'Vaneria.txt',ROOT/'Plano de ação - realinhamento da coleta e análise.md',
            ROOT/'Protocolo de busca bibliométrica - v1.3 fechamento nacional.md']
    if MANIFEST:
        inputs += [MANIFEST,ROOT/RUN['protocolo_adendo'],ROOT/'dados/brutos/portal-capes/portal-capes__nacional-filtrado__20261116__RIS.ris']
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    national=read(inputs[0]); allnational={r['obra_id']:r for r in read(inputs[1])}
    regional=read(inputs[3]);axes=read(inputs[6]);nids={r['obra_id'] for r in national}
    sizes={'nacional':len(national),'goiano':len(regional)}
    np=read(inputs[2]);rp=read(inputs[5]);byprov=defaultdict(list)
    for p in np:byprov[('nacional',p['obra_id'])].append(p)
    for p in rp:byprov[('goiano',p['obra_id'])].append(p)
    node_national={p['registro']:p['obra_id'] for p in np}
    # Ler as páginas uma única vez: extração necessária de autoria/afiliação/tópicos,
    # não uma nova triagem semântica nem reclassificação de elegibilidade.
    needed={p['registro'] for p in np if p['obra_id'] in nids and p['registro'].startswith('https://openalex.org/')}
    needed|={p['registro'] for p in rp if p['obra_id'] in {r['obra_id'] for r in regional} and p['registro'].startswith('https://openalex.org/')}
    raw={}; rawpaths={}
    pages=sorted((ROOT/'dados/brutos/openalex/busca-restrita-20261115').glob('pagina_*.json'))
    for p in pages:
        hashes[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
        for w in json.loads(p.read_text(encoding='utf8'))['response']['results']:
            if w['id'] in needed:raw[w['id']]=w;rawpaths[w['id']]=str(p.relative_to(ROOT))
    assert needed<=raw.keys()
    OUT.mkdir(exist_ok=True)
    orcids=defaultdict(set)
    for w in raw.values():
        for au in w.get('authorships',[]):
            x=au.get('author') or {}
            if x.get('id') and x.get('orcid'):orcids[x['id']].add(x['orcid'])
    aliases={aid:next(iter(values)) for aid,values in orcids.items() if len(values)==1}
    conflicts={aid for aid,values in orcids.items() if len(values)>1}
    save('Referencia cruzada de autoria.csv',[{'openalex_author_id':aid,'orcids_arquivados':';'.join(sorted(values)),
          'tratamento':'ORCID unívoco propagado aos registros com o mesmo OpenAlex Author ID' if len(values)==1 else 'Conflito; conservar OpenAlex Author ID sem fusão por ORCID'} for aid,values in sorted(orcids.items())])
    cross=[]; regional_affirmed=set()
    for r in regional:
        targets={node_national[p['registro']] for p in byprov[('goiano',r['obra_id'])] if p['registro'] in node_national}
        matched=targets&nids
        assert len(matched)<=1
        if r['afiliacao_goias']=='Sim':regional_affirmed|=matched
        cross.append({'obra_goias':r['obra_id'],'titulo':r['titulo'],'componentes_nacionais':';'.join(sorted(targets)),
                      'incluida_no_nacional':'Sim' if matched else 'Não',
                      'estado_nacional_atual':';'.join(sorted({allnational[t]['decisao'] for t in targets})),
                      'afiliacao_goias_regional':r['afiliacao_goias'],'contexto_goias':r['contexto_goias_estado'],
                      'base_temporal_regional':r['criterio_temporal'],
                      'uso_na_proporcao':'Somente se afiliação sustentada no corpus nacional' if matched else 'Fora do denominador nacional congelado; não promover automaticamente'})
    units=[]; authorrows=[]; instrows=[]; countryrows=[]; topicrows=[]; keywordrows=[]; anomalies=[]
    for scope,corpus in [('nacional',national),('goiano',regional)]:
        for r in corpus:
            gid=r['obra_id'];pp=byprov[(scope,gid)]
            records=[raw[p['registro']] for p in pp if p['registro'] in raw]
            w=max(records,key=lambda w:(sum(valid_author(author_key(a)[1]) for a in w.get('authorships',[])),
                                       sum(bool(a.get('institutions')) for a in w.get('authorships',[])),w['id'])) if records else {}
            auth=w.get('authorships',[]);valid=[a for a in auth if valid_author(author_key(a)[1])]
            invalid=[a for a in auth if not valid_author(author_key(a)[1])]
            for a in invalid:anomalies.append({'escopo':scope,'obra_id':gid,'campo':'autoria institucional ou vazia','valor':author_key(a)[1],
                                              'tratamento':'Conservar no arquivo bruto; não ranquear como pessoa; cobertura de autoria sinalizada.'})
            integration_alert=allnational.get(gid,{}).get('alertas_integracao','')
            if integration_alert:anomalies.append({'escopo':scope,'obra_id':gid,'campo':'divergência de autoria CAPES em conciliação','valor':integration_alert,
                'tratamento':'Preservar autoria arquivada e seus créditos; não substituir por AU concatenado. Cobertura descreve autorias observadas, não validação de sua completude.'})
            persons={author_key(a,aliases,conflicts)[0]:author_key(a)[1] for a in valid}
            if not persons:
                nr=allnational.get(gid,{})
                names=split(r.get('autoria',nr.get('autoria','')))
                persons={'nome:'+texto_normalizado(s):s for s in names if valid_author(s)}
            inst={}
            for a in valid:
                for i in a.get('institutions',[]):
                    if i.get('display_name'):
                        key=i.get('id') or 'nome:'+texto_normalizado(i['display_name'])
                        inst[key]={'nome':i['display_name'],'pais':i.get('country_code') or 'não informado'}
            state=affiliation_state(valid,bool(invalid))
            manual_go=(gid in regional_affirmed) if scope=='nacional' else r['afiliacao_goias']=='Sim'
            go=any(institution_signal(i['nome']) for i in inst.values()) or manual_go
            if manual_go and state=='desconhecida':state='parcial'
            country={i['pais'] for i in inst.values() if i['pais']!='não informado'}
            years=split(r['anos_publicacao']);eligible_years={y for y in years if y.isdigit() and 2007<=int(y)<=2026}
            basis='publicação'; y=next(iter(eligible_years)) if len(eligible_years)==1 else 'divergente' if eligible_years else 'não informado'
            if scope=='goiano' and r['criterio_temporal'].startswith('defesa alternativa'):
                dy=split(r['anos_defesa']);y=next(iter(dy)) if len(dy)==1 else 'divergente';basis='defesa alternativa'
            type_evidence=r.get('tipos_sustentados') or ';'.join(p['tipo_original'] for p in pp)
            dtype=documentary_type(type_evidence)
            for key,name in persons.items():authorrows.append({'escopo':scope,'obra_id':gid,'autor_id':key,'nome':name,
                         'peso_integral':1,'peso_fracionario':1/len(persons),'identidade':'identificador arquivado' if not key.startswith('nome:') else 'nome sem desambiguação global',
                         'fonte':w.get('id','registro de autoria do corpus')})
            for key,i in inst.items():instrows.append({'escopo':scope,'obra_id':gid,'instituicao_id':key,'instituicao':i['nome'],
                              'pais':i['pais'],'peso_integral':1,'peso_fracionario':1/len(inst),
                              'afiliacao_goiana':'Sim' if institution_signal(i['nome']) else 'não identificada como goiana',
                              'fonte':w['id']})
            for c in sorted(country):countryrows.append({'escopo':scope,'obra_id':gid,'pais_afiliacao':c,'peso_integral':1,'peso_fracionario':1/len(country),'fonte':w['id']})
            topic=w.get('primary_topic') or {}
            if topic:topicrows.append({'escopo':scope,'obra_id':gid,'topico_id':topic['id'],'topico':topic['display_name'],
                                      'origem':'classificação algorítmica OpenAlex; não codificação dos autores','fonte':w['id']})
            for k in {x['id']:x for x in w.get('keywords',[]) if x.get('id')}.values():keywordrows.append({'escopo':scope,'obra_id':gid,'palavra_id':k['id'],
                                'palavra':k['display_name'],'origem':'palavra-chave algorítmica OpenAlex','fonte':w['id']})
            units.append({'escopo':scope,'obra_id':gid,'titulo':r['titulo'],'ano_serie':y,'fundamento_ano':basis,
                          'anos_publicacao':r['anos_publicacao'],'anos_defesa':r.get('anos_defesa',''),
                          'tipo_indicador':dtype,'tipos_origem':type_evidence,'autores_observados':len(persons),
                          'autores_com_id':sum(not k.startswith('nome:') for k in persons),'autorias_sinalizadas':len(invalid),
                          'coautoria_observada':'Sim' if len(persons)>1 else 'Não' if persons else 'não informada',
                          'cobertura_afiliacao':state,'instituicoes_mapeadas':len(inst),'afiliacao_goias_observada':'Sim' if go else 'não identificada',
                          'paises_conhecidos':';'.join(sorted(country)),'topico_disponivel':'Sim' if topic else 'Não',
                          'registro_metadados':w.get('id','sem OpenAlex; proveniência complementar'),
                          'arquivo_metadados':rawpaths.get(w.get('id',''),';'.join(sorted({p['raw_file'] for p in pp}))),
                          'contexto_goias_estado':r.get('contexto_goias_estado','não avaliado nacionalmente'),
                          'registros_openalex_do_componente':len(records),**({'alertas_integracao':integration_alert} if MANIFEST else {})})
    save('Obras dos indicadores.csv',units)
    save('Correspondencia Goias Brasil.csv',cross)
    save('Creditos de autoria.csv',authorrows);save('Creditos institucionais.csv',instrows);save('Creditos geograficos.csv',countryrows)
    save('Topicos por obra.csv',topicrows);save('Palavras chave por obra.csv',keywordrows)
    save('Alertas de metadados.csv',anomalies,['escopo','obra_id','campo','valor','tratamento'])
    tables={};coverage=[]
    for scope,N in sizes.items():
        ur=[r for r in units if r['escopo']==scope];assert len(ur)==N
        annual=[]
        for basis in sorted({r['fundamento_ano'] for r in ur}):
            rr=[r for r in ur if r['fundamento_ano']==basis]
            years=range(2007 if scope=='nacional' else 2020,2027)
            for y in years:
                count=sum(r['ano_serie']==str(y) for r in rr)
                uncertain=sum(r['ano_serie']=='divergente' and str(y) in split(r['anos_publicacao']) for r in rr) if basis=='publicação' else 0
                annual.append({'ano':str(y),'fundamento':basis,'obras_com_ano_univoco':count,'obras_divergentes_que_podem_pertencer_ao_ano':uncertain,
                               'limite_superior_por_ano':count+uncertain,'denominador_corpus':N,'nota':'2026 incompleto: corte 08/11; limites superiores não são aditivos'})
            for value in ('divergente','não informado'):
                count=sum(r['ano_serie']==value for r in rr)
                if count:annual.append({'ano':value,'fundamento':basis,'obras_com_ano_univoco':count,'obras_divergentes_que_podem_pertencer_ao_ano':0,'limite_superior_por_ano':count,'denominador_corpus':N,'nota':'Categoria residual separada; não atribuir ano silenciosamente'})
        save('Evolucao '+scope+'.csv',annual)
        def distribution(name,values):
            rows=[{'categoria':v,'obras':c,'denominador':N,'percentual':100*c/N} for v,c in Counter(values).most_common()]
            save(name+' '+scope+'.csv',rows);return rows
        types=distribution('Tipos documentais',[r['tipo_indicador'] for r in ur])
        distribution('Coautoria',[r['coautoria_observada'] for r in ur])
        for field,label in [('cobertura_afiliacao','afiliação'),('topico_disponivel','tópico principal OpenAlex')]:
            for value,count in Counter(r[field] for r in ur).items():coverage.append({'escopo':scope,'campo':label,'estado':value,'obras':count,'denominador':N,'percentual':100*count/N})
        for label,condition in [('autoria informada',lambda r:r['autores_observados']>0),('todos os autores com identificador',lambda r:r['autores_observados']>0 and r['autores_observados']==r['autores_com_id']),('instituição mapeada',lambda r:r['instituicoes_mapeadas']>0),('país de afiliação mapeado',lambda r:bool(r['paises_conhecidos']))]:
            c=sum(condition(r) for r in ur);coverage.append({'escopo':scope,'campo':label,'estado':'disponível','obras':c,'denominador':N,'percentual':100*c/N})
        for rows,key,label,filename in [(authorrows,'autor_id','nome','Autorias'),(instrows,'instituicao_id','instituicao','Instituicoes')]:
            agg=defaultdict(lambda: {'nomes':Counter(),'works':set(),'fraction':0.0})
            for r in rows:
                if r['escopo']!=scope:continue
                v=agg[r[key]];v['nomes'][r[label]]+=1;v['works'].add(r['obra_id']);v['fraction']+=r['peso_fracionario']
            ranked=[{'identificador':k,'nome':v['nomes'].most_common(1)[0][0],'variantes_observadas':';'.join(sorted(v['nomes'])),
                     'obras_contagem_integral':len(v['works']),'credito_fracionario':v['fraction'],'denominador_corpus':N,
                     'percentual_integral':100*len(v['works'])/N,'limite':'Identidades arquivadas; sem auditoria global de homônimos/fragmentações; somas integrais não aditivas'} for k,v in agg.items()]
            ranked.sort(key=lambda r:(-r['obras_contagem_integral'],r['nome']));save(filename+' '+scope+'.csv',ranked)
        for rows,key,name in [(countryrows,'pais_afiliacao','Geografia pais'),(topicrows,'topico','Tematicas OpenAlex'),(keywordrows,'palavra','Palavras chave OpenAlex')]:
            counts=Counter(r[key] for r in rows if r['escopo']==scope)
            rr=[{'categoria':k,'obras':v,'denominador_corpus':N,'percentual_no_corpus':100*v/N,
                 'obras_com_campo':len({r['obra_id'] for r in rows if r['escopo']==scope}),
                 'origem':'país de instituição em authorships OpenAlex' if rows is countryrows else 'classificação algorítmica OpenAlex',
                 'regra':'uma obra por categoria; categorias podem se sobrepor' if rows is not topicrows else 'um tópico principal por obra com tópico'} for k,v in counts.most_common()]
            save(name+' '+scope+'.csv',rr)
        tables[scope]={'N':N,'afiliacao':dict(Counter(r['cobertura_afiliacao'] for r in ur)),
                       'goias':sum(r['afiliacao_goias_observada']=='Sim' for r in ur),
                       'autoria':sum(r['autores_observados']>0 for r in ur),'instituicao':sum(r['instituicoes_mapeadas']>0 for r in ur),
                       'geografia':sum(bool(r['paises_conhecidos']) for r in ur),'tematicas':sum(r['topico_disponivel']=='Sim' for r in ur),
                       'tipos':types,'anos':annual,'coautoria':dict(Counter(r['coautoria_observada'] for r in ur))}
    save('Cobertura de campos.csv',coverage)
    ecounts=[]
    for axis in sorted({r['eixo'] for r in axes}):
        for state,c in Counter(r['estado'] for r in axes if r['eixo']==axis).items():
            ecounts.append({'eixo':axis,'estado':state,'obras':c,'denominador':sizes['goiano'],'percentual':100*c/sizes['goiano'],
                            'alcance':'Estado no material consultado, não medida de eficácia ou ausência do fenômeno'})
    save('Indicadores dos eixos.csv',ecounts)
    save('Evidencias dos eixos.csv',[{'subquestao':'4;6' if not r['eixo'].startswith('Relações') else '5;6',**r} for r in axes])
    regionalu=[r for r in units if r['escopo']=='goiano'];nu=[r for r in units if r['escopo']=='nacional']
    N=sizes['nacional'];G=sum(r['afiliacao_goias_observada']=='Sim' for r in nu)
    participation=[{'indicador':'Fração com afiliação goiana identificada no corpus nacional operacional','numerador':G,'denominador':N,'percentual':100*G/N,
                    'estado':'parcial — fração observada, não estimativa de participação total','justificativa':f'Mesmas {N} obras, período 2007–08/11/2026, tipos e regras nacionais; nenhum pendente/regional por defesa acrescentado. Afiliação desconhecida não é ausência.'},
                   {'indicador':'Participação total da produção goiana na produção nacional sobre PIBID','numerador':'não estimável','denominador':'universo nacional completo desconhecido','percentual':'não estimável','estado':'não estimável',
                    'justificativa':f'Corpus operacional e cobertura incompleta; afiliações parciais/desconhecidas e decisões nacionais residuais. Não dividir {sizes["goiano"]} por {N}.'},
                   {'indicador':'Obras da revisão regional incluídas no corpus nacional congelado','numerador':sum(r['incluida_no_nacional']=='Sim' for r in cross),'denominador':sizes['goiano'],'percentual':'não usar como participação nacional','estado':'consolidado no cruzamento','justificativa':'Correspondência por registros e componentes, sem promover decisões regionais automaticamente.'}]
    for state,c in Counter(r['contexto_goias_estado'] for r in regional).items():participation.append({'indicador':'Contexto regional: '+state,'numerador':c,'denominador':sizes['goiano'],'percentual':100*c/sizes['goiano'],'estado':'consolidado no corpus regional observado','justificativa':'Contexto separado de afiliação; não somar a contextos não examinados no nacional.'})
    save('Participacao e contexto Goias.csv',participation)
    comparable=[r for r in nu if split(r['anos_publicacao']) and all(y.isdigit() and 2020<=int(y)<=2026 for y in split(r['anos_publicacao']))]
    cg=sum(r['afiliacao_goias_observada']=='Sim' for r in comparable)
    save('Participacao periodo comum.csv',[{'periodo':'2020–08/11/2026 por publicação','obras_nacionais':len(comparable),
         'obras_com_afiliacao_goiana_identificada':cg,'percentual_observado':100*cg/len(comparable),
         'estado':'parcial — fração identificada no mesmo corpus e período; não participação total',
         'regra':'Subconjunto nacional; inclui divergências inteiramente dentro do intervalo; não usa ano de defesa nem promove pendentes regionais.'}])
    save('Divergencias de ano.csv',[r for r in units if r['ano_serie']=='divergente'],list(units[0]))
    audit={'hashes_entradas':hashes,'paginas_openalex':len(pages),'obras_openalex_lidas':len(raw),'corpora':tables,
           'correspondencia':dict(Counter(r['incluida_no_nacional'] for r in cross)),
           'alertas_de_autoria':len(anomalies),'multiplos_openalex_por_componente':sum(r['registros_openalex_do_componente']>1 for r in units),
           'autores_com_orcid_univoco':len(aliases),'autores_com_conflito_orcid':len(conflicts),
           'eixos':len(axes),'redes':'não produzidas; identidades de autoria não auditadas globalmente e afiliações incompletas; grupos não coletados',
           'uf_regiao':'não estimáveis integralmente; arquivos de authorships não contêm UF/região; somente sinal goiano validado e países'}
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    (OUT/'Auditoria.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in audit.items() if k not in ('hashes_entradas','corpora')},ensure_ascii=False,indent=2))
    print(json.dumps({s:{k:v for k,v in t.items() if k not in ('anos','tipos')} for s,t in tables.items()},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
