"""Integra leituras temáticas de registros BDTD sem termo literal local."""

import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

from scripts.conferir_termos_e_resumos_20261115 import ler_exportacoes, tem_termo
from scripts.integrar_autoavaliacao_20261115 import anexar_tabela, indice_unico
from scripts.integrar_teses_e_datas_uel_20261115 import acrescentar
from scripts.preanalise_e_validacao_20261115 import cabecalhos, texto_normalizado


RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_catalogo_lote2_20261115.xlsx"
DECISOES = ANALISES / "avaliacao_bdtd_termos_lote_20261115.csv"
CONSULTA_UFS = ANALISES / "consulta_ufs_bdtd_20261115.json"
SAIDA = ANALISES / "triagem_bdtd_termos_lote_20261115.xlsx"
DATA = datetime(2026, 11, 15)
REVISOR = "Análise computacional e documental preliminar não independente"
CAMPOS_BRUTOS = ("Título", "Resumo", "Resumo em Português", "Resumo em Inglês",
                 "Assuntos em português", "Assuntos em inglês")


def possivel_traducao(texto):
    normalizado = texto_normalizado(texto or "")
    return bool(re.search(r"institutional\s+program(?:me)?", normalizado)
                and re.search(r"initiat", normalizado)
                and re.search(r"teach", normalizado))


def ler_decisoes(caminho):
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames != ["codigo", "tratamento", "evidencia", "limites"]:
            raise ValueError("Colunas das decisões inesperadas.")
        linhas = list(leitor)
    if len(linhas) != 24 or len({x["codigo"] for x in linhas}) != 24:
        raise ValueError("Esperadas 24 leituras distintas.")
    if any(None in x or any(not v for v in x.values()) or x["tratamento"] not in {"E", "P"} for x in linhas):
        raise ValueError("Decisão incompleta ou inválida.")
    if Counter(x["tratamento"] for x in linhas) != {"E": 22, "P": 2}:
        raise ValueError("Distribuição inesperada das decisões.")
    return linhas


def integrar(base, decisoes, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    leituras = ler_decisoes(decisoes)
    with CONSULTA_UFS.open(encoding="utf-8") as arquivo:
        consulta = json.load(arquivo)
    if consulta["data_consulta"] != "2026-11-15" or consulta["codigo"] != "05895f12":
        raise ValueError("Consulta UFS inesperada.")
    exportacoes = ler_exportacoes()
    indice_fontes = defaultdict(list)
    for origem, registros in zip(("nacional", "regional"), exportacoes):
        for registro in registros:
            chave = (registro["Título"], registro["Autor(a)"], registro["Link de acesso"])
            indice_fontes[chave].append((origem, registro))
    livro = load_workbook(base)
    triagem = livro["Triagem"]
    col = cabecalhos(triagem)
    indices = indice_unico(triagem, col["Código"], 1317)
    auditoria = livro.create_sheet("BDTD termos lote")
    auditoria.append(["Código", "Fonte de exportação", "Tratamento preliminar",
                      "Possível tradução inglesa", "Evidência", "Limites", "Data"])
    for item in leituras:
        codigo = item["codigo"]
        if codigo not in indices:
            raise ValueError(f"Código ausente: {codigo}")
        celula = lambda campo: triagem.cell(indices[codigo], col[campo])
        if (celula("Fonte").value != "BDTD"
                or celula("Relação com PIBID").value != "Incerto"
                or celula("Triagem de título e resumo").value != "Pendente"
                or celula("Decisão de elegibilidade").value != "Não iniciada"
                or celula("Motivo da exclusão").value is not None
                or celula("Revisor").value is not None):
            raise ValueError(f"Estado anterior requer conciliação: {codigo}")
        resumo = celula("Resumo").value
        if not resumo or len(resumo) < 500 or any(
            tem_termo(celula(campo).value) for campo in ("Título", "Resumo", "Palavras-chave")
        ):
            raise ValueError(f"Material local requer conciliação: {codigo}")
        chave = (celula("Título").value, celula("Autoria").value, celula("Link da fonte").value)
        fontes = indice_fontes[chave]
        if not fontes or len({origem for origem, _ in fontes}) != len(fontes):
            raise ValueError(f"Exportação ausente ou ambígua: {codigo}")
        traducao = False
        for _, registro in fontes:
            if registro["Resumo"] != resumo or any(tem_termo(registro[campo]) for campo in CAMPOS_BRUTOS):
                raise ValueError(f"Material da exportação exige reconciliação: {codigo}")
            traducao |= any(possivel_traducao(registro[campo]) for campo in CAMPOS_BRUTOS)
        if item["tratamento"] == "E" and traducao:
            raise ValueError(f"Possível tradução do programa exige leitura: {codigo}")
        if item["tratamento"] == "P" and not traducao:
            raise ValueError(f"Tradução indicada não identificada: {codigo}")
        celula("Decisão de elegibilidade").value = "Pendente"
        if item["tratamento"] == "E":
            celula("Triagem de título e resumo").value = "Excluir"
            celula("Motivo da exclusão").value = "Outro"
            tratamento = "Excluir preliminarmente pelo critério de termos e leitura temática."
        else:
            tratamento = "Pendente: possível tradução do nome do programa."
        origens = ", ".join(origem for origem, _ in fontes)
        evidencia = item["evidencia"] + f" Fonte: exportação BDTD {origens}; título, resumo e assuntos disponíveis."
        limites = (item["limites"] + " Não afirmar ausência no texto integral. Exclusão, quando aplicada, é preliminar "
                   "e reversível; não usar em contagens temáticas sem reavaliar o critério e a evidência. "
                   "Elegibilidade final e duplicidade não resolvidas; análise não independente.")
        if codigo == consulta["codigo"]:
            if (item["tratamento"] != "P" or celula("Título").value != consulta["titulo"]
                    or celula("Autoria").value != consulta["autoria"]
                    or celula("Link da fonte").value != consulta["link_exportacao"]
                    or not tem_termo(consulta["evidencia"])):
                raise ValueError("Consulta UFS não corresponde ao registro.")
            celula("Relação com PIBID").value = "Relação substantiva com PIBID"
            tratamento = "Pendente: vínculo com PIBID confirmado no resumo em português da UFS."
            evidencia += " " + consulta["evidencia"] + " Fonte: UFS, consulta de 15/11/2026: " + consulta["url_consultada"]
            limites += " " + consulta["limites"]
        for campo, valor in {
            "Fontes das evidências": evidencia,
            "Material consultado": "Título, resumo e assuntos disponíveis na exportação BDTD; leitura temática."
            + (" Resumo português no repositório UFS." if codigo == consulta["codigo"] else ""),
            "Limitações e pendências": limites,
            "Observações": f"Conferência BDTD 15/11/2026: {tratamento}",
        }.items():
            acrescentar(celula(campo), valor)
        celula("Revisor").value = REVISOR
        celula("Data da triagem").value = DATA
        auditoria.append([codigo, origens, tratamento, "Sim" if traducao else "Não",
                          evidencia, limites, DATA])
    anexar_tabela(auditoria, "BDTDTermosLote")
    livro["Limites da integração"].append([
        "24 linhas BDTD lidas sem termo literal local: 22 exclusões preliminares e duas pendências; "
        "vínculo de uma confirmado no resumo UFS. Ver aba BDTD termos lote; sem validação independente nem decisão final."
    ])
    livro.save(saida)


if __name__ == "__main__":
    integrar(BASE, DECISOES, SAIDA)
    print(f"Base criada: {SAIDA}")
