"""Entrega local, sem coleta, dos produtos congelados dos marcos 1–4."""
import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.workbook.properties import CalcProperties
from scripts.produzir_indicadores_marco4 import ROOT, OUT as M4, M2, M3, MANIFEST, RUN, read

OUT=ROOT/'dados/entregas/marco5'
if MANIFEST:
    OUT=(ROOT/RUN['diretorio_entrega_proposto']).resolve()
    assert OUT.is_relative_to((ROOT/'dados/entregas').resolve()) and OUT!=(ROOT/'dados/entregas/marco5').resolve()
BOOK=OUT/'Planilha final PIBID.xlsx'
BLUE='17365D'
WARN='Resultados observados: 871 pendências fora da revisão; quatro inclusões por defesa; artigo/capítulo podem acrescentar 1–2 obras; afiliações incompletas. Participação total não estimável.'
if MANIFEST:WARN+=' CAPES: dez ocorrências em componentes provisórios, sem inclusão automática.'


def delivery_counts():
    n=len(read(M2/'Corpus nacional.csv'));g=len(read(M3/'Corpus goiano.csv'))
    matched=sum(r['incluida_no_nacional']=='Sim' for r in read(M4/'Correspondencia Goias Brasil.csv'))
    p=read(M4/'Participacao e contexto Goias.csv')[0];common=read(M4/'Participacao periodo comum.csv')[0]
    return n,g,n+g-matched,int(p['numerador']),int(common['obras_com_afiliacao_goiana_identificada']),int(common['obras_nacionais'])


def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(2**20),b''):h.update(block)
    return h.hexdigest()


def save_csv(p,rows):
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def line(ws,values):
    ws.append(values)
    # max_row/max_column percorrem as células; não recalcular para cada linha.
    for col in range(1,len(values)+1):
        cell=ws.cell(ws._current_row,col)
        if isinstance(cell.value,str):cell.data_type='s'


def format_table(ws,name):
    import re
    if re.fullmatch(r'[A-Za-z]{1,3}[1-9][0-9]*',name):
        raise ValueError('Nome de tabela não pode ser uma referência de célula: '+name)
    ws.freeze_panes='B2';ws.sheet_view.showGridLines=False
    # Usar só o filtro da tabela; um filtro de planilha sobreposto faz
    # o Excel recusar o arquivo, embora openpyxl consiga ler o ZIP.
    table=Table(displayName=name,ref=ws.dimensions)
    table.tableStyleInfo=TableStyleInfo(name='TableStyleMedium2',showRowStripes=True)
    ws.add_table(table)
    for c in ws[1]:c.font=Font(bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor=BLUE)
    ws.row_dimensions[1].height=32
    for column in ws.columns:
        ws.column_dimensions[column[0].column_letter].width=min(48,max(15,len(str(column[0].value))+2))
    ws.print_options.horizontalCentered=True


def import_csv(wb,name,path):
    rows=read(path);ws=wb.create_sheet(name)
    line(ws,list(rows[0]))
    for r in rows:
        values=[]
        for value in r.values():
            try:values.append(float(value) if '.' in value and value.lstrip('-').replace('.','',1).isdigit() else int(value) if value.lstrip('-').isdigit() else value)
            except (TypeError,ValueError):values.append(value)
        line(ws,values)
    format_table(ws,'DadosTabela'+str(len(wb.worksheets)))
    return ws


