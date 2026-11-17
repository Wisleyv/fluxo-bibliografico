"""Integra um lote de leituras bilíngues CAPES à base técnica."""

import csv
from copy import copy
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

from scripts.conferir_catalogo_resumos_20261115 import identificador, ler_originais
from scripts.conferir_termos_e_resumos_20261115 import tem_termo
from scripts.integrar_autoavaliacao_20261115 import EIXOS, anexar_tabela, indice_unico
from scripts.integrar_teses_e_datas_uel_20261115 import acrescentar
from scripts.preanalise_e_validacao_20261115 import cabecalhos
from scripts.preencher_autoavaliacao_20261115 import OPCOES


RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_revisao_bilingue_catalogo_20261115.xlsx"
DECISOES = ANALISES / "avaliacao_catalogo_lote2_20261115.csv"
BRUTO = RAIZ / "dados" / "brutos" / "catalogo-capes" / "catalogo-capes__catalogo-2024__20261108T150417015445-0300__CSV.csv"
SAIDA = ANALISES / "triagem_catalogo_lote2_20261115.xlsx"
DATA = datetime(2026, 11, 15)
REVISOR = "Análise computacional e documental preliminar não independente"


def ler_decisoes(caminho):
    campos = ["codigo", "id", "pibid", "contexto", "eixos", "triagem", "evidencia", "limites"]
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames != campos:
            raise ValueError("Colunas das decisões inesperadas.")
        linhas = list(leitor)
    if len(linhas) != 10 or len({x["codigo"] for x in linhas}) != 10 or len({x["id"] for x in linhas}) != 10:
        raise ValueError("Esperadas dez avaliações distintas.")
    for item in linhas:
        if None in item or any(x is None for x in item.values()):
            raise ValueError("Linha malformada.")
        if not all(item[x] for x in ("codigo", "id", "pibid", "contexto", "triagem", "evidencia", "limites")):
            raise ValueError("Avaliação incompleta.")
        if item["pibid"] not in OPCOES["pibid"] or item["contexto"] != "N":
            raise ValueError(f"Classificação inválida: {item['codigo']}")
        if item["triagem"] == "E":
            if item["pibid"] != "M" or item["eixos"]:
                raise ValueError(f"Exclusão incompatível: {item['codigo']}")
        elif item["triagem"] != "P" or len(item["eixos"]) != 3 or any(
            estado not in OPCOES["eixo"] for estado in item["eixos"]
        ):
            raise ValueError(f"Triagem ou eixos inválidos: {item['codigo']}")
        if item["pibid"] == "I" and item["eixos"] != "VVV":
            raise ValueError(f"Relação incerta requer ressalvas nos eixos: {item['codigo']}")
    return linhas


