"""Consulta metadados bibliográficos de artigos já presentes na base."""

import json
import re
import socket
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, urlunparse
from urllib.request import Request, urlopen

from openpyxl import load_workbook

from scripts.preanalise_e_validacao_20261115 import ano, cabecalhos, texto_normalizado
from scripts.preparar_piloto_20261115 import normalizar_doi


RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_lote_goias_20261115.xlsx"
SAIDA = ANALISES / "metadados_scielo_recentes_20261115.json"


class Metadados(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.dados = {}

    def handle_starttag(self, tag, atributos):
        if tag.lower() != "meta":
            return
        attrs = dict(atributos)
        nome = attrs.get("name", "").lower()
        if nome in {
            "citation_author", "citation_author_affiliation", "citation_doi",
            "citation_publication_date", "citation_article_type",
        }:
            self.dados.setdefault(nome, []).append(attrs.get("content", ""))


def nome_comparavel(nome):
    return sorted(re.findall(r"[a-z0-9]+", texto_normalizado(nome)))


def consultar(base, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    aba = load_workbook(base, read_only=True, data_only=True)["Triagem"]
    col = cabecalhos(aba)
    selecionados = []
    for row in aba.iter_rows(min_row=2, values_only=True):
        item = {nome: row[numero - 1] for nome, numero in col.items()}
        publicacao = ano(item["Ano de publicação"])
        if (item["Fonte"] == "SciELO" and item["Relação com PIBID"] == "Incerto"
                and publicacao is not None and 2020 <= publicacao <= 2026):
            selecionados.append(item)
    if len(selecionados) != 28:
        raise ValueError(f"Esperados 28 artigos no lote congelado; encontrados {len(selecionados)}.")

    resultados = []
    for item in selecionados:
        identificador = urlparse(str(item["Link da fonte"] or ""))
        if identificador.hostname not in {"www.scielo.br", "scielo.br"}:
            raise ValueError(f"URL fora da fonte esperada: {item['Código']}")
        url = urlunparse(identificador._replace(scheme="https"))
        registro = {
            "codigo": item["Código"], "doi_esperado": item["DOI"], "url_consultada": url,
            "consultado_em": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        try:
            with urlopen(Request(url, headers={"User-Agent": "PesquisaBibliografica/1.0"}), timeout=20) as resposta:
                registro["url_final"] = resposta.url
                registro["http_status"] = resposta.status
                pagina = resposta.read().decode("utf-8", errors="strict")
        except (HTTPError, URLError, TimeoutError, socket.timeout, UnicodeDecodeError) as erro:
            registro["situacao"] = "Falha na consulta"
            registro["detalhe"] = str(erro)
            resultados.append(registro)
            continue
        parser = Metadados()
        parser.feed(pagina)
        dados = parser.dados
        registro["metadados"] = dados
        doi = dados.get("citation_doi", [])
        autores = dados.get("citation_author", [])
        autores_originais = str(item["Autoria"] or "").split(" | ")
        ano_publicado = dados.get("citation_publication_date", [])
        erros = []
        if len(doi) != 1 or normalizar_doi(doi[0]) != normalizar_doi(item["DOI"]):
            erros.append("DOI não conferido")
        if sorted(nome_comparavel(x) for x in autores) != sorted(nome_comparavel(x) for x in autores_originais):
            erros.append("Autoria não conferida")
        if len(ano_publicado) != 1 or not ano_publicado[0].startswith(str(item["Ano de publicação"])):
            erros.append("Ano não conferido")
        registro["situacao"] = "Conferido" if not erros else "Divergência de metadados"
        registro["detalhe"] = "; ".join(erros)
        resultados.append(registro)
    with saida.open("x", encoding="utf-8", newline="\n") as arquivo:
        json.dump({"fonte": "SciELO; metadados das páginas de artigos já existentes", "registros": resultados},
                  arquivo, ensure_ascii=False, indent=2)
    from collections import Counter
    print("Consultas:", len(resultados), "situações:", dict(Counter(r["situacao"] for r in resultados)))
    for r in resultados:
        md = r.get("metadados", {})
        print(r["codigo"], "|", r["situacao"], "|", r.get("detalhe", ""), "|",
              "; ".join(md.get("citation_author_affiliation", [])), "| publicação",
              md.get("citation_publication_date"))


if __name__ == "__main__":
    consultar(BASE, SAIDA)
    print("Registro de metadados:", SAIDA)
