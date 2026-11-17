"""Integra o lote de resumos e a conferência de datas UEL."""

import csv
import json
import re
import unicodedata
from copy import copy
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

from scripts.confirmar_duplicatas_amostra_20261115 import validar_par
from scripts.consultar_datas_uel_20261115 import texto
from scripts.integrar_autoavaliacao_20261115 import EIXOS, anexar_tabela, indice_unico
from scripts.preanalise_e_validacao_20261115 import cabecalhos
from scripts.preencher_autoavaliacao_20261115 import OPCOES


RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_temporal_artigos_20261115.xlsx"
DECISOES = ANALISES / "avaliacao_teses_lote_20261115.csv"
DATAS = ANALISES / "datas_uel_20261115.json"
SAIDA = ANALISES / "triagem_teses_datas_uel_20261115.xlsx"
DATA = datetime(2026, 11, 15)


def resumo_comparavel(valor):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", valor).casefold()).strip()


def instituicao_comparavel(valor):
    return texto(re.sub(r"\s*\([^()]*\)\s*", "", valor or ""))


def autores_comparaveis(valor):
    return sorted(texto(re.sub(r"\[[^]]+\]", "", valor or "")).split())


def ler_decisoes(caminho):
    campos = ["codigo", "par", "tipo_par", "pibid", "contexto", "eixos", "evidencia", "limites"]
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames != campos:
            raise ValueError("Colunas do lote inesperadas.")
        linhas = list(leitor)
    if len(linhas) != 29:
        raise ValueError("Esperadas 29 avaliações.")
    codigos = []
    for linha in linhas:
        if None in linha or any(v is None for v in linha.values()):
            raise ValueError("Linha malformada.")
        if not all(linha[c] for c in campos if c != "par"):
            raise ValueError(f"Avaliação incompleta: {linha['codigo']}")
        if linha["tipo_par"] not in {"N", "R", "C"} or bool(linha["par"]) != (linha["tipo_par"] != "N"):
            raise ValueError(f"Par inválido: {linha['codigo']}")
        for campo in ("pibid", "contexto"):
            if linha[campo] not in OPCOES[campo]:
                raise ValueError(f"Opção inválida: {linha['codigo']}, {campo}")
        if len(linha["eixos"]) != 3 or any(v not in OPCOES["eixo"] for v in linha["eixos"]):
            raise ValueError(f"Eixos inválidos: {linha['codigo']}")
        codigos.extend([linha["codigo"]] + ([linha["par"]] if linha["par"] else []))
    if len(codigos) != 35 or len(set(codigos)) != 35:
        raise ValueError("O lote deve conter 35 códigos distintos.")
    return linhas


def validar_par_fontes(triagem, col, n1, n2, codigo1, codigo2):
    valor = lambda n, nome: triagem.cell(n, col[nome]).value
    if {valor(n1, "Fonte"), valor(n2, "Fonte")} != {"BDTD", "Catálogo CAPES"}:
        raise ValueError(f"Fontes inesperadas: {codigo1}/{codigo2}")
    for campo, normalizar in (
        ("Título", texto), ("Autoria", autores_comparaveis), ("Tipo de produção", texto),
        ("Ano de defesa", texto), ("Instituição associada", instituicao_comparavel),
        ("Resumo", resumo_comparavel),
    ):
        a, b = valor(n1, campo), valor(n2, campo)
        if not a or not b or normalizar(a) != normalizar(b):
            raise ValueError(f"Material ou metadado divergente em {codigo1}/{codigo2}: {campo}")


def ler_datas(caminho):
    with caminho.open(encoding="utf-8") as arquivo:
        registros = json.load(arquivo)["registros"]
    if len(registros) != 31 or len({r["codigo"] for r in registros}) != 31:
        raise ValueError("Esperadas 31 consultas UEL distintas.")
    if any(r["situacao"] != "Identidade conferida" for r in registros):
        raise ValueError("Consultas UEL incompletas exigem conciliação.")
    return registros


def validar_datas(consulta, celula):
    codigo = consulta["codigo"]
    meta = consulta["metadados"]
    if (str(celula("Ano de defesa").value) != "2024" or celula("Ano de publicação").value is not None
            or celula("Publicação em 2020–2026").value != "Só ano de defesa disponível"
            or consulta["url_identificador"] != celula("Link da fonte").value):
        raise ValueError(f"Estado temporal anterior inesperado: {codigo}")
    titulos, autores = meta["dc.title"], meta["dc.contributor.author"]
    if (len(titulos) != 1 or texto(titulos[0]) != texto(celula("Título").value)
            or len(autores) != 1 or autores_comparaveis(autores[0]) != autores_comparaveis(celula("Autoria").value)
            or consulta["url_identificador"] not in meta["dc.identifier.uri"]):
        raise ValueError(f"Identidade da consulta não corresponde à base: {codigo}")
    defesas, emissao = meta["dc.date.defesa"], meta["dc.date.issued"]
    if len(defesas) == 1 and not emissao:
        try:
            defesa = datetime.strptime(defesas[0], "%d.%m.%Y")
        except ValueError as erro:
            raise ValueError(f"Data de defesa inválida: {codigo}") from erro
        if not 2007 <= defesa.year < 2024:
            raise ValueError(f"Ano de defesa exige conciliação: {codigo}")
        return str(defesa.year), None
    if codigo == "fe0699e5" and not defesas and emissao == ["2024-03-28"]:
        return None, 2024
    raise ValueError(f"Datas UEL incompletas ou conflitantes: {codigo}")


