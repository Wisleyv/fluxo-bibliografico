"""Apply the documented pilot assessments to a separate workbook."""

import csv
import json
from datetime import date, datetime
from pathlib import Path

from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parent.parent
ANALISES = ROOT / "dados" / "analises"
BASE = ANALISES / "triagem_base_diagnostico_20261115.xlsx"
METADADOS = ANALISES / "openalex_piloto_20261115.json"
AVALIACOES = ANALISES / "avaliacao_piloto_20261115.csv"
EIXOS = ANALISES / "extracao_eixos_piloto_20261115.csv"
SAIDA = ANALISES / "triagem_piloto_20261115_criterio_aprovado.xlsx"
CORTE = date(2026, 11, 8)
INSTITUICOES_GOIANAS = {
    "Universidade Federal de Goiás",
    "Universidade Estadual de Goiás",
    "Universidade Federal de Catalão",
    "Instituto Federal de Goiás",
    "Instituto Federal Goiano",
    "Secretaria de Estado da Educação de Goiás",
}


def ler_csv(caminho):
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    if not linhas or any(None in linha or None in linha.values() for linha in linhas):
        raise ValueError(f"CSV vazio ou malformado: {caminho}")
    return linhas


def colunas(aba):
    cabecalhos = [celula.value for celula in aba[1]]
    if len(cabecalhos) != len(set(cabecalhos)):
        raise ValueError(f"Cabeçalhos repetidos em {aba.title}")
    return {nome: indice for indice, nome in enumerate(cabecalhos, 1)}


def normalizar_doi(valor):
    return str(valor or "").strip().lower().removeprefix("https://doi.org/")


