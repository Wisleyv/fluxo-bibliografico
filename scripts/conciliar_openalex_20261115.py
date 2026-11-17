"""Identifica correspondências candidatas e sinais documentais, sem decidir elegibilidade."""

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from openpyxl import load_workbook

from scripts.conferir_amostra_por_regras_20261115 import titulo_normalizado
from scripts.preanalise_e_validacao_20261115 import PADRAO_GO, PADRAO_TEMA, sinal
from scripts.preparar_piloto_20261115 import normalizar_doi


ROOT = Path(__file__).resolve().parents[1]
ANALISES = ROOT / "dados" / "analises"
BASE = ANALISES / "triagem_criterio_defesa_20261115.xlsx"
OPENALEX = ANALISES / "openalex_busca_restrita_20261115.csv"
OUTPUT = ANALISES / "openalex_correspondencias_candidatas_20261115.csv"
SIGNALS = ANALISES / "openalex_sinais_triagem_20261115.csv"
AUDIT = ANALISES / "openalex_conciliacao_auditoria_20261115.json"
PAIR_FIELDS = (
    "openalex_id", "codigo_base", "fonte_base", "sinais_correspondencia",
    "titulo_openalex", "titulo_base", "tipo_openalex", "tipo_base",
    "data_publicacao_openalex", "ano_publicacao_base", "ano_defesa_base",
    "doi_openalex", "doi_base", "titulos_normalizados_iguais",
)
SIGNAL_FIELDS = (
    "openalex_id", "titulo", "tipo", "data_publicacao", "doi",
    "sinais_pibid_campos", "sinais_goias_texto_campos",
    "sinal_goias_instituicoes", "quantidade_correspondencias_base", "pagina_origem",
)


def find_pairs(works, base):
    indices = {field: defaultdict(set) for field in ("doi", "titulo", "openalex_id")}
    for row in base:
        for field, value in (
            ("doi", normalizar_doi(row["DOI"])),
            ("titulo", titulo_normalizado(row["Título"])),
            ("openalex_id", str(row["Link OpenAlex"] or "").strip().rstrip("/").lower()),
        ):
            if value:
                indices[field][value].add(row["Código"])
    base_by_code = {row["Código"]: row for row in base}
    pairs = []
    for work in works:
        candidates = defaultdict(set)
        for field, value in (
            ("doi", normalizar_doi(work["doi"])),
            ("titulo", titulo_normalizado(work["titulo"])),
            ("openalex_id", work["openalex_id"].strip().rstrip("/").lower()),
        ):
            if value:
                for code in indices[field].get(value, ()):
                    candidates[code].add(field)
        for code in sorted(candidates):
            row = base_by_code[code]
            pairs.append({
                "openalex_id": work["openalex_id"],
                "codigo_base": code,
                "fonte_base": row["Fonte"],
                "sinais_correspondencia": "; ".join(sorted(candidates[code])),
                "titulo_openalex": work["titulo"],
                "titulo_base": row["Título"] or "",
                "tipo_openalex": work["tipo"],
                "tipo_base": row["Tipo de produção"] or "",
                "data_publicacao_openalex": work["data_publicacao"],
                "ano_publicacao_base": row["Ano de publicação"] or "",
                "ano_defesa_base": row["Ano de defesa"] or "",
                "doi_openalex": work["doi"],
                "doi_base": row["DOI"] or "",
                "titulos_normalizados_iguais": (
                    "Sim" if titulo_normalizado(work["titulo"])
                    and titulo_normalizado(work["titulo"]) == titulo_normalizado(row["Título"])
                    else "Não ou não comparáveis"
                ),
            })
    return pairs


def make_signals(work, matched_count):
    fields = {
        "título": work["titulo"], "resumo": work["resumo"],
        "palavras-chave": work["palavras_chave"],
    }
    return {
        "openalex_id": work["openalex_id"],
        "titulo": work["titulo"],
        "tipo": work["tipo"],
        "data_publicacao": work["data_publicacao"],
        "doi": work["doi"],
        "sinais_pibid_campos": "; ".join(sinal(fields, PADRAO_TEMA)),
        "sinais_goias_texto_campos": "; ".join(sinal(fields, PADRAO_GO)),
        "sinal_goias_instituicoes": "; ".join(sinal({"instituições": work["instituicoes"]}, PADRAO_GO)),
        "quantidade_correspondencias_base": matched_count,
        "pagina_origem": work["pagina_origem"],
    }


def write_csv(path, fields, rows):
    with path.open("x", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    if any(path.exists() for path in (OUTPUT, SIGNALS, AUDIT)):
        raise FileExistsError("Produtos de conciliação já existem; não serão sobrescritos.")
    csv.field_size_limit(2**30)
    with OPENALEX.open(encoding="utf-8-sig", newline="") as file:
        works = list(csv.DictReader(file))
    if len(works) != 12431 or len({w["openalex_id"] for w in works}) != len(works):
        raise ValueError("Quantidade ou identificadores OpenAlex divergentes.")
    workbook = load_workbook(BASE, read_only=True, data_only=True)
    try:
        rows = workbook["Triagem"].values
        columns = next(rows)
        base = [dict(zip(columns, row)) for row in rows]
    finally:
        workbook.close()
    if len(base) != 1317 or len({r["Código"] for r in base}) != len(base):
        raise ValueError("Quantidade ou códigos da base técnica divergentes.")
    pairs = find_pairs(works, base)
    counts = Counter(pair["openalex_id"] for pair in pairs)
    signals = [make_signals(work, counts[work["openalex_id"]]) for work in works]
    audit = {
        "registros_openalex": len(works),
        "linhas_base": len(base),
        "pares_candidatos": len(pairs),
        "ids_openalex_com_candidato": len(counts),
        "linhas_base_com_candidato": len({p["codigo_base"] for p in pairs}),
        "pares_por_fonte_base": dict(Counter(p["fonte_base"] for p in pairs)),
        "pares_por_sinal": dict(Counter(
            name for p in pairs for name in p["sinais_correspondencia"].split("; ")
        )),
        "pares_titulo_divergente_ou_ausente": sum(
            p["titulos_normalizados_iguais"] != "Sim" for p in pairs
        ),
        "sinal_pibid_textual": sum(bool(s["sinais_pibid_campos"]) for s in signals),
        "sinal_goias_textual": sum(bool(s["sinais_goias_texto_campos"]) for s in signals),
        "sinal_goias_instituicoes": sum(bool(s["sinal_goias_instituicoes"]) for s in signals),
        "sinal_goias_textual_ou_instituicoes": sum(
            bool(s["sinais_goias_texto_campos"] or s["sinal_goias_instituicoes"])
            for s in signals
        ),
    }
    write_csv(OUTPUT, PAIR_FIELDS, pairs)
    write_csv(SIGNALS, SIGNAL_FIELDS, signals)
    with AUDIT.open("x", encoding="utf-8") as file:
        json.dump(audit, file, ensure_ascii=False, indent=2)
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
