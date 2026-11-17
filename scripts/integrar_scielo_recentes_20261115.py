"""Integra leitura de artigos recentes e conferência de pares de repositório."""

import csv
import json
from collections import defaultdict
from copy import copy
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from openpyxl import load_workbook

from scripts.confirmar_duplicatas_amostra_20261115 import IDENTIDADE, validar_par
from scripts.consultar_metadados_scielo_20261115 import nome_comparavel
from scripts.integrar_autoavaliacao_20261115 import EIXOS, anexar_tabela, indice_unico
from scripts.preanalise_e_validacao_20261115 import ano, cabecalhos
from scripts.preencher_autoavaliacao_20261115 import OPCOES
from scripts.preparar_piloto_20261115 import normalizar_doi


RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_lote_goias_20261115.xlsx"
DECISOES = ANALISES / "avaliacao_scielo_recentes_20261115.csv"
PARES = ANALISES / "pares_repositorio_recentes_20261115.csv"
METADADOS = ANALISES / "metadados_scielo_recentes_20261115.json"
COMPLEMENTO = ANALISES / "metadados_scielo_recentes_complemento_20261115.json"
SAIDA = ANALISES / "triagem_scielo_recentes_20261115.xlsx"
DATA = datetime(2026, 11, 15)


def ler_csv(caminho, campos, quantidade):
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames != campos:
            raise ValueError(f"Colunas inesperadas em {caminho}")
        linhas = list(leitor)
    if len(linhas) != quantidade or any(None in linha or any(v is None or not v.strip() for v in linha.values()) for linha in linhas):
        raise ValueError(f"Quantidade ou conteúdo inválido em {caminho}")
    return linhas


def ler_metadados(arquivo, complemento):
    with arquivo.open(encoding="utf-8") as fonte:
        originais = json.load(fonte)["registros"]
    with complemento.open(encoding="utf-8") as fonte:
        adicionais = json.load(fonte)["registros"]
    if len(originais) != 28 or len(adicionais) != 3:
        raise ValueError("Quantidade inesperada de consultas SciELO.")
    indice = {}
    falhas = set()
    for item in originais:
        codigo = item["codigo"]
        if codigo in indice or codigo in falhas:
            raise ValueError(f"Consulta repetida: {codigo}")
        if item["situacao"] == "Conferido":
            indice[codigo] = item
        elif item["situacao"] == "Falha na consulta":
            falhas.add(codigo)
        else:
            raise ValueError(f"Divergência de metadados exige conciliação: {codigo}")
    for item in adicionais:
        codigo = item["codigo"]
        if codigo not in falhas or codigo in indice:
            raise ValueError(f"Complemento inesperado: {codigo}")
        indice[codigo] = item
    if set(indice) != {item["codigo"] for item in originais}:
        raise ValueError("Há falhas sem complemento.")
    return indice


def checar_metadados(codigo, celula, consulta):
    meta = consulta["metadados"]
    doi, autores = meta.get("citation_doi", []), meta.get("citation_author", [])
    afiliacoes = meta.get("citation_author_affiliation", [])
    data = meta.get("citation_publication_date", [])
    tipos = meta.get("citation_article_type", [])
    if len(doi) != 1 or normalizar_doi(doi[0]) != normalizar_doi(celula("DOI").value):
        raise ValueError(f"DOI divergente: {codigo}")
    nomes = str(celula("Autoria").value or "").split(" | ")
    if sorted(nome_comparavel(a) for a in autores) != sorted(nome_comparavel(a) for a in nomes):
        raise ValueError(f"Autoria divergente: {codigo}")
    if len(data) != 1 or not data[0].startswith(str(celula("Ano de publicação").value)):
        raise ValueError(f"Publicação divergente: {codigo}")
    if len(tipos) != 1 or tipos[0] not in {"research-article", "case-report"}:
        raise ValueError(f"Tipo de artigo não conferido: {codigo}")
    if not afiliacoes or any(not nome.strip() for nome in afiliacoes):
        raise ValueError(f"Afiliações indisponíveis: {codigo}")
    return list(dict.fromkeys(afiliacoes))


