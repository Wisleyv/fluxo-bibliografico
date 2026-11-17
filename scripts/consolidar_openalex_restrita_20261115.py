import csv
import hashlib
import json
from collections import Counter

from coletar_openalex_restrita_20261115 import OUTPUT, PARAMS, validate_page


CSV_OUTPUT = OUTPUT.parent.parent.parent / "analises" / "openalex_busca_restrita_20261115.csv"
REPORT_OUTPUT = OUTPUT.parent.parent.parent / "analises" / "openalex_busca_restrita_auditoria_20261115.json"
FIELDS = (
    "openalex_id", "titulo", "data_publicacao", "ano_publicacao", "tipo",
    "autores", "instituicoes", "doi", "fonte", "palavras_chave", "resumo",
    "pagina_origem",
)


def abstract(index):
    if not index:
        return ""
    words = {}
    for word, positions in index.items():
        for position in positions:
            if position in words:
                raise ValueError("Posição duplicada no índice de resumo.")
            words[position] = word
    return " ".join(words[position] for position in sorted(words))


def main():
    if CSV_OUTPUT.exists() or REPORT_OUTPUT.exists():
        raise FileExistsError("Produto consolidado já existe; não será sobrescrito.")
    pages = sorted(OUTPUT.glob("pagina_*.json"))
    if not pages:
        raise ValueError("Não há páginas arquivadas.")
    seen = set()
    cursor = "*"
    records = []
    counts = []
    times = []
    hashes = {}
    cost = 0.0
    types = Counter()
    for number, path in enumerate(pages, 1):
        if path.name != f"pagina_{number:04d}.json" or cursor is None:
            raise ValueError("Sequência de páginas inválida.")
        payload = path.read_bytes()
        page = json.loads(payload)
        if page["request_parameters"] != PARAMS:
            raise ValueError("Parâmetros divergentes na página arquivada.")
        cursor = validate_page(page, cursor, seen)
        hashes[path.name] = hashlib.sha256(payload).hexdigest()
        times.append(page["retrieved_at"])
        counts.append(page["response"]["meta"]["count"])
        cost += float(page["rate_limit_headers"]["X-RateLimit-Cost-USD"])
        for item in page["response"]["results"]:
            authorships = item.get("authorships") or []
            institutions = sorted({
                institution["display_name"]
                for authorship in authorships
                for institution in (authorship.get("institutions") or [])
                if institution.get("display_name")
            })
            source = (item.get("primary_location") or {}).get("source") or {}
            kind = item.get("type") or ""
            types[kind or "(não informado)"] += 1
            records.append({
                "openalex_id": item["id"],
                "titulo": item.get("title") or "",
                "data_publicacao": item.get("publication_date") or "",
                "ano_publicacao": item.get("publication_year") or "",
                "tipo": kind,
                "autores": "; ".join(
                    (authorship.get("author") or {}).get("display_name") or ""
                    for authorship in authorships
                ),
                "instituicoes": "; ".join(institutions),
                "doi": item.get("doi") or "",
                "fonte": source.get("display_name") or "",
                "palavras_chave": "; ".join(
                    keyword.get("display_name") or "" for keyword in (item.get("keywords") or [])
                ),
                "resumo": abstract(item.get("abstract_inverted_index")),
                "pagina_origem": path.name,
            })
    if cursor is not None:
        raise ValueError("Coleta incompleta: o último cursor não é nulo.")
    if len(set(counts)) != 1 or len(records) != counts[0]:
        raise ValueError("Contagem da API não corresponde aos registros coletados.")
    with CSV_OUTPUT.open("x", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)
    audit = {
        "parameters": PARAMS,
        "first_retrieved_at": times[0],
        "last_retrieved_at": times[-1],
        "pages": len(pages),
        "api_reported_counts": sorted(set(counts)),
        "records": len(records),
        "unique_openalex_ids": len(seen),
        "types": dict(types),
        "with_doi": sum(bool(record["doi"]) for record in records),
        "with_abstract": sum(bool(record["resumo"]) for record in records),
        "with_institution": sum(bool(record["instituicoes"]) for record in records),
        "api_cost_usd": round(cost, 6),
        "csv_sha256": hashlib.sha256(CSV_OUTPUT.read_bytes()).hexdigest(),
        "page_sha256": hashes,
    }
    with REPORT_OUTPUT.open("x", encoding="utf-8") as file:
        json.dump(audit, file, ensure_ascii=False, indent=2)
    print(json.dumps({key: value for key, value in audit.items() if key != "page_sha256"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
