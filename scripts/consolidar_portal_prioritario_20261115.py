"""Consolida os dez registros prioritários com evidências já arquivadas."""

import csv
import hashlib
import json
from datetime import date, datetime
from pathlib import Path

from openpyxl import load_workbook

from scripts.conferir_campos_portal_20261115 import (
    URL, ler_decisoes as ler_campos, ler_ris, texto,
)
from scripts.conferir_termos_e_resumos_20261115 import tem_termo
from scripts.consolidar_decisoes_goias_20261115 import candidatos_duplicidade
from scripts.extrair_eixos_incluidos_20261115 import EIXOS_CODIGO
from scripts.integrar_autoavaliacao_20261115 import anexar_tabela, indice_unico
from scripts.integrar_teses_e_datas_uel_20261115 import acrescentar
from scripts.preanalise_e_validacao_20261115 import cabecalhos, reconstruir_resumo
from scripts.preencher_autoavaliacao_20261115 import OPCOES
from scripts.preparar_piloto_20261115 import CORTE, INSTITUICOES_GOIANAS, normalizar_doi
from scripts.triagem_temporal_artigos_20261115 import texto_comparavel

RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_lote_consolidada_20261115.xlsx"
CAMPOS = ANALISES / "conferencia_portal_campos_20261115.csv"
EXTRACOES = ANALISES / "extracao_portal_prioritario_20261115.csv"
METADADOS = ANALISES / "openalex_piloto_20261115.json"
BRUTOS = RAIZ / "dados" / "brutos" / "portal-capes"
SAIDA = ANALISES / "triagem_portal_prioritario_20261115.xlsx"
DATA = datetime(2026, 11, 15)
RESUMOS = {
    "05cbfe1e": "29525cbd18495fcba23166ae6a01ac68cc009e97d949c00448a768330614d295",
    "27027026": "5b955aa82749e9816a21bd2c37ca59191fad8d54629b1d41894e1b658bfc29d0",
    "2fee827b": "30806b5da1e9fa7e7a903c951c3d27e5dd7ee42801b2456683fd5d935f8db6eb",
    "3f830636": "1009c8e8594881931f435eb6e6414087fbeba2db620ea537f8475faf71af859f",
    "4a213f79": "a9cdbc918baef6d3120a572059b50c76c28cfd38be51b59da46a5f68f4127f9b",
    "678fd86d": "c7c0dfb015a9deb8a8923521ff23e0d143e2a58aa62c0b7710d039979c361591",
    "7d7f7dda": "bbb233a07890a4008c53fe491b0b60c2e75c9a0c13d9d3450b20ef2e8a1ea23e",
    "8819ba66": "3cab47c78737c215a4d22eda5ed5e5fb8da48b256d3d6fd498671b135909b44d",
    "8100e3f1": "6e5f04e168d20e6df10a6775d3333475cbe08780727c19ef49d8e33d09ba2cd4",
    "b954db99": "db8c30698d188898622569ad91ab37c40984390a111ba2fbd0c31622e5773b77",
}
INCERTOS = {
    "8100e3f1": "O resumo informa que licenciandos PIBID coletaram dados sobre ensino musical, mas não esclarece a análise substantiva do programa.",
    "b954db99": "O resumo apresenta pesquisa em andamento e prevê bolsistas PIBID como participantes; não esclarece análise substantiva do programa.",
}
PARA_EXTRAIR = {"05cbfe1e", "2fee827b", "4a213f79", "678fd86d", "8819ba66"}
LIMITE_INCLUSAO = (
    "Consolidação em 15/11/2026: inclusão operacional substitui a pendência anterior de elegibilidade. "
    "A busca de assunto de 08/11 recuperou o registro, mas não identifica o campo correspondente; "
    "o RIS não preservou resumo nem palavras-chave. O resumo complementar de 15/11 não comprova "
    "o conteúdo exibido no corte. Qualidade documental reduzida, sem percentual calibrado; "
    "análise não independente e sem leitura integral. Duplicidade permanece não verificada."
)


def ler_extracoes(caminho):
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames != ["codigo", "eixo", "estado", "sintese", "trecho", "limite"]:
            raise ValueError("Colunas das extrações divergentes.")
        itens = list(leitor)
    chaves = [(item["codigo"], item["eixo"]) for item in itens]
    if len(chaves) != 15 or set(chaves) != {(c, e) for c in PARA_EXTRAIR for e in EIXOS_CODIGO}:
        raise ValueError("Seleção das extrações divergente.")
    for item in itens:
        if (None in item or any(valor is None for valor in item.values())
                or not item["sintese"] or not item["limite"]
                or item["estado"] not in {"P", "N", "V"}
                or (item["estado"] != "N" and not item["trecho"])):
            raise ValueError("Extração incompleta ou malformada.")
    return itens


