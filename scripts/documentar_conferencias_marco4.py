"""Revisões adicionais focalizadas, preservando corpus e 291 estados históricos."""
import json
import re
from collections import Counter
from scripts.produzir_indicadores_marco4 import OUT, ROOT, M3, M2, MATERIALS, MANIFEST, read, save
import os
from scripts.executar_marco3 import institution_signal


def main():
    units=read(OUT/'Obras dos indicadores.csv');axes=read(OUT/'Evidencias dos eixos.csv')
    materials=read(MATERIALS);pv=read(M2/'Proveniencia.csv')
    multi={r['obra_id'] for r in units if int(r['registros_openalex_do_componente'])>1}
    records={p['registro']:p for p in pv if p['obra_id'] in multi and p['registro'].startswith('https://openalex.org/')}
    rows=[]
    for path in sorted({p['raw_file'] for p in records.values()}):
        for w in json.loads((ROOT/path).read_text(encoding='utf8'))['response']['results']:
            if w['id'] not in records:continue
            rows.append({'obra_id':records[w['id']]['obra_id'],'alvo':'múltiplos registros OpenAlex / ano divergente',
                         'fonte':w['id']+'; '+path,'localizacao':'publication_year; type; authorships; primary_topic',
                         'evidencia':json.dumps({'ano':w['publication_year'],'tipo':w['type'],'autores':[a['author']['display_name'] for a in w['authorships']],
                                    'instituicoes':sorted({i['display_name'] for a in w['authorships'] for i in a['institutions']})},ensure_ascii=False),
                         'resultado':'Autoria nominal, tipo e tópico concordantes no componente; afiliações diferem em completude. Usar registro mais completo; preservar anos discordantes sem eleição de ano canônico.'})
    selected={
        'M2-0058366d672e0953':('4','Percebeu-se que houve uma apropriação','Práticas e saberes experienciais relatados; sem atribuição causal.'),
        'M2-241143e71e333621':('4','Os resultados sinalizam que o Pibid','Trecho localizado para aprendizagem/atuação de egressos; o fragmento automático do eixo A tratava de orçamento. Estado Presente mantido com fundamento no resumo completo.'),
        'M2-3a5921f05110aa64':('4','We noticed that','Menor abandono, formação continuada e exercício profissional relatados; não corresponde a estudo causal ou seguimento nacional.'),
        'M2-8953b164f7af0cf4':('4','Na análise dos dados','Egressos UNIFESSPA/Pará; incluída por afiliação goiana. Não atribuir resultados a escolas de Goiás.'),
        'M2-c45f9d2575dddbd5':('4','Os dados obtidos demonstraram','Resultado crítico: categorias do subprojeto não cumpridas dificultam interesse pela carreira. Substitui, na síntese, dependência do trecho automático sobre objetivo genérico do programa.'),
        'M2-c90d6e68fcfaa58b':('4','Muitos deles definem','Decisão pela carreira relatada; não taxa de inserção profissional.'),
        'M2-5afeeb153a97359d':('5','As narrativas em portfólio','Indícios de espaços híbridos, com tensões; não comprovação de resultados generalizáveis.'),
        'M2-a9960de4732671f4':('5','Esta pesquisa tem como objetivo','Pesquisa em andamento/objetivo; não somar como intervenção independente ao relato posterior.'),
        'M2-25a08c2b555d1324':('5','Ademais, discute-se','Comunidade/extensão mencionadas; livros híbridos não são prova de espaços híbridos de formação.'),
    }
    for gid,(question,start,result) in selected.items():
        found=False
        for m in materials:
            if m['obra_id']!=gid:continue
            idx=m['resumo'].find(start)
            if idx<0:continue
            sentence=re.match(r'[^.!?]+[.!?]?',m['resumo'][idx:]).group()
            rows.append({'obra_id':gid,'alvo':'Subquestão '+question+' — conferência de afirmação qualitativa',
                         'fonte':m['registro']+'; '+m['raw_file'],'localizacao':f'Campo resumo; caracteres [{idx}:{idx+len(sentence)}]',
                         'evidencia':sentence,'resultado':result});found=True;break
        assert found,gid
    historical=[r for r in axes if r['obra_id']=='M2-d5b6da544288f2ae' and r['eixo'].startswith('Trajetórias')]
    for r in historical:rows.append({'obra_id':r['obra_id'],'alvo':'Subquestão 4 — sexta obra com trajetória',
             'fonte':r['fonte']+'; '+r['materiais_locais'],'localizacao':r['localizacao'],'evidencia':r['sintese'],
             'resultado':'Extração histórica reaproveitada: cinco egressos em educação básica; síntese, não transcrição. Não exige atribuir seguimento longitudinal à obra.'})
    for r in read(OUT/'Alertas de metadados.csv'):rows.append({'obra_id':r['obra_id'],'alvo':'Rótulo institucional em autoria',
             'fonte':'Obras dos indicadores.csv; '+r['obra_id'],'localizacao':'authorships.author.display_name',
             'evidencia':r['valor'],'resultado':'Conferência nominal confirma rótulo institucional; excluído do ranking de pessoas, sem excluir a obra ou alterar o arquivo bruto.'})
    save('Conferencia adicional.csv',rows)
    mentions=[]
    raxis=[r for r in axes if r['eixo'].startswith('Relações')]
    for f in ('comunidades','saberes_escolares_comunitarios','espacos_hibridos'):
        yes=[r for r in raxis if not r[f].startswith(('Não identificado','Não verificável'))]
        mentions.append({'aspecto':f,'obras_com_mencao_localizada':len(yes),'denominador':97,
                         'obra_ids':';'.join(r['obra_id'] for r in yes),
                         'origem':'Campos de menções da extração Marco 3; localização lexical conservadora, sem sinônimos novos',
                         'limite':'Não equivale a efeito demonstrado, intervenção comunitária ou ausência nos demais; livros híbridos não significam espaços híbridos.'})
    save('Mencoes especificas terceiro eixo.csv',mentions)
    contexts=[]
    byregional={r['obra_goias']:r for r in read(OUT/'Correspondencia Goias Brasil.csv')}
    for group,rr in [('97 obras regionais',[r for r in units if r['escopo']=='goiano']),
                     ('78 regionais correspondentes ao nacional',[r for r in units if r['escopo']=='goiano' and byregional[r['obra_id']]['incluida_no_nacional']=='Sim'])]:
        for state,c in Counter(r['contexto_goias_estado'] for r in rr).items():contexts.append({'conjunto':group,'estado_contexto':state,'obras':c,
                    'denominador_do_conjunto':len(rr),'limite':'Contextos verificados só no conjunto regional; não levantamento de todos os contextos do corpus nacional.'})
    save('Contexto Goias separado.csv',contexts)
    save('Instituicoes goianas no nacional.csv',[r for r in read(OUT/'Instituicoes nacional.csv') if institution_signal(r['nome'])])
    evidence=[
        ('1','Evolução, formatos, autoria, afiliação, países e tópicos no corpus operacional','Evolucao nacional.csv; Tipos documentais nacional.csv; Autorias nacional.csv; Instituicoes nacional.csv; Geografia pais nacional.csv; Tematicas OpenAlex nacional.csv; Cobertura de campos.csv','parcial; grupos/redes e distribuição completa por UF/região não estimáveis'),
        ('2','Participação identificada e correspondência, sem usar 97/7780','Participacao e contexto Goias.csv; Participacao periodo comum.csv; Correspondencia Goias Brasil.csv; Contexto Goias separado.csv; Instituicoes goiano.csv; Autorias goiano.csv','frações observadas parciais; participação total e grupos não estimáveis'),
        ('3','Distribuições e categorias da revisão de 97 obras','Evolucao goiano.csv; Tipos documentais goiano.csv; Instituicoes goiano.csv; Tematicas OpenAlex goiano.csv; Indicadores dos eixos.csv','consolidado no corpus observado; temáticas OpenAlex são algorítmicas'),
        ('4','Aprendizagens, identidades e trajetórias com achados positivos e críticos','Evidencias dos eixos.csv; Conferencia adicional.csv; Indicadores dos eixos.csv','66 e 6 abordagens; não 66 ou 6 provas de eficácia'),
        ('5','Parcerias, comunidades, saberes e espaços híbridos','Evidencias dos eixos.csv; Conferencia adicional.csv; Mencoes especificas terceiro eixo.csv','51 abordagens de relações; menções explícitas não são provas de participação comunitária'),
        ('6','Lacunas informacionais, limites do corpus e prioridades','Indicadores dos eixos.csv; Cobertura de campos.csv; Correspondencia Goias Brasil.csv; ../marco3/Pendencias regionais.csv','não informado difere de evidência insuficiente; 871 componentes pendentes')]
    evidence_rows=[{'subquestao':q,'afirmacao':text,'arquivos_relativos':files,'alcance':limit} for q,text,files,limit in evidence]
    if not MANIFEST:save('Mapa de evidencias das seis subquestoes.csv',evidence_rows)
    status=[
        ('Tamanho dos corpora e correspondência','consolidado nos arquivos operacionais','7780 nacionais; 97 regionais; 78 correspondentes','Não é fechamento do universo não observado.'),
        ('Evolução nacional','parcial','7780 obras; 7778 com ano unívoco; 2 divergentes','2026 incompleto e anos conflitantes em categoria própria.'),
        ('Tipos documentais','consolidado no corpus operacional','7780 / 97','Harmonização de rótulos; dissertation sem grau continua sem grau.'),
        ('Autorias e instituições','parcial','7753 / 97 com autoria; 4228 / 83 com instituição mapeada','Créditos integrais e fracionários; identidades arquivadas sem auditoria global.'),
        ('Distribuição por país de afiliação','parcial','4228 / 7780 nacionais; 83 / 97 regionais','País da instituição não é contexto empírico nem nacionalidade da autoria.'),
        ('Distribuição completa por UF/região','não estimável','UF/região não coletadas em authorships','Não inferir todas as UFs a partir de nomes institucionais.'),
        ('Grupos de pesquisa','não estimável','Sem campo identificador de grupo','Tópico, instituição e coautoria não substituem grupo.'),
        ('Redes de colaboração consolidadas','não estimável nesta rodada','6198 nacionais com coautoria observada; afiliação incompleta','Rótulos institucionais em autoria, fragmentação possível e cobertura desigual; não gerar grafo como rede nacional representativa.'),
        ('Temáticas OpenAlex','parcial','7777 / 7780 nacionais; 93 / 97 regionais com tópico principal','Classificação algorítmica, não categorias dos autores.'),
        ('Participação goiana identificada','parcial','196 / 7780; 67 / 3459 no período comum','Fração observada com os mesmos critérios; ausência de afiliação não é negativo.'),
        ('Participação total Goiás–Brasil','não estimável','Universo e afiliação incompletos','Não calcular 97 / 7780 nem extrapolar a fração identificada.'),
        ('Contexto goiano documentado','consolidado no corpus regional observado','56 contextos documentados e 2 objetos goianos; 97 obras examinadas','Não equivale a 58 pesquisas em escolas goianas; contexto nacional não foi triado integralmente.'),
        ('Três eixos canônicos','consolidado como estados de informação do corpus observado','291 pares = 97 obras x 3 eixos','Não informado e Não verificável não são ausência do fenômeno; sem inferência causal.')]
    statusrows=[{'indicador':name,'estado':state,'base_denominador':base,'limite':limit} for name,state,base,limit in status]
    if not MANIFEST:save('Estado dos indicadores.csv',statusrows)
    if MANIFEST:
        n=[r for r in units if r['escopo']=='nacional'];g=[r for r in units if r['escopo']=='goiano']
        N=len(n);G=len(g);cross=read(OUT/'Correspondencia Goias Brasil.csv');matched=sum(r['incluida_no_nacional']=='Sim' for r in cross)
        part=read(OUT/'Participacao e contexto Goias.csv')[0];common=read(OUT/'Participacao periodo comum.csv')[0]
        count=lambda rows,key:sum(bool(r[key]) and r[key]!='0' for r in rows)
        dynamic={
            'Tamanho dos corpora e correspondência':f'{N} nacionais; {G} regionais; {matched} correspondentes',
            'Evolução nacional':f'{N} obras; {sum(r["ano_serie"].isdigit() for r in n)} com ano unívoco; {sum(r["ano_serie"]=="divergente" for r in n)} divergentes',
            'Tipos documentais':f'{N} / {G}',
            'Autorias e instituições':f'{count(n,"autores_observados")} / {count(g,"autores_observados")} com autoria; {count(n,"instituicoes_mapeadas")} / {count(g,"instituicoes_mapeadas")} com instituição mapeada',
            'Distribuição por país de afiliação':f'{count(n,"paises_conhecidos")} / {N} nacionais; {count(g,"paises_conhecidos")} / {G} regionais',
            'Redes de colaboração consolidadas':f'{sum(r["coautoria_observada"]=="Sim" for r in n)} nacionais com coautoria observada; afiliação incompleta',
            'Temáticas OpenAlex':f'{sum(r["topico_disponivel"]=="Sim" for r in n)} / {N} nacionais; {sum(r["topico_disponivel"]=="Sim" for r in g)} / {G} regionais com tópico principal',
            'Participação goiana identificada':f'{part["numerador"]} / {N}; {common["obras_com_afiliacao_goiana_identificada"]} / {common["obras_nacionais"]} no período comum'}
        for row in statusrows:
            if row['indicador'] in dynamic:row['base_denominador']=dynamic[row['indicador']]
            if row['indicador']=='Participação total Goiás–Brasil':row['limite']=f'Não calcular {G} / {N} nem extrapolar a fração identificada.'
        save('Estado dos indicadores.csv',statusrows)
        for row in evidence_rows:
            if row['subquestao']=='2':row['afirmacao']=f'Participação identificada e correspondência, sem usar {G}/{N}'
            if row['subquestao']=='6':row['arquivos_relativos']=row['arquivos_relativos'].replace('../marco3/Pendencias regionais.csv',os.path.relpath(M3/'Pendencias regionais.csv',OUT).replace('\\','/'))
        save('Mapa de evidencias das seis subquestoes.csv',evidence_rows)
    print(json.dumps({'conferencias_adicionais':len(rows),'obras_qualitativas_conferidas':len(selected)+len(historical),'mencoes':mentions},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
