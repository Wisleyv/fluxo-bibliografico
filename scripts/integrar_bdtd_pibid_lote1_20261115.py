"""Integra leituras de registros BDTD com PIBID no título."""

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

from scripts.conferir_termos_e_resumos_20261115 import ler_exportacoes, tem_termo
from scripts.integrar_autoavaliacao_20261115 import anexar_tabela, indice_unico
from scripts.integrar_teses_e_datas_uel_20261115 import acrescentar
from scripts.preanalise_e_validacao_20261115 import ano, cabecalhos
from scripts.preencher_autoavaliacao_20261115 import OPCOES


RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_bdtd_termos_lote2_20261115.xlsx"
DECISOES = ANALISES / "avaliacao_bdtd_pibid_lote1_20261115.csv"
SAIDA = ANALISES / "triagem_bdtd_pibid_lote1_20261115.xlsx"
DATA = datetime(2026, 11, 15)
REVISOR = "Análise computacional e documental preliminar não independente"


def ler_decisoes(caminho):
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames != ["codigo", "pibid", "contexto", "evidencia_contexto", "evidencia", "limites"]:
            raise ValueError("Colunas das decisões inesperadas.")
        linhas = list(leitor)
    if len(linhas) != 20 or len({x["codigo"] for x in linhas}) != 20:
        raise ValueError("Esperadas 20 avaliações distintas.")
    if any(None in x or any(not v for v in x.values())
           or x["pibid"] not in {"T", "S", "I"} or x["contexto"] not in {"N", "I"} for x in linhas):
        raise ValueError("Avaliação incompleta ou inválida.")
    return linhas


def integrar(base, decisoes, saida, *, lote_recente=False):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    leituras = ler_decisoes(decisoes)
    fontes = defaultdict(list)
    for origem, registros in zip(("nacional", "regional"), ler_exportacoes()):
        for registro in registros:
            autor = registro["Autor(a)"].replace("||", " | ")
            fontes[(registro["Título"], autor, registro["Link de acesso"])].append((origem, registro))
    livro = load_workbook(base)
    triagem = livro["Triagem"]
    col = cabecalhos(triagem)
    indices = indice_unico(triagem, col["Código"], 1317)
    auditoria = livro.create_sheet("BDTD PIBID recentes" if lote_recente else "BDTD PIBID lote 1")
    auditoria.append(["Código", "Fonte de exportação", "Relação com PIBID", "Contexto de Goiás",
                      "Evidência do contexto", "Síntese", "Limites", "Data"])
    for item in leituras:
        codigo = item["codigo"]
        if codigo not in indices:
            raise ValueError(f"Código ausente: {codigo}")
        celula = lambda campo: triagem.cell(indices[codigo], col[campo])
        if (celula("Fonte").value != "BDTD"
                or celula("Relação com PIBID").value != "Incerto"
                or celula("Contexto de Goiás").value != "Incerto"
                or celula("Triagem de título e resumo").value != "Pendente"
                or celula("Decisão de elegibilidade").value != "Não iniciada"
                or celula("Motivo da exclusão").value is not None
                or celula("Revisor").value is not None):
            raise ValueError(f"Estado anterior requer conciliação: {codigo}")
        resumo = celula("Resumo").value
        if not tem_termo(celula("Título").value) or not resumo or len(resumo) < 500:
            raise ValueError(f"Material local requer conciliação: {codigo}")
        if lote_recente and (ano(celula("Ano de defesa").value) or 0) < 2020:
            raise ValueError(f"Ano de defesa incompatível com o lote recente: {codigo}")
        chave = (celula("Título").value, celula("Autoria").value, celula("Link da fonte").value)
        encontrados = fontes[chave]
        if not encontrados or len({origem for origem, _ in encontrados}) != len(encontrados):
            raise ValueError(f"Exportação ausente ou ambígua: {codigo}")
        if any(registro["Resumo"] != resumo for _, registro in encontrados):
            raise ValueError(f"Resumo divergente da exportação: {codigo}")
        celula("Relação com PIBID").value = OPCOES["pibid"][item["pibid"]]
        celula("Contexto de Goiás").value = OPCOES["contexto"][item["contexto"]]
        celula("Decisão de elegibilidade").value = "Pendente"
        origens = ", ".join(origem for origem, _ in encontrados)
        evidencia = item["evidencia"] + f" Fonte: título e resumo da exportação BDTD {origens}."
        contexto = item["evidencia_contexto"] + " Não identificar Goiás no material consultado não prova ausência de contexto ou afiliação."
        limites = (item["limites"] + " Ano de defesa não equivale a publicação; contexto e afiliação são dimensões distintas. "
                   "Elegibilidade, duplicidade e extrações de eixos permanecem pendentes; análise não independente.")
        for campo, valor in {
            "Evidência do contexto": contexto,
            "Fontes das evidências": evidencia,
            "Material consultado": "Título, resumo e assuntos disponíveis na exportação BDTD; leitura temática.",
            "Limitações e pendências": limites,
            "Observações": "Leitura preliminar 15/11/2026; triagem e elegibilidade final pendentes. Eixos não extraídos nesta etapa.",
        }.items():
            acrescentar(celula(campo), valor)
        celula("Revisor").value = REVISOR
        celula("Data da triagem").value = DATA
        auditoria.append([codigo, origens, celula("Relação com PIBID").value, celula("Contexto de Goiás").value,
                          contexto, evidencia, limites, DATA])
    anexar_tabela(auditoria, "BDTDPIBIDRecentes" if lote_recente else "BDTDPIBIDLote1")
    nome_lote = "BDTD PIBID recentes" if lote_recente else "BDTD PIBID lote 1"
    livro["Limites da integração"].append([
        f"20 registros BDTD com PIBID no título lidos; ver aba {nome_lote}. "
        "Eixos ainda não extraídos; sem validação independente nem decisão final."
    ])
    livro.save(saida)


if __name__ == "__main__":
    integrar(BASE, DECISOES, SAIDA)
    print(f"Base criada: {SAIDA}")
