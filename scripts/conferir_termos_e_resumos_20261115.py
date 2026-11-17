"""Reavalia pares sem termos locais, com controle de fontes e resumo incompleto."""

import csv
import io
import json
import re
import zipfile
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

from scripts.confirmar_duplicatas_amostra_20261115 import validar_par
from scripts.integrar_autoavaliacao_20261115 import EIXOS, anexar_tabela, indice_unico
from scripts.integrar_pares_pendentes_20261115 import ler_decisoes
from scripts.integrar_teses_e_datas_uel_20261115 import acrescentar
from scripts.preanalise_e_validacao_20261115 import cabecalhos, texto_normalizado
from scripts.preencher_autoavaliacao_20261115 import OPCOES


RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_pares_pendentes_20261115.xlsx"
DECISOES = ANALISES / "avaliacao_pares_pendentes_20261115.csv"
FONTES_UNB = ANALISES / "conferencia_resumos_unb_20261115.json"
NACIONAL = RAIZ / "dados" / "brutos" / "bdtd" / "bdtd__busca-nacional__20261108T113708926870-0300__CSV.csv"
REGIONAL = RAIZ / "dados" / "brutos" / "bdtd" / "bdtd__goias-descriptors__20261108T125842275582-0300__ZIP.zip"
SAIDA = ANALISES / "triagem_conferencia_termos_20261115.xlsx"
DATA = datetime(2026, 11, 15)
TERMO = re.compile(r"pibid|programa\s+institucional\s+de\s+bolsas?\s+de\s+iniciacao\s+a\s+docencia")


def tem_termo(valor):
    normalizado = re.sub(r"[^a-z0-9]+", " ", texto_normalizado(valor or ""))
    return bool(TERMO.search(normalizado))


def ler_exportacoes():
    with NACIONAL.open(encoding="utf-8-sig", newline="") as arquivo:
        nacional = list(csv.DictReader(arquivo))
    with zipfile.ZipFile(REGIONAL) as arquivo:
        membros = [nome for nome in arquivo.namelist() if nome.lower().endswith(".csv")]
        if len(membros) != 1:
            raise ValueError("Arquivo regional deve conter um CSV.")
        with arquivo.open(membros[0]) as bruto:
            with io.TextIOWrapper(bruto, encoding="utf-8-sig", newline="") as texto:
                regional = list(csv.DictReader(texto))
    return nacional, regional


def conferir_exportacoes(celula, exportacoes):
    for registros in exportacoes:
        candidatos = [r for r in registros if r["Título"] == celula("Título").value
                      and r["Autor(a)"] == celula("Autoria").value
                      and r["Link de acesso"] == celula("Link da fonte").value]
        if len(candidatos) != 1:
            raise ValueError(f"Exportação BDTD ausente ou ambígua: {celula('Código').value}")
        registro = candidatos[0]
        if registro["Resumo"] != celula("Resumo").value:
            raise ValueError(f"Resumo divergente da exportação: {celula('Código').value}")
        campos = ("Título", "Resumo", "Resumo em Português", "Resumo em Inglês",
                  "Assuntos em português", "Assuntos em inglês")
        if any(tem_termo(registro[campo]) for campo in campos):
            raise ValueError(f"Termo temático presente na exportação: {celula('Código').value}")


