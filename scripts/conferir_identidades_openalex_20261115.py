"""Confere identidade bibliográfica das correspondências candidatas já registradas."""

import csv
import html
import json
import re
from collections import Counter
from pathlib import Path

from openpyxl import load_workbook

from scripts.conferir_amostra_por_regras_20261115 import titulo_normalizado
from scripts.preanalise_e_validacao_20261115 import texto_normalizado
from scripts.preparar_piloto_20261115 import normalizar_doi


ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "dados" / "analises"
BASE = DIR / "triagem_criterio_defesa_20261115.xlsx"
WORKS = DIR / "openalex_busca_restrita_20261115.csv"
PAIRS = DIR / "openalex_correspondencias_candidatas_20261115.csv"
OUTPUT = DIR / "openalex_identidades_conferidas_20261115.csv"
AUDIT = DIR / "openalex_identidades_auditoria_20261115.json"
SAME = "Mesma obra: DOI e metadados concordantes"
REVIEW = "Identificador concordante; metadados requerem revisão"
TITLE_ONLY = "Título somente; identidade não estabelecida"
FIELDS = (
    "openalex_id", "codigo_base", "fonte_base", "classificacao",
    "doi_igual", "id_openalex_igual", "titulo_igual", "ano_publicacao_igual",
    "tipo_artigo_igual", "autoria_tokens_iguais", "autoria_base", "autoria_openalex",
    "titulo_base", "titulo_openalex", "ano_publicacao_base", "data_publicacao_openalex",
    "doi_base", "doi_openalex", "tipo_base", "tipo_openalex",
)


def author_names(value, separator):
    names = []
    for author in str(value or "").split(separator):
        normalized = texto_normalizado(html.unescape(author))
        tokens = tuple(sorted(re.findall(r"[a-z0-9]+", normalized)))
        if tokens:
            names.append(tokens)
    return Counter(names)


def assess(base, work):
    doi_base = normalizar_doi(base["DOI"])
    doi_oa = normalizar_doi(work["doi"])
    doi = bool(doi_base and doi_oa and doi_base == doi_oa)
    link_base = str(base["Link OpenAlex"] or "").strip().rstrip("/").lower()
    link_oa = work["openalex_id"].strip().rstrip("/").lower()
    same_id = bool(link_base and link_base == link_oa)
    title_base = titulo_normalizado(base["Título"])
    title_oa = titulo_normalizado(work["titulo"])
    title = bool(title_base and title_base == title_oa)
    year_base = str(base["Ano de publicação"] or "").strip()
    year = bool(year_base and year_base == work["data_publicacao"][:4])
    kind = base["Tipo de produção"] == "Artigo" and work["tipo"] == "article"
    separator = "|" if base["Fonte"] == "SciELO" else ","
    authors_base = author_names(base["Autoria"], separator)
    authors_oa = author_names(work["autores"], ";")
    authors = bool(authors_base and authors_oa and authors_base == authors_oa)
    if doi and title and year and kind and authors:
        status = SAME
    elif doi or same_id:
        status = REVIEW
    else:
        status = TITLE_ONLY
    return {
        "openalex_id": work["openalex_id"], "codigo_base": base["Código"],
        "fonte_base": base["Fonte"], "classificacao": status,
        "doi_igual": int(doi), "id_openalex_igual": int(same_id),
        "titulo_igual": int(title), "ano_publicacao_igual": int(year),
        "tipo_artigo_igual": int(kind), "autoria_tokens_iguais": int(authors),
        "autoria_base": base["Autoria"] or "", "autoria_openalex": work["autores"],
        "titulo_base": base["Título"] or "", "titulo_openalex": work["titulo"],
        "ano_publicacao_base": year_base, "data_publicacao_openalex": work["data_publicacao"],
        "doi_base": base["DOI"] or "", "doi_openalex": work["doi"],
        "tipo_base": base["Tipo de produção"] or "", "tipo_openalex": work["tipo"],
    }


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def main():
    if OUTPUT.exists() or AUDIT.exists():
        raise FileExistsError("Os produtos já existem; não serão sobrescritos.")
    csv.field_size_limit(2**30)
    pairs = read_csv(PAIRS)
    works = {r["openalex_id"]: r for r in read_csv(WORKS)}
    workbook = load_workbook(BASE, read_only=True, data_only=True)
    try:
        rows = workbook["Triagem"].values
        columns = next(rows)
        base = {r[0]: dict(zip(columns, r)) for r in rows}
    finally:
        workbook.close()
    if len(works) != 12431 or len(base) != 1317 or len(pairs) != 689:
        raise ValueError("Dimensões de entrada divergentes.")
    results = [assess(base[p["codigo_base"]], works[p["openalex_id"]]) for p in pairs]
    same = [r for r in results if r["classificacao"] == SAME]
    audit = {
        "pares_avaliados": len(results),
        "classificacoes": dict(Counter(r["classificacao"] for r in results)),
        "pares_sustentados_por_fonte": dict(Counter(r["fonte_base"] for r in same)),
        "ids_openalex_sustentados": len({r["openalex_id"] for r in same}),
        "codigos_base_sustentados": len({r["codigo_base"] for r in same}),
        "inclusoes_goias_com_correspondencia_sustentada": sum(
            base[r["codigo_base"]]["Decisão de elegibilidade"] == "Incluir" for r in same
        ),
    }
    with OUTPUT.open("x", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(results)
    with AUDIT.open("x", encoding="utf-8") as file:
        json.dump(audit, file, ensure_ascii=False, indent=2)
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
