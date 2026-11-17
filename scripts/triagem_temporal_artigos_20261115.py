"""Confere e aplica o critério temporal aos artigos pendentes."""

import re
from collections import defaultdict
from datetime import datetime
from html import unescape
from pathlib import Path

from openpyxl import load_workbook

from scripts.integrar_autoavaliacao_20261115 import anexar_tabela, indice_unico
from scripts.normalize_collection import _parse_ris
from scripts.preanalise_e_validacao_20261115 import ano, cabecalhos, texto_normalizado
from scripts.preparar_piloto_20261115 import normalizar_doi


RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_scielo_recentes_20261115.xlsx"
SAIDA = ANALISES / "triagem_temporal_artigos_20261115.xlsx"
BRUTOS = RAIZ / "dados" / "brutos"
DATA = datetime(2026, 11, 15)


def texto_comparavel(valor):
    return re.sub(r"[^a-z0-9]+", " ", texto_normalizado(unescape(str(valor or "")))).strip()


def indice_ris(brutos):
    portais = sorted((brutos / "portal-capes").glob("*.ris"))
    scielo = sorted((brutos / "scielo").glob("*.ris"))
    if len(portais) != 5 or len(scielo) != 1:
        raise ValueError("Quantidade inesperada de arquivos RIS.")
    indice = defaultdict(list)
    for fonte, arquivos in (("Portal CAPES", portais), ("SciELO", scielo)):
        for arquivo in arquivos:
            for tags, problemas in _parse_ris(arquivo):
                titulo = tags.get("TI", [])
                if len(titulo) != 1 or not titulo[0].strip():
                    raise ValueError(f"Título ausente ou ambíguo em {arquivo.name}")
                indice[(fonte, texto_comparavel(titulo[0]))].append((arquivo, tags, problemas))
    return indice


def conferir_ris(registro, indice):
    codigo = registro["Código"]
    candidatos = indice.get((registro["Fonte"], texto_comparavel(registro["Título"])), [])
    if len(candidatos) != 1:
        raise ValueError(f"Correspondência RIS ausente ou ambígua: {codigo}")
    arquivo, tags, problemas = candidatos[0]
    if problemas:
        raise ValueError(f"Problema de leitura RIS: {codigo}: {problemas}")
    anos = tags.get("PY", [])
    if len(anos) != 1 or not re.fullmatch(r"\d{4}", anos[0].strip()):
        raise ValueError(f"Ano de publicação RIS ausente ou ambíguo: {codigo}")
    ano_publicacao = ano(registro["Ano de publicação"])
    if ano_publicacao is None or ano_publicacao >= 2020 or int(anos[0]) != ano_publicacao:
        raise ValueError(f"Ano de publicação divergente ou fora do lote: {codigo}")
    for data in tags.get("DA", []):
        if data.strip():
            match = re.match(r"^(\d{4})(?:\b|/)", data.strip())
            if not match or int(match.group(1)) != ano_publicacao:
                raise ValueError(f"Data RIS divergente: {codigo}")
    autores = " ".join(tags.get("AU") or tags.get("A1") or [])
    if not autores or sorted(texto_comparavel(autores).split()) != sorted(texto_comparavel(registro["Autoria"]).split()):
        raise ValueError(f"Autoria divergente ou ausente: {codigo}")
    doi_ris = (tags.get("DO") or [""])[0]
    if registro["DOI"] and doi_ris and normalizar_doi(registro["DOI"]) != normalizar_doi(doi_ris):
        raise ValueError(f"DOI divergente: {codigo}")
    return arquivo, tags


def integrar(base, brutos, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    indice = indice_ris(brutos)
    livro = load_workbook(base)
    triagem = livro["Triagem"]
    col = cabecalhos(triagem)
    indices = indice_unico(triagem, col["Código"], 1317)
    selecionados = []
    for codigo, numero in indices.items():
        registro = {campo: triagem.cell(numero, coluna).value for campo, coluna in col.items()}
        if (registro["Publicação em 2020–2026"] == "Publicação fora de 2020–2026"
                and registro["Triagem de título e resumo"] == "Pendente"):
            if registro["Fonte"] not in {"Portal CAPES", "SciELO"}:
                raise ValueError(f"Fonte inesperada: {codigo}")
            if registro["Decisão de elegibilidade"] != "Não iniciada" or registro["Motivo da exclusão"]:
                raise ValueError(f"Estado anterior requer conciliação: {codigo}")
            arquivo, tags = conferir_ris(registro, indice)
            selecionados.append((codigo, numero, registro, arquivo, tags))
    if len(selecionados) != 85:
        raise ValueError(f"Esperados 85 registros pendentes; encontrados {len(selecionados)}.")

    auditoria = livro.create_sheet("Triagem temporal artigos")
    auditoria.append(["Código", "Fonte", "Título", "Tipo informado", "Ano de publicação",
                      "Arquivo RIS original", "Campo PY", "Campo DA", "Identificador no RIS",
                      "Triagem anterior", "Triagem revisada", "Limites"])
    for codigo, numero, registro, arquivo, tags in selecionados:
        campo = lambda nome: triagem.cell(numero, col[nome])
        caminho = str(arquivo.relative_to(RAIZ))
        evidencia = f"Triagem temporal 15/11/2026: publicação em {registro['Ano de publicação']}, confirmada pelo campo PY em {caminho}."
        limite = (
            "Exclusão preliminar somente do recorte goiano 2020–2026; o registro permanece disponível "
            "para o panorama nacional. Não foi feita análise semântica, de elegibilidade final nem de duplicidade nesta etapa."
        )
        campo("Triagem de título e resumo").value = "Excluir"
        campo("Decisão de elegibilidade").value = "Pendente"
        campo("Motivo da exclusão").value = "Fora do período"
        for nome, texto in {
            "Fontes das evidências": evidencia,
            "Material consultado": "Metadados de título, autoria, ano e identificador nos arquivos RIS locais.",
            "Limitações e pendências": limite,
            "Observações": "Triagem por ano de publicação; não implica exclusão do panorama nacional.",
        }.items():
            celula = campo(nome)
            valor = f"{celula.value}\n{texto}" if celula.value else texto
            if len(valor) > 32767:
                raise ValueError(f"Texto excede limite do Excel: {codigo}, {nome}")
            celula.value = valor
        campo("Revisor").value = "Conferência computacional temporal não independente"
        campo("Data da triagem").value = DATA
        auditoria.append([
            codigo, registro["Fonte"], registro["Título"], registro["Tipo de produção"],
            registro["Ano de publicação"], caminho, "; ".join(tags.get("PY", [])),
            "; ".join(tags.get("DA", [])) or "Não informado",
            "; ".join(tags.get("ID", [])) or "; ".join(tags.get("DO", [])) or "Não informado",
            registro["Triagem de título e resumo"], "Excluir", limite,
        ])
    anexar_tabela(auditoria, "TriagemTemporalArtigos")
    livro["Limites da integração"].append([
        "85 registros previamente pendentes receberam triagem temporal preliminar fora do recorte de Goiás, "
        "com ano conferido nos RIS locais; ver aba Triagem temporal artigos. Permanecem no panorama nacional."
    ])
    livro.save(saida)


if __name__ == "__main__":
    integrar(BASE, BRUTOS, SAIDA)
    print(f"Base criada: {SAIDA}")
