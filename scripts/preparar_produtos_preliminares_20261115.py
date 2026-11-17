"""Gera apresentação de resultados parciais a partir da base técnica preservada."""

import csv
from collections import Counter
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.label import DataLabel, DataLabelList
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

from scripts.extrair_eixos_incluidos_20261115 import EIXOS_CODIGO
from scripts.preanalise_e_validacao_20261115 import cabecalhos

RAIZ = Path(__file__).resolve().parents[1]
BASE = RAIZ / "dados" / "analises" / "triagem_criterio_defesa_20261115.xlsx"
BDTD_NACIONAL = (RAIZ / "dados" / "brutos" / "bdtd"
                 / "bdtd__busca-nacional__20261108T113708926870-0300__CSV.csv")
SAIDA = RAIZ / "dados" / "entregas" / "Resultados preliminares Brasil e Goiás 20261115.xlsx"
ESTADOS = ("Presente", "Não informado", "Não verificável")
EIXOS_CURTOS = {
    EIXOS_CODIGO["A"]: "Aprendizagem e identidade",
    EIXOS_CODIGO["T"]: "Trajetórias profissionais",
    EIXOS_CODIGO["R"]: "Relações IES, escolas e comunidades",
}
AZUL = "17365D"


def tabela(planilha, nome):
    ultima = get_column_letter(planilha.max_column)
    tab = Table(displayName=nome, ref=f"A1:{ultima}{planilha.max_row}")
    tab.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showFirstColumn=False,
                                       showLastColumn=False, showRowStripes=True,
                                       showColumnStripes=False)
    planilha.add_table(tab)


def linha_segura(planilha, valores):
    planilha.append(valores)
    for celula in planilha[planilha.max_row]:
        if isinstance(celula.value, str):
            celula.data_type = "s"


def anos_defesa_bdtd(caminho):
    with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if not leitor.fieldnames or "Ano de defesa" not in leitor.fieldnames:
            raise ValueError("Campo de ano de defesa ausente na exportação BDTD.")
        anos = []
        for linha in leitor:
            ano = linha["Ano de defesa"]
            if None in linha or not ano or not ano.isdigit() or not 2007 <= int(ano) <= 2026:
                raise ValueError("Ano de defesa inválido ou linha BDTD malformada.")
            anos.append(int(ano))
    if len(anos) != 1018:
        raise ValueError("Quantidade de linhas da busca nacional BDTD divergente.")
    return Counter(anos)


def rotulos_valores():
    return DataLabelList(showVal=True, showCatName=False, showSerName=False,
                         showLegendKey=False, showPercent=False, showBubbleSize=False)


def configurar_eixos(grafico, barras_horizontais=False):
    grafico.x_axis.axPos = "l" if barras_horizontais else "b"
    grafico.y_axis.axPos = "b" if barras_horizontais else "l"
    for eixo in (grafico.x_axis, grafico.y_axis):
        eixo.delete = False
        eixo.tickLblPos = "nextTo"
    grafico.y_axis.majorGridlines = None


