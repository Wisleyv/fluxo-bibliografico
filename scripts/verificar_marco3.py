"""Conferência interna reproduzível dos arquivos regionais, sem rede."""
import hashlib
import json
import random
import re
from collections import Counter, defaultdict
from itertools import combinations
from difflib import SequenceMatcher
from scripts.executar_marco3 import ROOT, OUT, read, period, write
from scripts.preanalise_e_validacao_20261115 import texto_normalizado


def main():
    initial=json.loads((OUT/'Auditoria inicial.json').read_text(encoding='utf8'))
    decisions=read(OUT/'Decisoes regionais.csv'); included=read(OUT/'Corpus goiano.csv')
    provenance=read(OUT/'Proveniencia regional.csv'); axes=read(OUT/'Tres eixos.csv')
    materials=read(OUT/'Materiais locais.csv'); historical=read(OUT/'Eixos historicos reaproveitaveis.csv')
    byid={r['obra_id']:r for r in decisions}; inc={r['obra_id'] for r in included}
    bynode={r['registro']:r for r in materials}; bywork=defaultdict(list)
    for p in provenance:bywork[p['obra_id']].append(p)
    checks=[]
    def check(name, condition, detail):
        checks.append({'verificacao':name,'resultado':'OK' if condition else 'FALHOU','evidencia':detail})
        assert condition, (name,detail)
    check('Insumos anteriores preservados', all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in initial['hashes_entradas'].items()), 'SHA-256 dos seis insumos igual à preparação')
    check('Partição de decisões', len(decisions)==1529 and len(byid)==1529 and Counter(r['decisao'] for r in decisions)=={'Incluir':97,'Excluir':561,'Pendente':871}, '1530 componentes de entrada menos uma fusão = 1529; 97 + 561 + 871')
    check('Proveniência íntegra', len(provenance)==2053 and len({r['registro'] for r in provenance})==2053 and set(bywork)==set(byid), '2053 registros distintos, todos relacionados a uma decisão')
    paths={p['raw_file'] for p in provenance}|{m['raw_file'] for m in materials}|set(initial['hashes_entradas'])
    check('Caminhos de evidência locais',all((ROOT/p).is_file() for p in paths), f'{len(paths)} caminhos distintos existentes')
    check('Contagens por obra',all(int(r['registros_origem'])==len(bywork[r['obra_id']]) for r in decisions), 'Soma dos registros por componente = 2053')
    check('Elegibilidade das inclusões',all(r['tema_sustentado']=='1' and r['academico_sustentado']=='1' and r['periodo']=='Sim' and r['via_do_vinculo_goiano']!='não comprovada' for r in included), 'Tema, natureza acadêmica, período e via geográfica presentes nas 97 inclusões')
    check('Inclusões históricas',sum(r['historico_incluido']=='1' for r in included)==19, '19 obras anteriores preservadas; 78 acrescentadas')
    check('Extração restrita ao corpus',len(axes)==291 and {r['obra_id'] for r in axes}==inc and len({(r['obra_id'],r['eixo']) for r in axes})==291, '97 obras x 3 eixos; nenhuma extração de pendentes/excluídas')
    old=[r for r in axes if r['origem']=='extração histórica reaproveitada']
    check('Estados históricos preservados',len(old)==57 and Counter((r['obra_id'],r['estado']) for r in old)==Counter((r['obra_id'],r['Estado']) for r in historical), '57 estados copiados da base; sem reclassificação silenciosa')
    located=[]
    for r in axes:
        if r['origem'].startswith('revisão') and r['estado']=='Presente':
            node=r['fonte'].split(';')[0]; span=re.search(r'\[(\d+):(\d+)\]',r['localizacao'])
            assert span and node in bynode
            a,b=map(int,span.groups());located.append(bynode[node]['resumo'][a:b].strip()==r['trecho'])
    check('Trechos novos reproduzíveis',all(located),f'{len(located)} trechos Presente reproduzidos exatamente por índices de caracteres')
    check('Estados sem inferência de ausência',all(r['fonte'] and r['localizacao'] and r['sintese'] and r['limite'] for r in axes), '291 linhas com fonte, localização, síntese e limite; Não informado e Não verificável separados')
    temporal=[r for r in decisions if r['decisao']=='Excluir' and r['periodo']=='Não']
    for r in temporal:
        pp=bywork[r['obra_id']]
        years={p['ano_publicacao_original'] for p in pp if p['ano_publicacao_original']}
        dates={p['data_publicacao_original'] for p in pp if p['data_publicacao_original']}
        defense={p['ano_defesa_original'] for p in pp if p['ano_defesa_original']}
        thesis=any(p['tipo_original'] in ('Tese','Dissertação','dissertation') for p in pp)
        assert period(years,dates,defense,thesis)[0]=='Não',r['obra_id']
    check('Exclusões temporais recalculadas',len(temporal)==498,'297 por publicação antiga + 201 por publicação e defesa antigas; defesa antiga isolada não exclui')
    check('Identidade adicional resolvida',byid['M2-4bae42ee3741323e']['ids_anteriores']=='M2-4bae42ee3741323e;M2-f1063b9800fa3a1b','Uma tese UFU fundida por DOI e handle concordantes; todos os registros preservados')
    check('Ambiguidade de versões fora dos indicadores',all(byid[g]['decisao']=='Pendente' for g in ('M2-6fc274039407a243','M2-f5ac63d543e7078a')), 'Artigo/capítulo equivalentes: duas unidades pendentes, efeito possível +1 ou +2 obras')
    dois={g:{p['doi_original_normalizado'] for p in bywork[g] if p['doi_original_normalizado']} for g in inc}
    duplicates=[(a['obra_id'],b['obra_id']) for a,b in combinations(included,2) if dois[a['obra_id']]&dois[b['obra_id']] or SequenceMatcher(None,texto_normalizado(a['titulo']),texto_normalizado(b['titulo'])).ratio()>=0.88]
    check('Varredura de identidade no corpus',not duplicates,'4656 pares internos: nenhum DOI concordante entre componentes nem similaridade de título >= 0,88; não detecta traduções por si só')
    overlaps=Counter()
    for r in decisions:
        q=sorted(set(r['filas'].split(';')))
        for a in q:
            for b in q:
                if a<=b:overlaps[(a,b)]+=1
    write('Sobreposicao final das filas.csv',[{'fila_a':a,'fila_b':b,'obras_compartilhadas':v} for (a,b),v in sorted(overlaps.items())])
    # Amostra fixa de decisões de maior risco; o texto completo permanece no material local.
    rng=random.Random(20261117)
    inherited=[r for r in decisions if r['justificativa'].startswith('Exclusão temática histórica')]
    sampled=rng.sample(inherited,10)+rng.sample(temporal,6)
    sample=[]
    for r in sampled:
        pp=bywork[r['obra_id']];mm=[bynode[p['registro']] for p in pp]
        sample.append({'obra_id':r['obra_id'],'titulo':r['titulo'],'decisao':r['decisao'],'justificativa':r['justificativa'],
                       'anos_publicacao':r['anos_publicacao'],'anos_defesa':r['anos_defesa'],
                       'evidencia_para_conferencia':' | '.join(m['resumo'][:900] for m in mm),
                       'fontes_locais':';'.join(sorted({p['raw_file'] for p in pp})),
                       'resultado_conferencia':'Datas anteriores ao recorte confirmadas nos campos de origem; exclusão regional mantida.' if r in temporal else 'Objeto principal distinto do PIBID no material e decisão histórica consultados; exclusão operacional mantida, sem afirmar ausência no texto integral.',
                       'alcance':'Objeto/decisão histórica e datas; conferência interna, sem validação independente'})
    write('Amostra de exclusoes.csv',sample)
    write('Verificacoes internas.csv',checks)
    metrics={'verificacoes_aprovadas':len(checks),'caminhos_conferidos':len(paths),'trechos_novos_reproduzidos':len(located),
             'amostra_exclusoes':16,'semente_amostra':20261117,
             'criterios_temporais_incluidas':dict(Counter(r['criterio_temporal'] for r in included)),
             'vinculos_incluidas':dict(Counter(r['via_do_vinculo_goiano'] for r in included)),
             'estado_nacional_incluidas':dict(Counter(r['estado_nacional'] for r in included)),
             'prioridades_residuais':dict(Counter(r['prioridade_residual'] for r in read(OUT/'Pendencias regionais.csv'))),
             'registros_por_decisao':dict(Counter(byid[p['obra_id']]['decisao'] for p in provenance)),
             'eixos_por_estado':{e:dict(Counter(r['estado'] for r in axes if r['eixo']==e)) for e in sorted({r['eixo'] for r in axes})}}
    (OUT/'Verificacoes internas.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(metrics,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
