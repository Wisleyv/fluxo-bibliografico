"""Reavalia registros CAPES considerando os dois resumos e o projeto associado."""

import csv
from collections import Counter
from copy import copy
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from openpyxl import load_workbook

from scripts.conferir_termos_e_resumos_20261115 import tem_termo
from scripts.integrar_autoavaliacao_20261115 import EIXOS, anexar_tabela, indice_unico
from scripts.integrar_teses_e_datas_uel_20261115 import acrescentar
from scripts.preanalise_e_validacao_20261115 import cabecalhos


RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_conferencia_termos_20261115.xlsx"
DECISOES = ANALISES / "avaliacao_catalogo_resumos_20261115.csv"
BRUTO = RAIZ / "dados" / "brutos" / "catalogo-capes" / "catalogo-capes__catalogo-2024__20261108T150417015445-0300__CSV.csv"
SAIDA = ANALISES / "triagem_catalogo_resumos_20261115.xlsx"
DATA = datetime(2026, 11, 15)
REVISOR = "Conferência computacional e documental não independente"


def identificador(link):
    valores = parse_qs(urlparse(link or "").query).get("id_trabalho", [])
    if len(valores) != 1 or not valores[0].isdigit():
        raise ValueError(f"Identificador CAPES inválido: {link}")
    return valores[0]


def ler_decisoes(caminho):
    campos = ["codigo", "id", "tratamento", "evidencia", "limites"]
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames != campos:
            raise ValueError("Colunas das decisões inesperadas.")
        linhas = list(leitor)
    if len(linhas) != 11 or len({x["codigo"] for x in linhas}) != 11 or len({x["id"] for x in linhas}) != 11:
        raise ValueError("Esperadas 11 avaliações únicas.")
    for item in linhas:
        if None in item or any(not v for v in item.values()) or item["tratamento"] not in {"E", "P"}:
            raise ValueError("Decisão incompleta ou inválida.")
    if Counter(x["tratamento"] for x in linhas) != {"E": 9, "P": 2}:
        raise ValueError("Distribuição de decisões inesperada.")
    return linhas


def ler_originais(caminho, ids):
    csv.field_size_limit(10_000_000)
    encontrados = {}
    with caminho.open(encoding="cp1252", errors="replace", newline="") as arquivo:
        for linha in csv.DictReader(arquivo, delimiter=";"):
            codigo = linha["ID_PRODUCAO_INTELECTUAL"]
            if codigo in ids:
                if codigo in encontrados:
                    raise ValueError(f"Identificador CAPES repetido: {codigo}")
                encontrados[codigo] = linha
    if set(encontrados) != ids:
        raise ValueError("Registros CAPES não encontrados no arquivo original.")
    return encontrados