def gerar(base, saida, bdtd_nacional=BDTD_NACIONAL):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    anos_nacionais = anos_defesa_bdtd(bdtd_nacional)
    origem = load_workbook(base, read_only=True, data_only=False)
    try:
        triagem = origem["Triagem"]
        ct = cabecalhos(triagem)
        registros = [{campo: linha[coluna - 1] for campo, coluna in ct.items()}
                     for linha in list(triagem.values)[1:]]
        if len(registros) != 1317 or len({r["Código"] for r in registros}) != 1317:
            raise ValueError("Quantidade ou códigos da base divergentes.")
        selecionados = [r for r in registros if r["Decisão de elegibilidade"] == "Incluir"]
        if len(selecionados) != 19:
            raise ValueError("Esta apresentação espera 19 registros incluídos.")
        codigos = {r["Código"] for r in selecionados}
        eixos = origem["Eixos de análise"]
        ce = cabecalhos(eixos)
        achados = [{campo: linha[coluna - 1] for campo, coluna in ce.items()}
                   for linha in list(eixos.values)[1:] if linha[ce["Código"] - 1] in codigos]
        chaves = [(r["Código"], r["Eixo"]) for r in achados]
        if (len(achados) != 57 or set(chaves) != {(c, e) for c in codigos for e in EIXOS_CURTOS}
                or any(r["Estado"] not in ESTADOS or not r["Achado ou observação"]
                       or not r["Limites da evidência"] for r in achados)):
            raise ValueError("Eixos incompletos, duplicados ou sem limites.")
        for r in selecionados:
            if (not all(r[c] for c in ("Código", "Fonte", "Tipo de produção", "Título", "Autoria",
                                       "Ano de publicação", "DOI", "Contexto de Goiás",
                                       "Afiliações de autoria", "Qualidade documental do resumo"))
                    or not str(r["Ano de publicação"]).isdigit()
                    or not 2020 <= int(r["Ano de publicação"]) <= 2026):
                raise ValueError(f"Referência incluída incompleta: {r['Código']}")
        contexto = Counter(r["Decisão de elegibilidade"] for r in registros)
        if contexto != {"Incluir": 19, "Excluir": 199, "Pendente": 247, "Não iniciada": 852}:
            raise ValueError("Situação da base divergente do retrato documentado.")

        livro = Workbook()
        leitura = livro.active
        leitura.title = "Leia primeiro"
        linhas = [
            ("RESULTADOS PRELIMINARES — BRASIL E GOIÁS", ""),
            ("Situação", "Retrato de 15/11/2026; seleção e deduplicação incompletas. Não é a revisão final."),
            ("Recorte", "Goiás: publicação ou ano de defesa de 2020–2026; 2026 é parcial até 08/11. Datas de defesa e publicação são distintas."),
            ("Unidade", "19 linhas incluídas; 1.099 das 1.317 linhas da base permanecem sem decisão. Linhas não são necessariamente obras únicas."),
            ("Cobertura", "18 linhas do Portal CAPES e 1 da SciELO. Não se pode generalizar esse conjunto nem calcular a participação de Goiás na produção nacional."),
            ("Panorama nacional", "A aba Panorama nacional apresenta 1.018 linhas recuperadas na busca nacional da BDTD, por ano de defesa. São candidatos, não publicações confirmadas nem estudos únicos."),
            ("Comparação", "Ainda não há denominador nacional comparável ao recorte goiano. As fontes, a seleção e os critérios temporais diferem; não calcular participação de Goiás."),
            ("Eixos", "Presente indica conteúdo no material consultado, não efeito comprovado. Não informado não demonstra ausência no texto integral. Não verificável indica evidência insuficiente."),
            ("Qualidade", "18 campos de resumo têm qualidade documental reduzida e um não foi avaliado nessa dimensão. Fontes complementares não comprovam necessariamente o conteúdo exibido no corte."),
            ("Confiança", "Análise não independente, sem taxa de acerto ou faixas percentuais calibradas."),
            ("Uso dos gráficos", "Gráficos nativos editáveis: copie também a nota correspondente ao gráfico. As tabelas são retratos estáticos; após alterações, atualize os dados dos gráficos ou gere nova versão."),
            ("Rastreabilidade", "Código vincula referências e achados à base técnica. Contexto e afiliação são distintos; a coluna de afiliações pode ser incompleta."),
            ("Documentos", "Base técnica: dados/analises/triagem_criterio_defesa_20261115.xlsx. Relatório: dados/entregas/Relatório metodológico preliminar 20261115.md."),
        ]
        for linha in linhas:
            linha_segura(leitura, linha)
        leitura.column_dimensions["A"].width = 23
        leitura.column_dimensions["B"].width = 105
        for linha in leitura:
            for celula in linha:
                celula.alignment = Alignment(vertical="top", wrap_text=True)
            leitura.row_dimensions[linha[0].row].height = 42 if linha[0].row != 1 else 28
            linha[0].font = Font(bold=True, color=AZUL)
        leitura["A1"].font = Font(bold=True, color="FFFFFF", size=14)
        leitura["A1"].fill = PatternFill("solid", fgColor=AZUL)
        leitura.freeze_panes = "B2"

        refs = livro.create_sheet("Referências")
        linha_segura(refs, ["Código", "Título", "Autoria", "Tipo", "Ano de publicação", "Fonte",
                           "DOI", "Link da fonte", "Link complementar", "Contexto de Goiás",
                           "Afiliações informadas", "Qualidade documental do resumo"])
        for r in sorted(selecionados, key=lambda x: (int(x["Ano de publicação"]), x["Título"])):
            linha_segura(refs, [r["Código"], r["Título"], r["Autoria"], r["Tipo de produção"],
                                int(r["Ano de publicação"]), r["Fonte"], r["DOI"], r["Link da fonte"],
                                r["Link OpenAlex"], r["Contexto de Goiás"], r["Afiliações de autoria"],
                                r["Qualidade documental do resumo"]])
        tabela(refs, "ReferenciasPreliminares")
        refs.freeze_panes = "B2"
        for indice, largura in enumerate((16, 55, 42, 16, 17, 18, 30, 48, 36, 27, 60, 33), 1):
            refs.column_dimensions[get_column_letter(indice)].width = largura
        for linha in refs.iter_rows(min_row=2):
            refs.row_dimensions[linha[0].row].height = 62
            for celula in linha:
                celula.alignment = Alignment(vertical="top", wrap_text=True)

        resultados = livro.create_sheet("Achados")
        linha_segura(resultados, ["Código", "Eixo", "Estado", "Síntese", "Limites da evidência",
                                 "Material consultado", "Referência consultada"])
        ordem = {eixo: n for n, eixo in enumerate(EIXOS_CURTOS)}
        for r in sorted(achados, key=lambda x: (x["Código"], ordem[x["Eixo"]])):
            linha_segura(resultados, [r["Código"], r["Eixo"], r["Estado"], r["Achado ou observação"],
                                      r["Limites da evidência"], r["Tipo de fonte"],
                                      r["Link ou referência consultada"]])
        tabela(resultados, "AchadosPreliminares")
        resultados.freeze_panes = "B2"
        for indice, largura in enumerate((16, 42, 20, 66, 75, 35, 44), 1):
            resultados.column_dimensions[get_column_letter(indice)].width = largura
        for linha in resultados.iter_rows(min_row=2):
            resultados.row_dimensions[linha[0].row].height = 70
            for celula in linha:
                celula.alignment = Alignment(vertical="top", wrap_text=True)

        graficos = livro.create_sheet("Gráficos")
        graficos.sheet_view.showGridLines = False
        for col, largura in {"A": 37, "B": 19, "C": 20, "D": 20, "F": 18}.items():
            graficos.column_dimensions[col].width = largura
        graficos["A1"] = "DADOS E GRÁFICOS PRELIMINARES"
        graficos["A1"].font = Font(bold=True, size=15, color=AZUL)
        graficos["A2"] = "Unidade: linhas incluídas; seleção e deduplicação incompletas."
        graficos["A3"] = "Valores estáticos: edite as tabelas para atualizar os gráficos."
        graficos["A5"] = "Eixo"
        for coluna, estado in enumerate(ESTADOS, 2):
            graficos.cell(5, coluna, estado)
        for numero, (eixo, curto) in enumerate(EIXOS_CURTOS.items(), 6):
            graficos.cell(numero, 1, curto)
            contagens = Counter(r["Estado"] for r in achados if r["Eixo"] == eixo)
            for coluna, estado in enumerate(ESTADOS, 2):
                graficos.cell(numero, coluna, contagens[estado])
            if sum(contagens.values()) != 19:
                raise ValueError(f"Denominador divergente: {eixo}")
        graficos["A12"] = "Ano de publicação"
        graficos["B12"] = "Registros"
        anos = Counter(int(r["Ano de publicação"]) for r in selecionados)
        for numero, ano in enumerate(range(2020, 2027), 13):
            graficos.cell(numero, 1, str(ano))
            graficos.cell(numero, 2, anos[ano])
        for linha in (5, 12):
            for celula in graficos[linha][:4 if linha == 5 else 2]:
                celula.font = Font(bold=True, color="FFFFFF")
                celula.fill = PatternFill("solid", fgColor=AZUL)
                celula.alignment = Alignment(wrap_text=True)
        graficos.row_dimensions[5].height = 30

        chart = BarChart()
        chart.type = "bar"
        chart.grouping = "stacked"
        chart.overlap = 100
        configurar_eixos(chart, barras_horizontais=True)
        chart.title = "Eixos — Goiás 2020–2026, 19 linhas (parcial)"
        chart.y_axis.scaling.min = 0
        chart.y_axis.scaling.max = 19
        chart.add_data(Reference(graficos, min_col=2, max_col=4, min_row=5, max_row=8),
                       titles_from_data=True)
        chart.set_categories(Reference(graficos, min_col=1, min_row=6, max_row=8))
        chart.legend.position = "b"
        chart.legend.overlay = False
        chart.width, chart.height = 25, 10
        for coluna, (serie, cor) in enumerate(zip(chart.series, ("356A95", "A8B9C9", "E2B55D")), 2):
            serie.graphicalProperties.solidFill = cor
            serie.graphicalProperties.line.solidFill = cor
            serie.dLbls = rotulos_valores()
            serie.dLbls.dLbl = [
                DataLabel(idx=linha - 6, showVal=False, showCatName=False, showSerName=False,
                          showLegendKey=False, showPercent=False, showBubbleSize=False)
                for linha in range(6, 9) if graficos.cell(linha, coluna).value == 0
            ]
        graficos.add_chart(chart, "F5")
        graficos.merge_cells("F27:U29")
        graficos["F27"] = ("Fonte: base técnica, 15/11/2026. Recorte 2020–2026, com 2026 até 08/11. "
                            "Linhas, não obras únicas; seleção e deduplicação incompletas. Análise não "
                            "independente; 18 campos de resumo têm qualidade reduzida e um não foi "
                            "avaliado. Os eixos podem se sobrepor.")
        graficos["F27"].alignment = Alignment(wrap_text=True, vertical="top")

        chart_ano = BarChart()
        chart_ano.type = "col"
        configurar_eixos(chart_ano)
        chart_ano.title = "Publicação por ano — Goiás, 19 linhas (parcial)"
        chart_ano.y_axis.scaling.min = 0
        chart_ano.y_axis.majorUnit = 1
        chart_ano.add_data(Reference(graficos, min_col=2, min_row=12, max_row=19),
                           titles_from_data=True)
        chart_ano.set_categories(Reference(graficos, min_col=1, min_row=13, max_row=19))
        chart_ano.legend = None
        chart_ano.dLbls = rotulos_valores()
        chart_ano.series[0].graphicalProperties.solidFill = "356A95"
        chart_ano.series[0].graphicalProperties.line.solidFill = "356A95"
        chart_ano.width, chart_ano.height = 25, 10
        graficos.add_chart(chart_ano, "F32")
        graficos.merge_cells("F54:U56")
        graficos["F54"] = ("Fonte: base técnica, 15/11/2026. Linhas incluídas, sem deduplicação "
                            "integral; 2026 é parcial até 08/11. Análise não independente; "
                            "18 campos de resumo têm qualidade reduzida e um não foi avaliado.")
        graficos["F54"].alignment = Alignment(wrap_text=True, vertical="top")

        nacional = livro.create_sheet("Panorama nacional", 1)
        nacional.sheet_view.showGridLines = False
        nacional.column_dimensions["A"].width = 20
        nacional.column_dimensions["B"].width = 24
        nacional.column_dimensions["D"].width = 18
        nacional["A1"] = "BUSCA NACIONAL BDTD — RETRATO PARCIAL"
        nacional["A1"].font = Font(bold=True, size=14, color=AZUL)
        nacional["A3"] = "Ano de defesa"
        nacional["B3"] = "Linhas recuperadas"
        for celula in nacional[3][:2]:
            celula.font = Font(bold=True, color="FFFFFF")
            celula.fill = PatternFill("solid", fgColor=AZUL)
        for numero, ano in enumerate(range(2007, 2027), 4):
            nacional.cell(numero, 1, str(ano))
            nacional.cell(numero, 2, anos_nacionais[ano])
        nacional["A25"] = "Total"
        nacional["B25"] = sum(anos_nacionais.values())
        nacional["A25"].font = nacional["B25"].font = Font(bold=True)
        grafico_nacional = BarChart()
        grafico_nacional.type = "col"
        configurar_eixos(grafico_nacional)
        grafico_nacional.title = "BDTD: registros por ano de defesa (2007–2026)"
        grafico_nacional.y_axis.scaling.min = 0
        grafico_nacional.add_data(Reference(nacional, min_col=2, min_row=3, max_row=23),
                                  titles_from_data=True)
        grafico_nacional.set_categories(Reference(nacional, min_col=1, min_row=4, max_row=23))
        grafico_nacional.legend = None
        grafico_nacional.series[0].graphicalProperties.solidFill = "356A95"
        grafico_nacional.series[0].graphicalProperties.line.solidFill = "356A95"
        grafico_nacional.width, grafico_nacional.height = 26, 11
        nacional.add_chart(grafico_nacional, "D4")
        nacional.merge_cells("D28:S31")
        nacional["D28"] = ("Fonte: busca nacional BDTD de 08/11/2026; filtro informado 2007–2026. "
                           "1.018 linhas recuperadas, sem seleção e deduplicação nacionais completas; "
                           "não representam toda a produção brasileira. Ano de defesa não equivale "
                           "a ano de publicação. Ano de 2026 parcial; a análise não teve validação independente.")
        nacional["D28"].alignment = Alignment(wrap_text=True, vertical="top")
        nacional.merge_cells("D34:S36")
        nacional["D34"] = ("Comparação com Goiás não calculada: fontes, seleção e critérios temporais "
                           "não formam ainda um conjunto comparável. Copie a nota junto com o gráfico.")
        nacional["D34"].alignment = Alignment(wrap_text=True, vertical="top")
        livro.calculation.fullCalcOnLoad = True
        livro.save(saida)
        livro.close()
    finally:
        origem.close()


if __name__ == "__main__":
    gerar(BASE, SAIDA)
    print(f"Apresentação criada: {SAIDA}")
