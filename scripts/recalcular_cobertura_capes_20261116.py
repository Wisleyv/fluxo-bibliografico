"""Etapa 5: cobertura CAPES e delta dos indicadores; sem nova entrega Excel."""
import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter,defaultdict
from itertools import combinations_with_replacement
from pathlib import Path
import re
from scripts.avaliar_capes_20261116 import A,ROOT,read,sha
from scripts.entregar_marco5 import save_csv

MANIFEST=A/'integracao_capes_20261116/elegibilidade/Manifesto de execucao.json'
SAME='mesma obra confirmada'
REVIEW='candidato em revisão'
MISSING='não recuperado na consulta OpenAlex arquivada'
UNVERIFIABLE='não verificável para o corte de publicação'
CLASSES=(SAME,REVIEW,MISSING,UNVERIFIABLE)


def classify(record,linked,has_openalex):
    if linked and has_openalex:return SAME
    if linked:
        return UNVERIFIABLE if record['ano_publicacao_ris']=='2026' else MISSING
    if record['obras_candidatas']:return REVIEW
    year=record['ano_publicacao_ris']
    if not year.isdigit() or int(year)==2026:return UNVERIFIABLE
    return MISSING


def coverage(rows):
    c=Counter(r['classe_cobertura'] for r in rows);den=len(rows)-c[REVIEW]-c[UNVERIFIABLE]
    return {'registros':len(rows),**{k:c[k] for k in CLASSES},'numerador_confirmado':c[SAME],
            'denominador_verificavel':den,'fracao_confirmada_verificavel_pct':100*c[SAME]/den if den else '',
            'confirmados_sobre_total_pct':100*c[SAME]/len(rows) if rows else '',
            'unidade':'registros CAPES; não obras únicas','limite':'Consulta CAPES filtrada coletada em 16/11 versus snapshot OpenAlex coletado em 15/11, corte 08/11; não completude do índice.'}


