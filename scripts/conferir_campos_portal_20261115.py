"""Integra a conferência documental de oito registros do Portal CAPES."""

import csv
from pathlib import Path

from openpyxl import load_workbook

from scripts.integrar_autoavaliacao_20261115 import anexar_tabela, indice_unico
from scripts.integrar_teses_e_datas_uel_20261115 import acrescentar
from scripts.normalize_collection import _parse_ris
from scripts.preanalise_e_validacao_20261115 import cabecalhos


RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_pares_conciliados_20261115.xlsx"
DECISOES = ANALISES / "conferencia_portal_campos_20261115.csv"
BRUTOS = RAIZ / "dados" / "brutos" / "portal-capes"
SAIDA = ANALISES / "triagem_portal_campos_20261115.xlsx"
URL = "https://www.periodicos.capes.gov.br/index.php/acervo/buscador.html?task=detalhes&source=digital&id="
CAMPOS = ["codigo", "id", "doi", "ano", "titulo", "autoria", "evidencia", "limites"]


def texto(valor):
    return " ".join(str(valor or "").split()).casefold()


def ler_decisoes(caminho):
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames != CAMPOS:
            raise ValueError("Colunas das conferências inesperadas.")
        linhas = list(leitor)
    if len(linhas) != 8 or len({x["codigo"] for x in linhas}) != 8 or len({x["id"] for x in linhas}) != 8:
        raise ValueError("Esperadas oito conferências únicas.")
    if any(None in x or any(not x[campo] for campo in CAMPOS) for x in linhas):
        raise ValueError("Conferência incompleta.")
    return linhas


def ler_ris(pasta, ids):
    encontrados = {}
    for arquivo in pasta.glob("*.ris"):
        for registro, erros in _parse_ris(arquivo):
            identificadores = registro.get("ID", [])
            if len(identificadores) == 1 and identificadores[0] in ids:
                identificador = identificadores[0]
                if erros or identificador in encontrados:
                    raise ValueError(f"RIS malformado ou identificador repetido: {identificador}")
                encontrados[identificador] = (arquivo.name, registro)
    if set(encontrados) != ids:
        raise ValueError("Registros não encontrados nos arquivos RIS.")
    return encontrados


def integrar(base, decisoes, brutos, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    linhas = ler_decisoes(decisoes)
    ris = ler_ris(brutos, {item["id"] for item in linhas})
    livro = load_workbook(base)
    triagem = livro["Triagem"]
    col = cabecalhos(triagem)
    indices = indice_unico(triagem, col["Código"], 1317)
    auditoria = livro.create_sheet("Campos Portal CAPES")
    auditoria.append(["Código", "ID", "Arquivo RIS", "DOI", "Fonte consultada",
                      "Evidência", "Limites", "Data da consulta"])
    for item in linhas:
        codigo, identificador = item["codigo"], item["id"]
        if codigo not in indices:
            raise ValueError(f"Código ausente: {codigo}")
        celula = lambda campo: triagem.cell(indices[codigo], col[campo])
        arquivo, registro = ris[identificador]
        for campo, tag, chave in (("Título", "TI", "titulo"), ("Autoria", "AU", "autoria"),
                                  ("Ano de publicação", "PY", "ano"), ("DOI", "DO", "doi")):
            original = registro.get(tag, [])
            if len(original) != 1 or texto(original[0]) != texto(item[chave]) or texto(celula(campo).value) != texto(item[chave]):
                raise ValueError(f"Identidade divergente: {codigo}, {campo}")
        if (celula("Fonte").value != "Portal CAPES"
                or celula("Link OpenAlex").value != f"https://openalex.org/{identificador}"
                or celula("Link da fonte").value is not None
                or celula("Resumo").value is not None
                or celula("Triagem de título e resumo").value != "Avançar para avaliação"
                or celula("Decisão de elegibilidade").value != "Pendente"
                or registro.get("AB") or registro.get("KW")):
            raise ValueError(f"Estado anterior inesperado: {codigo}")
        url = URL + identificador
        celula("Link da fonte").value = url
        acrescentar(celula("Fontes das evidências"),
                   f"Portal CAPES, página de detalhes consultada em 15/11/2026: {url}. {item['evidencia']}")
        acrescentar(celula("Material consultado"),
                   "Título, DOI, autoria, ano e campo Sobre na página atual do Portal CAPES; RIS preservado.")
        limite = (item["limites"] + " O RIS não registra resumo ou palavras-chave; a página atual não comprova "
                  "o conteúdo exibido em 08/11/2026. A elegibilidade e a duplicidade seguem pendentes; "
                  "conferência não independente.")
        acrescentar(celula("Limitações e pendências"), limite)
        auditoria.append([codigo, identificador, arquivo, item["doi"], url,
                          item["evidencia"], limite, "15/11/2026"])
    anexar_tabela(auditoria, "CamposPortalCAPES")
    livro["Limites da integração"].append([
        "Oito páginas atuais do Portal CAPES conferidas; termo presente no resumo exibido. "
        "RIS sem resumo; conteúdo histórico da interface e decisão final permanecem não comprovados."
    ])
    livro.save(saida)
    livro.close()


if __name__ == "__main__":
    integrar(BASE, DECISOES, BRUTOS, SAIDA)
    print(f"Base criada: {SAIDA}")
