"""Aplicar decisões registradas à cópia da amostra, sem alterar a amostra cega."""

import csv
import hashlib
from pathlib import Path

from openpyxl import load_workbook

from scripts.preanalise_e_validacao_20261115 import ano


RAIZ = Path(__file__).resolve().parents[1]
BASE = RAIZ / "dados" / "analises" / "validacao_independente_60_20261115.xlsx"
DECISOES = RAIZ / "dados" / "analises" / "decisoes_autoavaliacao_60_20261115.csv"
SAIDA = RAIZ / "dados" / "analises" / "amostra_60_autoavaliacao_20261115.xlsx"
DATA = "15/11/2026"

OPCOES = {
    "pibid": {
        "T": "Tema central do estudo",
        "S": "Relação substantiva com PIBID",
        "M": "Menção incidental",
        "I": "Incerto",
    },
    "contexto": {
        "G": "Pesquisa realizada em Goiás",
        "N": "Sem evidência de contexto goiano",
        "I": "Incerto",
    },
    "afiliacao": {"S": "Sim", "I": "Incerto"},
    "periodo": {
        "C": "Publicação 2020–2026 confirmada",
        "F": "Publicação fora de 2020–2026",
        "D": "Só ano de defesa disponível",
        "I": "Incerto",
    },
    "tipo": {"S": "Sim", "I": "Incerto"},
    "triagem": {"A": "Avançar para avaliação", "E": "Excluir", "P": "Pendente"},
    "eixo": {"P": "Presente", "N": "Não informado", "V": "Não verificável"},
}

FONTES_ADICIONAIS = {
    "06792f41": "Repositório UnB: https://repositorio.unb.br/handle/10482/51101",
    "c3920958": "Repositório UnB: https://repositorio.unb.br/handle/10482/38162",
    "1bfed0a9": "Repositório Unicamp: https://hdl.handle.net/20.500.12733/1634422",
    "e03ee3e1": "Repositório FURG: http://repositorio.furg.br/handle/1/3634",
    "46baf45a": "Repositório UEM: http://repositorio.uem.br:8080/jspui/handle/1/4692",
    "7b83d4de": "Biblioteca UFABC: https://biblioteca.ufabc.edu.br/index.php?codigo_sophia=47455&midiaext=42770",
    "fe4d6c4f": "Crossref: https://api.crossref.org/works/10.1590%2F1980531411328",
    "5dbf2cee": "Repositório IF Goiano: https://repositorio.ifgoiano.edu.br/handle/prefix/2162",
}


def ler_decisoes(caminho):
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    por_codigo = {}
    for linha in linhas:
        codigo = linha["codigo"]
        if not codigo or codigo in por_codigo:
            raise ValueError(f"Código ausente ou repetido: {codigo!r}")
        if not linha["evidencia"] or not linha["limites"]:
            raise ValueError(f"Evidência ou limitação ausente: {codigo}")
        for campo in ("pibid", "contexto", "afiliacao", "periodo", "tipo", "triagem"):
            if linha[campo] not in OPCOES[campo]:
                raise ValueError(f"Opção inválida em {campo}: {codigo}")
        if len(linha["eixos"]) != 3 or any(v not in OPCOES["eixo"] for v in linha["eixos"]):
            raise ValueError(f"Eixos inválidos: {codigo}")
        if linha["triagem"] == "A" and not (
            linha["pibid"] in {"T", "S"}
            and (linha["contexto"] == "G" or linha["afiliacao"] == "S")
            and linha["periodo"] == "C"
            and linha["tipo"] == "S"
        ):
            raise ValueError(f"Avanço sem requisitos suficientes: {codigo}")
        if linha["triagem"] == "E" and linha["periodo"] != "F":
            raise ValueError(f"Exclusão sem ano de publicação fora do recorte: {codigo}")
        por_codigo[codigo] = linha
    return por_codigo


