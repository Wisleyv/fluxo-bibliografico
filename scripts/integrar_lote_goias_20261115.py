"""Aplica uma leitura direcionada de registros com indícios regionais."""

import csv
from copy import copy
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

from scripts.confirmar_duplicatas_amostra_20261115 import validar_par
from scripts.integrar_autoavaliacao_20261115 import (
    EIXOS, anexar_tabela, indice_unico,
)
from scripts.preanalise_e_validacao_20261115 import ano, cabecalhos
from scripts.preencher_autoavaliacao_20261115 import OPCOES


RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_duplicatas_conferidas_20261115.xlsx"
DECISOES = ANALISES / "avaliacao_lote_goias_20261115.csv"
SAIDA = ANALISES / "triagem_lote_goias_20261115.xlsx"
DATA = datetime(2026, 11, 15)


def ler_decisoes(caminho):
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    if not linhas:
        raise ValueError("Lote vazio.")
    codigos = set()
    for linha in linhas:
        if any(v is None for v in linha.values()) or None in linha:
            raise ValueError("Linha CSV malformada.")
        if linha["incluir_par"] not in {"S", "N"} or (linha["incluir_par"] == "S" and not linha["par"]):
            raise ValueError(f"Par inválido: {linha['codigo']}")
        for campo in ("pibid", "contexto"):
            if linha[campo] not in OPCOES[campo]:
                raise ValueError(f"Opção inválida: {campo}, {linha['codigo']}")
        if len(linha["eixos"]) != 3 or any(v not in OPCOES["eixo"] for v in linha["eixos"]):
            raise ValueError(f"Eixos inválidos: {linha['codigo']}")
        if not linha["evidencia"] or not linha["limites"]:
            raise ValueError(f"Falta evidência ou limites: {linha['codigo']}")
        selecionados = [linha["codigo"]] + ([linha["par"]] if linha["incluir_par"] == "S" else [])
        if any(not c or c in codigos for c in selecionados) or len(set(selecionados)) != len(selecionados):
            raise ValueError(f"Código repetido ou ausente: {linha['codigo']}")
        codigos.update(selecionados)
    if len(codigos) != 36:
        raise ValueError(f"Esperados 36 registros; encontrados {len(codigos)}.")
    return linhas