def prepare():
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'matriz').mkdir(exist_ok=True);(OUT/'previews').mkdir(exist_ok=True)
    national=read(M2/'Corpus nacional.csv');regional=read(M3/'Corpus goiano.csv')
    N,G,U,GN,GC,NC=delivery_counts()
    cross={r['obra_goias']:r for r in read(M4/'Correspondencia Goias Brasil.csv')}
    units=read(M4/'Obras dos indicadores.csv');nu={r['obra_id']:r for r in units if r['escopo']=='nacional'}
    ru={r['obra_id']:r for r in units if r['escopo']=='goiano'};nr={r['obra_id']:r for r in read(M2/'Registro de decisoes.csv')}
    affiliations=defaultdict(set)
    for r in read(M4/'Creditos institucionais.csv'):affiliations[(r['escopo'],r['obra_id'])].add(r['instituicao'])
    regional_by_union={}
    for r in regional:
        cr=cross[r['obra_id']]
        gid=cr['componentes_nacionais'] if cr['incluida_no_nacional']=='Sim' else r['obra_id']
        assert gid not in regional_by_union
        regional_by_union[gid]=r
    union=sorted(set(nu)|set(regional_by_union));assert len(union)==U
    wb=Workbook();ws=wb.active;ws.title='Leia-me';ws.sheet_view.showGridLines=False
    rows=[['PIBID — resultados observados','Numerador','Denominador','Fração observada','Estado'],
          ['Obras nacionais operacionais',N,None,None,'Parcial quanto ao universo; congelado no corpus'],
          ['Obras da revisão Goiás',G,None,None,'Consolidado nas inclusões observadas'],
          ['Obras únicas na união dos corpora',U,None,None,'Consolidado na conciliação observada'],
          ['Afiliação goiana — publicação 2007–08/11/2026',GN,N,None,'Parcial: fração identificada no corpus nacional'],
          ['Afiliação goiana — publicação 2020–08/11/2026',GC,NC,None,'Parcial: fração identificada no período comum'],
          ['Participação total Goiás–Brasil',None,None,'Não estimável','Universo e afiliações incompletos'],
          ['Contexto local/institucional goiano documentado',56,97,None,'Consolidado no corpus regional observado'],
          ['Objeto goiano; local escolar não confirmado',2,97,None,'Separado de contexto escolar confirmado'],
          ['Afiliação goiana na revisão',80,97,None,'Não confundir com contexto goiano'],
          ['Data da coleta OpenAlex','15/11/2026',None,None,'Publicação até 08/11/2026'],
          ['Limitações',WARN,None,None,None],
          ['Uso','Filtros na aba Obras únicas; gráficos nativos G1–G6 vinculados a células; fórmulas recalculadas no Excel.',None,None,None],
          ['Contagem','Autoria e instituições: créditos integrais por obra e fracionários nas tabelas importadas. País é da instituição, não contexto.',None,None,None],
          ['Fontes','Corpora, indicadores e extrações congelados nos marcos 2–4; ver Relatorio metodologico.md e Inventario.csv.',None,None,None],
          ['Edição','Alterar fontes/categorias exige revisar denominadores e evidência; editar tabelas agregadas não reexecuta a triagem científica.',None,None,None]]
    for row in rows:line(ws,row)
    ws['D5']='=B5/C5';ws['D6']='=B6/C6';ws['D5'].number_format=ws['D6'].number_format='0.00%'
    ws.column_dimensions['A'].width=55;ws.column_dimensions['B'].width=28;ws.column_dimensions['C'].width=20
    ws.column_dimensions['D'].width=24;ws.column_dimensions['E'].width=58
    for row in ws:
        for c in row:c.alignment=Alignment(vertical='top',wrap_text=True)
    for i in range(12,17):ws.merge_cells(start_row=i,start_column=2,end_row=i,end_column=5);ws.row_dimensions[i].height=44
    if MANIFEST:
        for row in [['Coleta CAPES','16/11/2026',None,None,'Consulta filtrada; publicação até 08/11/2026'],
                    ['CAPES: registros recuperados',675,None,None,'Registros; não obras únicas'],
                    ['CAPES: vínculos bibliográficos',665,675,None,'Dez ocorrências com identidade provisória'],
                    ['CAPES: ID coincidente com snapshot',647,675,None,'Sobreposição nominal; não identidade validada'],
                    ['CAPES: correspondência verificável',664,671,None,'Parcial: exclui 3 revisões e 1 temporal não verificável'],
                    ['CAPES: obras elegíveis em todas as rodadas',571,N,None,'Proveniência documentada; não 571 obras novas'],
                    ['CAPES: novo lote, obras elegíveis',509,N,None,'21 já recuperadas na rodada anterior; 488 novas proveniências'],
                    ['Linha de base anterior','196/7.780 (2,52%); 67/3.459 (1,94%)',None,None,'Versão anterior preservada; valores atuais nas linhas 5–6']]:line(ws,row)
        for row in range(17,25):ws.row_dimensions[row].height=40
        for row in (19,20,21):ws.cell(row,4,f'=B{row}/C{row}');ws.cell(row,4).number_format='0.00%'
    for c in ws[1]:c.font=Font(bold=True,color='FFFFFF',size=13);c.fill=PatternFill('solid',fgColor=BLUE)
    ws.row_dimensions[1].height=38
    works=wb.create_sheet('Obras únicas')
    line(works,['obra_id','título','nacional','revisão Goiás','ano nacional','ano regional','base ano regional','tipo nacional','tipo regional','afiliação GO nacional','afiliação GO regional','cobertura nacional','cobertura regional','contexto Goiás','autoria','instituições mapeadas','fontes','anos publicação originais','anos defesa','registros OpenAlex','obra_id regional','estado','limite','publicação nacional no período comum'])
    if MANIFEST:works.cell(1,25,'alertas de autoria na integração')
    for gid in union:
        n=nu.get(gid,{});r=regional_by_union.get(gid,{});rg=ru.get(r.get('obra_id'),{});raw=nr.get(gid,{})
        institutions=affiliations[('nacional',gid)]|affiliations[('goiano',r.get('obra_id',''))]
        line(works,[gid,n.get('titulo',r.get('titulo','')),'Sim' if n else 'Não','Sim' if r else 'Não',n.get('ano_serie','fora do corpus'),
                    rg.get('ano_serie','fora da revisão'),rg.get('fundamento_ano',''),n.get('tipo_indicador',''),rg.get('tipo_indicador',''),
                    n.get('afiliacao_goias_observada','fora do corpus'),r.get('afiliacao_goias','fora da revisão'),n.get('cobertura_afiliacao',''),rg.get('cobertura_afiliacao',''),
                    r.get('contexto_goias_estado','não avaliado regionalmente'),raw.get('autoria','ver proveniência regional'),'; '.join(sorted(institutions)),raw.get('fontes','fontes complementares regionais'),
                    n.get('anos_publicacao',r.get('anos_publicacao','')),r.get('anos_defesa',''),raw.get('ids_openalex',r.get('ids_openalex','')),r.get('obra_id',''),
                    'Nacional operacional parcial; revisão consolidada no corpus observado' if r and n else 'Nacional operacional parcial' if n else 'Regional observado; compatibilidade nacional pendente',
                    'Ausência de afiliação não significa não Goiás; datas e identidades conforme fontes arquivadas.',
                    'Sim' if n and n['anos_publicacao'] and all(y.isdigit() and 2020<=int(y)<=2026 for y in n['anos_publicacao'].split(';')) else 'Não'])
        if MANIFEST:
            cell=works.cell(works._current_row,25,raw.get('alertas_integracao',''));cell.data_type='s'
    format_table(works,'ObrasUnicas');works.column_dimensions['B'].width=64;works.column_dimensions['O'].width=42
    end=works.max_row
    def rng(col):return f"'Obras únicas'!${col}$2:${col}${end}"
    ws['B2']=f'=COUNTIF({rng("C")},"Sim")';ws['B3']=f'=COUNTIF({rng("D")},"Sim")';ws['B4']=f'=COUNTA({rng("A")})'
    ws['B5']=f'=COUNTIFS({rng("C")},"Sim",{rng("J")},"Sim")';ws['C5']='=B2'
    ws['B6']=f'=COUNTIFS({rng("C")},"Sim",{rng("J")},"Sim",{rng("X")},"Sim")'
    ws['C6']=f'=COUNTIFS({rng("C")},"Sim",{rng("X")},"Sim")'
    ws['B8']=f'=COUNTIF({rng("N")},"Sim — contexto local/institucional documentado")'
    ws['B9']=f'=COUNTIF({rng("N")},"Objeto goiano; local da escola não verificado")'
    ws['B10']=f'=COUNTIF({rng("K")},"Sim")'
    for row in (8,9,10):ws.cell(row,3,"='Leia-me'!B3")
    axes=import_csv(wb,'Eixos',M3/'Tres eixos.csv')
    years=wb.create_sheet('Anos');line(years,['Ano','Nacional publicação','Goiás publicação','Goiás defesa'])
    for row,y in enumerate(range(2007,2027),2):
        line(years,[str(y),None,None,None]);years.cell(row,2,f'=COUNTIFS({rng("C")},"Sim",{rng("E")},A{row})')
        years.cell(row,3,f'=COUNTIFS({rng("D")},"Sim",{rng("F")},A{row},{rng("G")},"publicação")')
        years.cell(row,4,f'=COUNTIFS({rng("D")},"Sim",{rng("F")},A{row},{rng("G")},"defesa alternativa")')
    line(years,['Divergente',f'=COUNTIF({rng("E")},"divergente")',0,0]);years['B22']=f'=COUNTIF({rng("E")},"divergente")'
    format_table(years,'AnosTabela')
    types=wb.create_sheet('Tipos');line(types,['Escopo','Tipo documental','Obras','Estado'])
    for scope in ('nacional','goiano'):
        for r in read(M4/f'Tipos documentais {scope}.csv'):
            row=types.max_row+1;line(types,[scope,r['categoria'],None,'Consolidado no corpus operacional'])
            col,flag=('H','C') if scope=='nacional' else ('I','D')
            types.cell(row,3,f'=COUNTIFS({rng(flag)},"Sim",{rng(col)},B{row})')
    format_table(types,'TiposTabela')
    cov=wb.create_sheet('Afiliação');line(cov,['Estado','Obras BR','Fração BR','Obras GO','Fração GO'])
    for row,state in enumerate(('conhecida','parcial','desconhecida'),2):
        line(cov,[state,None,None,None,None]);cov.cell(row,2,f'=COUNTIF({rng("L")},A{row})');cov.cell(row,3,f"=B{row}/'Leia-me'!B2")
        cov.cell(row,4,f'=COUNTIF({rng("M")},A{row})');cov.cell(row,5,f"=D{row}/'Leia-me'!B3")
        cov.cell(row,3).number_format=cov.cell(row,5).number_format='0.0%'
    format_table(cov,'AfiliacaoTabela')
    er=wb.create_sheet('Indicadores eixos');line(er,['Eixo','Presente','Não informado','Não verificável','Nome completo'])
    for row,(short,full) in enumerate(zip(['Aprendizagem / identidade','Trajetórias','Relações IES–escola–comunidade'],dict.fromkeys(r['eixo'] for r in read(M3/'Tres eixos.csv'))),2):
        line(er,[short,None,None,None,full])
        for col,state in enumerate(('Presente','Não informado','Não verificável'),2):er.cell(row,col,f'=COUNTIFS(Eixos!$B$2:$B$292,E{row},Eixos!$C$2:$C$292,"{state}")')
    format_table(er,'EixosIndicadores')
    for name,path in [('Instituições BR',M4/'Instituicoes nacional.csv'),('Instituições GO',M4/'Instituicoes goiano.csv'),
                      ('Autorias BR',M4/'Autorias nacional.csv'),('Autorias GO',M4/'Autorias goiano.csv'),
                      ('Estado indicadores',M4/'Estado dos indicadores.csv'),('Contexto',M4/'Contexto Goias separado.csv')]:import_csv(wb,name,path)
    if MANIFEST:
        for name,file in [('Sobreposição CAPES','Niveis de sobreposicao CAPES OpenAlex.csv'),('Antes e depois','Comparacao antes depois.csv'),
                          ('Países BR','Geografia pais nacional.csv'),('Países GO','Geografia pais goiano.csv'),
                          ('Temáticas BR','Tematicas OpenAlex nacional.csv'),('Temáticas GO','Tematicas OpenAlex goiano.csv'),
                          ('Alertas metadados','Alertas de metadados.csv')]:import_csv(wb,name,M4/file)
    chartconfigs=[
        ('G1 Nacional','line','Anos',1,2,2,2,21,'Brasil — publicação por ano\nParcial | N=7.780; 2 obras divergentes fora da curva\n2026 até 08/11; coleta OpenAlex em 15/11/2026'),
        ('G2 Goiás','col','Anos',1,3,4,15,21,'Goiás — publicação e defesa separadas\nConsolidado nas 97 inclusões: 93 publicações + 4 defesas\n871 pendências fora; versões podem acrescentar 1–2 obras; 2026: corte 08/11'),
        ('G3 Tipos GO','bar','Tipos',2,3,3,15,19,'Goiás — tipos documentais\nConsolidado nas 97 obras observadas\n871 pendências fora; quatro inclusões por defesa'),
        ('G4 Afiliação','col','Afiliação',1,2,2,2,4,'Brasil — cobertura de afiliação\nParcial | N=7.780; conhecida 3.024, parcial 1.485, desconhecida 3.271\nConhecida refere-se às autorias observadas no arquivo'),
        ('G5 Eixos','col','Indicadores eixos',1,2,4,2,4,'Goiás — estados da evidência nos três eixos\nConsolidado: 97 obras por eixo; 291 extrações\nNão informado e Não verificável não são ausência do fenômeno'),
        ('G6 Tipos BR','bar','Tipos',2,3,3,2,14,'Brasil — tipos documentais\nConsolidado no corpus operacional de 7.780 obras\nGrau não discriminado preservado; universo nacional parcial')]
    manifest=[]
    for name,kind,source,cat,lo,hi,start,stop,title in chartconfigs:
        title=title.replace('7.780',f'{N:,}'.replace(',','.'))
        if name=='G4 Afiliação':
            unknown=next(r['obras'] for r in read(M4/'Cobertura de campos.csv') if r['escopo']=='nacional' and r['campo']=='afiliação' and r['estado']=='desconhecida')
            title=title.replace('3.271',f'{int(unknown):,}'.replace(',','.'))
        if MANIFEST and name=='G1 Nacional':title=title.replace('coleta OpenAlex em 15/11/2026','coletas: OpenAlex 15/11 e CAPES 16/11/2026')
        sh=wb.create_sheet(name);sh.sheet_view.showGridLines=False
        sh.column_dimensions['A'].width=4
        for col in 'BCDEFGHIJKLMN':sh.column_dimensions[col].width=12
        sh.merge_cells('B2:N3');sh['B2']=name+' | dados e evidências nos marcos 2–4';sh['B2'].font=Font(size=15,bold=True,color=BLUE)
        chart=LineChart() if kind=='line' else BarChart()
        if kind!='line':chart.type=kind
        chart.style=13;chart.title=title;chart.width=29;chart.height=17
        src=wb[source]
        # Cabeçalho separado do intervalo para evitar os anos anteriores no gráfico regional.
        for col in range(lo,hi+1):
            chart.add_data(Reference(src,min_col=col,min_row=start,max_row=stop),titles_from_data=False)
            chart.series[-1].title=__import__('openpyxl.chart.series',fromlist=['SeriesLabel']).SeriesLabel(strRef=__import__('openpyxl.chart.data_source',fromlist=['StrRef']).StrRef(f=f"'{source}'!${get_column_letter(col)}$1"))
        chart.set_categories(Reference(src,min_col=cat,min_row=start,max_row=stop))
        chart.y_axis.title='Obras' if kind!='bar' else None
        chart.x_axis.title='Obras' if kind=='bar' else None
        chart.legend=None if lo==hi else chart.legend
        if kind=='line':chart.series[0].graphicalProperties.line.solidFill=BLUE
        sh.add_chart(chart,'B5');sh.merge_cells('B39:N42');sh['B39']=WARN;sh['B39'].alignment=Alignment(wrap_text=True,vertical='top');sh['B39'].font=Font(size=11,color='7F4D00')
        sh.print_area='B2:N43';sh.sheet_properties.pageSetUpPr.fitToPage=True;sh.page_setup.orientation='landscape';sh.page_setup.paperSize=sh.PAPERSIZE_A3;sh.page_setup.fitToWidth=1;sh.page_setup.fitToHeight=1
        manifest.append({'aba':name,'fonte':source,'linhas':f'{start}:{stop}','titulo_e_nota':title,'estado':'nativo e editável; aguarda conferência Excel/visual'})
    save_csv(OUT/'Graficos.csv',manifest)
    checks=wb.create_sheet('Conferências');line(checks,['Verificação','Valor calculado','Esperado','Resultado'])
    for label,formula,expected in [('Nacional',"='Leia-me'!B2",N),('Regional',"='Leia-me'!B3",G),('União única',"='Leia-me'!B4",U),
         ('Fração nacional — numerador',"='Leia-me'!B5",GN),('Período comum — numerador',"='Leia-me'!B6",GC),('Período comum — denominador',"='Leia-me'!C6",NC),
         ('Anos nacional','=SUM(Anos!B2:B22)',N),('Anos Goiás','=SUM(Anos!C2:D21)',G),('Eixos','=SUM(\'Indicadores eixos\'!B2:D4)',3*G),
         ('Afiliação nacional',"=SUM('Afiliação'!B2:B4)",N),('Afiliação regional',"=SUM('Afiliação'!D2:D4)",G)]:
        row=checks.max_row+1;line(checks,[label,None,expected,None]);checks.cell(row,2,formula);checks.cell(row,4,f'=IF(B{row}=C{row},"OK","DIVERGÊNCIA")')
    format_table(checks,'ConferenciasTabela')
    wb.calculation=CalcProperties(calcId=191029,fullCalcOnLoad=True)
    wb.save(BOOK)
    # Cobertura histórica e cobertura elegível atual são universos diferentes.
    copies=[(ROOT/'dados/analises/marco1/Matriz de cobertura.csv','Controles Marco 1.csv'),
            (ROOT/'dados/analises/marco1/Sobreposicao entre fontes.csv','Sobreposicao controles Marco 1.csv'),
            (ROOT/'dados/analises/marco2_fechamento/Cobertura atualizada.csv','Cobertura operacional Marco 2.csv')]
    for src,name in copies:shutil.copy2(src,OUT/'matriz'/name)
    prov=read(M2/'Proveniencia.csv');sources=defaultdict(set)
    for p in prov:
        if p['obra_id'] in nu:sources[p['obra_id']].add(p['fonte'])
    combos=Counter(tuple(sorted(s)) for s in sources.values())
    save_csv(OUT/'matriz/Combinacoes fontes corpus nacional.csv',[{'fontes':';'.join(s),'obras':c,'denominador':N,'estado':'Consolidado no corpus operacional observado; não completude'} for s,c in sorted(combos.items())])
    names=sorted(set().union(*sources.values()));overlap=[]
    for a in names:
        for b in names:
            if a<=b:overlap.append({'fonte_a':a,'fonte_b':b,'obras_compartilhadas':sum(a in s and b in s for s in sources.values()),'denominador':N,'estado':'Consolidado no corpus elegível operacional; contagens não aditivas'})
    save_csv(OUT/'matriz/Sobreposicao corpus nacional.csv',overlap)
    matrix=Workbook();matrix.remove(matrix.active)
    for name,file in [('Controles M1','Controles Marco 1.csv'),('Sobreposição M1','Sobreposicao controles Marco 1.csv'),('Cobertura M2','Cobertura operacional Marco 2.csv'),('Combinações elegíveis','Combinacoes fontes corpus nacional.csv'),('Sobreposição elegível','Sobreposicao corpus nacional.csv')]:import_csv(matrix,name,OUT/'matriz'/file)
    if MANIFEST:
        source_prov=defaultdict(list)
        for p in prov:source_prov[p['fonte']].append(p)
        source_coverage=[]
        for source,pp in sorted(source_prov.items()):
            gids={p['obra_id'] for p in pp};states=Counter(nr[g]['decisao'] for g in gids)
            source_coverage.append({'fonte':source,'registros':len(pp),'componentes_incluindo_provisorios':len(gids),
                'incluidas':states['incluída'],'elegiveis_identidade_pendente':states['elegível com identidade pendente'],'pendentes':states['pendente'],
                'componentes_provisorios':sum(g.startswith('CAPES-PROVISORIO-') for g in gids),'limite':'Registros e componentes não são obras únicas; fontes se sobrepõem; não completude.'})
        save_csv(OUT/'matriz/Cobertura operacional integrada.csv',source_coverage)
        import_csv(matrix,'Cobertura integrada',OUT/'matriz/Cobertura operacional integrada.csv')
        for name,file in [('CAPES por registro','Cobertura CAPES por registro.csv'),('CAPES por estrato','Matriz de cobertura CAPES.csv'),
                          ('Níveis de sobreposição','Niveis de sobreposicao CAPES OpenAlex.csv'),('OA CAPES elegíveis','OpenAlex CAPES por periodo e tipo.csv')]:
            shutil.copy2(M4/file,OUT/'matriz'/file);import_csv(matrix,name,M4/file)
    notes=matrix.create_sheet('Leia-me',0)
    for row in [['Matriz de cobertura e sobreposição','Estado / unidade'],['Marco 1','Medição observada nos 1.317 controles; categorias em revisão fora do denominador verificável. Preservada historicamente.'],['Marco 2','Histórico anterior à integração; não confundir com os indicadores incrementais.'],['Corpus nacional',f'Sobreposição entre fontes nas {N} inclusões operacionais; não estima completude nacional.'],['Interpretação',WARN]]:line(notes,row)
    if MANIFEST:
        line(notes,['CAPES — coleta 16/11','675 registros = 664 confirmados com snapshot + 3 revisões + 7 não recuperados + 1 temporal não verificável; 664/671 verificáveis.'])
        line(notes,['Unidades distintas','647 IDs coincidentes; 665 vínculos; 509 obras elegíveis no novo lote; 571 na união das rodadas. Não são medidas de completude.'])
    notes.column_dimensions['A'].width=30;notes.column_dimensions['B'].width=110
    for row in notes:
        for c in row:c.alignment=Alignment(wrap_text=True,vertical='top')
        notes.row_dimensions[row[0].row].height=44
    matrix.save(OUT/'Matriz de cobertura e sobreposicao.xlsx')
    shutil.copy2(M4/'Sintese das seis subquestoes.md',OUT/'Sintese das seis subquestoes.md')
    # Corrigir somente caminhos de links ao transportar a síntese; o texto científico é preservado.
    text=(OUT/'Sintese das seis subquestoes.md').read_text(encoding='utf8')
    import re
    def adjust(m):
        target=m.group(1)
        if MANIFEST:
            from urllib.parse import unquote,quote
            import os
            return ']('+quote(os.path.relpath((M4/unquote(target)).resolve(),OUT).replace('\\','/'),safe='/')+')'
        return ']('+('../../analises/marco3/'+target[len('../marco3/'):] if target.startswith('../marco3/') else '../../analises/marco4/'+target)+')'
    (OUT/'Sintese das seis subquestoes.md').write_text(re.sub(r'\]\(([^)]+)\)',adjust,text),encoding='utf8')
    basefiles={p for folder in {M2,M3,M4} for p in folder.iterdir() if p.is_file() and p.suffix in ('.csv','.json','.md')}
    if MANIFEST:
        basefiles.update(p for p in (M2.parent/'conciliacao').iterdir() if p.is_file() and p.suffix in ('.csv','.json','.md'))
        basefiles.update([ROOT/'dados/CAPES-concatenado.ris',ROOT/RUN['protocolo_adendo'],ROOT/'Vaneria.txt',ROOT/'dados/analises/marco3/Materiais locais.csv'])
    with zipfile.ZipFile(OUT/'Base tecnica PIBID.zip','w',zipfile.ZIP_DEFLATED,compresslevel=4) as z:
        base_note=('# Base técnica separada\n\nDados e decisões preservados dos marcos 2–4, com proveniência, evidências e pendências. '+WARN+f'\n\nFrações observadas: {GN}/{N} (2,52%), publicação 2007–08/11/2026; {GC}/{NC} (1,94%), publicação 2020–08/11/2026, sempre dentro do corpus nacional operacional. Participação total não estimável. Contexto e afiliação são dimensões distintas.\n\nEstado dos indicadores: '+str((M4/'Estado dos indicadores.csv').relative_to(ROOT))+'. Este ZIP contém a base técnica; o pacote completo de reconstrução é entregue separadamente.\n')
        if MANIFEST:base_note+='\nVersão corrente dos corpora: '+str(M2.relative_to(ROOT))+'. A pasta conciliacao preserva a fase anterior. CAPES: 647 IDs coincidentes; 665 vínculos bibliográficos; 509 obras elegíveis no novo lote e 571 na união de rodadas; 675 ocorrências inventariadas, dez provisórias sem inclusão automática. Não é completude do Portal.\n'
        z.writestr('LEIA-ME BASE TECNICA.md',base_note.encode('utf8'))
        for p in sorted(basefiles):z.write(p,str(p.relative_to(ROOT)))
        z.write(ROOT/'dados/analises/triagem_criterio_defesa_20261115.xlsx','dados/analises/triagem_criterio_defesa_20261115.xlsx')
    print(json.dumps({'obras_uniao':len(union),'graficos':len(manifest),'planilha':str(BOOK.relative_to(ROOT))},ensure_ascii=False))


