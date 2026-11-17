"""Decisões regionais e eixos: revisão individual registrada, sem novas coletas."""
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from scripts.executar_marco3 import OUT, M2, BASE, A, ROOT, read, texto_normalizado
from openpyxl import load_workbook

# Número na fila congelada de 87 casos. H = reaproveitar inclusão/eixos históricos.
# P/N/V = presente / não informado no material / não verificável.
# Contexto vazio conserva desconhecido; afiliação nunca é convertida em contexto.
REVIEWS={
 1:('PNN','IFG/Uruaçu','Questionários e narrativas identificam apropriação de práticas e saberes docentes.'),
 2:('PNP','IFG/Goiânia','Relato de proposta de ensino desenvolvimental no curso do IFG campus Goiânia.'),
 3:('NNP','Itumbiara/GO','Jogo executado por licenciandos PIBID em escola; resultados são dos alunos da educação básica.'),
 4:('PNP','PUC Goiás','Pesquisa de formação continuada e colaboração de supervisores com futuros professores.'),
 6:('PNP','Jataí/GO','Reuniões e trocas entre bolsistas, coordenador e supervisor na escola parceira.'),
 7:('PNN','','Saberes docentes em relatórios do subprojeto; inclusão por afiliação goiana, sem presumir local do estudo.'),
 9:('NNN','IFG/Anápolis','Projeto em andamento prevê participantes PIBID como sujeitos da pesquisa; inclusão pelo critério de participantes, coerente com as pesquisas em andamento. Não atribuir resultados esperados ao programa.'),
 11:('PNP','','Análise de políticas e questionários a bolsistas; inclusão por afiliação.'),
 12:('NNN','IFG/Jataí','Oficina OBAFOG no PIBID; aprendizagem/motivação relatadas são dos escolares, não evidência de aprendizagem docente.'),
 14:('PNP','','Experiência de extensão e oficinas do PIBID Psicologia; formação dos bolsistas relatada.'),
 15:('PPP','','Narrativas de cinco professores egressos; saberes mobilizados na atuação e aproximação IES–escola.'),
 18:('PNP','Morrinhos/GO','Relato no CEPI Sílvio Gomes com teoria–prática e relação universidade, escola e comunidade como abordagem.'),
 19:('PENDENTE','Fora de Goiás: Araguaína/TO','Norte Goiano é nome de escola em Tocantins. Contexto não é Goiás; afiliação goiana não é verificável no material.'),
 20:('NNN','','Catapulta desenvolvida no PIBID; resultados matemáticos de escolares não demonstram aprendizagem docente. Afiliação UFJ sustenta inclusão.'),
 21:('PNP','','Oficina de inglês e formação de licenciandos em pesquisa linguística e material didático.'),
 23:('PNN','UFCAT','Oito bolsistas de Educação Física da UFCAT; processo de ser professor, sem seguimento profissional demonstrado.'),
 24:('PPN','UFG','Relato sobre egressos de Ciências Biológicas, permanência no curso e atuação profissional em docência.'),
 25:('PNN','UEG/Anápolis','Autoetnografia de portfólio e relato de bolsista; saberes, autoconhecimento e formação humana.'),
 28:('PNN','UEG','Tese sobre política, formação e trabalho docente na UEG; não transformar período do programa em trajetória individual.'),
 29:('NNP','Goiânia/GO','Projeto PIBID História em escola de Goiânia; resultados sobre consciência histórica dos escolares.'),
 31:('PNP','Sudoeste goiano','Portfólios abordam saberes da IES, escola e comunidade e indícios de espaços híbridos.'),
 35:('PNN','Nacional/bibliográfico','Análise bibliográfico-documental de teorias de formação docente; inclusão por afiliação.'),
 36:('PNP','','Relato de robótica e educação matemática; aproximação universidade–escola explicitamente relatada.'),
 37:('NNN','Catalão/GO','Relato em anais do barquinho; efeitos relatados referem-se aos escolares.'),
 38:('PNP','Senador Canedo/GO','Bolsistas analisam PPP e contexto sociocultural da escola parceira.'),
 39:('PENDENTE','Jataí/GO','Tema, período e contexto sustentados; possível versão do capítulo inglês da unidade 82 com mesmos autores e resumo traduzido. DOI e formato diferentes não resolvem sozinhos obra versus versão; fora da contagem até verificar identidade textual.'),
 40:('NNN','Catalão/GO','Artigo sobre barquinho; resultados de aprendizagem dos escolares, publicação distinta do relato em anais.'),
 41:('NNN','Objeto em Goiás; local da escola não informado','Oficina com maquete do território Kalunga; não presumir participação direta da comunidade ou local da escola.'),
 42:('PNP','Jataí/GO','Licenciandos UFJ e escola: PPP, reforço e competências/práticas docentes.'),
 43:('PNP','Sudoeste goiano','Subprojeto Pedagogia articula licenciandos, escola e identidade docente; não tratar avanços como causalidade demonstrada.'),
 44:('PPN','Fora de Goiás: UNIFESSPA/Pará','Pesquisa com egressos de Geografia; inclusão pela afiliação UFCAT, não pelo lugar da pesquisa.'),
 46:('VVV','','Título de experiência de graduandos; resumo não preservado. Afiliação UFG permite inclusão, mas não extração de resultados.'),
 47:('PNP','','Vivência de pibidianas na elaboração de jogos: identidade docente e conhecimentos; não trajetória de egressos.'),
 48:('PNP','','Museu Itinerante de Química articula tríade formativa, exposições nas escolas e saberes docentes.'),
 49:('PNP','Jataí/GO','Apoio e monitorias na escola: autoconfiança e aprender a lidar com situações de sala de aula.'),
 50:('NNN','','Metodologias ativas em Biologia; benefícios descritos são dos alunos, sem evidência específica dos três eixos docentes.'),
 51:('PNP','IF Goiano/Morrinhos','Dissertação por defesa 2021; formação, socialização docente e relação teoria–prática com supervisores.'),
 52:('NNN','','Intervenção de Física no PIBID; resultados dos escolares. Inclusão por afiliação UFG.'),
 53:('NNN','Catalão/GO','Experiência lúdica com escolares; não transferir os ganhos dos escolares aos professores.'),
 54:('PNP','','Narrativa autobiográfica: saberes dos bolsistas e trabalho de coordenador, supervisor e bolsistas.'),
 55:('PNP','Teórico/nacional','Ensaio discute formação e papel de escola/universidade; abordagem teórica, não efeito empírico.'),
 56:('PNP','','Pesquisa em andamento propõe espaços híbridos e saberes comunitários; expectativas, sem resultados consolidados.'),
 57:('PNP','Catalão/GO','Experiência de licenciandos UFCAT com escola e supervisores; identidade e práticas docentes.'),
 58:('NNN','','Experiência em imunologia: compreensão/vacinação dos escolares; título situa PIBID, afiliação UEG.'),
 59:('PNN','UEG','Relato de bolsista sobre experiências inventivas e formação; não inferir trajetória profissional do percurso no projeto.'),
 60:('PNP','Goiás','Revisão sobre universidade goiana, formação inicial e relação entre bolsistas, supervisores e escolas.'),
 61:('NNP','Rio Verde/GO','Gestão democrática e mobilização de comunidade em experiência PIVIC/PIBID; não efeito isolado do PIBID.'),
 62:('PNP','UFJ; locais das escolas não informados','Relato de comunicação do PIBID interdisciplinar, sistematização das práticas e engajamento escola–academia.'),
 63:('PNP','UFCAT','Podcast experimentado no subprojeto História e escola Instituto Matilde Margon Vaz.'),
 64:('PNN','Catalão/GO','Diagrama de Gowin: o resumo também relata aprimoramento da prática dos bolsistas.'),
 65:('PPN','UFG/Jataí','Questionário a participantes e entrevista com coordenador; interesse na carreira docente e formação.'),
 66:('PNP','Morrinhos/GO','Oito bolsistas, supervisão e direção escolar; reflexão coletiva e formação docente.'),
 67:('NNP','Rio Verde/GO','Resumo expandido de gestão democrática e comunidade escolar; distinto do artigo por veículo, extensão e DOI.'),
 68:('VVV','IFG','Título situa PIBID/PRP na licenciatura em Música do IFG; sem resumo, eixos não verificáveis.'),
 69:('PPP','','Investigação sobre práxis universidade–escola, confiança e decisão pela carreira.'),
 70:('NNN','IFG/Jataí','Questionários aos escolares orientam futura ação; não demonstram aprendizagem docente ou trajetória.'),
 71:('NNN','','Estratégia ambiental iniciada no PIBID e aprimorada em disciplina posterior; benefícios descritos são escolares.'),
 73:('PNP','Morrinhos/GO','Subprojeto UEG no CEPI Alfredo Nasser; progressos no processo de formação e na intervenção escolar.'),
 74:('PNP','Objeto em Goiás; escola anonimizada','Relato do PIBID com educação ambiental e vídeos para comunidade; afiliação UFJ preservada, escola ocultada.'),
 75:('VVV','UEG/Anápolis','Título do capítulo sustenta contexto; resumo é apresentação do livro inteiro, não fonte suficiente para eixos do capítulo.'),
 76:('PNP','Catalão/GO','Estudo sobre PIBID Geografia UFCAT em escolas de Catalão; autonomia, identidade e relação universidade–escola.'),
 77:('FUNDIR','UEG','Mesmo DOI/handle de tese UFU da unidade 28; autoria abreviada OpenAlex não cria outra obra.'),
 80:('PNP','Pires do Rio/GO','Projeto interdisciplinar do IF Goiano Urutaí em escola de Pires do Rio; preparação de licenciandos para tema sexualidade.'),
 81:('PNN','Nacional/bibliográfico','Analisa paradigmas de formação docente na produção stricto sensu; não trajetória profissional individual.'),
 82:('PENDENTE','Jataí/GO','Tema, período e contexto sustentados; possível tradução/republicação do artigo da unidade 39. Mesmos autores e resumo equivalente; capítulo não contado adicionalmente sem resolver obra versus versão.'),
 83:('PNN','Nacional/múltiplos contextos','394 participantes de 83 universidades; aprendizagem docente. Afiliação goiana não torna a amostra exclusivamente goiana.'),
 84:('PENDENTE','','Resumo é metadado de evento do IF Goiano Morrinhos, não demonstra contexto da contribuição ou afiliação da autoria.'),
 85:('PENDENTE','Fora de Goiás: São Bernardo do Campo/SP','Goiás aparece na bibliografia; contexto real é São Paulo e afiliação goiana não foi identificada. Não excluir enquanto a via de afiliação estiver não verificável.'),
}
AXIS_NAMES=('Aprendizagem da docência e identidade profissional','Trajetórias profissionais','Relações IES, escolas e comunidades; saberes e espaços híbridos')
EXTRA={
 'M2-25a08c2b555d1324':('PNP','UEG/Quirinópolis','OFIR tem inserção no PIBID e extensão junto à rede goiana; relato articula formação inventiva e comunidade.'),
 'M2-2682d1ca7b392c34':('PNN','IFG/Anápolis','Dissertação com defesa 2024: grupo formativo composto por licenciandos vinculados ao PIBID é objeto empírico. Relação substantiva pelos participantes, sem afirmar intervenção oficial do programa.'),
 'M2-3398c3fe22bb5ba2':('PNN','IFG/Anápolis','Dissertação com defesa 2024: encontros e produção colaborativa envolveram bolsistas PIBID. Resolve a dúvida de tema pelo critério de participantes, sem atribuir efeito exclusivo ao programa.'),
 'M2-3e5ab5abc1872736':('PENDENTE','','PIBID surge entre programas precarizados em análise geral de reformas; papel substantivo no objeto não suficientemente esclarecido.'),
 'M2-52700ca2c35b1b91':('NNP','Catalão/GO','Feira desenvolvida por subprojetos PIBID UFCAT e dez escolas; aprendizagem dos escolares, não docente.'),
 'M2-5293936e79b4e25a':('NNP','UFG','Reflexão sobre experiência no Pibid Dança UFG e mediações no campo escolar e comunidades escolares.'),
 'M2-5a5cb491a121c1c9':('PNP','Teórico/nacional','Políticas de estágio, PIBID e residência constituem objeto comparativo sobre trabalho do professor supervisor; inclusão por afiliação.'),
 'M2-630042aaef574c5e':('PENDENTE','','Material preservado é biografia de coordenadora; não comprova conteúdo temático da apresentação.'),
 'M2-776d321946f772d7':('PNP','IF Goiano','Projeto Beija-Flor articula atividades teóricas do PIBID, escola e instituição formadora e identidade investigativa.'),
 'M2-7a5a6304a9b10d06':('NNN','Jataí/GO','Projeto inicial de intervenção matemática surgido de experiência PIBID; resultados previstos são escolares, não ganhos docentes medidos.'),
 'M2-7ae3036bd7ecd118':('PNP','Revisão/múltiplos contextos','Revisão analisa experiências formativas incluindo PIBID e relações com comunidades campesinas; inclusão por afiliação.'),
 'M2-7b6aee07790481c7':('EXCLUIR','','Objeto é PIBIC-EM e iniciação científica no ensino médio, não PIBID. Exclusão temática operacional pela leitura do resumo; siglas/programas distintos.'),
 'M2-88cf34b2d43b662b':('PENDENTE','','Resumo preservado é biografia da entrevistada; coordenação do PIBID não comprova objeto da entrevista.'),
 'M2-ac432d97ca8e4178':('EXCLUIR','','Título trata desjudicialização e direito registral. PIBID está somente no nome do evento agregado ao metadado, não no objeto descrito. Exclusão temática operacional e reversível.'),
 'M2-b18766b67a9fb6e7':('PNP','','Pesquisa questiona como cursos/PIBID discutem educação especial e experiências dos pibidianos com escolares; vínculo por afiliação.'),
 'M2-c72ae4fbb14526ac':('VVV','','Título explicita intervenção PIBID; resumo é introdução geral e não caracteriza suficientemente os eixos da intervenção.'),
 'M2-ce86429a9010d3d9':('PNP','IF Goiano','Beija-Flor inclui bolsistas PIBID/residência/estágio e orientação colaborativa IES–escolas; efeitos não isoláveis por programa.'),
 'M2-d60f2687fc41e7b7':('NNN','','Revisão de OBI tem uma ação PIBID como único estudo selecionado; a ação integra o objeto analisado, com resultados dos escolares.'),
 'M2-d622edae67c7cdfa':('PENDENTE','','Resumo é somente nome do evento e título; não demonstra papel substantivo do PIBID na contribuição.'),
 'M2-e827a6e9875feed3':('NNP','Goiânia/GO','Survey foi coletado por licenciandos PIBID IFG em escolas de Goiânia; participantes/ação do programa integram método e contexto.'),
 'M2-eb78ff95d29b193e':('NNN','','Pesquisa intervém com seis escolares e dois pibidianos de Pedagogia; mediação na ação integra contexto, mas resultados são das crianças.'),
 'M2-fe8509b5ce920bf3':('PNN','','Memoriais e encontros refletem saber/fazer docente e experiências PIBID/PRP; não atribuir efeitos exclusivamente ao PIBID.'),
}
PATTERNS=(r'aprendiz.{0,80}docen|saberes.{0,80}docen|identidad.{0,50}docen|formac|pratica.{0,50}docen|teacher.{0,50}train|training|qualification|graduates|teaching.{0,50}learn|profissionalidade|pedagogic|licenciand|pibidian',
          r'trajetoria.{0,40}profiss|carreira|egress|graduat|work professionally|career|profissao',
          r'hibrid|comunit|comunidad|comunidade|parcer|supervisor|\bies\b|universidade.{0,300}escola|escola.{0,300}universidade|university.{0,300}school|tr[ií]ade|bolsist.{0,300}escola|escola.{0,300}bolsist|licenciand.{0,300}escola|escola.{0,300}licenciand|subprojeto.{0,300}escola|escola.{0,300}subprojeto')