def integrar(base, decisoes, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    entradas = ler_decisoes(decisoes)
    livro = load_workbook(base)
    triagem, eixos = livro["Triagem"], livro["Eixos de análise"]
    ct, ce = cabecalhos(triagem), cabecalhos(eixos)
    indices = indice_unico(triagem, ct["Código"], 1317)
    existentes = {}
    for numero in range(2, eixos.max_row + 1):
        chave = (eixos.cell(numero, ce["Código"]).value, eixos.cell(numero, ce["Eixo"]).value)
        if chave in existentes:
            raise ValueError(f"Eixo duplicado: {chave}")
        existentes[chave] = numero

    auditoria = livro.create_sheet("Lote prioritário GO")
    auditoria.append([
        "Código", "Par bibliográfico", "PIBID anterior", "PIBID revisado",
        "Contexto anterior", "Contexto revisado", "Triagem anterior", "Triagem revisada",
        "Evidência", "Limites", "Duplicidade anterior", "Duplicidade revisada",
    ])
    for item in entradas:
        codigo, par = item["codigo"], item["par"]
        if codigo not in indices or (par and par not in indices):
            raise ValueError(f"Código não encontrado: {codigo}/{par}")
        if par:
            n1, n2 = indices[codigo], indices[par]
            validar_par(triagem, ct, n1, n2, codigo, par)
            for campo in ("Resumo", "Palavras-chave"):
                if triagem.cell(n1, ct[campo]).value != triagem.cell(n2, ct[campo]).value:
                    raise ValueError(f"Material diferente no par {codigo}/{par}: {campo}")
        selecionados = [(codigo, par)]
        if item["incluir_par"] == "S":
            selecionados.append((par, codigo))
        for atual, outro in selecionados:
            n = indices[atual]
            celula = lambda campo: triagem.cell(n, ct[campo])
            if celula("Relação com PIBID").value != "Incerto":
                raise ValueError(f"Registro já avaliado requer conciliação: {atual}")
            if celula("Triagem de título e resumo").value != "Pendente":
                raise ValueError(f"Triagem anterior inesperada: {atual}")
            duplicidade_anterior = celula("Duplicidade").value
            if outro and duplicidade_anterior not in {"Não verificada", "Duplicata provável", "Duplicata confirmada"}:
                raise ValueError(f"Duplicidade anterior inesperada: {atual}")
            ano_publicacao = ano(celula("Ano de publicação").value)
            if ano_publicacao is not None:
                if 2020 <= ano_publicacao <= 2026:
                    raise ValueError(f"Publicação inesperada no lote de exclusões: {atual}")
                triagem_nova = "Excluir"
            else:
                if celula("Publicação em 2020–2026").value != "Só ano de defesa disponível":
                    raise ValueError(f"Período inesperado para dissertação ou tese: {atual}")
                triagem_nova = "Pendente"
            anterior_pibid = celula("Relação com PIBID").value
            anterior_contexto = celula("Contexto de Goiás").value
            anterior_triagem = celula("Triagem de título e resumo").value
            celula("Relação com PIBID").value = OPCOES["pibid"][item["pibid"]]
            celula("Contexto de Goiás").value = OPCOES["contexto"][item["contexto"]]
            celula("Triagem de título e resumo").value = triagem_nova
            celula("Decisão de elegibilidade").value = "Pendente"
            if triagem_nova == "Excluir":
                celula("Motivo da exclusão").value = "Fora do período"
            if outro:
                celula("Duplicidade").value = "Duplicata confirmada"
            evidencia = item["evidencia"] + " Fonte: título, resumo e metadados locais desta linha."
            limites = item["limites"]
            for campo, novo in {
                "Evidência do contexto": evidencia,
                "Fontes das evidências": evidencia,
                "Material consultado": "Título e resumo locais, ou título e metadados quando não há resumo.",
                "Limitações e pendências": limites,
                "Observações": (
                    "Leitura direcionada preliminar não independente; elegibilidade final pendente."
                    + (f" Mesmo identificador de repositório e metadados do par {outro}; sem escolha de principal." if outro else "")
                ),
            }.items():
                c = celula(campo)
                novo_valor = f"Anterior: {c.value}\nLote prioritário GO: {novo}" if c.value else f"Lote prioritário GO: {novo}"
                if len(novo_valor) > 32767:
                    raise ValueError(f"Texto excede limite do Excel: {atual}, {campo}")
                c.value = novo_valor
            celula("Revisor").value = "Análise computacional preliminar não independente"
            celula("Data da triagem").value = DATA
            for (nome, eixo), estado in zip(EIXOS.items(), item["eixos"]):
                if (atual, eixo) in existentes:
                    raise ValueError(f"Eixo preexistente requer conciliação: {atual}, {eixo}")
                num = eixos.max_row + 1
                for coluna in range(1, eixos.max_column + 1):
                    eixos.cell(num, coluna)._style = copy(eixos.cell(2, coluna)._style)
                preenchimento = {
                    "Código": atual, "Título": celula("Título").value, "Eixo": eixo,
                    "Estado": OPCOES["eixo"][estado], "Achado ou observação": evidencia,
                    "Trecho ou localização": "Síntese e localização no campo de evidência.",
                    "Tipo de fonte": "Metadados e material local",
                    "Link ou referência consultada": celula("Link da fonte").value or "Metadados locais da planilha",
                    "Limites da evidência": limites + " Extração preliminar; elegibilidade não definida.",
                    "Revisor": "Análise computacional preliminar não independente", "Data": DATA,
                }
                for campo, conteudo in preenchimento.items():
                    eixos.cell(num, ce[campo]).value = conteudo
                existentes[(atual, eixo)] = num
            auditoria.append([
                atual, outro or "Não identificado", anterior_pibid, celula("Relação com PIBID").value,
                anterior_contexto, celula("Contexto de Goiás").value, anterior_triagem, triagem_nova,
                evidencia, limites, duplicidade_anterior, celula("Duplicidade").value,
            ])

    tabela_eixos = eixos.tables["Eixos"]
    tabela_eixos.ref = f"A1:K{eixos.max_row}"
    if tabela_eixos.autoFilter is not None:
        tabela_eixos.autoFilter.ref = tabela_eixos.ref
    if len(eixos.data_validations.dataValidation) != 1:
        raise ValueError("Validação de eixos inesperada.")
    eixos.data_validations.dataValidation[0].sqref = f"D2:D{eixos.max_row}"
    anexar_tabela(auditoria, "LotePrioritarioGoias")
    livro["Limites da integração"].append([
        "Lote de 36 linhas com indícios regionais analisado; ver aba Lote prioritário GO. "
        "As extrações são preliminares, incluem duplicatas e não equivalem a elegibilidade final."
    ])
    livro.save(saida)


if __name__ == "__main__":
    integrar(BASE, DECISOES, SAIDA)
    print(f"Base criada: {SAIDA}")
