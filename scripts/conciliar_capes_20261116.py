"""Fase bibliográfica: concilia os 49 casos, sem nova coleta ou triagem temática."""
import json
import re
import html
from collections import Counter,defaultdict
from scripts.avaliar_capes_20261116 import A,ROOT,read,sha,titulo_normalizado,texto_normalizado
from scripts.entregar_marco5 import save_csv

BASE=A/'integracao_capes_20261116'
OUT=BASE/'conciliacao'
MASTER='M2-a279c6aac5c92b01'
MERGED='M2-d0c27c83901c3376'


def validate_merge(a,b,work):
    assert titulo_normalizado(a['titulo'])==titulo_normalizado(b['titulo'])
    tokens=lambda v:Counter(re.findall(r'\w+',texto_normalizado(html.unescape(v))))
    assert tokens(a['autoria'])==tokens(b['autoria'])
    assert a['anos_publicacao']==b['anos_publicacao']=='2016'
    urls=' '.join(str(l.get('landing_page_url') or '').lower() for l in work['locations'])
    assert all(x in urls for x in ['10.1590/s2176-6681/3368314027','10.24109/2176-6681.rbep.97i245.3421','s2176-66812016000100031'])
    assert work['biblio']['volume']=='97' and work['biblio']['first_page']=='31'