def integrar(base, decisoes, fontes_unb, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    pares = [x for x in ler_decisoes(decisoes) if x["pibid"] == "I"]
    if len(pares) != 16:
        raise ValueError("Esperados 16 pares inicialmente incertos.")
    with fontes_unb.open(encoding="utf-8") as arquivo:
        fontes = json.load(arquivo)
    if fontes["data_consulta"] != "2026-11-15":
        raise ValueError("Data das consultas inesperada.")
    unb = {x["codigo"]: x for x in fontes["registros"]}
    if set(unb) != {"a3e7321c", "e92d970d"}:
        raise ValueError("Consultas UnB incompletas.")
    exportacoes = ler_exportacoes()
    livro = load_workbook(base)
    triagem, eixos = livro["Triagem"], livro["Eixos de análise"]
    ct, ce = cabecalhos(triagem), cabecalhos(eixos)
    indices = indice_unico(triagem, ct["Código"], 1317)
    indices_eixos = {}
    for numero in range(2, eixos.max_row + 1):
        chave = (eixos.cell(numero, ce["Código"]).value, eixos.cell(numero, ce["Eixo"]).value)
        if chave in indices_eixos:
            raise ValueError(f"Eixo duplicado: {chave}")
        indices_eixos[chave] = numero
    auditoria = livro.create_sheet("Conferência termos e UnB")
    auditoria.append(["Código", "Par confirmado", "Tratamento preliminar", "Fonte e evidência",
                      "Limites", "Triagem anterior", "Triagem revisada", "Período anterior", "Período revisado"])
    for item in pares:
        codigo, par = item["codigo"], item["par"]
        n1, n2 = indices[codigo], indices[par]
        validar_par(triagem, ct, n1, n2, codigo, par)
        for campo in ("Resumo", "Palavras-chave"):
            if triagem.cell(n1, ct[campo]).value != triagem.cell(n2, ct[campo]).value:
                raise ValueError(f"Conteúdo divergente em {codigo}/{par}: {campo}")
        for atual, outro, numero in ((codigo, par, n1), (par, codigo, n2)):
            celula = lambda campo: triagem.cell(numero, ct[campo])
            if (celula("Duplicidade").value != "Duplicata confirmada"
                    or celula("Relação com PIBID").value != "Incerto"
                    or celula("Triagem de título e resumo").value != "Pendente"
                    or celula("Decisão de elegibilidade").value != "Pendente"
                    or celula("Motivo da exclusão").value is not None
                    or celula("Publicação em 2020–2026").value != "Só ano de defesa disponível"):
                raise ValueError(f"Estado anterior requer conciliação: {atual}")
            conferir_exportacoes(celula, exportacoes)
            if any(tem_termo(celula(campo).value) for campo in ("Título", "Resumo", "Palavras-chave")):
                raise ValueError(f"Termo temático presente: {atual}")
            periodo_anterior = celula("Publicação em 2020–2026").value
            consulta = unb.get(codigo)
            if consulta:
                if (consulta["par"] != par or consulta["titulo"] != celula("Título").value
                        or consulta["autoria"] != celula("Autoria").value
                        or len(celula("Resumo").value or "") > 200):
                    raise ValueError(f"Identidade ou material UnB exige conciliação: {atual}")
                celula("Relação com PIBID").value = OPCOES["pibid"]["S"]
                celula("Contexto de Goiás").value = OPCOES["contexto"]["G"]
                if codigo == "a3e7321c":
                    if consulta["data_emissao"] != "2017-05-26" or consulta["ano_na_referencia"] != 2017:
                        raise ValueError("Data UnB inesperada.")
                    celula("Ano de publicação").value = 2017
                    celula("Publicação em 2020–2026").value = OPCOES["periodo"]["F"]
                    celula("Triagem de título e resumo").value = "Excluir"
                    celula("Motivo da exclusão").value = "Fora do período"
                    tratamento = "PIBID e Goiás confirmados; exclusão preliminar do recorte goiano por período."
                else:
                    if consulta["data_emissao"] != "2020-06-29" or consulta["ano_na_referencia"] != 2019:
                        raise ValueError("Data UnB inesperada.")
                    celula("Publicação em 2020–2026").value = OPCOES["periodo"]["I"]
                    tratamento = "PIBID e Goiás confirmados; período incerto, sem exclusão."
                evidencia = consulta["evidencia"] + " Fonte: resumo do repositório UnB, consulta de 15/11/2026: " + consulta["url"]
                limites = consulta["limites"] + " Leitura não independente; elegibilidade final pendente."
                material = "Resumo e metadados públicos do repositório UnB; exportações BDTD preservadas."
                for eixo, estado in zip(EIXOS.values(), consulta["eixos"]):
                    chave = (atual, eixo)
                    if chave not in indices_eixos:
                        raise ValueError(f"Eixo anterior ausente: {atual}/{eixo}")
                    linha = indices_eixos[chave]
                    campo_eixo = lambda nome: eixos.cell(linha, ce[nome])
                    if campo_eixo("Estado").value != "Não verificável":
                        raise ValueError(f"Eixo anterior exige conciliação: {atual}/{eixo}")
                    campo_eixo("Estado").value = OPCOES["eixo"][estado]
                    acrescentar(campo_eixo("Achado ou observação"), evidencia)
                    acrescentar(campo_eixo("Limites da evidência"), limites)
                    campo_eixo("Trecho ou localização").value = "Resumo na página pública do repositório UnB."
                    campo_eixo("Tipo de fonte").value = "Resumo e metadados do repositório UnB"
                    campo_eixo("Link ou referência consultada").value = consulta["url"]
            else:
                if len(celula("Resumo").value or "") < 500:
                    raise ValueError(f"Resumo insuficiente para exclusão preliminar: {atual}")
                celula("Triagem de título e resumo").value = "Excluir"
                celula("Motivo da exclusão").value = "Outro"
                tratamento = "Exclusão preliminar pelo critério de termos nos metadados disponíveis."
                evidencia = (
                    "Título, resumo substantivo e palavras-chave nas exportações BDTD nacional e regional "
                    "não apresentam PIBID nem a expressão completa do programa; leitura temática registrada no lote anterior."
                )
                limites = (
                    "Exclusão operacional preliminar, reversível se outra fonte demonstrar termo ou pertinência. "
                    "Não comprova ausência do programa no texto integral nem valida campos não exportados. "
                    "Não usar no panorama nacional sem reavaliar o critério; elegibilidade final pendente."
                )
                material = "Título, resumo e palavras-chave na base local e exportações BDTD nacional e regional."
            for campo, conteudo in {
                "Fontes das evidências": evidencia,
                "Material consultado": material,
                "Limitações e pendências": limites,
                "Observações": f"Conferência temática 15/11/2026: {tratamento} Par {outro}.",
            }.items():
                acrescentar(celula(campo), conteudo)
            if consulta:
                acrescentar(celula("Evidência do contexto"), evidencia)
            celula("Revisor").value = "Conferência computacional e documental não independente"
            celula("Data da triagem").value = DATA
            auditoria.append([atual, outro, tratamento, evidencia, limites, "Pendente",
                              celula("Triagem de título e resumo").value, periodo_anterior,
                              celula("Publicação em 2020–2026").value])
    anexar_tabela(auditoria, "ConferenciaTermosUnB")
    livro["Limites da integração"].append([
        "16 pares reavaliados: 14 excluídos preliminarmente por ausência de termos nos metadados locais; "
        "dois têm resumo relevante na UnB, um com exclusão temporal preliminar e outro com período incerto. "
        "Ver aba Conferência termos e UnB; sem validação independente nem decisão final."
    ])
    livro.save(saida)


if __name__ == "__main__":
    integrar(BASE, DECISOES, FONTES_UNB, SAIDA)
    print(f"Base criada: {SAIDA}")
