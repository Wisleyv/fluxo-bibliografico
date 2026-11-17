"""Fechamento local incremental: regras explícitas, evidência e histórico preservados."""
import csv
import hashlib
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from openpyxl import load_workbook
from scripts.construir_corpus_marco2 import A, ROOT, read, tokens
from scripts.preanalise_e_validacao_20261115 import texto_normalizado

OLD=A/'marco2'
OUT=A/'marco2_fechamento'
PROG=r'\bpibid\w*\b|programa institucional de bolsas? de iniciacao (?:a |à )?docencia|institutional scholarship.{0,70}(?:teaching initiation|initiation (?:to|into) teaching)|programa institucional de becas.{0,60}(?:docencia|ensenanza)'
FRAME=r'formac|docenc|aprendiz|contribui|impact|experien|relato|identidad|trajet|pratic|particip|percep|saberes|politic|avaliac|analise|ensino|desenvolvimento|investiga|training|teaching|learning|contribut|identity|analysis|education|practice'
ACTION=r'analisa|analisar|investiga|investigar|discute|discutir|relata|relatar|objetiv|experienci|pesquisa|estud[oa]|desenvolvid|realizad|participantes|bolsistas|analy[sz]|investigat|discuss|report|aim|study|research|develop|conduct|accompanied'
EDUC=r'docen|profess|licenc|pedagog|escol|ensino|formac|educac|teach|school|education|training|ensenanza'
STUDY=r'este (?:artigo|trabalho|estudo|relato|articulo|trabajo|estudio)|esta (?:pesquisa|investigacao|investigacion)|objetivo (?:deste|desta)|relata se|relata-se|investigamos|analisamos|this (?:article|paper|study|work|research)|a group of.{0,100}teachers|desenvolvid.{0,180}(?:pibid|programa institucional)|realizad.{0,180}(?:pibid|programa institucional)|(?:participantes|sujeitos).{0,120}(?:pibid|programa institucional)'
BASIC={'article','dissertation','book','book-chapter','conference-paper','review'}
EXTENDED={'conference-abstract','preprint','editorial','book-review','report','letter'}


def thematic(title,abstract,previous=False):
    if previous:return 'incluir','leitura anterior reaproveitada',''
    t=texto_normalizado(title or '')
    if re.search(PROG,t) and re.search(FRAME,t):
        return 'incluir','título explicita programa e objeto formativo/investigativo',title
    for sentence in re.split(r'[.!?;\n]+',abstract or ''):
        s=texto_normalizado(sentence)
        if len(tokens(s))>=14 and re.search(PROG,s) and re.search(ACTION,s) and re.search(EDUC,s):
            if not re.search(STUDY,s):continue
            if re.search(r'financiamento|agradec|palavras chave|keywords',s):continue
            # Descartar descrições que se resumem a nome de evento ou referência.
            if re.match(r'^\s*(enfoc|anais|seminario|congresso|encontro)\b',s):continue
            return 'incluir','resumo explicita pesquisa/ação/participantes e contexto PIBID',sentence[:1400]
    return 'pendente','evidência temática insuficiente para decisão por regra',''