def integrar(base, decisoes, bruto, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    leituras = ler_decisoes(decisoes)
    livro = load_workbook(base)
    triagem, eixos = livro["Triagem"], livro["Eixos de análise"]
    ct, ce = cabecalhos(triagem), cabecalhos(eixos)
    indices = indice_unico(triagem, ct["Código"], 1317)
    catalogo = {}
    for numero in indices.values():
        if triagem.cell(numero, ct["Fonte"]).value == "Catálogo CAPES":
            fonte_id = identificador(triagem.cell(numero, ct["Link da fonte"]).value)
            if fonte_id in catalogo:
                raise ValueError(f"Identificador duplicado na base: {fonte_id}")
            catalogo[fonte_id] = numero
    if len(catalogo) != 78:
        raise ValueError("Esperados 78 registros do Catálogo CAPES.")
    originais = ler_originais(bruto, set(catalogo))
    for fonte_id, numero in catalogo.items():
        registro = originais[fonte_id]
        if (registro["NM_PRODUCAO"] != triagem.cell(numero, ct["Título"]).value
                or registro["NM_DISCENTE"] != triagem.cell(numero, ct["Autoria"]).value):
            raise ValueError(f"Identidade divergente no Catálogo CAPES: {fonte_id}")
    inventario = livro.create_sheet("Inventário inglês CAPES")
    inventario.append(["Código", "ID CAPES", "Revisão anterior", "Termo em campos locais",
                       "Resumo em inglês disponível", "Termo no resumo em inglês",
                       "Caractere de substituição no resumo em inglês", "Leitura nesta etapa"])
    lidos = {item["codigo"] for item in leituras}
    for fonte_id, numero in catalogo.items():
        registro = originais[fonte_id]
        codigo = triagem.cell(numero, ct["Código"]).value
        locais = ("Título", "Resumo", "Palavras-chave")
        inventario.append([
            codigo, fonte_id, "Sim" if triagem.cell(numero, ct["Revisor"]).value else "Não",
            "Sim" if any(tem_termo(triagem.cell(numero, ct[campo]).value) for campo in locais) else "Não",
            "Sim" if registro["DS_ABSTRACT"] else "Não",
            "Sim" if tem_termo(registro["DS_ABSTRACT"]) else "Não",
            "Sim" if "\ufffd" in registro["DS_ABSTRACT"] else "Não",
            "Sim" if codigo in lidos else "Não",
        ])
    existentes = set()
    for numero in range(2, eixos.max_row + 1):
        chave = (eixos.cell(numero, ce["Código"]).value, eixos.cell(numero, ce["Eixo"]).value)
        if chave in existentes:
            raise ValueError(f"Eixo duplicado: {chave}")
        existentes.add(chave)

    auditoria = livro.create_sheet("Resumos Catálogo CAPES")
    auditoria.append(["Código", "ID CAPES", "Projeto no arquivo original", "Termo no resumo inglês",
                      "Decisão preliminar", "Evidência", "Limites"])
    for item in leituras:
        codigo, fonte_id = item["codigo"], item["id"]
        if codigo not in indices or fonte_id not in catalogo or indices[codigo] != catalogo[fonte_id]:
            raise ValueError(f"Identidade divergente: {codigo}/{fonte_id}")
        numero, registro = indices[codigo], originais[fonte_id]
        celula = lambda campo: triagem.cell(numero, ct[campo])
        if (celula("Relação com PIBID").value != "Incerto"
                or celula("Triagem de título e resumo").value != "Pendente"
                or celula("Decisão de elegibilidade").value != "Não iniciada"
                or celula("Revisor").value is not None
                or celula("Motivo da exclusão").value is not None):
            raise ValueError(f"Estado anterior requer conciliação: {codigo}")
        if (registro["DS_RESUMO"] != celula("Resumo").value or len(registro["DS_RESUMO"]) < 500
                or len(registro["DS_ABSTRACT"] or "") < 500):
            raise ValueError(f"Resumo divergente ou insuficiente: {codigo}")
        campos = ("NM_PRODUCAO", "DS_RESUMO", "DS_ABSTRACT", "DS_PALAVRA_CHAVE", "DS_KEYWORD")
        tem_local = any(tem_termo(registro[campo]) for campo in campos)
        if item["tratamento"] == "E":
            if tem_local or not tem_termo(registro["NM_PROJETO"]):
                raise ValueError(f"Evidência temática exige reconciliação: {codigo}")
            celula("Triagem de título e resumo").value = "Excluir"
            celula("Motivo da exclusão").value = "Outro"
            decisao = "Excluir preliminarmente pelo critério de termos; reavaliar se houver evidência complementar."
        elif codigo == "11047151":
            if not tem_termo(registro["DS_ABSTRACT"]):
                raise ValueError(f"Menção no resumo inglês não encontrada: {codigo}")
            decisao = "Pendente: participação no PIBID relatada no resumo inglês; função no estudo incerta."
        elif codigo == "598f4ee2":
            if tem_local or not tem_termo(registro["NM_PROJETO"]):
                raise ValueError(f"Projeto temático não identificado: {codigo}")
            decisao = "Pendente: possível vínculo com projeto PIBID de temática próxima."
        else:
            raise ValueError(f"Pendência não prevista: {codigo}")
        celula("Decisão de elegibilidade").value = "Pendente"
        evidencia = (item["evidencia"] + " Fonte: arquivo anual CAPES 2024, registro "
                     + fonte_id + ", campos DS_RESUMO, DS_ABSTRACT e NM_PROJETO.")
        limites = (item["limites"] + " Exclusão, quando aplicada, é preliminar e reversível; "
                   "não prova ausência no texto integral. Ano de defesa não equivale a publicação. "
                   "Sem decisão final ou validação independente.")
        for campo, conteudo in {
            "Fontes das evidências": evidencia,
            "Material consultado": "Título, resumos em português e inglês, palavras-chave e projeto do arquivo CAPES original.",
            "Limitações e pendências": limites,
            "Observações": f"Conferência CAPES 15/11/2026: {decisao}",
        }.items():
            acrescentar(celula(campo), conteudo)
        celula("Revisor").value = REVISOR
        celula("Data da triagem").value = DATA
        if item["tratamento"] == "P":
            for eixo in EIXOS.values():
                if (codigo, eixo) in existentes:
                    raise ValueError(f"Eixo anterior requer conciliação: {codigo}/{eixo}")
                linha = eixos.max_row + 1
                for coluna in range(1, eixos.max_column + 1):
                    eixos.cell(linha, coluna)._style = copy(eixos.cell(2, coluna)._style)
                valores = {
                    "Código": codigo, "Título": celula("Título").value, "Eixo": eixo,
                    "Estado": "Não verificável", "Achado ou observação": evidencia,
                    "Trecho ou localização": "Campos DS_RESUMO, DS_ABSTRACT e NM_PROJETO no arquivo original.",
                    "Tipo de fonte": "Metadados e resumos do Catálogo CAPES",
                    "Link ou referência consultada": celula("Link da fonte").value,
                    "Limites da evidência": limites, "Revisor": REVISOR, "Data": DATA,
                }
                for campo, conteudo in valores.items():
                    eixos.cell(linha, ce[campo]).value = conteudo
                existentes.add((codigo, eixo))
        auditoria.append([codigo, fonte_id, registro["NM_PROJETO"], "Sim" if tem_termo(registro["DS_ABSTRACT"]) else "Não",
                          decisao, evidencia, limites])

    tabela = eixos.tables["Eixos"]
    tabela.ref = f"A1:K{eixos.max_row}"
    if tabela.autoFilter is not None:
        tabela.autoFilter.ref = tabela.ref
    if len(eixos.data_validations.dataValidation) != 1:
        raise ValueError("Validação de eixos inesperada.")
    eixos.data_validations.dataValidation[0].sqref = f"D2:D{eixos.max_row}"
    anexar_tabela(inventario, "InventarioInglesCAPES")
    anexar_tabela(auditoria, "ResumosCatalogoCAPES")
    livro["Limites da integração"].append([
        "11 registros CAPES reavaliados com os dois resumos e projeto; nove exclusões preliminares "
        "e duas pendências. O campo DS_ABSTRACT não foi incorporado na normalização anterior; "
        "rever seu possível efeito nos demais registros CAPES antes dos resultados finais."
    ])
    livro.save(saida)


if __name__ == "__main__":
    integrar(BASE, DECISOES, BRUTO, SAIDA)
    print(f"Base criada: {SAIDA}")
