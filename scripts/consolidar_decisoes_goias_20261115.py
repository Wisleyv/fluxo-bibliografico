"""Consolida decisões sustentadas por evidências já preservadas."""

import json
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

from openpyxl import load_workbook

from scripts.conferir_termos_e_resumos_20261115 import tem_termo
from scripts.integrar_autoavaliacao_20261115 import anexar_tabela, indice_unico
from scripts.integrar_teses_e_datas_uel_20261115 import acrescentar
from scripts.preanalise_e_validacao_20261115 import cabecalhos, reconstruir_resumo
from scripts.preparar_piloto_20261115 import CORTE, INSTITUICOES_GOIANAS, normalizar_doi
from scripts.triagem_temporal_artigos_20261115 import (
    BRUTOS, conferir_ris, indice_ris, texto_comparavel,
)

RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_fontes_cruzadas_20261115.xlsx"
METADADOS = ANALISES / "openalex_piloto_20261115.json"
SAIDA = ANALISES / "triagem_decisoes_goias_20261115.xlsx"
INCLUIDOS = {
    "95dee571", "22f73924", "25b844fb", "813fdfa6", "91522d0b",
    "768c2970", "e76a8964", "00683d4e", "4e3f5a3d", "796dae04", "910fa3c6",
}


def conferir_inclusao(registro, indice, obras):
    codigo = registro["Código"]
    candidatos = indice.get((registro["Fonte"], texto_comparavel(registro["Título"])), [])
    if len(candidatos) != 1:
        raise ValueError(f"RIS ausente ou ambíguo: {codigo}")
    arquivo, tags, problemas = candidatos[0]
    autores = " ".join(tags.get("AU") or tags.get("A1") or [])
    if (problemas or tags.get("PY") != [str(registro["Ano de publicação"])]
            or not autores
            or sorted(texto_comparavel(autores).split())
            != sorted(texto_comparavel(registro["Autoria"]).split())
            or not registro["DOI"] or len(tags.get("DO", [])) != 1
            or normalizar_doi(tags["DO"][0]) != normalizar_doi(registro["DOI"])):
        raise ValueError(f"Metadados RIS divergentes: {codigo}")
    for data in tags.get("DA", []):
        if data and not data.startswith(str(registro["Ano de publicação"])):
            raise ValueError(f"Data RIS divergente: {codigo}")
    if (registro["Decisão de elegibilidade"] != "Pendente"
            or registro["Triagem de título e resumo"] != "Avançar para avaliação"
            or registro["Publicação em 2020–2026"] != "Publicação 2020–2026 confirmada"
            or registro["Produção acadêmica"] != "Sim"
            or registro["Relação com PIBID"] not in {"Tema central do estudo", "Relação substantiva com PIBID"}
            or not (registro["Afiliação em Goiás"] == "Sim"
                    or registro["Contexto de Goiás"] == "Pesquisa realizada em Goiás")
            or registro["Duplicidade"] != "Não verificada"):
        raise ValueError(f"Critérios ou estado anterior divergentes: {codigo}")
    if registro["Fonte"] == "Portal CAPES":
        if not tem_termo(registro["Título"]):
            raise ValueError(f"Termo não identificado no título: {codigo}")
        obra = obras[registro["Link OpenAlex"]]
        titulo, titulo_oa = map(texto_comparavel, (registro["Título"], obra["display_name"]))
        instituicoes = {i["display_name"] for a in obra["authorships"] for i in a["institutions"]}
        data = date.fromisoformat(obra["publication_date"])
        if (not (titulo == titulo_oa or titulo_oa.startswith(titulo + " "))
                or normalizar_doi(obra["doi"]) != normalizar_doi(registro["DOI"])
                or obra["type"] != "article" or not instituicoes & INSTITUICOES_GOIANAS
                or data.year != int(registro["Ano de publicação"])
                or not date(2020, 1, 1) <= data <= CORTE
                or len(reconstruir_resumo(obra["abstract_inverted_index"])) < 500):
            raise ValueError(f"Metadados complementares divergentes: {codigo}")
        material = f"RIS {arquivo.name}; título e metadados/resumo OpenAlex; publicação {data.isoformat()}."
    elif registro["Fonte"] == "SciELO" and codigo == "910fa3c6":
        if not tem_termo(registro["Resumo"]) or int(registro["Ano de publicação"]) != 2025:
            raise ValueError(f"Evidência SciELO divergente: {codigo}")
        material = f"RIS {arquivo.name}; resumo local e metadados SciELO previamente registrados."
    else:
        raise ValueError(f"Fonte de inclusão inesperada: {codigo}")
    return material


