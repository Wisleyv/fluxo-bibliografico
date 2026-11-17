"""Integração incremental de proveniência com identidades objetivamente sustentadas."""
import json
import shutil
from collections import Counter
from scripts.avaliar_capes_20261116 import ROOT,A,SOURCE,URL,sha,read
from scripts.entregar_marco5 import save_csv


def main():
    out=A/'integracao_capes_20261116'
    if out.exists():raise FileExistsError('Preservar rodada existente')
    audit=json.loads((A/'capes_20261116_avaliacao/Auditoria.json').read_text(encoding='utf8'))
    assert all(sha(ROOT/p)==h for p,h in audit['hashes_insumos_preservados'].items())
    out.mkdir()
    archived=ROOT/'dados/brutos/portal-capes/portal-capes__nacional-filtrado__20261116__RIS.ris'
    if archived.exists():assert sha(archived)==sha(SOURCE)
    else:shutil.copy2(SOURCE,archived)
    rows=read(A/'capes_20261116_avaliacao/Registros e correspondencias.csv')
    variants=read(A/'capes_20261116_avaliacao/Variantes e prioridades bibliograficas.csv')
    objective={r['registro_capes'] for r in variants if r['caso']=='variação por subtítulo/prefixo'}
    old=read(A/'marco2_fechamento/Proveniencia.csv');units=read(A/'marco2_fechamento/Registro de decisoes.csv')
    byid={r['obra_id']:r for r in units};accepted=[];pending=[]
    for r in rows:
        targets=r['obras_candidatas'].split(';') if r['obras_candidatas'] else []
        stable=(r['categoria']=='identificador concordante com acervo' or r['registro_capes'] in objective) and len(targets)==1
        decision={**r,'estado_integracao':'proveniência vinculada' if stable else 'pendente de conciliação',
                  'obra_id_confirmada':targets[0] if stable else '',
                  'regra_integracao':'Identificador e metadados comparados concordantes' if r['categoria']=='identificador concordante com acervo' else 'ID, DOI, ano, autoria e prefixo de título concordantes' if stable else 'Não promover correspondência candidata a identidade'}
        (accepted if stable else pending).append(decision)
        if stable:
            p={k:'' for k in old[0]};p.update(obra_id=targets[0],registro=r['registro_capes'],fonte='Portal CAPES',record_id=r['registro_capes'],source_record_id=r['id_original'],source_run_id='capes-nacional-filtrado-20261116',raw_file=str(archived.relative_to(ROOT)),coletado_em='2026-11-16',ano_publicacao_original=r['ano_publicacao_ris'],tipo_original=r['tipo_original'],titulo_original=r['titulo'],autoria_original=r['autoria_original'],doi_original_normalizado=r['doi_normalizado'],tema_previo=byid[targets[0]]['decisao'],evidencia_tema='Decisão da obra preservada; recuperação CAPES não é critério de elegibilidade.')
            old.append(p)
    save_csv(out/'Registros CAPES integrados.csv',accepted)
    save_csv(out/'Pendencias CAPES.csv',pending)
    save_csv(out/'Proveniencia vinculada.csv',old)
    for name in ['Corpus nacional.csv','Registro de decisoes.csv']:shutil.copy2(A/'marco2_fechamento'/name,out/name)
    counts=Counter(p['obra_id'] for p in old)
    for u in units:
        u['registros_origem']=str(counts[u['obra_id']])
        u['fontes']=';'.join(sorted({p['fonte'] for p in old if p['obra_id']==u['obra_id']}))
    save_csv(out/'Registro de decisoes.csv',units)
    save_csv(out/'Corpus nacional.csv',[u for u in units if u['decisao']=='incluída'])
    manifest={'estado':'integração de proveniência executada; fechamento bibliográfico e nova entrega pendentes','consulta':URL,'coleta_capes':'2026-11-16','corte_publicacao':'2026-11-08','registros_capes':len(rows),'vinculados':len(accepted),'pendentes':len(pending),'proveniencias_vinculadas':len(old),'corpus_nacional_preservado':7780,'snapshot_openalex_ids_coincidentes':647,'sha256_ris':sha(SOURCE),'limitacao':'Sobreposição nominal não equivale a identidades confirmadas nem completude. Campos de autoria concatenada não foram desmembrados.'}
    assert len(accepted)+len(pending)==675
    assert len({p['registro'] for p in old})==len(old)
    assert len([u for u in units if u['decisao']=='incluída'])==7780
    (out/'Manifesto.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
