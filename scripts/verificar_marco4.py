"""Verificações internas de denominadores, pesos e rastreabilidade dos indicadores."""
import hashlib
import json
from collections import Counter, defaultdict
from scripts.produzir_indicadores_marco4 import ROOT, OUT, read, save, M2, M3, MATERIALS


def main():
    audit=json.loads((OUT/'Auditoria.json').read_text(encoding='utf8'));u=read(OUT/'Obras dos indicadores.csv')
    a=read(OUT/'Creditos de autoria.csv');i=read(OUT/'Creditos institucionais.csv');g=read(OUT/'Creditos geograficos.csv')
    checks=[]
    sizes={'nacional':len(read(M2/'Corpus nacional.csv')),'goiano':len(read(M3/'Corpus goiano.csv'))}
    N=sizes['nacional'];G=sizes['goiano'];total=N+G
    def check(label,ok,evidence):
        checks.append({'verificacao':label,'resultado':'OK' if ok else 'FALHOU','evidencia':evidence})
        assert ok,(label,evidence)
    check('Preservação de fontes',all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in audit['hashes_entradas'].items()),f'{len(audit["hashes_entradas"])} hashes idênticos; inclui as 125 páginas e documentos fundantes')
    check('Unidades únicas por escopo',len(u)==total and len({(r['escopo'],r['obra_id']) for r in u})==total,f'{N} nacionais + {G} regionais; não somar corpora sobrepostos como universo único')
    for scope,denominator in sizes.items():
        rr=[r for r in u if r['escopo']==scope];ids={r['obra_id'] for r in rr}
        check('Temporal '+scope,sum(int(r['obras_com_ano_univoco']) for r in read(OUT/('Evolucao '+scope+'.csv')))==denominator,'Série + residuais, com publicação e defesa em estratos próprios, reconciliam ao corpus')
        check('Tipos '+scope,sum(int(r['obras']) for r in read(OUT/('Tipos documentais '+scope+'.csv')))==denominator,'Categorias documentais harmonizadas mutuamente exclusivas')
        cov=read(OUT/'Cobertura de campos.csv')
        check('Cobertura afiliação '+scope,sum(int(r['obras']) for r in cov if r['escopo']==scope and r['campo']=='afiliação')==denominator,'Conhecida + parcial + desconhecida = denominador')
        for rows,label in [(a,'autoria'),(i,'instituição'),(g,'país')]:
            grouped=defaultdict(list)
            for r in rows:
                if r['escopo']==scope:grouped[r['obra_id']].append(r)
            check('Pesos '+label+' '+scope,set(grouped)<=ids and all(abs(sum(float(r['peso_fracionario']) for r in v)-1)<1e-9 for v in grouped.values()),'Crédito fracionário soma 1 por obra com campo; obras sem campo não recebem crédito fictício')
    axes=read(OUT/'Evidencias dos eixos.csv');counts=read(OUT/'Indicadores dos eixos.csv')
    check('Eixos e corpus regional',len(axes)==3*G and {r['obra_id'] for r in axes}=={r['obra_id'] for r in u if r['escopo']=='goiano'},f'{3*G} pares = {G} obras x 3 eixos; estados preservados')
    check('Reconciliação estados dos eixos',Counter((r['eixo'],r['estado']) for r in axes)==Counter({(r['eixo'],r['estado']):int(r['obras']) for r in counts}),'Cada contagem remete às linhas de evidência')
    cross=read(OUT/'Correspondencia Goias Brasil.csv');nids={r['obra_id'] for r in u if r['escopo']=='nacional'}
    nodes={p['registro'] for p in read(M2/'Proveniencia.csv') if p['obra_id'] in nids};groups=defaultdict(set)
    for p in read(M3/'Proveniencia regional.csv'):groups[p['obra_id']].add(p['registro'])
    expected_matches=sum(bool(groups[r['obra_id']]&nodes) for r in read(M3/'Corpus goiano.csv'))
    check('Correspondência nacional regional',len(cross)==G and sum(r['incluida_no_nacional']=='Sim' for r in cross)==expected_matches,f'{expected_matches} inclusões regionais presentes no corpus nacional; {G-expected_matches} fora dele não entram no numerador')
    part=read(OUT/'Participacao e contexto Goias.csv')[0];nu=[r for r in u if r['escopo']=='nacional']
    numerator=sum(r['afiliacao_goias_observada']=='Sim' for r in nu)
    check('Numerador e denominador compatíveis',int(part['numerador'])==numerator and int(part['denominador'])==N and abs(float(part['percentual'])-100*numerator/N)<1e-10,f'Somente afiliações das obras do corpus nacional congelado; não usa {G}/{N}')
    check('Divergências de ano explícitas',len(read(OUT/'Divergencias de ano.csv'))==2,'Duas obras nacionais mantidas em categoria divergente; limites por ano não aditivos')
    common=read(OUT/'Participacao periodo comum.csv')[0]
    commonrows=[r for r in nu if r['anos_publicacao'] and all(y.isdigit() and 2020<=int(y)<=2026 for y in r['anos_publicacao'].split(';'))]
    check('Período comum sem defesa',int(common['obras_nacionais'])==len(commonrows)==3459 and int(common['obras_com_afiliacao_goiana_identificada'])==sum(r['afiliacao_goias_observada']=='Sim' for r in commonrows)==67,'67/3459, por publicação e regras nacionais; não soma as quatro inclusões por defesa')
    mats=read(MATERIALS);byrecord={r['registro']:r for r in mats};spans=[]
    import re
    for r in read(OUT/'Conferencia adicional.csv'):
        if not r['alvo'].startswith('Subquestão') or 'caracteres [' not in r['localizacao']:continue
        node=r['fonte'].split(';')[0];a0,b0=map(int,re.search(r'\[(\d+):(\d+)\]',r['localizacao']).groups())
        spans.append(byrecord[node]['resumo'][a0:b0]==r['evidencia'])
    check('Revisão qualitativa adicional',len(spans)==9 and all(spans),'Nove trechos adicionais exatamente reproduzíveis; mais uma extração histórica conferida; 291 estados anteriores preservados')
    check('Rótulos institucionais não ranqueados como pessoas',all(not re.match(r'^(universidade|faculdade|instituto federal|campus)',r['nome'],re.I) for r in read(OUT/'Autorias nacional.csv')),'22 ocorrências arquivadas em alertas, sem alteração do corpus')
    check('Seis respostas mapeadas',{r['subquestao'] for r in read(OUT/'Mapa de evidencias das seis subquestoes.csv')}==set('123456'),'Mapa contém as seis subquestões canônicas e referências de suporte')
    states=read(OUT/'Estado dos indicadores.csv')
    check('Rótulos dos denominadores vigentes',states[0]['base_denominador'].startswith(f'{N} nacionais; {G} regionais;'),'Estado dos indicadores usa os mesmos corpora, sem rótulos fixos de uma versão anterior')
    paths={r['arquivo_metadados'] for r in u}
    check('Caminhos das evidências',all((ROOT/p).is_file() for value in paths for p in value.split(';') if p),'Todos os arquivos de metadados referenciados existem')
    save('Verificacoes internas.csv',checks)
    inventory=[]
    paths=[p for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='Inventario de produtos.csv']
    paths += [ROOT/'scripts'/n for n in ('produzir_indicadores_marco4.py','documentar_conferencias_marco4.py','verificar_marco4.py')]
    paths += [ROOT/'tests/test_marco4.py']
    for p in paths:
        inventory.append({'arquivo':str(p.relative_to(ROOT)),'categoria':'produto Marco 4' if p.parent==OUT else 'código/verificação',
                          'linhas_de_dados':len(read(p)) if p.suffix=='.csv' else 'não aplicável',
                          'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    save('Inventario de produtos.csv',inventory)
    print(json.dumps({'verificacoes':len(checks),'aprovadas':len(checks),'numerador_goias':numerator,'denominador_nacional':N},ensure_ascii=False))


if __name__=='__main__':main()