def acrescentar(celula, novo):
    valor = f"{celula.value}\n{novo}" if celula.value else novo
    if len(valor) > 32767:
        raise ValueError(f"Texto excede limite do Excel: {celula.coordinate}")
    celula.value = valor


def integrar(base, decisoes, datas, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    leituras, consultas = ler_decisoes(decisoes), ler_datas(datas)
    livro = load_workbook(base)
    triagem, eixos = livro["Triagem"], livro["Eixos de análise"]
    ct, ce = cabecalhos(triagem), cabecalhos(eixos)
    indices = indice_unico(triagem, ct["Código"], 1317)
    existentes = {}
    for n in range(2, eixos.max_row + 1):
        chave = (eixos.cell(n, ce["Código"]).value, eixos.cell(n, ce["Eixo"]).value)
        if chave in existentes:
            raise ValueError(f"Eixo duplicado: {chave}")
        existentes[chave] = n

    auditoria_data = livro.create_sheet("Datas UEL conferidas")
    auditoria_data.append(["Código", "Ano de defesa anterior", "Defesa na UEL", "Ano de defesa integrado",
                           "Ano de publicação anterior", "Data de emissão UEL", "Ano de publicação integrado",
                           "Data de incorporação UEL", "Consulta", "Decisão e limites"])
    alterados_defesa = 0
    for consulta in consultas:
        codigo = consulta["codigo"]
        if codigo not in indices:
            raise ValueError(f"Registro UEL ausente: {codigo}")
        numero = indices[codigo]
        celula = lambda campo: triagem.cell(numero, ct[campo])
        defesa, publicacao = validar_datas(consulta, celula)
        meta = consulta["metadados"]
        antes_defesa, antes_publicacao = celula("Ano de defesa").value, celula("Ano de publicação").value
        url = consulta["url_identificador"]
        if defesa:
            celula("Ano de defesa").value = defesa
            alterados_defesa += 1
            decisao = (
                f"BDTD informava defesa 2024; UEL informa defesa em {meta['dc.date.defesa'][0]}. "
                "O ano de defesa foi corrigido; não foi estabelecido ano de publicação."
            )
        else:
            celula("Ano de publicação").value = publicacao
            celula("Publicação em 2020–2026").value = OPCOES["periodo"]["C"]
            decisao = (
                "UEL informa data de emissão 28/03/2024; publicação em 2024 registrada. "
                "A defesa 2024 informada na BDTD não foi confirmada nos metadados UEL."
            )
        fonte = f"Metadados UEL consultados em 15/11/2026: {url}; API: {consulta['url_api']}."
        acrescentar(celula("Fontes das evidências"), fonte + " " + decisao)
        acrescentar(celula("Limitações e pendências"), decisao)
        acrescentar(celula("Observações"), "Conferência temporal UEL: " + decisao)
        auditoria_data.append([
            codigo, antes_defesa, "; ".join(meta["dc.date.defesa"]) or "Não informada",
            celula("Ano de defesa").value, antes_publicacao, "; ".join(meta["dc.date.issued"]) or "Não informada",
            celula("Ano de publicação").value, "; ".join(meta["dc.date.accessioned"]) or "Não informada",
            fonte, decisao,
        ])
    if alterados_defesa != 30:
        raise ValueError(f"Esperadas 30 correções de defesa; encontradas {alterados_defesa}.")

    auditoria = livro.create_sheet("Lote teses recente")
    auditoria.append(["Código", "Par candidato", "Tipo de par", "PIBID anterior", "PIBID revisado",
                      "Contexto anterior", "Contexto revisado", "Evidência", "Limites"])
    for item in leituras:
        codigo, par = item["codigo"], item["par"]
        if codigo not in indices or (par and par not in indices):
            raise ValueError(f"Registro ausente: {codigo}/{par}")
        n1 = indices[codigo]
        if par:
            n2 = indices[par]
            if item["tipo_par"] == "R":
                validar_par(triagem, ct, n1, n2, codigo, par)
                for campo in ("Resumo", "Palavras-chave"):
                    if triagem.cell(n1, ct[campo]).value != triagem.cell(n2, ct[campo]).value:
                        raise ValueError(f"Conteúdo divergente no par {codigo}/{par}: {campo}")
                if any(triagem.cell(n, ct["Duplicidade"]).value != "Duplicata confirmada" for n in (n1, n2)):
                    raise ValueError(f"Par de repositório não confirmado: {codigo}/{par}")
            else:
                validar_par_fontes(triagem, ct, n1, n2, codigo, par)
        for atual, outro in [(codigo, par)] + ([(par, codigo)] if par else []):
            n = indices[atual]
            celula = lambda campo: triagem.cell(n, ct[campo])
            if (celula("Relação com PIBID").value != "Incerto"
                    or celula("Triagem de título e resumo").value != "Pendente"
                    or celula("Revisor").value is not None):
                raise ValueError(f"Estado anterior requer conciliação: {atual}")
            if celula("Produção acadêmica").value != "Sim":
                raise ValueError(f"Tipo acadêmico não estabelecido: {atual}")
            anterior_pibid, anterior_contexto = celula("Relação com PIBID").value, celula("Contexto de Goiás").value
            contexto = OPCOES["contexto"][item["contexto"]]
            if anterior_contexto == "Pesquisa realizada em Goiás" and contexto != anterior_contexto:
                raise ValueError(f"Contexto positivo anterior requer conciliação: {atual}")
            celula("Relação com PIBID").value = OPCOES["pibid"][item["pibid"]]
            celula("Contexto de Goiás").value = contexto
            celula("Decisão de elegibilidade").value = "Pendente"
            evidencia = item["evidencia"] + " Fonte: título, resumo e metadados locais desta linha."
            limites = item["limites"] + (
                " Extração preliminar não independente; elegibilidade e duplicidade não estão resolvidas "
                "salvo indicação específica. Ano de defesa não equivale a publicação."
            )
            for campo, valor in {
                "Evidência do contexto": evidencia,
                "Fontes das evidências": evidencia,
                "Material consultado": "Título, resumo e metadados locais; eventual consulta temporal à UEL indicada separadamente.",
                "Limitações e pendências": limites,
                "Observações": (
                    "Leitura preliminar não independente; triagem e elegibilidade final permanecem pendentes."
                    + (f" Comparar com {outro}; " + (
                        "par já confirmado." if item["tipo_par"] == "R" else "candidato entre fontes, não confirmado."
                    ) if outro else "")
                ),
            }.items():
                acrescentar(celula(campo), valor)
            celula("Revisor").value = "Análise computacional preliminar não independente"
            celula("Data da triagem").value = DATA
            for eixo, estado in zip(EIXOS.values(), item["eixos"]):
                if (atual, eixo) in existentes:
                    raise ValueError(f"Eixo anterior requer conciliação: {atual}/{eixo}")
                num = eixos.max_row + 1
                for coluna in range(1, eixos.max_column + 1):
                    eixos.cell(num, coluna)._style = copy(eixos.cell(2, coluna)._style)
                preenchimento = {
                    "Código": atual, "Título": celula("Título").value, "Eixo": eixo,
                    "Estado": OPCOES["eixo"][estado], "Achado ou observação": evidencia,
                    "Trecho ou localização": "Síntese e localização no campo de evidência.",
                    "Tipo de fonte": "Título, resumo e metadados locais",
                    "Link ou referência consultada": celula("Link da fonte").value or "Metadados locais da planilha",
                    "Limites da evidência": limites, "Revisor": "Análise computacional preliminar não independente",
                    "Data": DATA,
                }
                for campo, valor in preenchimento.items():
                    eixos.cell(num, ce[campo]).value = valor
                existentes[(atual, eixo)] = num
            auditoria.append([atual, outro or "Não identificado", item["tipo_par"], anterior_pibid,
                              celula("Relação com PIBID").value, anterior_contexto, contexto, evidencia, limites])

    tabela = eixos.tables["Eixos"]
    tabela.ref = f"A1:K{eixos.max_row}"
    if tabela.autoFilter is not None:
        tabela.autoFilter.ref = tabela.ref
    if len(eixos.data_validations.dataValidation) != 1:
        raise ValueError("Validação de eixos inesperada.")
    eixos.data_validations.dataValidation[0].sqref = f"D2:D{eixos.max_row}"
    anexar_tabela(auditoria_data, "DatasUELConferidas")
    anexar_tabela(auditoria, "LoteTesesRecente")
    livro["Limites da integração"].append([
        "35 linhas lidas em lote preliminar e datas de 31 registros UEL conferidas; "
        "ver abas Lote teses recente e Datas UEL conferidas. Sem validação independente nem decisão final."
    ])
    livro.save(saida)


if __name__ == "__main__":
    integrar(BASE, DECISOES, DATAS, SAIDA)
    print(f"Base criada: {SAIDA}")
