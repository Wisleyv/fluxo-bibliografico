"""Integra dez leituras CAPES e corrige campos de resumo que contêm apenas metadados."""

import csv
import re
from collections import Counter
from copy import copy
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

from scripts.classificar_resumos_ausentes_20261115 import NAO_AVALIADA, NOTA, REDUZIDA
from scripts.conferir_catalogo_resumos_20261115 import identificador, ler_originais
from scripts.conferir_termos_e_resumos_20261115 import tem_termo
from scripts.integrar_autoavaliacao_20261115 import EIXOS, anexar_tabela, indice_unico
from scripts.integrar_catalogo_lote2_20261115 import BRUTO, REVISOR
from scripts.integrar_teses_e_datas_uel_20261115 import acrescentar
from scripts.preanalise_e_validacao_20261115 import cabecalhos, texto_normalizado
from scripts.preencher_autoavaliacao_20261115 import OPCOES


RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_qualidade_resumos_20261115.xlsx"
DECISOES = ANALISES / "avaliacao_catalogo_lote3_20261115.csv"
SAIDA = ANALISES / "triagem_catalogo_lote3_20261115.xlsx"
DATA = datetime(2026, 11, 15)


def tipo_metadado(valor):
    texto = texto_normalizado(valor or "").strip()
    if len(texto) > 500:
        return None
    if texto in {"em construcao", "nao foi possivel inserir o abstract."}:
        return "Marcador de resumo indisponível"
    if texto.startswith(("orientacao:", "a orientadora do trabalho")):
        return "Informação de orientação"
    if (texto.startswith(("dissertacao", "tese de doutorado"))
            or re.fullmatch(r"\d+\s*[pf]\.", texto)
            or re.search(r"\b(?:dissertacao|tese)\s*\((?:mestrado|doutorado)\)", texto)):
        return "Referência ou descrição bibliográfica"
    if texto.startswith(("programa de pos-graduacao", "linha de pesquisa:",
                         "universidade estadual paulista julio de mesquita filho")):
        return "Instituição ou linha de pesquisa"
    if texto.startswith("acompanha"):
        return "Descrição de material acompanhante"
    if texto.startswith(("coordenacao de aperfeicoamento", "conselho nacional de desenvolvimento",
                         "o presente trabalho foi realizado com apoio")):
        return "Informação de financiamento"
    return None


def ler_decisoes(caminho):
    campos = ["codigo", "id", "pibid", "eixos", "evidencia", "limites"]
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames != campos:
            raise ValueError("Colunas das avaliações inesperadas.")
        linhas = list(leitor)
    if len(linhas) != 10 or len({x["codigo"] for x in linhas}) != 10 or len({x["id"] for x in linhas}) != 10:
        raise ValueError("Esperadas dez avaliações distintas.")
    for item in linhas:
        if (None in item or not all(item.values()) or item["pibid"] not in {"T", "S", "I"}
                or len(item["eixos"]) != 3 or any(x not in OPCOES["eixo"] for x in item["eixos"])
                or (item["pibid"] == "I" and item["eixos"] != "VVV")):
            raise ValueError(f"Avaliação inválida: {item}")
    return linhas


