import json
from datetime import datetime
from pathlib import Path

from urllib.parse import urlencode
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "dados" / "analises" / "openalex_busca_piloto_20261115.json"
URL = "https://api.openalex.org/works"
QUERY = 'PIBID OR "Programa Institucional de Bolsa de Iniciação à Docência"'
DATE_FILTER = "from_publication_date:2007-01-01,to_publication_date:2026-11-08"
SEARCH_FIELDS = ("search", "search.title_abstract_keywords")


def main():
    if OUTPUT.exists():
        raise FileExistsError(f"Arquivo já existe; não será sobrescrito: {OUTPUT}")

    responses = []
    for field in SEARCH_FIELDS:
        for page in (1, 2):
            params = {
                field: QUERY,
                "filter": DATE_FILTER,
                "per_page": 10,
                "page": page,
            }
            request_url = f"{URL}?{urlencode(params)}"
            with urlopen(request_url, timeout=60) as response:
                data = json.load(response)
                if not isinstance(data.get("results"), list) or not isinstance(data.get("meta"), dict):
                    raise ValueError(f"Resposta inesperada: {field}, página {page}")
                if not isinstance(data["meta"].get("count"), int):
                    raise ValueError(f"Contagem ausente: {field}, página {page}")
                responses.append({
                    "retrieved_at": datetime.now().astimezone().isoformat(),
                    "search_parameter": field,
                    "page": page,
                    "request_url": request_url,
                    "http_status": response.status,
                    "rate_limit_headers": {
                        key: value
                        for key, value in response.headers.items()
                        if key.lower().startswith("x-ratelimit-")
                    },
                    "response": data,
                })
                print(f"{field} página {page}: {len(data['results'])} de {data['meta']['count']}")

    with OUTPUT.open("x", encoding="utf-8") as file:
        json.dump({"responses": responses}, file, ensure_ascii=False, indent=2)
    print(f"Respostas salvas em: {OUTPUT}")


if __name__ == "__main__":
    main()