def preencher(base, decisoes, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    hash_base = hashlib.sha256(base.read_bytes()).hexdigest()
    avaliacoes = ler_decisoes(decisoes)
    workbook = load_workbook(base)
    aba = workbook["Avaliação independente"]
    codigos = [aba.cell(i, 1).value for i in range(2, aba.max_row + 1)]
    if len(codigos) != 60 or len(set(codigos)) != 60 or set(codigos) != set(avaliacoes):
        raise ValueError("A amostra e as decisões devem conter os mesmos 60 códigos únicos.")

    aba.title = "Autoavaliação"
    aba.cell(1, 21).value = "Triagem da autoavaliação"
    tabela = next(iter(aba.tables.values()))
    tabela.displayName = "Autoavaliacao"
    tabela.name = "Autoavaliacao"
    tabela.tableColumns[20].name = "Triagem da autoavaliação"
    for numero in range(2, aba.max_row + 1):
        codigo = aba.cell(numero, 1).value
        linha = avaliacoes[codigo]
        if linha["periodo"] == "F":
            ano_publicacao = ano(aba.cell(numero, 6).value)
            if ano_publicacao is None or 2020 <= ano_publicacao <= 2026:
                raise ValueError(f"Exclusão temporal sem publicação fora do período: {codigo}")
        if codigo == "06792f41":
            aba.cell(numero, 6).value = 2024
        if codigo in {"06792f41", "1bfed0a9", "e03ee3e1"}:
            aba.cell(numero, 8).value = "Não"
        evid = linha["evidencia"]
        if codigo in FONTES_ADICIONAIS:
            evid += f" Fonte adicional consultada em {DATA}: {FONTES_ADICIONAIS[codigo]}."
        elif codigo == "83224e28":
            evid += " Fonte cruzada: resumo do registro SciELO 387c5254, na própria amostra."
        else:
            evid += " Fonte: metadados e material local da linha."
        valores = [
            OPCOES["pibid"][linha["pibid"]],
            OPCOES["contexto"][linha["contexto"]],
            OPCOES["afiliacao"][linha["afiliacao"]],
            OPCOES["periodo"][linha["periodo"]],
            OPCOES["tipo"][linha["tipo"]],
            OPCOES["triagem"][linha["triagem"]],
            *(OPCOES["eixo"][v] for v in linha["eixos"]),
            evid,
            linha["limites"],
            DATA,
            "Autoavaliação computacional; não independente",
        ]
        for coluna, valor in enumerate(valores, 16):
            aba.cell(numero, coluna).value = valor

    instrucoes = workbook["Instruções"]
    textos = [
        "Autoavaliação computacional — 60 registros; NÃO é validação independente.",
        "A mesma assistência participou da pré-análise e da revisão. Não calcular acurácia ou confiança por esta comparação.",
        "Decisões provisórias para o recorte de Goiás 2020–2026; exclusões temporais não excluem o panorama nacional.",
        "A evidência identifica o material local ou fonte adicional; consultas pontuais realizadas em 15/11/2026.",
        "Ano de defesa não equivale automaticamente a publicação; 2026 exige data até 08/11/2026.",
        "Contexto e afiliação em Goiás são distintos; ausência de informação não prova ausência no estudo.",
        "Nos eixos, Não informado limita-se ao material examinado; Não verificável indica material insuficiente.",
        "Resumo disponível refere-se à célula local; textos de referência ou orientação não são resumos substantivos.",
        "O formulário cego original e o manifesto do sorteio permanecem preservados; revisão independente ainda necessária.",
    ]
    for i, texto in enumerate(textos, 1):
        instrucoes.cell(i, 1).value = texto
    workbook.save(saida)
    if hashlib.sha256(base.read_bytes()).hexdigest() != hash_base:
        raise RuntimeError("A amostra original mudou durante o preenchimento.")


if __name__ == "__main__":
    preencher(BASE, DECISOES, SAIDA)
    print(f"Planilha criada: {SAIDA}")
