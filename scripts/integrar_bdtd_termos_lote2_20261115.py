"""Integra outro lote BDTD e uma consulta complementar à UFS."""

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

from scripts.confirmar_duplicatas_amostra_20261115 import validar_par
from scripts.conferir_termos_e_resumos_20261115 import ler_exportacoes, tem_termo
from scripts.integrar_autoavaliacao_20261115 import anexar_tabela, indice_unico
from scripts.integrar_bdtd_termos_lote_20261115 import CAMPOS_BRUTOS, possivel_traducao
from scripts.integrar_teses_e_datas_uel_20261115 import acrescentar
from scripts.preanalise_e_validacao_20261115 import cabecalhos


RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_bdtd_termos_lote_20261115.xlsx"
DECISOES = ANALISES / "avaliacao_bdtd_termos_lote2_20261115.csv"
CONSULTA_UFS = ANALISES / "consulta_ufs_bdtd_lote2_20261115.json"
SAIDA = ANALISES / "triagem_bdtd_termos_lote2_20261115.xlsx"
DATA = datetime(2026, 11, 15)
REVISOR = "Análise computacional e documental preliminar não independente"
PARES_CONFIRMADOS = (("361dd6b1", "f1d6e487"), ("5f5259e7", "3ee25c3e"))
PARES_CONTEUDO = (("cc9255f4", "03f41e0d"), ("f2e72aea", "14bf350a"),
                  ("ac0cfaa4", "c339d9bf"))
ANTERIORMENTE_LIDOS = {"f1d6e487", "3ee25c3e", "9d2082d5"}


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
    if {x["codigo"] for x in linhas if x["tratamento"] == "P"} != {"52ecb111", "9d2082d5"}:
        raise ValueError("Pendências inesperadas.")
    return linhas