def integrar(base, decisoes, bruto, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    leituras = ler_decisoes(decisoes)
    originais = ler_originais(bruto, {x["id"] for x in leituras})
    livro = load_workbook(base)
    triagem, eixos = livro["Triagem"], livro["Eixos de análise"]
    ct, ce = cabecalhos(triagem), cabecalhos(eixos)
    indices = indice_unico(triagem, ct["Código"], 1317)
    inventario = {r[0]: r for r in list(livro["Inventário inglês CAPES"].values)[1:]}
    revisados = {r[0] for r in list(livro["Revisão bilíngue CAPES"].values)[1:]}
    existentes = set()
    for row in list(eixos.values)[1:]:
        chave = (row[ce["Código"] - 1], row[ce["Eixo"] - 1])
        if chave in existentes:
            raise ValueError(f"Eixo duplicado: {chave}")
        existentes.add(chave)
    auditoria = livro.create_sheet("CAPES bilíngue lote 2")
    auditoria.append(["Código", "ID CAPES", "Relação PIBID", "Contexto de Goiás",
                      "Triagem preliminar", "Eixos", "Evidência", "Limites", "Data"])
    for item in leituras:
        codigo, fonte_id = item["codigo"], item["id"]
        if codigo not in indices or codigo not in inventario or codigo in revisados:
            raise ValueError(f"Registro ausente ou já revisado: {codigo}")
        inv = inventario[codigo]
        if inv[1] != fonte_id or inv[2] != "Não" or inv[7] != "Não":
            raise ValueError(f"Histórico de leitura inesperado: {codigo}")
        celula = lambda campo: triagem.cell(indices[codigo], ct[campo])
        registro = originais[fonte_id]
        if (celula("Fonte").value != "Catálogo CAPES"
                or identificador(celula("Link da fonte").value) != fonte_id
                or celula("Título").value != registro["NM_PRODUCAO"]
                or celula("Autoria").value != registro["NM_DISCENTE"]
                or celula("Resumo").value != registro["DS_RESUMO"]
                or len(registro["DS_RESUMO"]) < 500 or len(registro["DS_ABSTRACT"]) < 500):
            raise ValueError(f"Identidade ou resumos divergentes ou insuficientes: {codigo}")
        if (celula("Relação com PIBID").value != "Incerto"
                or celula("Contexto de Goiás").value != "Incerto"
                or celula("Triagem de título e resumo").value != "Pendente"
                or celula("Decisão de elegibilidade").value != "Não iniciada"
                or celula("Motivo da exclusão").value is not None
                or celula("Revisor").value is not None):
            raise ValueError(f"Estado anterior requer conciliação: {codigo}")
        if any((codigo, eixo) in existentes for eixo in EIXOS.values()):
            raise ValueError(f"Extração anterior requer conciliação: {codigo}")
        if item["triagem"] == "E" and not any(
            tem_termo(registro[campo]) for campo in ("NM_PRODUCAO", "DS_RESUMO", "DS_ABSTRACT")
        ):
            raise ValueError(f"Menção incidental não encontrada: {codigo}")
        celula("Relação com PIBID").value = OPCOES["pibid"][item["pibid"]]
        celula("Contexto de Goiás").value = OPCOES["contexto"][item["contexto"]]
        celula("Decisão de elegibilidade").value = "Pendente"
        if item["triagem"] == "E":
            celula("Triagem de título e resumo").value = "Excluir"
            celula("Motivo da exclusão").value = "Sem relação substantiva com PIBID"
        evidencia = item["evidencia"] + f" Fonte: arquivo anual CAPES 2024, registro {fonte_id}, título e resumos DS_RESUMO e DS_ABSTRACT."
        limites = (item["limites"] + " Não identificar Goiás no material consultado não prova ausência de contexto ou afiliação; "
                   "ano de defesa não equivale a publicação. Elegibilidade e duplicidade permanecem pendentes; conferência não independente.")
        for campo, valor in {
            "Evidência do contexto": "Sem evidência de contexto goiano no título e nos resumos consultados; não equivale a ausência comprovada.",
            "Fontes das evidências": evidencia,
            "Material consultado": "Título, resumos em português e inglês e palavras-chave do arquivo CAPES original.",
            "Limitações e pendências": limites,
            "Observações": "Leitura bilíngue preliminar de 15/11/2026; " + (
                "exclusão por menção incidental é reversível." if item["triagem"] == "E"
                else "triagem e elegibilidade final permanecem pendentes."
            ),
        }.items():
            acrescentar(celula(campo), valor)
        celula("Revisor").value = REVISOR
        celula("Data da triagem").value = DATA
        for eixo, estado in zip(EIXOS.values(), item["eixos"]):
            numero = eixos.max_row + 1
            for coluna in range(1, eixos.max_column + 1):
                eixos.cell(numero, coluna)._style = copy(eixos.cell(2, coluna)._style)
            valores = {
                "Código": codigo, "Título": celula("Título").value, "Eixo": eixo,
                "Estado": OPCOES["eixo"][estado], "Achado ou observação": evidencia,
                "Trecho ou localização": "Título e campos DS_RESUMO e DS_ABSTRACT do arquivo CAPES.",
                "Tipo de fonte": "Metadados e resumos do Catálogo CAPES",
                "Link ou referência consultada": celula("Link da fonte").value,
                "Limites da evidência": limites, "Revisor": REVISOR, "Data": DATA,
            }
            for campo, valor in valores.items():
                eixos.cell(numero, ce[campo]).value = valor
        auditoria.append([codigo, fonte_id, celula("Relação com PIBID").value,
                          celula("Contexto de Goiás").value, celula("Triagem de título e resumo").value,
                          " | ".join(OPCOES["eixo"][estado] for estado in item["eixos"]) or "Não extraídos",
                          evidencia, limites, DATA])
    tabela = eixos.tables["Eixos"]
    tabela.ref = f"A1:K{eixos.max_row}"
    if tabela.autoFilter is not None:
        tabela.autoFilter.ref = tabela.ref
    if len(eixos.data_validations.dataValidation) != 1:
        raise ValueError("Validação de eixos inesperada.")
    eixos.data_validations.dataValidation[0].sqref = f"D2:D{eixos.max_row}"
    anexar_tabela(auditoria, "CAPESBilingueLote2")
    livro["Limites da integração"].append([
        "Dez registros CAPES adicionais lidos em português e inglês; ver aba CAPES bilíngue lote 2. "
        "Uma exclusão preliminar reversível; sem validação independente nem decisão final."
    ])
    livro.save(saida)


if __name__ == "__main__":
    integrar(BASE, DECISOES, BRUTO, SAIDA)
    print(f"Base criada: {SAIDA}")
