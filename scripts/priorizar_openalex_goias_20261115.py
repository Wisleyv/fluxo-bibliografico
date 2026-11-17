"""Organiza sinais geográficos para leitura, sem decidir elegibilidade."""

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from scripts.conferir_identidades_openalex_20261115 import SAME, read_csv


ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "dados" / "analises"
WORKS = DIR / "openalex_busca_restrita_20261115.csv"
SIGNALS = DIR / "openalex_sinais_triagem_20261115.csv"
IDENTITIES = DIR / "openalex_identidades_conferidas_20261115.csv"
OUTPUT = DIR / "openalex_prioridade_goias_20261115.csv"
AUDIT = DIR / "openalex_prioridade_goias_auditoria_20261115.json"
FIELDS = (
    "openalex_id", "faixa_publicacao_openalex", "titulo", "autores", "tipo",
    "data_publicacao", "instituicoes", "sinais_goias_texto_campos",
    "sinal_goias_instituicoes", "sinais_pibid_campos", "doi", "resumo",
    "codigos_mesma_obra", "codigos_outros_candidatos", "pagina_origem",
)


def publication_band(date):
    year = int(date[:4])
    if 2020 <= year <= 2025:
        return "2020–2025"
    if year == 2026:
        return "2026; data de indexação no corte não comprovada"
    return "2007–2019; não excluir automaticamente"


def main():
    if OUTPUT.exists() or AUDIT.exists():
        raise FileExistsError("Produtos de priorização já existem; não serão sobrescritos.")
    csv.field_size_limit(2**30)
    works = {item["openalex_id"]: item for item in read_csv(WORKS)}
    signals = read_csv(SIGNALS)
    matches = defaultdict(list)
    for pair in read_csv(IDENTITIES):
        matches[pair["openalex_id"]].append(pair)
    if len(works) != 12431 or len(signals) != 12431:
        raise ValueError("Dimensões de entrada divergentes.")
    chosen = [
        item for item in signals
        if item["sinais_goias_texto_campos"] or item["sinal_goias_instituicoes"]
    ]
    if len(chosen) != 333:
        raise ValueError("Quantidade de sinais geográficos divergente.")
    rows = []
    for signal in chosen:
        work = works[signal["openalex_id"]]
        pairs = matches[work["openalex_id"]]
        rows.append({
            "openalex_id": work["openalex_id"],
            "faixa_publicacao_openalex": publication_band(work["data_publicacao"]),
            "titulo": work["titulo"], "autores": work["autores"], "tipo": work["tipo"],
            "data_publicacao": work["data_publicacao"], "instituicoes": work["instituicoes"],
            "sinais_goias_texto_campos": signal["sinais_goias_texto_campos"],
            "sinal_goias_instituicoes": signal["sinal_goias_instituicoes"],
            "sinais_pibid_campos": signal["sinais_pibid_campos"],
            "doi": work["doi"], "resumo": work["resumo"],
            "codigos_mesma_obra": "; ".join(p["codigo_base"] for p in pairs if p["classificacao"] == SAME),
            "codigos_outros_candidatos": "; ".join(p["codigo_base"] for p in pairs if p["classificacao"] != SAME),
            "pagina_origem": work["pagina_origem"],
        })
    rows.sort(key=lambda row: (row["data_publicacao"], row["openalex_id"]), reverse=True)
    audit = {
        "registros_com_sinal": len(rows),
        "por_faixa_publicacao": dict(Counter(r["faixa_publicacao_openalex"] for r in rows)),
        "com_vinculo_mesma_obra": sum(bool(r["codigos_mesma_obra"]) for r in rows),
        "com_alguma_correspondencia_base": sum(
            bool(r["codigos_mesma_obra"] or r["codigos_outros_candidatos"]) for r in rows
        ),
    }
    with OUTPUT.open("x", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    with AUDIT.open("x", encoding="utf-8") as file:
        json.dump(audit, file, ensure_ascii=False, indent=2)
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