def period(years):
    ys={int(y) for y in years.split(';') if y.isdigit()}
    if ys and all(y<2020 for y in ys):return '2007–2019'
    if ys and all(y>=2020 for y in ys):return '2020–2026'
    return 'período divergente/não informado'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--atualizar',action='store_true');parser.add_argument('--recalcular',action='store_true');args=parser.parse_args()
    run=json.loads(MANIFEST.read_text(encoding='utf8'));data=ROOT/run['diretorio_nacional'];out=ROOT/run['diretorio_indicadores_proposto']
    if (out/'Cobertura CAPES por registro.csv').exists() and not args.atualizar:raise FileExistsError('Cobertura existente; preservar ou usar --atualizar.')
    baseline={r['arquivo']:r['sha256'] for r in read(A/'marco4/Inventario de produtos.csv') if r['arquivo'].replace('\\','/').startswith('dados/analises/marco4/')}
    assert all(sha(ROOT/p)==h for p,h in baseline.items()),'Resultados anteriores alterados'
    logs=[]
    if args.recalcular:
        for module in ['produzir_indicadores_marco4','documentar_conferencias_marco4','verificar_marco4']:
            command=[sys.executable,'-X','utf8','-m','scripts.'+module,'--manifesto',str(MANIFEST)]
            if args.atualizar:command.append('--atualizar')
            result=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf8',errors='replace')
            logs.append({'modulo':module,'codigo_saida':result.returncode,'saida':result.stdout})
            assert result.returncode==0,result.stdout
    prov=read(data/'Proveniencia.csv');registry={r['obra_id']:r for r in read(data/'Registro de decisoes.csv')}
    nids={r['obra_id'] for r in read(data/'Corpus nacional.csv')};sources=defaultdict(set);bywork=defaultdict(list)
    for p in prov:sources[p['obra_id']].add(p['fonte']);bywork[p['obra_id']].append(p)
    pointers={r['registro']:r for r in read(data/'Ponte registro CAPES componente.csv')}
    records=read(A/'capes_20261116_avaliacao/Registros e correspondencias.csv');raw_oa={r['openalex_id'].rsplit('/',1)[-1] for r in read(A/'openalex_busca_restrita_20261115.csv')}
    rows=[]
    for r in records:
        p=pointers[r['registro_capes']];gid=p['obra_id'];linked=p['estado_identidade']=='conciliada'
        has_oa=any(x['registro'].startswith('https://openalex.org/') for x in bywork[gid])
        rows.append({'registro_capes':r['registro_capes'],'id_original':r['id_original'],'obra_id':gid,'titulo':r['titulo'],
            'fonte':'Portal CAPES — coleta 16/11/2026','ano_ris':r['ano_publicacao_ris'],'periodo_ris':period(r['ano_publicacao_ris']),
            'tipo_ris':r['tipo_original'],'id_no_snapshot':'Sim' if r['id_original'] in raw_oa else 'Não',
            'estado_identidade':p['estado_identidade'],'classe_cobertura':classify(r,linked,has_oa),
            'estado_nacional':registry[gid]['decisao'],'incluida_no_corpus':'Sim' if gid in nids else 'Não',
            'criterio_temporal':r['evidencia_temporal_disponivel'],
            'limite':'Identidade conciliada não equivale a elegibilidade; ausência na consulta arquivada não significa inexistência no OpenAlex.'})
    save_csv(out/'Cobertura CAPES por registro.csv',rows)
    matrix=[{'nivel':'total','categoria':'todos',**coverage(rows)}]
    for field in ('periodo_ris','ano_ris','tipo_ris','estado_identidade'):
        for value in sorted({r[field] for r in rows}):matrix.append({'nivel':field,'categoria':value,**coverage([r for r in rows if r[field]==value])})
    save_csv(out/'Matriz de cobertura CAPES.csv',matrix)
    eligible={g:sources[g] for g in nids};names=sorted(set().union(*eligible.values()));overlaps=[]
    for a,b in combinations_with_replacement(names,2):overlaps.append({'fonte_a':a,'fonte_b':b,'obras_compartilhadas':sum(a in s and b in s for s in eligible.values()),'denominador_corpus':len(nids),
        'unidade':'obras únicas incluídas','estado':'consolidado no corpus observado; não completude; interseções não aditivas'})
    save_csv(out/'Sobreposicao fontes corpus elegivel.csv',overlaps)
    combos=Counter(';'.join(sorted(s)) for s in eligible.values())
    save_csv(out/'Combinacoes exclusivas de fontes.csv',[{'fontes':s,'obras':n,'denominador_corpus':len(nids),'estado':'Combinações disjuntas no corpus observado'} for s,n in sorted(combos.items())])
    indicators={r['obra_id']:r for r in read(out/'Obras dos indicadores.csv') if r['escopo']=='nacional'}
    cells=[('total','todos',nids)]
    for label,field in [('periodo','periodo'),('tipo_documental','tipo_indicador')]:
        vals={g:period(indicators[g]['anos_publicacao']) if field=='periodo' else indicators[g][field] for g in nids}
        cells.extend((label,v,{g for g in nids if vals[g]==v}) for v in sorted(set(vals.values())))
    venn=[]
    for level,value,gids in cells:
        c=Counter(('ambas' if {'OpenAlex','Portal CAPES'}<=eligible[g] else 'somente OpenAlex' if 'OpenAlex' in eligible[g] else 'somente Portal CAPES' if 'Portal CAPES' in eligible[g] else 'outras fontes sem as duas') for g in gids)
        venn.append({'nivel':level,'categoria':value,'obras_no_estrato':len(gids),**{s:c[s] for s in ['ambas','somente OpenAlex','somente Portal CAPES','outras fontes sem as duas']},
            'unidade':'obras únicas elegíveis','escopo_capes':'União das rodadas CAPES históricas e de 16/11; tipos e anos do corpus canônico.'})
    save_csv(out/'OpenAlex CAPES por periodo e tipo.csv',venn)
    lot_ids={r['obra_id'] for r in rows if r['estado_identidade']=='conciliada'};lot_n=lot_ids&nids
    oldprov=read(A/'marco2_fechamento/Proveniencia.csv');old_nids={r['obra_id'] for r in read(A/'marco2_fechamento/Corpus nacional.csv')}
    master_map={'M2-d0c27c83901c3376':'M2-a279c6aac5c92b01'}
    old_portal={master_map.get(p['obra_id'],p['obra_id']) for p in oldprov if p['fonte']=='Portal CAPES' and p['obra_id'] in old_nids}
    levels=[{'medida':'Coincidência nominal de ID','numerador':sum(r['id_no_snapshot']=='Sim' for r in rows),'denominador':675,'unidade':'registros RIS','limite':'Não é identidade validada nem sobreposição por obras elegíveis'},
        {'medida':'Vínculos com componentes conciliados','numerador':sum(r['estado_identidade']=='conciliada' for r in rows),'denominador':675,'unidade':'registros RIS','limite':'Inclui obras pendentes e uma obra de controle sem OpenAlex no snapshot'},
        {'medida':'Mesma obra confirmada com snapshot OpenAlex','numerador':matrix[0]['numerador_confirmado'],'denominador':matrix[0]['denominador_verificavel'],'unidade':'registros verificáveis','limite':'Exclui três revisões e um caso temporal não verificável; não mede completude'},
        {'medida':'Obras elegíveis recuperadas na nova rodada CAPES','numerador':len(lot_n),'denominador':len(nids),'unidade':'obras incluídas','limite':'Mesmas obras do corpus nacional; recuperação adicional não é inclusão nova'},
        {'medida':'Obras elegíveis CAPES — todas as rodadas','numerador':sum('Portal CAPES' in s for s in eligible.values()),'denominador':len(nids),'unidade':'obras incluídas','limite':'União por obra; inclui controles anteriores, sem duplicar rodadas'}]
    for r in levels:r['percentual']=100*r['numerador']/r['denominador']
    save_csv(out/'Niveis de sobreposicao CAPES OpenAlex.csv',levels)
    # Antes/depois das medidas principais e das frequências com mudança absoluta.
    audit=json.loads((out/'Auditoria.json').read_text(encoding='utf8'));old_audit=json.loads((A/'marco4/Auditoria.json').read_text(encoding='utf8'))
    delta=[]
    for scope in ('nacional','goiano'):
        for key in ('N','autoria','instituicao','geografia','tematicas','goias'):
            a=old_audit['corpora'][scope][key];b=audit['corpora'][scope][key]
            delta.append({'escopo':scope,'indicador':key,'antes':a,'depois':b,'diferenca':b-a,'unidade':'obras no corpus observado'})
    for filename,key,count in [('Evolucao nacional.csv','ano','obras_com_ano_univoco'),('Tipos documentais nacional.csv','categoria','obras'),('Coautoria nacional.csv','categoria','obras')]:
        old={r[key]:int(r[count]) for r in read(A/'marco4'/filename)};new={r[key]:int(r[count]) for r in read(out/filename)}
        for value in sorted(set(old)|set(new)):
            if old.get(value,0)!=new.get(value,0):delta.append({'escopo':'nacional','indicador':filename+': '+value,'antes':old.get(value,0),'depois':new.get(value,0),'diferenca':new.get(value,0)-old.get(value,0),'unidade':'obras'})
    delta.append({'escopo':'nacional','indicador':'Obras com recuperação Portal CAPES','antes':len(old_portal),'depois':sum('Portal CAPES' in s for s in eligible.values()),'diferenca':sum('Portal CAPES' in s for s in eligible.values())-len(old_portal),'unidade':'obras elegíveis; proveniência, não novas inclusões'})
    save_csv(out/'Comparacao antes depois.csv',delta)
    # Preservar a redação qualitativa já fundamentada; atualizar somente fatos
    # quantitativos afetados e acrescentar a contribuição documentada da CAPES.
    synthesis=(A/'marco4/Sintese das seis subquestoes.md').read_text(encoding='utf8')
    for old,new in [('7.780','7.779'),('5.968','5.967'),('7.753','7.752'),('3.271','3.270'),('54,34%','54,35%'),('99,96%','99,97%')]:synthesis=synthesis.replace(old,new)
    def adjust_link(match):
        link=match.group(1)
        if link=='../marco3/Pendencias%20regionais.csv':return '](../elegibilidade/Pendencias%20regionais.csv)'
        if link.startswith('../marco3/'):return '](../../marco3/'+link[len('../marco3/'):]+')'
        return match.group(0)
    synthesis=re.sub(r'\]\(([^)]+)\)',adjust_link,synthesis)
    opening=('> Versão após integração CAPES, com corpus nacional operacional de 7.779 obras. A versão anterior e sua redação permanecem preservadas. A fração observada de afiliação goiana identificada passa de 196/7.780 para **196/7.779**; ambas arredondam para 2,52%. O período comum permanece **67/3.459 (1,94%)**. Participação total não estimável.\n\n')
    synthesis=opening+synthesis
    q1=('A integração CAPES acrescenta proveniência de recuperação, não uma nova população de 675 obras. No novo lote, 665 registros têm vínculos bibliográficos conciliados, mas a sobreposição com o snapshot OpenAlex é de 664 registros confirmados, três em revisão, sete não recuperados e um temporalmente não verificável. O denominador verificável é 671; a fração confirmada é 664/671 (98,96%). Os 647/675 IDs coincidentes são medida nominal diferente. As consultas têm datas e filtros distintos; nenhuma dessas proporções comprova completude ou independência dos índices. Evidência: [matriz CAPES](Matriz%20de%20cobertura%20CAPES.csv), [níveis de sobreposição](Niveis%20de%20sobreposicao%20CAPES%20OpenAlex.csv) e [decisões por registro](Cobertura%20CAPES%20por%20registro.csv).\n\n')
    synthesis=synthesis.replace('## 2.',q1+'## 2.',1)
    q2=('No corpus nacional atualizado, 571 obras têm proveniência Portal CAPES considerando todas as rodadas; todas também têm recuperação OpenAlex neste conjunto observado. O novo lote recuperou 509 dessas obras; 21 já tinham proveniência Portal. Assim, 488 obras incluídas passaram a ter também essa proveniência, sem aumento do corpus. A fusão da publicação duplicada de 2016 explica a redução de uma unidade nacional. Afiliações e contexto regional não foram inferidos do filtro de produção nacional da interface CAPES. Evidência: [sobreposição elegível](OpenAlex%20CAPES%20por%20periodo%20e%20tipo.csv) e [comparação antes/depois](Comparacao%20antes%20depois.csv).\n\n')
    synthesis=synthesis.replace('## 3.',q2+'## 3.',1)
    synthesis += ('\nAlém das pendências regionais anteriores, a integração mantém dez ocorrências CAPES em componentes provisórios: uma com sinais de elegibilidade e identidade pendente, nove pendentes por critérios não sustentados. Nenhuma entra automaticamente na contagem confirmada. A fila regional adicional contém quatro ocorrências com publicação anterior a 2020 e seis pendentes, sem comprovação de vínculo goiano; não são dez obras novas nem alteração automática das 871 pendências históricas. As divergências de autoria CAPES continuam sinalizadas, com créditos do material arquivado preservados. Evidência: [delta de elegibilidade](../elegibilidade/Relatorio%20do%20delta%20de%20elegibilidade.md) e [alertas](Alertas%20de%20metadados.csv).\n')
    (out/'Sintese das seis subquestoes.md').write_text(synthesis,encoding='utf8')
    checks=[]
    def check(name,ok,evidence):
        assert ok,(name,evidence)
        checks.append({'verificacao':name,'resultado':'OK','evidencia':evidence})
    check('Partição dos registros CAPES',sum(matrix[0][k] for k in CLASSES)==675 and len(rows)==675,'664 confirmados + 3 revisões + 7 não recuperados + 1 não verificável')
    check('Estratos dos registros CAPES',all(sum(r['registros'] for r in matrix if r['nivel']==level)==675 for level in ['periodo_ris','ano_ris','tipo_ris','estado_identidade']),'Cada dimensão particiona os mesmos 675 registros; subtotais de dimensões diferentes não são somados')
    check('Denominador verificável',matrix[0]['denominador_verificavel']==671 and matrix[0]['numerador_confirmado']==664,'675 − 3 revisões − 1 temporal não verificável = 671')
    check('Vínculos de recuperação distintos de identidade OpenAlex',levels[0]['numerador']==647 and levels[1]['numerador']==665,'647 IDs nominais; 665 vínculos; 664 identidades com snapshot + 1 controle sem OA')
    check('Combinações exclusivas',sum(combos.values())==len(nids)==7779,'Todas as combinações disjuntas reconciliam ao corpus elegível')
    check('Estratos por período e tipo',all(sum(int(r[k]) for k in ['ambas','somente OpenAlex','somente Portal CAPES','outras fontes sem as duas'])==r['obras_no_estrato'] for r in venn),'Categorias mutuamente exclusivas dentro de cada estrato')
    check('Totais de estratos elegíveis',all(sum(r['obras_no_estrato'] for r in venn if r['nivel']==level)==len(nids) for level in ['periodo','tipo_documental']),'Cada dimensão elegível reconcilia às 7779 obras, sem duplicar anos discordantes dentro do mesmo período')
    check('União de rodadas CAPES',len(lot_n)==509 and len(old_portal)==83 and len(lot_n&old_portal)==21 and len(lot_n|old_portal)==571,'83 antigas + 509 novas recuperações por obra − 21 compartilhadas = 571')
    check('Sobreposição elegível OpenAlex CAPES',venn[0]['ambas']==571 and venn[0]['somente OpenAlex']==7206 and venn[0]['somente Portal CAPES']==0 and venn[0]['outras fontes sem as duas']==2,'571 + 7206 + 0 + 2 = 7779; não é comparação dos índices completos')
    check('Eixos preservados',read(out/'Indicadores dos eixos.csv')==read(A/'marco4/Indicadores dos eixos.csv'),'Nove frequências obra/eixo/estado idênticas à versão anterior')
    check('Correspondência regional preservada',read(out/'Correspondencia Goias Brasil.csv')==read(A/'marco4/Correspondencia Goias Brasil.csv'),'78/97 presentes no nacional; não usar 97/N como participação')
    check('Insumos dos indicadores preservados',all(sha(ROOT/p)==h for p,h in audit['hashes_entradas'].items()),f'{len(audit["hashes_entradas"])} hashes conferidos')
    check('Produtos anteriores preservados',all(sha(ROOT/p)==h for p,h in baseline.items()),f'{len(baseline)} arquivos históricos do Marco 4 conferidos por inventário')
    save_csv(out/'Verificacoes da integracao.csv',checks)
    summary={'etapa':'5 — cobertura, indicadores e respostas','estado':'cálculos e síntese atualizados e conferidos; nova entrega final permanece etapa posterior',
        'nacional':len(nids),'regional':97,'classes_capes':{k:matrix[0][k] for k in CLASSES},'denominador_verificavel':671,
        'ids_nominais':647,'vinculos_bibliograficos':665,'obras_elegiveis_novo_lote_capes':len(lot_n),'obras_elegiveis_capes_uniao':571,
        'proveniencia_capes_em_obras_previamente_sem_portal':len(lot_n-old_portal),'verificacoes_integracao':len(checks),
        'baseline_hashes_preservados':baseline,'manifesto_insumos':str(MANIFEST.relative_to(ROOT)),'limite':'Não gera planilhas Excel nem substitui a entrega anterior.'}
    (out/'Auditoria da integracao.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
    code_paths=[ROOT/'scripts'/n for n in ['produzir_indicadores_marco4.py','documentar_conferencias_marco4.py','verificar_marco4.py','recalcular_cobertura_capes_20261116.py','testar_indicadores_manifesto.py']]
    code_paths += [ROOT/'tests'/n for n in ['test_indicadores_capes_20261116.py','test_delta_capes_20261116.py','test_marco4.py']]
    output_manifest={'etapa':'5 — integração CAPES','estado':'cobertura, indicadores e síntese concluídos; entrega final ainda não gerada',
        'manifesto_entrada':str(MANIFEST.relative_to(ROOT)),'hash_manifesto_entrada':sha(MANIFEST),
        'diretorio_indicadores':str(out.relative_to(ROOT)),
        'proxima_etapa':'6 — regerar planilhas/gráficos, relatório metodológico e pacote em versão paralela',
        'diretorio_entrega_proposto':run['diretorio_entrega_proposto'],
        'hashes_codigo_etapa':{str(p.relative_to(ROOT)):sha(p) for p in code_paths}}
    (out/'Manifesto de saida.json').write_text(json.dumps(output_manifest,ensure_ascii=False,indent=2),encoding='utf8')
    if logs:(out/'Logs de execucao.json').write_text(json.dumps(logs,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in summary.items() if k!='baseline_hashes_preservados'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