def main():
    if SAIDA.exists():
        raise FileExistsError(f"Saída já existe; não será sobrescrita: {SAIDA}")

    dados = json.loads(METADADOS.read_text(encoding="utf-8"))
    consultado = datetime.fromisoformat(dados["consultado_em"])
    obras = dados["response"]["results"]
    por_id = {obra["id"]: obra for obra in obras}
    if len(obras) != 36 or len(por_id) != 36:
        raise ValueError("A resposta OpenAlex não contém 36 identificadores únicos")

    avaliacoes = ler_csv(AVALIACOES)
    por_codigo = {linha["codigo"]: linha for linha in avaliacoes}
    if len(avaliacoes) != 36 or len(por_codigo) != 36:
        raise ValueError("A avaliação deve conter 36 códigos únicos")

    workbook = load_workbook(BASE)
    triagem = workbook["Triagem"]
    c = colunas(triagem)
    pilotos = {
        triagem.cell(linha, c["Código"]).value: linha
        for linha in range(2, triagem.max_row + 1)
        if triagem.cell(linha, c["Piloto CAPES"]).value == "Sim"
    }
    if len(pilotos) != 36 or set(pilotos) != set(por_codigo):
        raise ValueError("Códigos da planilha e da avaliação não correspondem")

    mapa_contexto = {
        "go": "Pesquisa realizada em Goiás",
        "sem": "Sem evidência de contexto goiano",
        "incerto": "Incerto",
    }
    mapa_pibid = {
        "substantiva": "Relação substantiva com PIBID",
        "incerto": "Incerto",
    }
    for codigo, numero_linha in pilotos.items():
        avaliacao = por_codigo[codigo]
        link = triagem.cell(numero_linha, c["Link OpenAlex"]).value
        obra = por_id[link]
        if normalizar_doi(obra["doi"]) != normalizar_doi(
            triagem.cell(numero_linha, c["DOI"]).value
        ):
            raise ValueError(f"DOI divergente: {codigo}")
        data_publicacao = date.fromisoformat(obra["publication_date"])
        if (
            data_publicacao.year != obra["publication_year"]
            or str(data_publicacao.year)
            != str(triagem.cell(numero_linha, c["Ano de publicação"]).value)
            or not date(2020, 1, 1) <= data_publicacao <= CORTE
        ):
            raise ValueError(f"Data de publicação divergente ou fora do recorte: {codigo}")
        if obra["type"] != "article" or not obra["abstract_inverted_index"]:
            raise ValueError(f"Tipo ou resumo inesperado: {codigo}")

        afiliacoes = []
        instituicoes = set()
        for autoria in obra["authorships"]:
            nome = autoria["author"]["display_name"]
            nomes = [
                instituicao["display_name"]
                for instituicao in autoria["institutions"]
                if instituicao.get("display_name")
            ]
            instituicoes.update(nomes)
            afiliacoes.append(f"{nome}: {', '.join(nomes) if nomes else 'não informada'}")
        tem_go = bool(instituicoes & INSTITUICOES_GOIANAS)
        contexto = mapa_contexto[avaliacao["contexto"]]
        relacao = mapa_pibid[avaliacao["pibid"]]
        avancar = (
            (avaliacao["contexto"] == "go" or tem_go)
            and avaliacao["pibid"] == "substantiva"
        )
        valores = {
            "Afiliações de autoria": "; ".join(afiliacoes) if afiliacoes else None,
            "Relação com PIBID": relacao,
            "Contexto de Goiás": contexto,
            "Publicação em 2020–2026": "Publicação 2020–2026 confirmada",
            "Produção acadêmica": "Sim",
            "Triagem de título e resumo": "Avançar para avaliação" if avancar else "Pendente",
            "Decisão de elegibilidade": "Pendente",
            "Evidência do contexto": avaliacao["nota"],
            "Afiliação em Goiás": "Sim" if tem_go else "Incerto",
            "Evidência da afiliação": (
                "OpenAlex informa: " + ", ".join(sorted(instituicoes & INSTITUICOES_GOIANAS))
                if tem_go
                else "Afiliações OpenAlex não confirmam ausência de vínculo goiano."
            ),
            "Fontes das evidências": link,
            "Material consultado": "Título CAPES; resumo e metadados OpenAlex.",
            "Limitações e pendências": (
                "Análise preliminar não validada; verificar fonte primária, duplicidade e "
                "afiliações. O resumo não substitui necessariamente o texto integral."
            ),
            "Observações": (
                f"Consulta OpenAlex em {consultado.date().isoformat()}; "
                "critérios de contexto ou afiliação; classificação sujeita à revisão."
            ),
            "Data da triagem": consultado.date(),
        }
        for nome, valor in valores.items():
            triagem.cell(numero_linha, c[nome]).value = valor

    eixos = workbook["Eixos de análise"]
    ce = colunas(eixos)
    posicoes = {
        (eixos.cell(linha, ce["Código"]).value, eixos.cell(linha, ce["Eixo"]).value): linha
        for linha in range(2, eixos.max_row + 1)
    }
    extracoes = ler_csv(EIXOS)
    chaves = [(linha["codigo"], linha["eixo"]) for linha in extracoes]
    if len(chaves) != 9 or len(set(chaves)) != 9:
        raise ValueError("A extração piloto deve conter nove pares código/eixo únicos")
    for extracao in extracoes:
        codigo = extracao["codigo"]
        numero_linha = posicoes[(codigo, extracao["eixo"])]
        if extracao["estado"] not in {"Presente", "Não informado", "Não verificável", "Pendente"}:
            raise ValueError(f"Estado de eixo inválido: {codigo}")
        link = triagem.cell(pilotos[codigo], c["Link OpenAlex"]).value
        valores = {
            "Estado": extracao["estado"],
            "Achado ou observação": extracao["achado"],
            "Trecho ou localização": "Resumo OpenAlex; síntese, não transcrição.",
            "Tipo de fonte": "Resumo",
            "Link ou referência consultada": link,
            "Limites da evidência": (
                extracao["limite"] + " Extração piloto preliminar; elegibilidade pendente."
            ),
            "Data": consultado.date(),
        }
        for nome, valor in valores.items():
            eixos.cell(numero_linha, ce[nome]).value = valor

    with SAIDA.open("xb") as arquivo:
        workbook.save(arquivo)
    print(f"Planilha criada: {SAIDA}")
    print(f"Registros piloto: {len(pilotos)}; extrações de eixo: {len(extracoes)}")


if __name__ == "__main__":
    main()