def integrar(base, campos, extracoes, metadados, brutos, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    conferencias = ler_campos(campos)
    itens = ler_extracoes(extracoes)
    if {x["codigo"] for x in conferencias} != set(RESUMOS) - set(INCERTOS):
        raise ValueError("Conferências do Portal divergentes.")
    ris = ler_ris(brutos, {x["id"] for x in conferencias})
    dados = json.loads(metadados.read_text(encoding="utf-8"))
    obras = {obra["id"]: obra for obra in dados["response"]["results"]}
    if len(obras) != 36 or datetime.fromisoformat(dados["consultado_em"]).date() != DATA.date():
        raise ValueError("Resposta OpenAlex inesperada.")
    livro = load_workbook(base)
    triagem, eixos = livro["Triagem"], livro["Eixos de análise"]
    ct, ce = cabecalhos(triagem), cabecalhos(eixos)
    indices = indice_unico(triagem, ct["Código"], 1317)
    registros = [{campo: triagem.cell(n, coluna).value for campo, coluna in ct.items()}
                 for n in range(2, triagem.max_row + 1)]
    por_codigo = {r["Código"]: r for r in registros}
    existentes = {}
    for numero in range(2, eixos.max_row + 1):
        chave = (eixos.cell(numero, ce["Código"]).value, eixos.cell(numero, ce["Eixo"]).value)
        if chave in existentes:
            raise ValueError(f"Eixo duplicado: {chave}")
        existentes[chave] = numero

    resumos = {}
    for codigo, hash_esperado in RESUMOS.items():
        r = por_codigo[codigo]
        obra = obras[r["Link OpenAlex"]]
        resumo = reconstruir_resumo(obra["abstract_inverted_index"])
        if (hashlib.sha256(resumo.encode("utf-8")).hexdigest() != hash_esperado
                or normalizar_doi(obra["doi"]) != normalizar_doi(r["DOI"])
                or r["Fonte"] != "Portal CAPES" or r["Decisão de elegibilidade"] != "Pendente"
                or r["Publicação em 2020–2026"] != "Publicação 2020–2026 confirmada"
                or r["Produção acadêmica"] != "Sim"
                or r["Afiliação em Goiás"] != "Sim"
                or r["Duplicidade"] != "Não verificada"
                or not tem_termo(resumo)):
            raise ValueError(f"Estado ou resumo divergente: {codigo}")
        resumos[codigo] = resumo

    auditoria = livro.create_sheet("Portal prioritário")
    auditoria.append(["Código", "Decisão", "Fundamento", "Material e limites"])
    for item in conferencias:
        codigo = item["codigo"]
        r = por_codigo[codigo]
        obra = obras[r["Link OpenAlex"]]
        arquivo, tags = ris[item["id"]]
        for campo, tag, chave in (("Título", "TI", "titulo"), ("Autoria", "AU", "autoria"),
                                  ("Ano de publicação", "PY", "ano"), ("DOI", "DO", "doi")):
            if (len(tags.get(tag, [])) != 1 or texto(tags[tag][0]) != texto(item[chave])
                    or texto(r[campo]) != texto(item[chave])):
                raise ValueError(f"Identidade RIS divergente: {codigo}/{campo}")
        titulo, titulo_oa = map(texto_comparavel, (r["Título"], obra["display_name"]))
        instituicoes = {i["display_name"] for a in obra["authorships"] for i in a["institutions"]}
        publicacao = date.fromisoformat(obra["publication_date"])
        if (not arquivo.startswith("portal-capes__goias-page") or tags.get("AB") or tags.get("KW")
                or r["Link OpenAlex"] != f"https://openalex.org/{item['id']}"
                or r["Link da fonte"] != URL + item["id"] or r["Resumo"] is not None
                or r["Tipo de produção"] != "Artigo" or obra["type"] != "article"
                or not (titulo == titulo_oa or titulo_oa.startswith(titulo + " "))
                or publicacao.year != int(item["ano"]) or not date(2020, 1, 1) <= publicacao <= CORTE
                or not instituicoes & INSTITUICOES_GOIANAS
                or r["Relação com PIBID"] != "Relação substantiva com PIBID"
                or r["Triagem de título e resumo"] != "Avançar para avaliação"):
            raise ValueError(f"Critérios ou origem divergentes: {codigo}")
        candidatos = candidatos_duplicidade(r, registros)
        esperados = ["dd5b9244"] if codigo == "4a213f79" else []
        if candidatos != esperados:
            raise ValueError(f"Candidatos de duplicidade divergentes: {codigo}: {candidatos}")
        if candidatos:
            outro = por_codigo[candidatos[0]]
            if (outro["Tipo de produção"] != "Tese" or outro["Autoria"] == r["Autoria"]
                    or outro["DOI"] is not None):
                raise ValueError("Metadados do candidato de duplicidade divergentes.")
        linha = indices[codigo]
        triagem.cell(linha, ct["Decisão de elegibilidade"]).value = "Incluir"
        acrescentar(triagem.cell(linha, ct["Limitações e pendências"]), LIMITE_INCLUSAO)
        limite = LIMITE_INCLUSAO + " " + item["limites"]
        if candidatos:
            limite += " Título semelhante ao de dd5b9244: tese de outra autoria, sem DOI; duplicata não confirmada."
            acrescentar(triagem.cell(linha, ct["Limitações e pendências"]),
                       "Candidato dd5b9244 é tese de outra autoria, sem DOI; duplicata não confirmada.")
        auditoria.append([codigo, "Incluir", item["evidencia"],
                          f"RIS {arquivo}; OpenAlex {publicacao.isoformat()}; {limite}"])

    for codigo, fundamento in INCERTOS.items():
        r = por_codigo[codigo]
        if r["Relação com PIBID"] != "Incerto" or r["Triagem de título e resumo"] != "Pendente":
            raise ValueError(f"Estado temático divergente: {codigo}")
        limite = ("Reavaliação em 15/11/2026: " + fundamento
                  + " Incerteza temática, não decorrente da falta do resumo na planilha; "
                  "não houve nova consulta individual.")
        acrescentar(triagem.cell(indices[codigo], ct["Limitações e pendências"]), limite)
        auditoria.append([codigo, "Pendente", fundamento, "Resumo OpenAlex arquivado em 15/11/2026. " + limite])

    campos_eixo = ("Estado", "Achado ou observação", "Trecho ou localização", "Tipo de fonte",
                   "Link ou referência consultada", "Limites da evidência", "Revisor", "Data")
    for item in itens:
        codigo, eixo = item["codigo"], EIXOS_CODIGO[item["eixo"]]
        numero = existentes.get((codigo, eixo))
        if not numero:
            raise ValueError(f"Eixo ausente: {codigo}/{eixo}")
        if (eixos.cell(numero, ce["Título"]).value != por_codigo[codigo]["Título"]
                or any(eixos.cell(numero, ce[campo]).value is not None for campo in campos_eixo)):
            raise ValueError(f"Eixo anteriormente preenchido ou título divergente: {codigo}/{eixo}")
        if item["trecho"] and item["trecho"].casefold() not in resumos[codigo].casefold():
            raise ValueError(f"Trecho não localizado no resumo: {codigo}/{eixo}")
        valores = {
            "Estado": OPCOES["eixo"][item["estado"]],
            "Achado ou observação": item["sintese"],
            "Trecho ou localização": (f"Resumo OpenAlex: {item['trecho']}" if item["trecho"]
                                     else "Resumo OpenAlex completo; informação não identificada."),
            "Tipo de fonte": "Título e resumo OpenAlex arquivado",
            "Link ou referência consultada": por_codigo[codigo]["Link OpenAlex"],
            "Limites da evidência": (item["limite"] + " Análise do resumo arquivado em 15/11/2026, "
                                     "não independente; não equivale à leitura integral nem comprova "
                                     "o conteúdo exibido no corte da coleta."),
            "Revisor": "Análise computacional e documental preliminar não independente",
            "Data": DATA,
        }
        for campo, valor in valores.items():
            eixos.cell(numero, ce[campo]).value = valor
    anexar_tabela(auditoria, "PortalPrioritario")
    livro["Limites da integração"].append([
        "Após a priorização histórica, oito inclusões operacionais e 15 extrações de eixo foram "
        "registradas com qualidade documental reduzida; duas dúvidas temáticas permanecem. "
        "Consultar Triagem e Portal prioritário para o estado atual; Priorização lote é retrato anterior."
    ])
    livro.save(saida)
    livro.close()


if __name__ == "__main__":
    integrar(BASE, CAMPOS, EXTRACOES, METADADOS, BRUTOS, SAIDA)
    print(f"Base criada: {SAIDA}")