def save(name,rows,fields=None):
    with (OUT/name).open('w' if '--atualizar' in sys.argv else 'x',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    if OUT.exists() and '--atualizar' not in sys.argv:raise FileExistsError('Rodada existente; preservar ou atualizar explicitamente os produtos desta rodada.')
    inputs=[OLD/n for n in ('Registro de unidades.csv','Proveniencia.csv','Corpus nacional provisorio.csv','Conciliacao de identidades.csv','Conferencia amostral.csv')]
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    units=read(inputs[0]);prov=read(inputs[1]);prior_core={r['obra_id'] for r in read(inputs[2])};edges=read(inputs[3])
    by_old={r['obra_id']:r for r in units}; nodes={r['registro']:r for r in prov}
    old_by_node={r['registro']:r['obra_id'] for r in prov}
    oa={r['openalex_id']:r for r in read(A/'openalex_busca_restrita_20261115.csv')}
    w=load_workbook(A/'triagem_criterio_defesa_20261115.xlsx',read_only=True,data_only=True)
    it=iter(w['Triagem'].values);hh=next(it);base={v[0]:dict(zip(hh,v)) for v in it if v[0]};w.close()
    parent={k:k for k in by_old}
    def find(k):
        while parent[k]!=k:parent[k]=parent[parent[k]];k=parent[k]
        return k
    new_decisions=[]
    def confirm(a,b,reason):
        x,y=find(old_by_node[a]),find(old_by_node[b]);parent[max(x,y)]=min(x,y)
        new_decisions.append({'registro_a':a,'registro_b':b,'decisao':'confirmada','fundamento':reason})
    # Três controles bilíngues: título/autoria/tipo/defesa e instituição conferidos.
    for a,b,reason in (
        ('BASE:c370c6d5','BASE:bc0f1ea5','UNIPAMPA/Jaguarão; título, Igor Galho Teixeira, dissertação e defesa 2024; resumos espanhol/português com mesmos objetivos e três encontros de duas horas.'),
        ('BASE:ced05892','BASE:b05f93c0','UFS; título, Cheila Raiane Menezes Oliveira, dissertação e defesa 2024; resumos inglês/português com mesmo objeto de pensamento computacional e oficinas PIBID.'),
        ('BASE:dcee17bd','BASE:f40e06af','UFMS/TeDiMEM; título, Juliana Leal Salmasio, tese e defesa 2024; resumos traduzidos com oito estudantes e 32 reuniões PIBID.'),
        ('BASE:ebceb9d5','https://openalex.org/W1980441681','Mesmo URL SciELO PID S2176-66812013000300007 nas localizações OpenAlex; título, 2013 e três autoras compatíveis; afiliações indevidamente concatenadas como autores na API.')):
        confirm(a,b,reason)
    # Uma tese e um texto em periódico são publicações relacionadas, não uma obra única.
    distinct={frozenset(('BASE:a87df351','https://openalex.org/W4292209810')),
              frozenset(('https://openalex.org/W4292209810','https://openalex.org/W7119248750'))}
    for pair in distinct:
        a,b=sorted(pair)
        new_decisions.append({'registro_a':a,'registro_b':b,'decisao':'distintas relacionadas',
          'fundamento':'Tese UECE 2021, ID siduece 98506, versus publicação em periódico RBPAB 2022, volume 7(20), páginas 241–246 e DOI próprio. Resumo de tese reproduzido não apaga a publicação distinta.'})
    mapping={u:find(u) for u in by_old}
    group=defaultdict(list)
    for old in by_old:group[mapping[old]].append(old)
    updated_edges=[];identity_pending=set()
    for e in edges:
        x,y=mapping[old_by_node[e['registro_a']]],mapping[old_by_node[e['registro_b']]]
        d=dict(e)
        if x==y:d['estado_fechamento']='absorvida por identidade sustentada'
        elif frozenset((e['registro_a'],e['registro_b'])) in distinct:d['estado_fechamento']='distintas relacionadas'
        elif e['efeito_residual']=='pode alterar contagem':
            d['estado_fechamento']='pendente';identity_pending.update((x,y))
        else:d['estado_fechamento']='sem efeito'
        updated_edges.append(d)
    records_by_group=defaultdict(list)
    for p in prov:
        p['obra_id_anterior']=p['obra_id'];p['obra_id']=mapping[p['obra_id']]
        records_by_group[p['obra_id']].append(p)
    final=[];sample_candidates=defaultdict(list)
    for gid,oldids in sorted(group.items()):
        rr=records_by_group[gid];uu=[by_old[k] for k in oldids]
        has_previous=any(u['nucleo_com_evidencia_temática']=='1' for u in uu)
        evidence=[];kind_support=[];kind_pending=[]
        for r in rr:
            if r['registro'] in oa:
                o=oa[r['registro']];abstract=o['resumo'];venue=o['fonte'];kind=o['tipo']
            else:
                b=base[r['registro'][5:]];abstract=b['Resumo'] or '';venue=b['Instituição associada'] or '';kind=r['tipo_original']
            st,rule,excerpt=thematic(r['titulo_original'],abstract,False)
            if st=='incluir':evidence.append((rule,excerpt,r['registro']))
            known=r['fonte']!='OpenAlex' and any(u['suporte_documental']=='compatível com escopo' for u in uu)
            if kind in BASIC or known:kind_support.append(kind)
            elif kind in EXTENDED and r['autoria_original'] and (venue or (kind=='preprint' and r['doi_original_normalizado'])) and st=='incluir' and (kind!='editorial' or re.search(PROG,texto_normalizado(r['titulo_original'])) or (texto_normalizado(r['titulo_original']).strip() not in ('editorial','apresentacao do dossie') and re.search(r'neste artigo|este artigo',texto_normalizado(abstract)))):kind_support.append(kind)
            elif kind=='other' and r['autoria_original'] and venue and st=='incluir' and re.search(r'este artigo|presente trabalho|relato de experi|pesquisa.{0,80}qualitativ',texto_normalizado(abstract)):
                kind_support.append('outro acadêmico: gênero explícito no resumo')
            else:kind_pending.append(kind)
        thematic_yes=has_previous or bool(evidence)
        theme_rule='leitura anterior reaproveitada' if has_previous else evidence[0][0] if evidence else 'insuficiente'
        # Se nenhuma evidência acadêmica existe, não incluir por tipo isolado.
        academic=bool(kind_support)
        times={u['suporte_temporal'] for u in uu}
        time_ok='no período' in times and not (times & {'fora do período','conflito temporal'})
        eligible=thematic_yes and academic and time_ok
        status='incluída' if eligible and gid not in identity_pending else 'elegível com identidade pendente' if eligible else 'pendente'
        reasons=[]
        if not thematic_yes:reasons.append('pertinência temática insuficientemente sustentada')
        if not academic:reasons.append('natureza acadêmica/tipo sem suporte suficiente')
        if not time_ok:reasons.append('publicação no corte não comprovada')
        if gid in identity_pending:reasons.append('identidade pode alterar contagem')
        previous_count=sum(k in prior_core for k in oldids)
        old0=uu[0]
        entry={'obra_id':gid,'ids_anteriores':';'.join(oldids),'decisao':status,
               'titulo':old0['titulo'],'autoria':old0['autoria'],
               'fontes':';'.join(sorted({r['fonte'] for r in rr})),
               'ids_openalex':';'.join(sorted(r['registro'] for r in rr if r['fonte']=='OpenAlex')),
               'codigos_base':';'.join(sorted(r['registro'][5:] for r in rr if r['fonte']!='OpenAlex')),
               'registros_origem':len(rr),'tipos_sustentados':';'.join(sorted(set(kind_support))),
               'tipos_sem_suporte':';'.join(sorted(set(kind_pending))),
               'criterio_tema':theme_rule,'registro_evidencia':evidence[0][2] if evidence else '',
               'trecho_evidencia':evidence[0][1] if evidence else 'Ver leitura anterior na proveniência e conferência amostral.',
               'suporte_temporal':'no período' if time_ok else 'pendente',
               'anos_publicacao':';'.join(sorted({v for u in uu for v in u['anos_publicacao'].split(';') if v})),
               'datas_publicacao':';'.join(sorted({v for u in uu for v in u['datas_publicacao'].split(';') if v})),
               'pendencias':';'.join(reasons),'unidades_nucleo_anterior':previous_count,
               'interpretacao_nacional':'escopo temático nacional aprovado; sem filtro de afiliação'}
        final.append(entry)
        if not previous_count:sample_candidates[(theme_rule,status)].append(entry)
    OUT.mkdir(exist_ok=True)
    save('Registro de decisoes.csv',final)
    save('Corpus nacional.csv',[u for u in final if u['decisao']=='incluída'],list(final[0]))
    save('Elegiveis com identidade pendente.csv',[u for u in final if u['decisao']=='elegível com identidade pendente'],list(final[0]))
    save('Pendencias residuais.csv',[u for u in final if u['decisao']!='incluída'],list(final[0]))
    save('Tipos com efeito imediato.csv',[u for u in final if 'natureza acadêmica' in u['pendencias'] and u['criterio_tema']!='insuficiente' and u['suporte_temporal']=='no período'],list(final[0]))
    save('Proveniencia.csv',prov)
    save('Revisao de identidades prioritarias.csv',new_decisions)
    save('Estado de todas as relacoes.csv',updated_edges)
    transfers=[]
    for c,b in base.items():
        dy=str(b['Ano de defesa'] or '')
        if dy.isdigit() and 2020<=int(dy)<=2026 and b['Tipo de produção'] in ('Tese','Dissertação'):
            transfers.append({'codigo_base':c,'obra_id':mapping[old_by_node['BASE:'+c]],'ano_defesa':dy,
                'titulo':b['Título'],'contexto_goias':b['Contexto de Goiás'],'afiliacao_goias':b['Afiliação em Goiás'],
                'limite':'Candidato por defesa; não é inclusão goiana. Defesa 2026 sem data completa tem evidência limitada.'})
    save('Candidatos por defesa para Marco 3.csv',transfers)
    coverage=[]
    fi={u['obra_id']:u for u in final}
    for source in sorted({p['fonte'] for p in prov}):
        pp=[p for p in prov if p['fonte']==source];ids={p['obra_id'] for p in pp}
        coverage.append({'fonte':source,'registros':len(pp),'unidades':len(ids),**dict(Counter(fi[k]['decisao'] for k in ids))})
    fields=['fonte','registros','unidades','incluída','elegível com identidade pendente','pendente']
    for c in coverage:
        for k in fields:c.setdefault(k,0)
    save('Cobertura atualizada.csv',coverage,fields)
    rng=random.Random(20261116);sample=[]
    for (rule,status),items in sorted(sample_candidates.items()):
        for u in rng.sample(items,min(6,len(items))):sample.append(u)
    save('Amostra de conferencia de regras.csv',sample,list(final[0]))
    assert len(prov)==13748==len({p['registro'] for p in prov})
    assert sum(u['registros_origem'] for u in final)==13748
    assert all((ROOT/p['raw_file']).exists() for p in prov)
    assert all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h for name,h in hashes.items())
    result={'entradas':13748,'unidades_antes':len(units),'unidades_depois':len(final),'fusoes_novas':len(units)-len(final),
      'decisoes':dict(Counter(u['decisao'] for u in final)),
      'motivos_inclusao':dict(Counter(u['criterio_tema'] for u in final if u['decisao']=='incluída')),
      'nucleo_138':dict(Counter(u['decisao'] for u in final if u['unidades_nucleo_anterior'])),
      'nucleo_origens_preservadas':sum(u['unidades_nucleo_anterior'] for u in final),
      'novas_inclusoes':sum(u['decisao']=='incluída' and not u['unidades_nucleo_anterior'] for u in final),
      'exclusoes':0,'transferencias_defesa':len(transfers),'amostra':len(sample),
      'pendencias_por_motivo':dict(Counter(m for u in final for m in u['pendencias'].split(';') if m)),
      'hashes_entradas':hashes}
    (OUT/'Auditoria.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