def integrar(base, decisoes, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    leituras = ler_decisoes(decisoes)
    with CONSULTA_UFS.open(encoding="utf-8") as arquivo:
        consulta = json.load(arquivo)
    if consulta["data_consulta"] != "2026-11-15" or consulta["codigo"] != "9d2082d5":
        raise ValueError("Consulta UFS inesperada.")
    indice_fontes = defaultdict(list)
    for origem, registros in zip(("nacional", "regional"), ler_exportacoes()):
        for registro in registros:
            chave = (registro["Título"], registro["Autor(a)"], registro["Link de acesso"])
            indice_fontes[chave].append((origem, registro))
    livro = load_workbook(base)
    triagem = livro["Triagem"]
    col = cabecalhos(triagem)
    indices = indice_unico(triagem, col["Código"], 1317)
    for primeiro, segundo in PARES_CONFIRMADOS:
        n1, n2 = indices[primeiro], indices[segundo]
        validar_par(triagem, col, n1, n2, primeiro, segundo)
        for campo in ("Resumo", "Palavras-chave"):
            if triagem.cell(n1, col[campo]).value != triagem.cell(n2, col[campo]).value:
                raise ValueError(f"Conteúdo divergente no par {primeiro}/{segundo}: {campo}")
        if any(triagem.cell(n, col["Duplicidade"]).value != "Duplicata confirmada" for n in (n1, n2)):
            raise ValueError(f"Par não confirmado: {primeiro}/{segundo}")
    for primeiro, segundo in PARES_CONTEUDO:
        for campo in ("Título", "Autoria", "Resumo", "Palavras-chave", "Link da fonte"):
            if triagem.cell(indices[primeiro], col[campo]).value != triagem.cell(indices[segundo], col[campo]).value:
                raise ValueError(f"Conteúdo divergente em {primeiro}/{segundo}: {campo}")
    auditoria = livro.create_sheet("BDTD termos lote 2")
    auditoria.append(["Código", "Fonte de exportação", "Triagem anterior", "Triagem revisada",
                      "Relação anterior", "Relação revisada", "Evidência", "Limites", "Data"])
    for item in leituras:
        codigo = item["codigo"]
        if codigo not in indices:
            raise ValueError(f"Código ausente: {codigo}")
        celula = lambda campo: triagem.cell(indices[codigo], col[campo])
        elegibilidade_esperada = "Pendente" if codigo in ANTERIORMENTE_LIDOS else "Não iniciada"
        if (celula("Fonte").value != "BDTD"
                or celula("Relação com PIBID").value != "Incerto"
                or celula("Triagem de título e resumo").value != "Pendente"
                or celula("Decisão de elegibilidade").value != elegibilidade_esperada
                or celula("Motivo da exclusão").value is not None
                or bool(celula("Revisor").value) != (codigo in ANTERIORMENTE_LIDOS)):
            raise ValueError(f"Estado anterior requer conciliação: {codigo}")
        resumo = celula("Resumo").value
        if not resumo or len(resumo) < 500 or any(
            tem_termo(celula(campo).value) for campo in ("Título", "Resumo", "Palavras-chave")
        ):
            raise ValueError(f"Material local requer conciliação: {codigo}")
        link = celula("Link da fonte").value
        if link is None:
            if codigo not in {"ac0cfaa4", "c339d9bf"}:
                raise ValueError(f"Link ausente inesperado: {codigo}")
            link = "Não informado pela instituição"
        chave = (celula("Título").value, celula("Autoria").value, link)
        fontes = indice_fontes[chave]
        if not fontes or len({origem for origem, _ in fontes}) != len(fontes):
            raise ValueError(f"Exportação ausente ou ambígua: {codigo}")
        traducao = False
        for _, registro in fontes:
            if registro["Resumo"] != resumo or any(tem_termo(registro[campo]) for campo in CAMPOS_BRUTOS):
                raise ValueError(f"Material da exportação exige reconciliação: {codigo}")
            traducao |= any(possivel_traducao(registro[campo]) for campo in CAMPOS_BRUTOS)
        if (item["tratamento"] == "E" and traducao) or (item["tratamento"] == "P" and not traducao):
            raise ValueError(f"Tradução exige conciliação: {codigo}")
        celula("Decisão de elegibilidade").value = "Pendente"
        tratamento = "Pendente: possível tradução do nome do programa."
        if item["tratamento"] == "E":
            celula("Triagem de título e resumo").value = "Excluir"
            celula("Motivo da exclusão").value = "Outro"
            tratamento = "Excluir preliminarmente pelo critério de termos e leitura temática."
        origens = ", ".join(origem for origem, _ in fontes)
        evidencia = item["evidencia"] + f" Fonte: exportação BDTD {origens}; título, resumo e assuntos disponíveis."
        limites = (item["limites"] + " Não afirmar ausência no texto integral. Exclusão, quando aplicada, é preliminar "
                   "e reversível; não usar em contagens temáticas sem reavaliar o critério e a evidência. "
                   "Elegibilidade final pendente; análise não independente.")
        if codigo == consulta["codigo"]:
            if (celula("Título").value != consulta["titulo"] or celula("Autoria").value != consulta["autoria"]
                    or celula("Link da fonte").value != consulta["url_consultada"]
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
            "Observações": f"Conferência BDTD lote 2 de 15/11/2026: {tratamento}",
        }.items():
            acrescentar(celula(campo), valor)
        if codigo not in ANTERIORMENTE_LIDOS:
            celula("Revisor").value = REVISOR
            celula("Data da triagem").value = DATA
        auditoria.append([codigo, origens, "Pendente", celula("Triagem de título e resumo").value,
                          "Incerto", celula("Relação com PIBID").value, evidencia, limites, DATA])
    anexar_tabela(auditoria, "BDTDTermosLote2")
    livro["Limites da integração"].append([
        "24 linhas BDTD conferidas no lote 2, incluindo três anteriormente lidas: 22 exclusões "
        "preliminares e duas pendências; ver aba BDTD termos lote 2. Sem validação independente nem decisão final."
    ])
    livro.save(saida)


if __name__ == "__main__":
    integrar(BASE, DECISOES, SAIDA)
    print(f"Base criada: {SAIDA}")
