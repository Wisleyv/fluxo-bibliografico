"""Integra leituras de pares já confirmados, sem decidir elegibilidade."""

import csv
from copy import copy
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

from scripts.confirmar_duplicatas_amostra_20261115 import validar_par
from scripts.integrar_autoavaliacao_20261115 import EIXOS, anexar_tabela, indice_unico
from scripts.integrar_teses_e_datas_uel_20261115 import acrescentar
from scripts.preanalise_e_validacao_20261115 import cabecalhos
from scripts.preencher_autoavaliacao_20261115 import OPCOES


RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_teses_datas_uel_20261115.xlsx"
DECISOES = ANALISES / "avaliacao_pares_pendentes_20261115.csv"
SAIDA = ANALISES / "triagem_pares_pendentes_20261115.xlsx"
DATA = datetime(2026, 11, 15)
REVISOR = "Análise computacional preliminar não independente"


def ler_decisoes(caminho):
    campos = ["codigo", "par", "pibid", "contexto", "eixos", "evidencia", "limites"]
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames != campos:
            raise ValueError("Colunas do lote inesperadas.")
        linhas = list(leitor)
    if len(linhas) != 19:
        raise ValueError("Esperadas 19 avaliações de pares.")
    codigos = []
    for linha in linhas:
        if None in linha or any(not v for v in linha.values()):
            raise ValueError("Avaliação incompleta ou malformada.")
        for campo in ("pibid", "contexto"):
            if linha[campo] not in OPCOES[campo]:
                raise ValueError(f"Opção inválida: {linha['codigo']}, {campo}")
        if len(linha["eixos"]) != 3 or any(v not in OPCOES["eixo"] for v in linha["eixos"]):
            raise ValueError(f"Eixos inválidos: {linha['codigo']}")
        codigos.extend((linha["codigo"], linha["par"]))
    if len(set(codigos)) != 38:
        raise ValueError("O lote deve conter 38 códigos distintos.")
    return linhas


def integrar(base, decisoes, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    entradas = ler_decisoes(decisoes)
    livro = load_workbook(base)
    triagem, eixos = livro["Triagem"], livro["Eixos de análise"]
    ct, ce = cabecalhos(triagem), cabecalhos(eixos)
    indices = indice_unico(triagem, ct["Código"], 1317)
    existentes = set()
    for numero in range(2, eixos.max_row + 1):
        chave = (eixos.cell(numero, ce["Código"]).value, eixos.cell(numero, ce["Eixo"]).value)
        if chave in existentes:
            raise ValueError(f"Eixo duplicado: {chave}")
        existentes.add(chave)

    auditoria = livro.create_sheet("Pares pendentes lidos")
    auditoria.append(["Código", "Par confirmado", "PIBID anterior", "PIBID revisado",
                      "Contexto anterior", "Contexto revisado", "Evidência", "Limites"])
    for item in entradas:
        codigo, par = item["codigo"], item["par"]
        if codigo not in indices or par not in indices:
            raise ValueError(f"Código ausente: {codigo}/{par}")
        n1, n2 = indices[codigo], indices[par]
        validar_par(triagem, ct, n1, n2, codigo, par)
        for campo in ("Resumo", "Palavras-chave"):
            if triagem.cell(n1, ct[campo]).value != triagem.cell(n2, ct[campo]).value:
                raise ValueError(f"Conteúdo divergente em {codigo}/{par}: {campo}")
        for atual, outro, numero in ((codigo, par, n1), (par, codigo, n2)):
            celula = lambda campo: triagem.cell(numero, ct[campo])
            if (celula("Duplicidade").value != "Duplicata confirmada"
                    or celula("Relação com PIBID").value != "Incerto"
                    or celula("Contexto de Goiás").value != "Incerto"
                    or celula("Triagem de título e resumo").value != "Pendente"
                    or celula("Decisão de elegibilidade").value != "Não iniciada"
                    or celula("Revisor").value is not None):
                raise ValueError(f"Estado anterior requer conciliação: {atual}")
            anterior_pibid, anterior_contexto = celula("Relação com PIBID").value, celula("Contexto de Goiás").value
            celula("Relação com PIBID").value = OPCOES["pibid"][item["pibid"]]
            celula("Contexto de Goiás").value = OPCOES["contexto"][item["contexto"]]
            celula("Decisão de elegibilidade").value = "Pendente"
            evidencia = item["evidencia"] + " Fonte: título, campo de resumo, palavras-chave e metadados locais."
            limites = (item["limites"] + " A ausência de menção não prova ausência no estudo; "
                       "ano de defesa não equivale a publicação. Leitura preliminar não independente; "
                       "elegibilidade pendente.")
            for campo, conteudo in {
                "Evidência do contexto": evidencia,
                "Fontes das evidências": evidencia,
                "Material consultado": "Título, campo de resumo, palavras-chave e metadados locais.",
                "Limitações e pendências": limites,
                "Observações": f"Leitura preliminar não independente; mesmo conteúdo do par confirmado {outro}. Sem escolha de principal.",
            }.items():
                acrescentar(celula(campo), conteudo)
            celula("Revisor").value = REVISOR
            celula("Data da triagem").value = DATA
            for eixo, estado in zip(EIXOS.values(), item["eixos"]):
                chave = (atual, eixo)
                if chave in existentes:
                    raise ValueError(f"Eixo anterior requer conciliação: {atual}/{eixo}")
                linha = eixos.max_row + 1
                for coluna in range(1, eixos.max_column + 1):
                    eixos.cell(linha, coluna)._style = copy(eixos.cell(2, coluna)._style)
                valores = {
                    "Código": atual, "Título": celula("Título").value, "Eixo": eixo,
                    "Estado": OPCOES["eixo"][estado], "Achado ou observação": evidencia,
                    "Trecho ou localização": "Síntese e localização no campo de evidência.",
                    "Tipo de fonte": "Metadados e material local",
                    "Link ou referência consultada": celula("Link da fonte").value,
                    "Limites da evidência": limites, "Revisor": REVISOR, "Data": DATA,
                }
                for campo, conteudo in valores.items():
                    eixos.cell(linha, ce[campo]).value = conteudo
                existentes.add(chave)
            auditoria.append([atual, outro, anterior_pibid, celula("Relação com PIBID").value,
                              anterior_contexto, celula("Contexto de Goiás").value, evidencia, limites])

    tabela = eixos.tables["Eixos"]
    tabela.ref = f"A1:K{eixos.max_row}"
    if tabela.autoFilter is not None:
        tabela.autoFilter.ref = tabela.ref
    if len(eixos.data_validations.dataValidation) != 1:
        raise ValueError("Validação de eixos inesperada.")
    eixos.data_validations.dataValidation[0].sqref = f"D2:D{eixos.max_row}"
    anexar_tabela(auditoria, "ParesPendentesLidos")
    livro["Limites da integração"].append([
        "19 pares confirmados lidos em 38 linhas; ver aba Pares pendentes lidos. "
        "Sem seleção de registro principal, validação independente ou decisão final."
    ])
    livro.save(saida)


if __name__ == "__main__":
    integrar(BASE, DECISOES, SAIDA)
    print(f"Base criada: {SAIDA}")