def integrar(base, decisoes, bruto, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    leituras = ler_decisoes(decisoes)
    originais = ler_originais(bruto, {x["id"] for x in leituras})
    livro = load_workbook(base)
    triagem, eixos, qualidade = livro["Triagem"], livro["Eixos de análise"], livro["Qualidade dos resumos"]
    ct, ce = cabecalhos(triagem), cabecalhos(eixos)
    indices = indice_unico(triagem, ct["Código"], 1317)
    if "CAPES bilíngue lote 3" in livro.sheetnames or qualidade.max_row != 210:
        raise ValueError("Histórico documental inesperado.")
    inventario = {r[0]: r for r in list(livro["Inventário inglês CAPES"].values)[1:]}
    lidos = set()
    for nome in ("Resumos Catálogo CAPES", "Revisão bilíngue CAPES", "CAPES bilíngue lote 2"):
        lidos.update(r[0] for r in list(livro[nome].values)[1:])
    existentes = set()
    for row in list(eixos.values)[1:]:
        chave = (row[ce["Código"] - 1], row[ce["Eixo"] - 1])
        if chave in existentes:
            raise ValueError(f"Eixo duplicado: {chave}")
        existentes.add(chave)

    correcoes = []
    for codigo, numero in indices.items():
        if triagem.cell(numero, ct["Qualidade documental do resumo"]).value == NAO_AVALIADA:
            tipo = tipo_metadado(triagem.cell(numero, ct["Resumo"]).value)
            if tipo:
                correcoes.append((codigo, numero, tipo))
    fontes = Counter(triagem.cell(n, ct["Fonte"]).value for _, n, _ in correcoes)
    if len(correcoes) != 64 or fontes != {"BDTD": 62, "Catálogo CAPES": 2}:
        raise ValueError(f"Correções documentais inesperadas: {len(correcoes)}, {fontes}")
    for codigo, numero, tipo in correcoes:
        celula = lambda campo: triagem.cell(numero, ct[campo])
        celula("Qualidade documental do resumo").value = REDUZIDA
        acrescentar(celula("Limitações e pendências"), NOTA)
        qualidade.append([
            codigo, celula("Fonte").value, celula("Título").value, tipo,
            "Sim" if tem_termo(celula("Título").value) else "Não identificado por regra",
            "Sim" if tem_termo(celula("Palavras-chave").value) else "Não identificado por regra",
            "Não identificado nesta conferência", celula("Material consultado").value or "Não registrado",
            REDUZIDA,
            "O campo da base contém metadado ou marcador, não resumo substantivo. "
            "A classificação não comprova elegibilidade ou acurácia; outras fontes já consultadas podem ter resumo.",
        ])
        for coluna in range(1, qualidade.max_column + 1):
            qualidade.cell(qualidade.max_row, coluna)._style = copy(qualidade.cell(2, coluna)._style)
    tabela_qualidade = qualidade.tables["QualidadeResumos"]
    tabela_qualidade.ref = f"A1:J{qualidade.max_row}"
    tabela_qualidade.autoFilter.ref = tabela_qualidade.ref

    auditoria = livro.create_sheet("CAPES bilíngue lote 3")
    auditoria.append(["Código", "ID CAPES", "Relação PIBID", "Contexto de Goiás",
                      "Eixos", "Evidência", "Limites", "Data"])
    for item in leituras:
        codigo, fonte_id = item["codigo"], item["id"]
        if codigo not in indices or codigo not in inventario or codigo in lidos:
            raise ValueError(f"Registro ausente ou já lido: {codigo}")
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
                or celula("Revisor").value is not None
                or any((codigo, eixo) in existentes for eixo in EIXOS.values())):
            raise ValueError(f"Estado anterior requer conciliação: {codigo}")
        celula("Relação com PIBID").value = OPCOES["pibid"][item["pibid"]]
        celula("Contexto de Goiás").value = OPCOES["contexto"]["N"]
        celula("Decisão de elegibilidade").value = "Pendente"
        evidencia = item["evidencia"] + f" Fonte: arquivo anual CAPES 2024, registro {fonte_id}, título e campos DS_RESUMO e DS_ABSTRACT."
        limites = (item["limites"] + " Não identificar Goiás no material consultado não prova ausência de contexto ou afiliação; "
                   "ano de defesa não equivale a publicação. Elegibilidade e duplicidade permanecem pendentes; conferência não independente.")
        for campo, valor in {
            "Evidência do contexto": "Sem evidência de contexto goiano no título e nos resumos consultados; não equivale a ausência comprovada.",
            "Fontes das evidências": evidencia,
            "Material consultado": "Título, campos DS_RESUMO e DS_ABSTRACT e palavras-chave do arquivo CAPES original.",
            "Limitações e pendências": limites,
            "Observações": "Leitura preliminar dos dois resumos em 15/11/2026; triagem e elegibilidade final permanecem pendentes.",
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
                          celula("Contexto de Goiás").value,
                          " | ".join(OPCOES["eixo"][estado] for estado in item["eixos"]),
                          evidencia, limites, DATA])
    tabela = eixos.tables["Eixos"]
    tabela.ref = f"A1:K{eixos.max_row}"
    tabela.autoFilter.ref = tabela.ref
    if len(eixos.data_validations.dataValidation) != 1:
        raise ValueError("Validação de eixos inesperada.")
    eixos.data_validations.dataValidation[0].sqref = f"D2:D{eixos.max_row}"
    anexar_tabela(auditoria, "CAPESBilingueLote3")
    livro["Limites da integração"].append([
        "Dez registros CAPES adicionais lidos nos dois resumos; um campo DS_ABSTRACT está em espanhol. "
        "64 campos com metadados ou marcadores foram corrigidos para qualidade documental reduzida. "
        "Sem validação independente nem decisão final."
    ])
    livro.save(saida)
    livro.close()


if __name__ == "__main__":
    integrar(BASE, DECISOES, BRUTO, SAIDA)
    print(f"Base criada: {SAIDA}")
