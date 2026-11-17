"""Reconcilia avaliações CAPES anteriores com os resumos em ambos os idiomas."""

import csv
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
BASE = ANALISES / "triagem_catalogo_resumos_20261115.xlsx"
DECISOES = ANALISES / "revisao_bilingue_catalogo_20261115.csv"
BRUTO = RAIZ / "dados" / "brutos" / "catalogo-capes" / "catalogo-capes__catalogo-2024__20261108T150417015445-0300__CSV.csv"
SAIDA = ANALISES / "triagem_revisao_bilingue_catalogo_20261115.xlsx"
DATA = datetime(2026, 11, 15)
ANTERIORES = {
    "fe0ff0a0": "PNP",
    "bebf73ba": "PPP",
    "011e7d10": "PNN",
}


def ler_decisoes(caminho):
    campos = ["codigo", "id", "acao", "relacao", "eixos", "evidencia", "limites"]
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames != campos:
            raise ValueError("Colunas das decisões inesperadas.")
        linhas = list(leitor)
    if len(linhas) != 17 or len({x["codigo"] for x in linhas}) != 17 or len({x["id"] for x in linhas}) != 17:
        raise ValueError("Esperadas 17 avaliações únicas.")
    for item in linhas:
        if None in item or any(x is None for x in item.values()):
            raise ValueError("Linha malformada.")
        if not all(item[x] for x in ("codigo", "id", "acao", "evidencia", "limites")):
            raise ValueError("Avaliação incompleta.")
        if item["acao"] not in {"M", "E"} or item["relacao"] not in {"", "I"}:
            raise ValueError(f"Decisão inválida: {item['codigo']}")
        if item["eixos"] and (len(item["eixos"]) != 3 or any(x not in OPCOES["eixo"] for x in item["eixos"])):
            raise ValueError(f"Eixos inválidos: {item['codigo']}")
    if {x["codigo"] for x in linhas if x["acao"] == "E"} != {"5dec546a", "16954ac9", "401f22b2"}:
        raise ValueError("Exclusões inesperadas.")
    if {x["codigo"] for x in linhas if x["eixos"]} != set(ANTERIORES):
        raise ValueError("Revisões de eixos inesperadas.")
    if [(x["codigo"], x["relacao"]) for x in linhas if x["relacao"]] != [("011e7d10", "I")]:
        raise ValueError("Revisão de relação inesperada.")
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
    inventario = livro["Inventário inglês CAPES"]
    revisados_antes = {r[0] for r in list(inventario.values)[1:] if r[2] == "Sim"}
    if revisados_antes != {x["codigo"] for x in leituras}:
        raise ValueError("O lote não corresponde às avaliações anteriores do inventário.")
    indice_eixos = {}
    for numero in range(2, eixos.max_row + 1):
        chave = (eixos.cell(numero, ce["Código"]).value, eixos.cell(numero, ce["Eixo"]).value)
        if chave in indice_eixos:
            raise ValueError(f"Eixo duplicado: {chave}")
        indice_eixos[chave] = numero
    auditoria = livro.create_sheet("Revisão bilíngue CAPES")
    auditoria.append(["Código", "ID CAPES", "Triagem anterior", "Triagem revisada",
                      "Relação anterior", "Relação revisada", "Eixos anteriores", "Eixos revisados",
                      "Evidência", "Limites", "Data"])
    for item in leituras:
        codigo, fonte_id = item["codigo"], item["id"]
        if codigo not in indices:
            raise ValueError(f"Código ausente: {codigo}")
        celula = lambda campo: triagem.cell(indices[codigo], ct[campo])
        registro = originais[fonte_id]
        if (celula("Fonte").value != "Catálogo CAPES"
                or identificador(celula("Link da fonte").value) != fonte_id
                or celula("Título").value != registro["NM_PRODUCAO"]
                or celula("Autoria").value != registro["NM_DISCENTE"]
                or celula("Resumo").value != registro["DS_RESUMO"]
                or not registro["DS_ABSTRACT"]):
            raise ValueError(f"Identidade ou resumos divergentes: {codigo}")
        if (celula("Triagem de título e resumo").value != "Pendente"
                or celula("Decisão de elegibilidade").value != "Pendente"
                or celula("Motivo da exclusão").value is not None
                or not celula("Revisor").value):
            raise ValueError(f"Estado anterior requer conciliação: {codigo}")
        anteriores = []
        for eixo in EIXOS.values():
            chave = (codigo, eixo)
            if chave not in indice_eixos:
                raise ValueError(f"Eixo anterior ausente: {codigo}/{eixo}")
            anteriores.append(eixos.cell(indice_eixos[chave], ce["Estado"]).value)
        if item["eixos"]:
            esperado = [OPCOES["eixo"][x] for x in ANTERIORES[codigo]]
            if anteriores != esperado:
                raise ValueError(f"Eixos anteriores inesperados: {codigo}")
        relacao_anterior = celula("Relação com PIBID").value
        if codigo == "011e7d10" and relacao_anterior != "Relação substantiva com PIBID":
            raise ValueError("Relação anterior inesperada.")
        if codigo in {"5dec546a", "16954ac9"} and relacao_anterior != "Menção incidental":
            raise ValueError(f"Relação anterior inesperada: {codigo}")
        if codigo == "401f22b2":
            campos = ("NM_PRODUCAO", "DS_RESUMO", "DS_ABSTRACT", "DS_PALAVRA_CHAVE", "DS_KEYWORD")
            if any(tem_termo(registro[x]) for x in campos) or not tem_termo(registro["NM_PROJETO"]):
                raise ValueError("Evidência temática inesperada para 401f22b2.")
        if item["acao"] == "E":
            celula("Triagem de título e resumo").value = "Excluir"
            celula("Motivo da exclusão").value = "Outro" if codigo == "401f22b2" else "Sem relação substantiva com PIBID"
        if item["relacao"]:
            celula("Relação com PIBID").value = OPCOES["pibid"][item["relacao"]]
        novos = list(anteriores)
        evidencia = (item["evidencia"] + " Fonte: arquivo anual CAPES 2024, registro "
                     + fonte_id + ", campos DS_RESUMO e DS_ABSTRACT.")
        limites = (item["limites"] + " Avaliação preliminar e reversível; elegibilidade final pendente. "
                   "Ano de defesa não equivale a publicação; conferência não independente.")
        for campo, conteudo in {
            "Fontes das evidências": evidencia,
            "Material consultado": "Conferência dos resumos em português e inglês do arquivo CAPES original; " + (
                "projeto e palavras-chave também examinados." if codigo == "401f22b2" else "metadados bibliográficos confrontados."
            ),
            "Limitações e pendências": limites,
            "Observações": (
                "Revisão bilíngue 15/11/2026; decisões anteriores preservadas no histórico de auditoria."
                + (" Triagem de exclusão preliminar, reversível." if item["acao"] == "E" else "")
            ),
        }.items():
            acrescentar(celula(campo), conteudo)
        if item["eixos"]:
            for posicao, (eixo, estado) in enumerate(zip(EIXOS.values(), item["eixos"])):
                numero = indice_eixos[(codigo, eixo)]
                novo = OPCOES["eixo"][estado]
                if novo != anteriores[posicao]:
                    eixos.cell(numero, ce["Estado"]).value = novo
                    acrescentar(eixos.cell(numero, ce["Achado ou observação"]), "Revisão bilíngue: " + evidencia)
                    acrescentar(eixos.cell(numero, ce["Limites da evidência"]), limites)
                novos[posicao] = novo
        auditoria.append([codigo, fonte_id, "Pendente", celula("Triagem de título e resumo").value,
                          relacao_anterior, celula("Relação com PIBID").value, " | ".join(anteriores),
                          " | ".join(novos), evidencia, limites, DATA])
    anexar_tabela(auditoria, "RevisaoBilingueCAPES")
    livro["Limites da integração"].append([
        "17 avaliações CAPES anteriores confrontadas com resumos em ambos os idiomas; "
        "ver aba Revisão bilíngue CAPES. Sem validação independente nem decisão final."
    ])
    livro.save(saida)


if __name__ == "__main__":
    integrar(BASE, DECISOES, BRUTO, SAIDA)
    print(f"Base criada: {SAIDA}")
