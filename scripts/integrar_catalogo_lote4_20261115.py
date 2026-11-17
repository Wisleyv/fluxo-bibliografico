"""Integra leituras adicionais dos resumos disponíveis do Catálogo CAPES."""

import csv
from copy import copy
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

from scripts.conferir_catalogo_resumos_20261115 import identificador, ler_originais
from scripts.conferir_termos_e_resumos_20261115 import tem_termo
from scripts.integrar_autoavaliacao_20261115 import EIXOS, anexar_tabela, indice_unico
from scripts.integrar_catalogo_lote2_20261115 import BRUTO, REVISOR
from scripts.integrar_teses_e_datas_uel_20261115 import acrescentar
from scripts.preanalise_e_validacao_20261115 import cabecalhos
from scripts.preencher_autoavaliacao_20261115 import OPCOES


RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_catalogo_lote3_20261115.xlsx"
DECISOES = ANALISES / "avaliacao_catalogo_lote4_20261115.csv"
SAIDA = ANALISES / "triagem_catalogo_lote4_20261115.xlsx"
DATA = datetime(2026, 11, 15)
ABA = "CAPES bilíngue lote 4"
ANTERIORES = ("Resumos Catálogo CAPES", "Revisão bilíngue CAPES",
              "CAPES bilíngue lote 2", "CAPES bilíngue lote 3")


def ler_decisoes(caminho, quantidade=18):
    campos = ["codigo", "id", "pibid", "eixos", "evidencia", "limites"]
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames != campos:
            raise ValueError("Colunas das avaliações inesperadas.")
        linhas = list(leitor)
    if (len(linhas) != quantidade or len({x["codigo"] for x in linhas}) != quantidade
            or len({x["id"] for x in linhas}) != quantidade):
        raise ValueError(f"Esperadas {quantidade} avaliações distintas.")
    for item in linhas:
        if (None in item or any(not item[c] for c in campos if c != "eixos")
                or item["pibid"] not in OPCOES["pibid"]):
            raise ValueError(f"Avaliação inválida: {item}")
        if item["pibid"] == "M":
            if item["eixos"]:
                raise ValueError(f"Exclusão com extrações: {item['codigo']}")
        elif (len(item["eixos"]) != 3 or any(x not in OPCOES["eixo"] for x in item["eixos"])
              or (item["pibid"] == "I" and item["eixos"] != "VVV")):
            raise ValueError(f"Eixos incompatíveis: {item['codigo']}")
    return linhas


def integrar(base, decisoes, bruto, saida, *, quantidade=18, aba=ABA,
             anteriores=ANTERIORES, total_restantes=30, ignorar=(),
             nome_tabela="CAPESBilingueLote4",
             mensagem_limites="18 registros CAPES adicionais lidos nos dois resumos; uma exclusão temática preliminar "
             "e reversível por menção incidental. Sem validação independente nem decisão final."):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    leituras = ler_decisoes(decisoes, quantidade)
    originais = ler_originais(bruto, {x["id"] for x in leituras})
    livro = load_workbook(base)
    triagem, eixos = livro["Triagem"], livro["Eixos de análise"]
    ct, ce = cabecalhos(triagem), cabecalhos(eixos)
    indices = indice_unico(triagem, ct["Código"], 1317)
    if aba in livro.sheetnames:
        raise ValueError("Lote já integrado.")
    inventario = list(livro["Inventário inglês CAPES"].values)[1:]
    lidos = set()
    for nome in anteriores:
        lidos.update(r[0] for r in list(livro[nome].values)[1:])
    restantes = [r for r in inventario if r[0] not in lidos]
    if (len(restantes) != total_restantes or not set(ignorar).issubset({r[0] for r in restantes})
            or [(x["codigo"], x["id"]) for x in leituras] != [
                (r[0], r[1]) for r in restantes if r[0] not in ignorar
            ][:quantidade]):
        raise ValueError("Seleção ou histórico do inventário divergente.")
    existentes = set()
    for row in list(eixos.values)[1:]:
        chave = (row[ce["Código"] - 1], row[ce["Eixo"] - 1])
        if chave in existentes:
            raise ValueError(f"Eixo duplicado: {chave}")
        existentes.add(chave)

    auditoria = livro.create_sheet(aba)
    auditoria.append(["Código", "ID CAPES", "Relação PIBID", "Contexto de Goiás",
                      "Triagem preliminar", "Eixos", "Evidência", "Limites", "Data"])
    for item in leituras:
        codigo, fonte_id = item["codigo"], item["id"]
        if codigo not in indices:
            raise ValueError(f"Registro ausente: {codigo}")
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
        if item["pibid"] == "M" and not any(
            tem_termo(registro[campo]) for campo in ("NM_PRODUCAO", "DS_RESUMO", "DS_ABSTRACT")
        ):
            raise ValueError(f"Menção incidental não identificada: {codigo}")
        celula("Relação com PIBID").value = OPCOES["pibid"][item["pibid"]]
        celula("Contexto de Goiás").value = OPCOES["contexto"]["N"]
        celula("Decisão de elegibilidade").value = "Pendente"
        if item["pibid"] == "M":
            celula("Triagem de título e resumo").value = "Excluir"
            celula("Motivo da exclusão").value = "Sem relação substantiva com PIBID"
        evidencia = item["evidencia"] + f" Fonte: arquivo anual CAPES 2024, registro {fonte_id}, título e campos DS_RESUMO e DS_ABSTRACT."
        limites = (item["limites"] + " Não identificar Goiás no material consultado não prova ausência de contexto ou afiliação; "
                   "ano de defesa não equivale a publicação. Elegibilidade e duplicidade permanecem pendentes; conferência não independente.")
        for campo, valor in {
            "Evidência do contexto": "Sem evidência de contexto goiano no título e nos resumos consultados; não equivale a ausência comprovada.",
            "Fontes das evidências": evidencia,
            "Material consultado": "Título, campos DS_RESUMO e DS_ABSTRACT e palavras-chave do arquivo CAPES original.",
            "Limitações e pendências": limites,
            "Observações": "Leitura preliminar dos dois resumos em 15/11/2026; " + (
                "exclusão por menção incidental é reversível." if item["pibid"] == "M"
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
    tabela.autoFilter.ref = tabela.ref
    if len(eixos.data_validations.dataValidation) != 1:
        raise ValueError("Validação de eixos inesperada.")
    eixos.data_validations.dataValidation[0].sqref = f"D2:D{eixos.max_row}"
    anexar_tabela(auditoria, nome_tabela)
    livro["Limites da integração"].append([mensagem_limites])
    livro.save(saida)
    livro.close()


if __name__ == "__main__":
    integrar(BASE, DECISOES, BRUTO, SAIDA)
    print(f"Base criada: {SAIDA}")