def verify():
    f=load_workbook(BOOK,data_only=False);v=load_workbook(BOOK,data_only=True)
    N,G,U,GN,GC,NC=delivery_counts()
    checks=[]
    def check(name,condition,detail):
        checks.append({'verificacao':name,'resultado':'OK' if condition else 'FALHOU','evidencia':detail})
        assert condition,(name,detail)
    check('Obras únicas e pertinência aos corpora',f['Obras únicas'].max_row-1==U and len({r[0] for r in f['Obras únicas'].iter_rows(min_row=2,values_only=True)})==U,f'{N} + {G} − {N+G-U} = {U}; uma linha por obra na união observada')
    check('Fórmulas recalculadas no Excel',all(r[3]=='OK' for r in v['Conferências'].iter_rows(min_row=2,values_only=True)),'11 conferências de totais e denominadores calculadas e armazenadas')
    check('Frações observadas',abs(v['Leia-me']['D5'].value-GN/N)<1e-12 and abs(v['Leia-me']['D6'].value-GC/NC)<1e-12,f'{GN}/{N} e {GC}/{NC}, com recortes explícitos; participação total não estimável')
    check('Eixos preservados',v['Eixos'].max_row-1==291 and sum(v['Indicadores eixos'].cell(i,j).value for i in range(2,5) for j in range(2,5))==291,'97 obras; três eixos; estados sem inferência de ausência')
    check('Totais gráficos e séries',sum(v['Anos'].cell(i,2).value for i in range(2,22))==N-2 and v['Anos']['B22'].value==2 and sum(v['Anos'].cell(i,j).value for i in range(15,22) for j in (3,4))==G,f'{N-2} anos nacionais unívocos + 2 divergentes; Goiás 93 publicações + 4 defesas')
    check('Tipos e gráficos',sum(v['Tipos'].cell(i,3).value for i in range(2,15))==N and sum(v['Tipos'].cell(i,3).value for i in range(15,20))==G,'Categorias documentais reconciliam ao corpus')
    check('Gráficos nativos editáveis',sum(len(s._charts) for s in f)==6 and all(len(s._charts)==1 for s in f if s.title.startswith('G')),'Seis objetos de gráfico ligados às células, sem substituição por imagens')
    for filename in [BOOK,OUT/'Matriz de cobertura e sobreposicao.xlsx']:
        with zipfile.ZipFile(filename) as z:
            check('Integridade '+filename.name,z.testzip() is None,'ZIP/XML íntegros')
            if filename==BOOK:
                chartfiles=[n for n in z.namelist() if n.startswith('xl/charts/chart') and n.endswith('.xml')]
                check('Referências dos gráficos',len(chartfiles)==6 and all(b'<c:f>' in z.read(n) or b'<f>' in z.read(n) for n in chartfiles),'Todas as séries possuem referências a células; editabilidade estrutural verificada')
        book=load_workbook(filename,data_only=False)
        tables=[t for s in book for t in s.tables.values()]
        check('Tabelas e filtros '+filename.name,len(tables)>0 and len({t.name for t in tables})==len(tables) and all(t.autoFilter is not None for t in tables),'Nomes únicos, tabelas estruturadas e filtros mantidos pelo Excel')
        errors=[]
        for s in book:
            for row in s:
                for c in row:
                    if c.data_type=='e':errors.append((s.title,c.coordinate,c.value))
        check('Sem erros Excel '+filename.name,not errors,str(errors))
    check('Pré-visualizações de todos os gráficos',all((OUT/'previews'/f'G{i}.png').is_file() for i in range(1,7)),'Seis exportações nativas pelo Excel; conferência visual registrada separadamente')
    sources=read(OUT/'matriz/Combinacoes fontes corpus nacional.csv')
    check('Combinações disjuntas de fontes',sum(int(r['obras']) for r in sources)==N,'Combinações exclusivas somam N; interseções par a par não são aditivas')
    if MANIFEST:
        check('CAPES no resumo editável',all(v['Leia-me'].cell(row,2).value==expected for row,expected in [(18,675),(19,665),(20,647),(21,664),(22,571),(23,509)]) and v['Leia-me']['C21'].value==671,'Unidades e denominadores separados: registros, vínculos, coincidência nominal e obras elegíveis')
        check('CAPES nas matrizes',{'CAPES por registro','CAPES por estrato','Níveis de sobreposição','OA CAPES elegíveis'}<=set(load_workbook(OUT/'Matriz de cobertura e sobreposicao.xlsx',read_only=True).sheetnames),'Matriz histórica e medição incremental em abas distintas')
        raw_coverage=read(OUT/'matriz/Cobertura operacional integrada.csv')
        check('Proveniência integrada por fonte',sum(int(r['registros']) for r in raw_coverage)==14423 and next(int(r['registros']) for r in raw_coverage if r['fonte']=='Portal CAPES')==778,'14423 registros; Portal CAPES 103 históricos + 675 novos; não somar componentes de fontes sobrepostas')
    save_csv(OUT/'Conferencias da entrega.csv',checks)
    chartlog=json.loads((OUT/'Conferencia Excel.json').read_text(encoding='utf-8-sig'))
    charts={r['aba']:r for r in chartlog if 'aba' in r}
    graphrows=read(OUT/'Graficos.csv')
    for r in graphrows:
        r['titulo_e_nota']=charts[r['aba']]['titulo_e_nota']
        r['estado']='Nativo/editável, recalculado e exportado no Excel; ver Conferencia visual.csv'
    save_csv(OUT/'Graficos.csv',graphrows)
    print(json.dumps({'verificacoes_marco5':len(checks),'resultado':'OK'},ensure_ascii=False))