def main():
    if OUT.exists():raise FileExistsError('Conciliação existente; preservar.')
    inputs=[BASE/n for n in ['Pendencias CAPES.csv','Registros CAPES integrados.csv','Proveniencia vinculada.csv','Registro de decisoes.csv']]
    hashes={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    pending=read(inputs[0]);accepted=read(inputs[1]);prov=read(inputs[2]);units={u['obra_id']:u for u in read(inputs[3])}
    raw=ROOT/next(p['raw_file'] for p in prov if p['registro']=='https://openalex.org/W2345075798')
    work=next(w for w in json.loads(raw.read_text(encoding='utf8'))['response']['results'] if w['id']=='https://openalex.org/W2345075798')
    validate_merge(units[MASTER],units[MERGED],work)
    hold={'0161':'Autoria CAPES Rálita Murila versus Rafael Rodrigues no arquivo; não escolher autoria nem identidade por ID isolado.',
          '0249':'Lista de autores diverge: Wanieverlyn versus Wagner; conteúdo/título compatíveis, mas requer conciliação específica.',
          '0651':'CAPES omite coautor Vanderlei; falta evidência independente para concluir composição autoral/versão.'}
    ledger=[];remaining=[]
    for r in pending:
        code=r['registro_capes'][-4:];gid=r['obras_candidatas'];note='';resolved=True
        if code in hold:resolved=False;note=hold[code]
        elif not gid and code!='0134':resolved=False;note='Sem identidade local sustentada; tema/data e busca de variantes ainda necessários. Não é exclusão nem obra nova confirmada.'
        elif code=='0029':
            gid=MASTER;note='Mesma obra confirmada: as localizações arquivadas W2345075798 contêm ambos os DOIs e o PID S2176-66812016000100031 da base SciELO b0560bbc; autores, título, ano 2016 e volume 97(245), pp.31–45 concordantes. Fundir dois componentes incluídos.'
        elif code=='0048':note='Identidade sustentada por ID/DOI, título e autoria compatíveis. Manter publicação 2013 sustentada pelo PID/volume e data arquivada; guardar 2019 como metadado discordante CAPES, sem substituição de ano.'
        elif code=='0094':note='Reaproveitada identidade conferida no fechamento do Marco 2: artigo SciELO/PID, título, três autoras e 2013; ID W3196821779 e DOI alternativo são nova proveniência da mesma obra. Instituições no AU não são novas pessoas.'
        elif code=='0134':gid='M2-7e1c0fb88fce15de';note='Cury: retirar DOI anexado apenas da chave de título; título, autoria, 2013 e DOI correto 10.5752/p.2318-7344.2013v1n1p13 concordam com W2141262701. Campo DO com prefixo repetido preservado como erro de origem.'
        elif 'DOI difere' in r['conflitos']:note='Mesmo ID, título específico, autoria e ano concordantes; vincular recuperação à obra. Preservar divergência DOI como problema de metadado, sem declarar DOI novo canônico.'
        elif r['categoria'].startswith('somente título'):note='Leitura individual: título específico, ano e autoria compatíveis (abreviações/ordem de nomes); vincular como nova recuperação, preservando diferenças e identificadores. Não aplicar esta decisão a títulos genéricos.'
        else:note='Leitura individual: mesmo ID e DOI, ano e título completo/abreviado ou traduzido compatíveis; autoria conferida, sem substituir nomes do acervo.'
        entry={**r,'estado_integracao':'proveniência vinculada' if resolved else 'pendente de conciliação','obra_id_confirmada':gid if resolved else '',
               'regra_integracao':note}
        ledger.append({'registro_capes':r['registro_capes'],'decisao':'vincular' if resolved else 'pendente','obra_id':gid if resolved else '',
                       'fundamento':note,'evidencia':'RIS por posição; Registros e correspondencias.csv; metadados/locais OpenAlex e proveniência dos marcos anteriores'})
        if not resolved:remaining.append(entry);continue
        accepted.append(entry)
        p={k:'' for k in prov[0]};p.update(obra_id=gid,registro=r['registro_capes'],fonte='Portal CAPES',record_id=r['registro_capes'],source_record_id=r['id_original'],source_run_id='capes-nacional-filtrado-20261116',raw_file='dados/brutos/portal-capes/portal-capes__nacional-filtrado__20261116__RIS.ris',coletado_em='2026-11-16',ano_publicacao_original=r['ano_publicacao_ris'],tipo_original=r['tipo_original'],titulo_original=r['titulo'],autoria_original=r['autoria_original'],doi_original_normalizado=r['doi_normalizado'],evidencia_tema='Identidade conciliada; elegibilidade anterior preservada.')
        prov.append(p)
    # Uma fusão com evidência primária local; preservar todos os identificadores.
    old=units.pop(MERGED);u=units[MASTER]
    for field in ['ids_anteriores','codigos_base','ids_openalex','tipos_sustentados']:
        u[field]=';'.join(sorted(set(filter(None,(u[field]+';'+old[field]).split(';')))))
    for p in prov:
        p['obra_id_antes_conciliacao']=p['obra_id']
        if p['obra_id']==MERGED:p['obra_id']=MASTER
    for r in accepted:
        if r['obra_id_confirmada']==MERGED:r['obra_id_confirmada']=MASTER
    by=defaultdict(list)
    for p in prov:by[p['obra_id']].append(p)
    for gid,u in units.items():
        u['fontes']=';'.join(sorted({p['fonte'] for p in by[gid]}));u['registros_origem']=str(len(by[gid]))
    OUT.mkdir()
    save_csv(OUT/'Revisao dos 49 registros.csv',ledger);save_csv(OUT/'Registros CAPES integrados.csv',accepted)
    save_csv(OUT/'Pendencias CAPES.csv',remaining);save_csv(OUT/'Proveniencia vinculada.csv',prov)
    save_csv(OUT/'Registro de decisoes.csv',list(units.values()));corpus=[u for u in units.values() if u['decisao']=='incluída'];save_csv(OUT/'Corpus nacional.csv',corpus)
    save_csv(OUT/'Ponte de identidades.csv',[{'id_anterior':MERGED,'id_vigente':MASTER,'evidencia':'Mesmo PID e ambos os DOIs nas localizações arquivadas; uma obra, todas as proveniências preservadas.'}])
    assert len(ledger)==49 and len(accepted)==665 and len(remaining)==10
    assert len(prov)==14413 and len({p['registro'] for p in prov})==len(prov)
    assert len(corpus)==7779 and sum(int(u['registros_origem']) for u in units.values())==len(prov)
    assert all(sha(ROOT/p)==h for p,h in hashes.items())
    result={'estado':'fase bibliográfica executada; delta de elegibilidade, indicadores e entrega ainda pendentes','revisados':49,'resolvidos':39,'residuais':10,'total_capes_vinculado':665,'proveniencias_vinculadas':len(prov),'fusoes_entre_inclusoes':1,'nacional_operacional_apos_fusao':len(corpus),'inclusoes_novas_nesta_fase':0,'insumos_preservados':hashes}
    (OUT/'Verificacoes.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