def candidatos_duplicidade(registro, registros):
    titulo = texto_comparavel(registro["Título"])
    doi = normalizar_doi(registro["DOI"])
    candidatos = []
    for outro in registros:
        if outro["Código"] == registro["Código"]:
            continue
        titulo_outro = texto_comparavel(outro["Título"])
        mesmo_doi = doi and doi == normalizar_doi(outro["DOI"])
        prefixo = (min(len(titulo), len(titulo_outro)) >= 20
                   and (titulo.startswith(titulo_outro) or titulo_outro.startswith(titulo)))
        if mesmo_doi or prefixo or SequenceMatcher(None, titulo, titulo_outro).ratio() >= 0.80:
            candidatos.append(outro["Código"])
    return candidatos


def integrar(base, brutos, metadados, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    dados = json.loads(metadados.read_text(encoding="utf-8"))
    obras = {obra["id"]: obra for obra in dados["response"]["results"]}
    if len(obras) != 36:
        raise ValueError("Resposta OpenAlex inesperada.")
    indice = indice_ris(brutos)
    livro = load_workbook(base)
    triagem = livro["Triagem"]
    col = cabecalhos(triagem)
    indices = indice_unico(triagem, col["Código"], 1317)
    registros = [{campo: triagem.cell(n, coluna).value for campo, coluna in col.items()}
                 for n in range(2, triagem.max_row + 1)]
    por_codigo = {r["Código"]: r for r in registros}
    if not INCLUIDOS <= por_codigo.keys():
        raise ValueError("Candidatos de inclusão incompletos.")

    decisoes = []
    for codigo in sorted(INCLUIDOS):
        r = por_codigo[codigo]
        fonte = conferir_inclusao(r, indice, obras)
        candidatos = candidatos_duplicidade(r, registros)
        if candidatos:
            raise ValueError(f"Candidatos de duplicidade para {codigo}: {candidatos}")
        decisoes.append((r, "Incluir", fonte))

    for r in registros:
        if (r["Motivo da exclusão"] == "Fora do período"
                and r["Fonte"] in {"Portal CAPES", "SciELO"}):
            if (r["Decisão de elegibilidade"] != "Pendente"
                    or r["Triagem de título e resumo"] != "Excluir"
                    or r["Publicação em 2020–2026"] != "Publicação fora de 2020–2026"):
                raise ValueError(f"Estado temporal divergente: {r['Código']}")
            arquivo, _ = conferir_ris(r, indice)
            decisoes.append((r, "Excluir", f"Ano de publicação conferido no campo PY de {arquivo.name}."))
    if len(decisoes) != 121 or sum(decisao == "Excluir" for _, decisao, _ in decisoes) != 110:
        raise ValueError("Quantidade de decisões divergente.")

    auditoria = livro.create_sheet("Decisões Goiás")
    auditoria.append(["Código", "Fonte", "Decisão", "Fundamento", "Material e limites"])
    for registro, decisao, material in decisoes:
        codigo = registro["Código"]
        celula = lambda campo: triagem.cell(indices[codigo], col[campo])
        celula("Decisão de elegibilidade").value = decisao
        if decisao == "Incluir":
            fundamento = "PIBID, período, produção acadêmica e contexto ou afiliação em Goiás."
            limite = (
                "Inclusão no recorte goiano com as evidências disponíveis; análise não independente. "
                "Busca local de duplicidade sem candidato não prova ausência de duplicatas. "
                "Dados e resultados continuam sujeitos às limitações das fontes e dos resumos."
            )
        else:
            fundamento = "Ano de publicação anterior a 2020."
            limite = (
                "Exclusão somente da revisão goiana de 2020–2026; o registro permanece disponível "
                "para análise do panorama nacional. Não foi decidida a pertinência temática nacional."
            )
        acrescentar(celula("Observações"), "Decisão do recorte goiano: " + decisao + ". " + limite)
        acrescentar(celula("Limitações e pendências"),
                   "Consolidação do recorte goiano: a decisão de elegibilidade foi registrada. " + limite)
        auditoria.append([codigo, registro["Fonte"], decisao, fundamento, material + " " + limite])
    anexar_tabela(auditoria, "DecisoesGoias")
    livro["Limites da integração"].append([
        "11 inclusões e 110 exclusões temporais na revisão goiana, com evidências disponíveis; "
        "não constituem validação independente nem excluem artigos do panorama nacional."
    ])
    livro.save(saida)
    livro.close()


if __name__ == "__main__":
    integrar(BASE, BRUTOS, METADADOS, SAIDA)
    print(f"Base criada: {SAIDA}")