def quote_for(materials,axis):
    hits=[]
    for m in materials:
        for match in re.finditer(r'[^.!?\n]+[.!?\n]?',m['resumo']):
            text=match.group().strip()
            if re.search(PATTERNS[axis],texto_normalizado(text)):
                score=bool(re.search(r'resultad|conclu|evidenc|percebeu|sinaliz|findings|results',texto_normalizado(text)))
                hits.append((score,len(text)>60,text,m['registro'],match.start(),match.end(),m['raw_file']))
    return max(hits,key=lambda h:(h[0],h[1],min(len(h[2]),1200))) if hits else None


def save(name,rows,fields=None):
    with (OUT/name).open('w' if '--atualizar' in sys.argv else 'x',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    if (OUT/'Decisoes regionais.csv').exists() and '--atualizar' not in sys.argv:raise FileExistsError('Fechamento já existe.')
    priority=read(OUT/'Revisao individual prioritaria.csv');initial=read(OUT/'Triagem regional inicial.csv')
    materials=read(OUT/'Materiais locais.csv');history=read(OUT/'Eixos historicos reaproveitaveis.csv')
    assert len(priority)==87 and sum(r['historico_incluido']=='1' for r in priority)==19
    mapping={r['obra_id']:r['obra_id'] for r in initial}
    target=priority[27]['obra_id'];merged=priority[76]['obra_id']
    assert target=='M2-4bae42ee3741323e' and merged=='M2-f1063b9800fa3a1b'
    mapping[merged]=target
    bymat=defaultdict(list)
    for m in materials:bymat[mapping[m['obra_id']]].append(m)
    byhist=defaultdict(list)
    for h in history:byhist[mapping[h['obra_id']]].append(h)
    manual={};ledger=[];axisflags={};notes={}
    for idx,p in enumerate(priority,1):
        gid=mapping[p['obra_id']]
        if p['historico_incluido']=='1':
            flags='H';ctx=p['contexto_goias'];note='Inclusão histórica conferida: evidências, período, tema e eixos reaproveitados.'
        else:flags,ctx,note=REVIEWS[idx]
        ledger.append({'numero_fila':idx,'obra_id_anterior':p['obra_id'],'obra_id':gid,'titulo':p['titulo'],
                       'avaliacao':flags,'contexto_revisado':ctx,'parecer':note,
                       'material':'Materiais locais.csv; resumo/título/afiliações e metadados arquivados; revisão interna'})
        if flags=='FUNDIR':continue
        manual[gid]=(flags,ctx,note);axisflags[gid]=flags;notes[gid]=note
    initial_by_id={r['obra_id']:r for r in initial}
    for gid,(flags,ctx,note) in EXTRA.items():
        assert gid in initial_by_id
        manual[gid]=(flags,ctx,note);axisflags[gid]=flags;notes[gid]=note
        ledger.append({'numero_fila':'complementar','obra_id_anterior':gid,'obra_id':gid,'titulo':initial_by_id[gid]['titulo'],
                       'avaliacao':flags,'contexto_revisado':ctx,'parecer':note,
                       'material':'Materiais locais.csv; revisão de lacunas com período e vínculo forte, mesmo sem regra temática positiva.'})
    # Evidência de exclusão temática já lida: reaproveitar só se não houver suporte positivo conflitante.
    w=load_workbook(BASE,read_only=True,data_only=True);it=iter(w['Triagem'].values);hh=next(it);base={v[0]:dict(zip(hh,v)) for v in it if v[0]};w.close()
    groups=defaultdict(list)
    for r in initial:groups[mapping[r['obra_id']]].append(r)
    decisions=[]
    for gid,rr in sorted(groups.items()):
        r=dict(next((v for v in rr if v['obra_id']==gid),rr[0]));r['obra_id']=gid
        r['ids_anteriores']=';'.join(sorted(v['obra_id'] for v in rr))
        r['codigos_base']=';'.join(sorted({c for v in rr for c in v['codigos_base'].split(';') if c}))
        r['ids_openalex']=';'.join(sorted({c for v in rr for c in v['ids_openalex'].split(';') if c}))
        r['filas']=';'.join(sorted({f for v in rr for f in v['filas'].split(';')}))
        r['registros_origem']=len(bymat[gid]);r.pop('potencial_inclusao',None)
        if gid in manual:
            flags,ctx,note=manual[gid]
            r['decisao']='Pendente' if flags=='PENDENTE' else 'Excluir' if flags=='EXCLUIR' else 'Incluir'
            if r['decisao']=='Incluir':r['tema_sustentado']='1'
            if ctx:r['contexto_goias']=ctx
            r['justificativa']=note
            # Contexto confirmado por leitura é uma via regional, não uma afiliação inferida.
            if ctx:r['evidencia_contexto']=note
        elif r['decisao']!='Excluir':
            bs=[base[c] for c in r['codigos_base'].split(';') if c]
            prev_negative=any(b['Decisão de elegibilidade']=='Excluir' and b['Motivo da exclusão'] in ('Outro','Sem relação substantiva com PIBID') for b in bs)
            if prev_negative and r['tema_sustentado']=='0':
                r['decisao']='Excluir';r['justificativa']='Exclusão temática histórica documentada, operacional e reversível; sem evidência positiva conflitante nos materiais conciliados.'
            else:
                reasons=[]
                if r['periodo']!='Sim':reasons.append('período regional não comprovado; defesa antiga isolada não exclui')
                if r['tema_sustentado']=='0':reasons.append('pertinência temática insuficiente')
                if r['academico_sustentado']=='0':reasons.append('natureza acadêmica insuficientemente documentada')
                if r['afiliacao_goias']!='Sim' and not r['evidencia_contexto']:reasons.append('vínculo goiano não comprovado no material; ausência de sinal não é exclusão')
                r['justificativa']='; '.join(reasons) or 'Evidência regional requer leitura; não incluída por regra geográfica isolada.'
        ctx=r['contexto_goias']
        if ctx.startswith('Fora de Goiás'):context_state='Não — contexto explicitamente fora de Goiás'
        elif any(s in ctx for s in ('Nacional','nacional','múltiplos')):context_state='Nacional/múltiplos; Goiás não individualizado'
        elif ctx.startswith('Objeto em Goiás'):context_state='Objeto goiano; local da escola não verificado'
        elif ctx in ('A verificar','Não identificado no material','Não identificada no material',''):context_state='Não verificável no material'
        else:context_state='Sim — contexto local/institucional documentado'
        r['contexto_goias_estado']=context_state
        ways=[]
        if r['afiliacao_goias']=='Sim':ways.append('afiliação')
        if context_state.startswith(('Sim','Objeto')):ways.append('contexto/objeto')
        r['via_do_vinculo_goiano']=' e '.join(ways) if ways else 'não comprovada'
        decisions.append(r)
    included=[r for r in decisions if r['decisao']=='Incluir'];axes=[];corrections=[]
    for r in included:
        gid=r['obra_id'];flags=axisflags[gid];mm=bymat[gid]
        for axis,name in enumerate(AXIS_NAMES):
            if flags=='H':
                hist=byhist[gid]
                # Ordem canônica identifica os três eixos; códigos da base podem ser duplicados.
                candidates=[h for h in hist if ('aprendiz' if axis==0 else 'trajet' if axis==1 else 'rela') in texto_normalizado(h['Eixo'])]
                assert candidates, (gid,name)
                h=candidates[0]
                row={'obra_id':gid,'eixo':name,'estado':h['Estado'],'sintese':h['Achado ou observação'],
                     'fonte':h['Link ou referência consultada'],'localizacao':h['Trecho ou localização'],
                     'trecho':'','limite':h['Limites da evidência'],'origem':'extração histórica reaproveitada'}
            else:
                flag=flags[axis];hit=quote_for(mm,axis) if flag=='P' else None
                if flag=='P' and not hit and axis==2:
                    # O parecer individual já examinou a relação em múltiplas frases.
                    # O localizador lexical não substitui essa leitura: citar o resumo inteiro.
                    source=max(mm,key=lambda m:len(m['resumo']))
                    if len(source['resumo'])>100:
                        hit=(False,True,source['resumo'],source['registro'],0,len(source['resumo']),source['raw_file'])
                        corrections.append({'obra_id':gid,'eixo':name,'correcao':'Relação verificada no parecer individual depende do contexto de várias frases; localização substituída por resumo completo, sem inferência de ausência pelo localizador.'})
                if flag=='P' and not hit:
                    corrections.append({'obra_id':gid,'eixo':name,'correcao':'Presente proposto na revisão não tinha trecho localizável pela regra; mantido Não verificável até localização específica.'});flag='V'
                state={'P':'Presente','N':'Não informado','V':'Não verificável'}[flag]
                row={'obra_id':gid,'eixo':name,'estado':state,
                     'sintese':(name+': '+notes[gid]) if flag=='P' else
                       'Aspecto não identificado nos resumos/títulos consultados; não significa ausência no estudo integral.' if flag=='N' else
                       'Material específico insuficiente para caracterizar o eixo; resumo ausente, genérico ou trecho ainda não localizado.',
                     'fonte':hit[3]+'; '+hit[6] if flag=='P' else ';'.join(sorted({m['registro']+'; '+m['raw_file'] for m in mm})),
                     'localizacao':f'Campo resumo; caracteres [{hit[4]}:{hit[5]}]; trecho aparado nas extremidades' if flag=='P' else 'Resumo/título integral disponível no arquivo Materiais locais.csv',
                     'trecho':hit[2] if flag=='P' else '',
                     'limite':'Verificação interna de metadados/resumo; Presente indica abordagem, objetivo, expectativa ou relato, não efeito causal nem validação independente. Não inferir comunidade/espaço híbrido da mera parceria escolar.',
                     'origem':'revisão individual Marco 3 e localização reproduzível'}
            row['materiais_locais']=';'.join(sorted({m['raw_file'] for m in mm}))
            row['auditoria_origem']=(str(BASE.relative_to(ROOT))+'; aba Eixos de análise; códigos '+r['codigos_base']) if flags=='H' else 'Revisao individual.csv; Materiais locais.csv'
            for label,pattern in (('comunidades',r'comunidad|comunit|comunidade'),('saberes_escolares_comunitarios',r'saberes.{0,100}(?:escol|comunit|comunidade)|school.{0,60}knowledge'),('espacos_hibridos',r'espacos? hibrid|hybrid spaces?')):
                mentions=[]
                if axis==2 and row['estado']!='Não verificável':
                    for m in mm:
                        for sentence in re.findall(r'[^.!?\n]+[.!?\n]?',m['resumo']):
                            if re.search(pattern,texto_normalizado(sentence)):
                                mentions.append(m['registro']+': '+sentence.strip())
                row[label]=' | '.join(mentions) if mentions else 'Não verificável' if axis==2 and row['estado']=='Não verificável' else 'Não identificado no material' if axis==2 else ''
            axes.append(row)
    save('Revisao individual.csv',ledger)
    save('Decisoes regionais.csv',decisions)
    save('Corpus goiano.csv',included)
    save('Tres eixos.csv',axes)
    pending=[]
    for r in decisions:
        if r['decisao']!='Pendente':continue
        p=dict(r)
        identity=r['obra_id'] in ('M2-6fc274039407a243','M2-f5ac63d543e7078a')
        strong=r['afiliacao_goias']=='Sim' or r['via_do_vinculo_goiano']!='não comprovada'
        p['prioridade_residual']='1 — identidade com elegibilidade sustentada' if identity else '2 — vínculo sustentado; outro critério incompleto' if strong else '3 — vínculo regional e/ou outros critérios não comprovados'
        p['efeito_potencial']='Duas unidades podem acrescentar uma ou duas obras ao corpus; não somar antes de resolver versões.' if identity else 'Pode alterar inclusão regional; eventual inclusão exige todos os critérios e nova conferência de identidade.'
        p['evidencia_faltante']='Texto específico do artigo/capítulo para decidir identidade de obra versus versão.' if identity else r['justificativa']
        pending.append(p)
    save('Pendencias regionais.csv',pending)
    save('Correcoes de extracao.csv',corrections,['obra_id','eixo','correcao'])
    pv=read(OUT/'Proveniencia.csv')
    for p in pv:p['obra_id_anterior_marco3']=p['obra_id'];p['obra_id']=mapping[p['obra_id']]
    save('Proveniencia regional.csv',pv)
    relations=[]
    for ia,ib,status,note in (
        (28,77,'mesma obra; fundida','Tese UFU: mesmo DOI 10.14393/ufu.te.2022.620 e handle 123456789/37389; autoria abreviada no OpenAlex.'),
        (37,40,'publicações relacionadas preservadas','Relato em anais versus artigo de periódico, DOIs próprios e formatos distintos; não interpretar como duas intervenções independentes.'),
        (39,82,'pendente; ambas fora da contagem','Artigo e capítulo inglês com autores e resumo traduzido equivalentes; sem texto integral não se resolve obra versus versão. Contagem possível de uma ou duas obras, a decidir.'),
        (61,67,'publicações relacionadas preservadas','Artigo Poliges e resumo expandido têm DOIs, veículos e extensões distintos; mesma pesquisa não significa duas amostras independentes.'),
        (31,56,'relatos sucessivos preservados','Projeto em andamento e relato posterior com resultados de portfólios; títulos/anos distintos. Não somar participantes como amostras independentes.')):
        relations.append({'obra_a':mapping[priority[ia-1]['obra_id']],'obra_b':mapping[priority[ib-1]['obra_id']],
                          'estado':status,'evidencia_e_limite':note})
    save('Relacoes bibliograficas regionais.csv',relations)
    result={'unidades_antes':len(initial),'unidades_depois':len(decisions),'fusoes_adicionais':1,
            'decisoes':dict(Counter(r['decisao'] for r in decisions)),
            'registros_origem':len(pv),'revisoes_individuais':len(ledger),
            'eixos':len(axes),'estados_eixos':dict(Counter(r['estado'] for r in axes)),
            'extracoes_historicas':sum(r['origem']=='extração histórica reaproveitada' for r in axes),
            'correcoes_de_extracao':len(corrections)}
    assert len(decisions)==1529 and len(pv)==2053
    assert len(axes)==3*len(included)
    assert len({(r['obra_id'],r['eixo']) for r in axes})==len(axes)
    assert len({p['registro'] for p in pv})==len(pv)
    (OUT/'Auditoria final.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
