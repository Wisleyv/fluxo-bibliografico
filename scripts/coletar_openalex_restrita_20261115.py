import json
import os
import time
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "dados" / "brutos" / "openalex" / "busca-restrita-20261115"
URL = "https://api.openalex.org/works"
QUERY = 'PIBID OR "Programa Institucional de Bolsa de Iniciação à Docência"'
PARAMS = {
    "search.title_abstract_keywords": QUERY,
    "filter": "from_publication_date:2007-01-01,to_publication_date:2026-11-08",
    "per_page": 100,
}
MAX_COST_USD = 0.20


def validate_page(page, cursor, seen):
    if page["request_cursor"] != cursor:
        raise ValueError("Sequência de cursores inconsistente.")
    data = page["response"]
    meta = data.get("meta")
    results = data.get("results")
    if not isinstance(meta, dict) or not isinstance(meta.get("count"), int):
        raise ValueError("Contagem da API ausente.")
    if "next_cursor" not in meta or not isinstance(results, list):
        raise ValueError("Resposta sem cursor ou lista de resultados.")
    next_cursor = meta["next_cursor"]
    if next_cursor is not None and (not isinstance(next_cursor, str) or not next_cursor or next_cursor == cursor):
        raise ValueError("Cursor seguinte inválido.")
    if not results and next_cursor is not None:
        raise ValueError("Página vazia com cursor seguinte.")
    ids = [record.get("id") for record in results]
    if any(not isinstance(identifier, str) or not identifier for identifier in ids):
        raise ValueError("Registro sem identificador OpenAlex.")
    if len(set(ids)) != len(ids) or set(ids) & seen:
        raise ValueError("Identificadores repetidos entre ou dentro das páginas.")
    for record in results:
        date = record.get("publication_date") or ""
        if not "2007-01-01" <= date <= "2026-11-08":
            raise ValueError("Data de publicação ausente ou fora do filtro.")
    seen.update(ids)
    return next_cursor


def fetch_page(cursor, key):
    params = {**PARAMS, "cursor": cursor}
    request = Request(
        f"{URL}?{urlencode(params)}",
        headers={"Authorization": f"Bearer {key}", "Accept": "application/json"},
    )
    for attempt in range(4):
        try:
            with urlopen(request, timeout=90) as response:
                data = json.load(response)
                return {
                    "retrieved_at": datetime.now().astimezone().isoformat(),
                    "request_parameters": PARAMS,
                    "request_cursor": cursor,
                    "http_status": response.status,
                    "rate_limit_headers": {
                        k: v for k, v in response.headers.items()
                        if k.lower().startswith("x-ratelimit-")
                    },
                    "response": data,
                }
        except HTTPError as exc:
            if exc.code != 429 or attempt == 3:
                raise RuntimeError(f"OpenAlex retornou HTTP {exc.code}; coleta interrompida.") from exc
            retry = exc.headers.get("Retry-After")
            if not retry or not retry.isdigit() or int(retry) > 600:
                raise RuntimeError("Limite da API atingido sem espera curta informada; coleta interrompida.") from exc
            print(f"Limite da API: aguardando {retry} segundos.", flush=True)
            time.sleep(int(retry) + 1)
        except URLError as exc:
            raise RuntimeError(f"Erro de conexão com OpenAlex: {exc.reason}") from exc
    raise RuntimeError("Não foi possível consultar a API.")


def main():
    key = os.environ.get("OPENALEX_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Variável OPENALEX_API_KEY ausente.")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    existing = sorted(OUTPUT.glob("pagina_*.json"))
    seen = set()
    cursor = "*"
    cost = 0.0
    remaining = None
    for number, path in enumerate(existing, 1):
        if path.name != f"pagina_{number:04d}.json" or cursor is None:
            raise ValueError("Arquivos de páginas não estão em sequência.")
        page = json.loads(path.read_text(encoding="utf-8"))
        if page["request_parameters"] != PARAMS:
            raise ValueError("Parâmetros de coleta anteriores não correspondem.")
        cursor = validate_page(page, cursor, seen)
        headers = page["rate_limit_headers"]
        cost += float(headers["X-RateLimit-Cost-USD"])
        remaining = float(headers["X-RateLimit-Remaining-USD"])

    while cursor is not None:
        if cost >= MAX_COST_USD or (remaining is not None and remaining <= 0.001):
            raise RuntimeError("Limite preventivo de custo ou saldo da API atingido; coleta interrompida.")
        number = len(existing) + 1
        page = fetch_page(cursor, key)
        path = OUTPUT / f"pagina_{number:04d}.json"
        with path.open("x", encoding="utf-8") as file:
            json.dump(page, file, ensure_ascii=False, indent=2)
        existing.append(path)
        cursor = validate_page(page, cursor, seen)
        headers = page["rate_limit_headers"]
        cost += float(headers["X-RateLimit-Cost-USD"])
        remaining = float(headers["X-RateLimit-Remaining-USD"])
        print(f"Página {number}: {len(seen)} registros; API informa {page['response']['meta']['count']}; uso US$ {cost:.3f}.", flush=True)

    print(f"Coleta concluída: {len(seen)} identificadores em {len(existing)} páginas; uso US$ {cost:.3f}.", flush=True)


if __name__ == "__main__":
    main()
