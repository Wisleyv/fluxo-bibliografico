"""Consulta datas dos registros UEL já coletados com ano de defesa 2024."""

import json
import re
import socket
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from openpyxl import load_workbook

from scripts.preanalise_e_validacao_20261115 import cabecalhos, texto_normalizado


RAIZ = Path(__file__).resolve().parents[1]
BASE = RAIZ / "dados" / "analises" / "triagem_temporal_artigos_20261115.xlsx"
SAIDA = RAIZ / "dados" / "analises" / "datas_uel_20261115.json"
API = "https://repositorio.uel.br/srv-c0003-s01/api/core/items/"


def texto(valor):
    return re.sub(r"[^a-z0-9]+", " ", texto_normalizado(valor)).strip()


def consultar(base, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    aba = load_workbook(base, read_only=True, data_only=True)["Triagem"]
    col = cabecalhos(aba)
    registros = []
    for row in aba.iter_rows(min_row=2, values_only=True):
        item = {nome: row[numero - 1] for nome, numero in col.items()}
        url = urlparse(str(item["Link da fonte"] or ""))
        if (item["Fonte"] == "BDTD" and str(item["Ano de defesa"]) == "2024"
                and url.hostname == "repositorio.uel.br" and url.path.startswith("/handle/")):
            registros.append(item)
    if len(registros) != 31:
        raise ValueError(f"Esperados 31 registros UEL; encontrados {len(registros)}.")

    resultados = []
    for item in registros:
        url = item["Link da fonte"]
        resultado = {
            "codigo": item["Código"], "url_identificador": url,
            "consultado_em": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        try:
            with urlopen(Request(url, method="HEAD"), timeout=20) as resposta:
                final = urlparse(resposta.url)
            uuid = re.fullmatch(r"/items/([0-9a-fA-F-]{36})/?", final.path)
            if final.scheme != "https" or final.hostname != "repositorio.uel.br" or not uuid:
                raise ValueError("Redirecionamento para registro UEL não reconhecido")
            api_url = API + uuid.group(1)
            with urlopen(api_url, timeout=20) as resposta:
                if resposta.url != api_url:
                    raise ValueError("Redirecionamento inesperado na API de metadados")
                dados = json.load(resposta)
            meta = dados["metadata"]
            campos = ("dc.title", "dc.contributor.author", "dc.identifier.uri", "dc.date.defesa",
                      "dc.date.created", "dc.date.accessioned", "dc.date.available", "dc.date.issued")
            selecionados = {campo: [v["value"] for v in meta.get(campo, [])] for campo in campos}
            titulos = selecionados["dc.title"]
            autores = selecionados["dc.contributor.author"]
            if len(titulos) != 1 or texto(titulos[0]) != texto(item["Título"]):
                raise ValueError("Título divergente")
            if len(autores) != 1 or sorted(texto(autores[0]).split()) != sorted(texto(item["Autoria"]).split()):
                raise ValueError("Autoria divergente ou ambígua")
            if url not in selecionados["dc.identifier.uri"]:
                raise ValueError("Identificador divergente")
            resultado.update({"situacao": "Identidade conferida", "url_api": api_url, "metadados": selecionados})
        except (HTTPError, URLError, TimeoutError, socket.timeout, ValueError, KeyError, json.JSONDecodeError) as erro:
            resultado.update({"situacao": "Pendente", "detalhe": str(erro)})
        resultados.append(resultado)
    with saida.open("x", encoding="utf-8", newline="\n") as arquivo:
        json.dump({"fonte": "Metadados do repositório UEL; obras já presentes na base", "registros": resultados},
                  arquivo, ensure_ascii=False, indent=2)
    from collections import Counter
    print("Situações:", dict(Counter(r["situacao"] for r in resultados)))
    for item in resultados:
        meta = item.get("metadados", {})
        print(item["codigo"], item["situacao"], item.get("detalhe", ""), "| defesa", meta.get("dc.date.defesa"),
              "| criação", meta.get("dc.date.created"), "| depósito", meta.get("dc.date.accessioned"),
              "| publicação", meta.get("dc.date.issued"))


if __name__ == "__main__":
    consultar(BASE, SAIDA)
    print(f"Consultas registradas: {SAIDA}")
