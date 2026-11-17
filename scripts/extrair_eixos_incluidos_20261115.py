"""Integra extrações dos resumos já preservados dos registros incluídos."""

import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

from scripts.integrar_autoavaliacao_20261115 import EIXOS, indice_unico
from scripts.preanalise_e_validacao_20261115 import cabecalhos, reconstruir_resumo
from scripts.preencher_autoavaliacao_20261115 import OPCOES
from scripts.preparar_piloto_20261115 import normalizar_doi

RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_decisoes_goias_20261115.xlsx"
DECISOES = ANALISES / "extracao_eixos_incluidos_20261115.csv"
METADADOS = ANALISES / "openalex_piloto_20261115.json"
SAIDA = ANALISES / "triagem_eixos_incluidos_20261115.xlsx"
DATA = datetime(2026, 11, 15)
EIXOS_CODIGO = dict(zip(("A", "T", "R"), EIXOS.values()))
RESUMOS = {
    "00683d4e": "d2a511bfcbf5e880c5edb9f892876c260aed9f069ac19af1c57bc7ec2d700229",
    "22f73924": "58deeb5a47b572953be09ca02446695f7dc5e2c9cb9ab1568b6360feaad7f6b7",
    "25b844fb": "fb0c0dc5fcb11b437e256a55fd7e8033c7e761810e6a1475023ab8194706018c",
    "768c2970": "a25df7182c23e871331d8f216904a7b38a148caaa3d70192909d66065aefb3af",
    "813fdfa6": "7374fa73a80be593e61b2ac1950049f2debbf53e80ef857dc588c09f1fa0535e",
    "91522d0b": "44129c44a698f563ff9701d49e6d60b9b5b32449cab151627887d5b76f278fe5",
    "e76a8964": "2aa7cbc9648ce475a76ccf4d328def55efd7a5168fcec1cfe81d57ddc0f264b9",
}


def ler_decisoes(caminho):
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames != ["codigo", "eixo", "estado", "sintese", "trecho", "limite"]:
            raise ValueError("Colunas das extrações divergentes.")
        linhas = list(leitor)
    if any(None in item or any(valor is None for valor in item.values()) for item in linhas):
        raise ValueError("Extração malformada.")
    chaves = [(item["codigo"], item["eixo"]) for item in linhas]
    esperadas = {(codigo, eixo) for codigo in RESUMOS for eixo in EIXOS_CODIGO}
    if len(chaves) != 21 or set(chaves) != esperadas:
        raise ValueError("Seleção das extrações divergente.")
    for item in linhas:
        if (not item["sintese"] or not item["limite"]
                or item["estado"] not in {"P", "N", "V"}
                or (item["estado"] != "N" and not item["trecho"])):
            raise ValueError(f"Extração incompleta: {item['codigo']}/{item['eixo']}")
    return linhas


def integrar(base, decisoes, metadados, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    leituras = ler_decisoes(decisoes)
    dados = json.loads(metadados.read_text(encoding="utf-8"))
    obras = {obra["id"]: obra for obra in dados["response"]["results"]}
    if len(obras) != 36 or datetime.fromisoformat(dados["consultado_em"]).date() != DATA.date():
        raise ValueError("Resposta OpenAlex inesperada.")
    livro = load_workbook(base)
    triagem, eixos = livro["Triagem"], livro["Eixos de análise"]
    ct, ce = cabecalhos(triagem), cabecalhos(eixos)
    indices = indice_unico(triagem, ct["Código"], 1317)
    existentes = {}
    for numero in range(2, eixos.max_row + 1):
        chave = (eixos.cell(numero, ce["Código"]).value, eixos.cell(numero, ce["Eixo"]).value)
        if chave in existentes:
            raise ValueError(f"Eixo duplicado: {chave}")
        existentes[chave] = numero

    incluidos = {codigo for codigo, numero in indices.items()
                 if triagem.cell(numero, ct["Decisão de elegibilidade"]).value == "Incluir"}
    vazios = {(codigo, eixo) for codigo in incluidos for eixo in EIXOS.values()
              if (codigo, eixo) not in existentes
              or eixos.cell(existentes[(codigo, eixo)], ce["Estado"]).value is None}
    if vazios != {(codigo, eixo) for codigo in RESUMOS for eixo in EIXOS.values()}:
        raise ValueError("Seleção dos eixos vazios divergente.")

    resumos = {}
    for codigo, hash_esperado in RESUMOS.items():
        linha = indices[codigo]
        valor = lambda campo: triagem.cell(linha, ct[campo]).value
        if valor("Fonte") != "Portal CAPES" or valor("Decisão de elegibilidade") != "Incluir":
            raise ValueError(f"Registro não incluído ou fonte divergente: {codigo}")
        obra = obras[valor("Link OpenAlex")]
        resumo = reconstruir_resumo(obra["abstract_inverted_index"])
        if (normalizar_doi(obra["doi"]) != normalizar_doi(valor("DOI"))
                or hashlib.sha256(resumo.encode("utf-8")).hexdigest() != hash_esperado):
            raise ValueError(f"Identidade ou resumo divergente: {codigo}")
        resumos[codigo] = resumo
    for item in leituras:
        codigo, eixo = item["codigo"], EIXOS_CODIGO[item["eixo"]]
        numero = existentes.get((codigo, eixo))
        if not numero:
            raise ValueError(f"Eixo ausente: {codigo}/{eixo}")
        if eixos.cell(numero, ce["Título"]).value != triagem.cell(indices[codigo], ct["Título"]).value:
            raise ValueError(f"Título divergente no eixo: {codigo}")
        campos = ("Estado", "Achado ou observação", "Trecho ou localização", "Tipo de fonte",
                  "Link ou referência consultada", "Limites da evidência", "Revisor", "Data")
        if any(eixos.cell(numero, ce[campo]).value is not None for campo in campos):
            raise ValueError(f"Eixo anteriormente preenchido: {codigo}/{eixo}")
        if item["trecho"] and item["trecho"].casefold() not in resumos[codigo].casefold():
            raise ValueError(f"Trecho não localizado no resumo: {codigo}/{eixo}")
        trecho = (f"Resumo OpenAlex: {item['trecho']}"
                  if item["trecho"] else "Resumo OpenAlex completo; informação não identificada.")
        valores = {
            "Estado": OPCOES["eixo"][item["estado"]],
            "Achado ou observação": item["sintese"],
            "Trecho ou localização": trecho,
            "Tipo de fonte": "Título e resumo OpenAlex arquivado",
            "Link ou referência consultada": triagem.cell(indices[codigo], ct["Link OpenAlex"]).value,
            "Limites da evidência": (
                item["limite"] + " Análise do resumo arquivado em 15/11/2026, não independente; "
                "não equivale à leitura integral nem comprova o conteúdo exibido no corte da coleta."
            ),
            "Revisor": "Análise computacional e documental preliminar não independente",
            "Data": DATA,
        }
        for campo, valor in valores.items():
            eixos.cell(numero, ce[campo]).value = valor
    livro["Limites da integração"].append([
        "21 estados de eixos preenchidos para sete registros incluídos a partir dos resumos OpenAlex "
        "arquivados; a análise não é independente nem substitui leitura integral."
    ])
    livro.save(saida)
    livro.close()


if __name__ == "__main__":
    integrar(BASE, DECISOES, METADADOS, SAIDA)
    print(f"Base criada: {SAIDA}")