def validar_par_com_identificador(triagem, col, n1, n2, codigo1, codigo2):
    campo_link = triagem.cell(n1, col["Link da fonte"]).value
    if "||" not in str(campo_link):
        return validar_par(triagem, col, n1, n2, codigo1, codigo2)
    for campo in IDENTIDADE:
        valor = triagem.cell(n1, col[campo]).value
        if not valor or valor != triagem.cell(n2, col[campo]).value:
            raise ValueError(f"Dados diferentes ou ausentes para {codigo1}/{codigo2}: {campo}")
    partes = [parte.strip() for parte in campo_link.split("||")]
    if len(partes) != 3 or not partes[0]:
        raise ValueError(f"Identificador composto não reconhecido: {codigo1}")
    repositorio, doi = map(urlparse, partes[1:])
    if (repositorio.scheme not in {"http", "https"} or not repositorio.netloc
            or not repositorio.path.startswith("/handle/") or not repositorio.path[len("/handle/"):].strip("/")
            or doi.scheme not in {"http", "https"} or doi.netloc.lower() not in {"doi.org", "dx.doi.org"}
            or not doi.path.strip("/")):
        raise ValueError(f"Identificadores compostos inválidos: {codigo1}")
    return partes[1]


def integrar(base, decisoes, pares, metadados, complemento, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    leituras = ler_csv(decisoes, ["codigo", "pibid", "contexto", "afiliacao", "triagem", "eixos", "evidencia", "limites"], 28)
    pares_lidos = ler_csv(pares, ["codigo_1", "codigo_2"], 23)
    consultas = ler_metadados(metadados, complemento)
    codigos = [item["codigo"] for item in leituras]
    codigos_pares = [p[chave] for p in pares_lidos for chave in ("codigo_1", "codigo_2")]
    if len(set(codigos)) != 28 or set(codigos) != set(consultas):
        raise ValueError("Os artigos e as consultas devem ter os mesmos 28 códigos únicos.")
    if len(set(codigos_pares)) != 46 or set(codigos) & set(codigos_pares):
        raise ValueError("Os códigos dos pares devem ser distintos entre si e do lote SciELO.")

    livro = load_workbook(base)
    triagem, eixos = livro["Triagem"], livro["Eixos de análise"]
    ct, ce = cabecalhos(triagem), cabecalhos(eixos)
    indices = indice_unico(triagem, ct["Código"], 1317)
    existentes = {}
    grupos = defaultdict(list)
    for numero in range(2, triagem.max_row + 1):
        chave = tuple(triagem.cell(numero, ct[c]).value for c in ("Título", "Autoria", "Tipo de produção", "Ano de defesa"))
        if all(chave):
            grupos[chave].append(numero)
    for numero in range(2, eixos.max_row + 1):
        chave = (eixos.cell(numero, ce["Código"]).value, eixos.cell(numero, ce["Eixo"]).value)
        if chave in existentes:
            raise ValueError(f"Eixo duplicado: {chave}")
        existentes[chave] = numero

    auditoria = livro.create_sheet("Lote SciELO recente")
    auditoria.append(["Código", "PIBID anterior", "PIBID revisado", "Contexto anterior", "Contexto revisado",
                      "Afiliação anterior", "Afiliação revisada", "Triagem anterior", "Triagem revisada",
                      "Evidência", "Afiliações listadas", "Fonte primária", "Limites"])
    for item in leituras:
        codigo = item["codigo"]
        if codigo not in indices:
            raise ValueError(f"Artigo ausente: {codigo}")
        for campo in ("pibid", "contexto", "afiliacao", "triagem"):
            if item[campo] not in OPCOES[campo]:
                raise ValueError(f"Opção inválida em {codigo}: {campo}")
        if len(item["eixos"]) != 3 or any(v not in OPCOES["eixo"] for v in item["eixos"]):
            raise ValueError(f"Eixos inválidos: {codigo}")
        n = indices[codigo]
        celula = lambda campo: triagem.cell(n, ct[campo])
        if celula("Fonte").value != "SciELO" or celula("Relação com PIBID").value != "Incerto" or celula("Triagem de título e resumo").value != "Pendente":
            raise ValueError(f"Estado anterior inesperado: {codigo}")
        if celula("Afiliações de autoria").value:
            raise ValueError(f"Afiliação anterior requer conciliação: {codigo}")
        ano_publicacao = ano(celula("Ano de publicação").value)
        if ano_publicacao is None or not 2020 <= ano_publicacao <= 2026:
            raise ValueError(f"Ano fora do lote: {codigo}")
        if item["triagem"] == "E":
            raise ValueError(f"Exclusão regional não sustentada neste lote: {codigo}")
        if item["triagem"] == "A" and not (
            item["pibid"] in {"T", "S"} and (item["contexto"] == "G" or item["afiliacao"] == "S")
            and celula("Publicação em 2020–2026").value == OPCOES["periodo"]["C"]
        ):
            raise ValueError(f"Avanço sem requisitos suficientes: {codigo}")
        instituicoes = checar_metadados(codigo, celula, consultas[codigo])
        if item["afiliacao"] == "S" and (codigo != "910fa3c6" or instituicoes != ["Universidade Estadual de Goiás (UEG)"]):
            raise ValueError(f"Afiliação goiana sem comprovação registrada: {codigo}")
        origem = consultas[codigo]["url_consultada"]
        fonte = f"SciELO, metadados de DOI, autores, tipo, ano e afiliações; consulta em 15/11/2026: {origem}"
        evidencia = item["evidencia"] + " Fonte: resumo local." + (
            " Texto SciELO, seção '1 Enredamento de vozes: palavras iniciais': " + origem + "." if codigo == "910fa3c6" else ""
        )
        limites = item["limites"] + (
            " Afiliações listadas não demonstram ausência de vínculo goiano não informado."
            " Análise preliminar não independente; texto integral não foi avaliado como um todo."
        )
        anteriores = [celula(campo).value for campo in ("Relação com PIBID", "Contexto de Goiás", "Afiliação em Goiás", "Triagem de título e resumo")]
        for campo, valor in {
            "Relação com PIBID": OPCOES["pibid"][item["pibid"]],
            "Contexto de Goiás": OPCOES["contexto"][item["contexto"]],
            "Afiliação em Goiás": OPCOES["afiliacao"][item["afiliacao"]],
            "Triagem de título e resumo": OPCOES["triagem"][item["triagem"]],
            "Produção acadêmica": "Sim",
            "Decisão de elegibilidade": "Pendente",
            "Afiliações de autoria": "Instituições listadas na SciELO, sem atribuição individual: " + "; ".join(instituicoes),
            "Evidência do contexto": evidencia,
            "Evidência da afiliação": "Instituições listadas nos metadados: " + "; ".join(instituicoes) + ". " + fonte,
            "Fontes das evidências": evidencia + " " + fonte,
            "Material consultado": "Resumo local e metadados da página SciELO." + (
                " Também foi consultada a seção inicial do texto para localização da pesquisa." if codigo == "910fa3c6" else ""
            ),
            "Limitações e pendências": limites,
            "Observações": "Leitura preliminar não independente; elegibilidade final e deduplicação permanecem pendentes.",
            "Revisor": "Análise computacional preliminar não independente",
            "Data da triagem": DATA,
        }.items():
            c = celula(campo)
            if campo in {"Evidência do contexto", "Evidência da afiliação", "Fontes das evidências",
                         "Material consultado", "Limitações e pendências", "Observações"} and c.value:
                valor = f"Anterior: {c.value}\nLote SciELO recente: {valor}"
            if isinstance(valor, str) and len(valor) > 32767:
                raise ValueError(f"Texto excede limite do Excel: {codigo}, {campo}")
            c.value = valor
        for eixo, estado in zip(EIXOS.values(), item["eixos"]):
            if (codigo, eixo) in existentes:
                raise ValueError(f"Eixo anterior requer conciliação: {codigo}, {eixo}")
            numero = eixos.max_row + 1
            for coluna in range(1, eixos.max_column + 1):
                eixos.cell(numero, coluna)._style = copy(eixos.cell(2, coluna)._style)
            valores = {
                "Código": codigo, "Título": celula("Título").value, "Eixo": eixo,
                "Estado": OPCOES["eixo"][estado], "Achado ou observação": evidencia,
                "Trecho ou localização": "Síntese e localização no campo de evidência.",
                "Tipo de fonte": "Resumo local; eventual fonte primária indicada",
                "Link ou referência consultada": origem, "Limites da evidência": limites,
                "Revisor": "Análise computacional preliminar não independente", "Data": DATA,
            }
            for campo, valor in valores.items():
                eixos.cell(numero, ce[campo]).value = valor
            existentes[(codigo, eixo)] = numero
        auditoria.append([codigo, anteriores[0], celula("Relação com PIBID").value, anteriores[1],
                          celula("Contexto de Goiás").value, anteriores[2], celula("Afiliação em Goiás").value,
                          anteriores[3], celula("Triagem de título e resumo").value, evidencia,
                          "; ".join(instituicoes), fonte, limites])

    audit_pares = livro.create_sheet("Pares recentes conferidos")
    audit_pares.append(["Código 1", "Código 2", "Título", "Autoria", "Ano de defesa", "Identificador de repositório",
                        "Estado anterior 1", "Estado anterior 2", "Situação", "Limites"])
    for par in pares_lidos:
        a, b = par["codigo_1"], par["codigo_2"]
        if a not in indices or b not in indices:
            raise ValueError(f"Par não encontrado: {a}/{b}")
        n1, n2 = indices[a], indices[b]
        link = validar_par_com_identificador(triagem, ct, n1, n2, a, b)
        chave = tuple(triagem.cell(n1, ct[c]).value for c in ("Título", "Autoria", "Tipo de produção", "Ano de defesa"))
        if set(grupos[chave]) != {n1, n2}:
            raise ValueError(f"Grupo maior exige conciliação: {a}/{b}")
        for campo in ("DOI", "Ano de publicação"):
            valores = {str(triagem.cell(n, ct[campo]).value) for n in (n1, n2) if triagem.cell(n, ct[campo]).value is not None}
            if len(valores) > 1:
                raise ValueError(f"Campo divergente no par {a}/{b}: {campo}")
        anteriores = [triagem.cell(n, ct["Duplicidade"]).value for n in (n1, n2)]
        if any(v not in {"Não verificada", "Duplicata provável"} for v in anteriores):
            raise ValueError(f"Duplicidade anterior inesperada: {a}/{b}")
        audit_pares.append([a, b, chave[0], chave[1], chave[3], link, *anteriores, "Duplicata confirmada",
                            "Metadados e identificador locais coincidentes; sem remoção nem escolha de principal."])
        for numero, outro in ((n1, b), (n2, a)):
            triagem.cell(numero, ct["Duplicidade"]).value = "Duplicata confirmada"
            obs = triagem.cell(numero, ct["Observações"])
            novo = f"Conferência 15/11/2026: identificador e metadados coincidem com {outro}; sem escolha de principal."
            obs.value = f"{obs.value}\n{novo}" if obs.value else novo
            if len(obs.value) > 32767:
                raise ValueError(f"Observação excede limite do Excel: {outro}")

    tabela = eixos.tables["Eixos"]
    tabela.ref = f"A1:K{eixos.max_row}"
    if tabela.autoFilter is not None:
        tabela.autoFilter.ref = tabela.ref
    if len(eixos.data_validations.dataValidation) != 1:
        raise ValueError("Validação de eixos inesperada.")
    eixos.data_validations.dataValidation[0].sqref = f"D2:D{eixos.max_row}"
    anexar_tabela(auditoria, "LoteScieloRecente")
    anexar_tabela(audit_pares, "ParesRecentesConferidos")
    livro["Limites da integração"].append([
        "28 artigos SciELO recentes e 23 pares de repositório conferidos; ver abas Lote SciELO recente e Pares recentes conferidos. "
        "A análise é preliminar e não independente; não é inclusão final nem valida confiança."
    ])
    livro.save(saida)


if __name__ == "__main__":
    integrar(BASE, DECISOES, PARES, METADADOS, COMPLEMENTO, SAIDA)
    print(f"Base criada: {SAIDA}")