def package():
    # Os diretórios normalizados/staging completos não participam da reconstrução
    # a partir dos corpora congelados; a geração normalizada vigente é incluída.
    paths=set()
    for folder in ('scripts','tests','dados/analises','dados/brutos','dados/logs','dados/triagem'):
        paths.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    paths.update(ROOT.glob('*.md'));paths.add(ROOT/'Vaneria.txt')
    from scripts.construir_corpus_marco2 import NORMAL
    paths.add(NORMAL)
    for pattern in ('*.ris','*.csv','*.zip'):paths.update(ROOT.glob(pattern))
    paths.update(p for p in OUT.rglob('*') if p.is_file() and p.name not in ('Pacote reproduzivel PIBID.zip','Inventario.csv','Verificacao do pacote.json'))
    paths.add(ROOT/'requirements-marco5.txt');paths.add(ROOT/'REPRODUZIR_MARCO5.md')
    if MANIFEST:
        paths.add(ROOT/'dados/CAPES-concatenado.ris')
        paths.add(ROOT/'REPRODUZIR_INTEGRACAO_CAPES.md')
    manifest=[{'caminho':str(p.relative_to(ROOT)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(paths)]
    save_csv(OUT/'Inventario.csv',manifest)
    target=OUT/'Pacote reproduzivel PIBID.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=4) as z:
        for p in sorted(paths):z.write(p,str(p.relative_to(ROOT)))
        z.write(OUT/'Inventario.csv',str((OUT/'Inventario.csv').relative_to(ROOT)))
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for r in manifest:
            h=hashlib.sha256()
            with z.open(r['caminho']) as stream:
                for block in iter(lambda:stream.read(2**20),b''):h.update(block)
            assert h.hexdigest()==r['sha256'],r['caminho']
    result={'arquivos_manifesto':len(manifest),'bytes_zip':target.stat().st_size,'sha256_zip':digest(target),'integridade':'OK; cada membro do manifesto reconferido por SHA-256'}
    (OUT/'Verificacao do pacote.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('acao',choices=['preparar','verificar','empacotar']);parser.add_argument('--manifesto');args=parser.parse_args()
    {'preparar':prepare,'verificar':verify,'empacotar':package}[args.acao]()
