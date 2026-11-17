"""Compara candidatos entre fontes e reaproveita três avaliações documentais."""

import re
from collections import Counter, defaultdict
from copy import copy
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

from scripts.conferir_amostra_por_regras_20261115 import titulo_normalizado
from scripts.conferir_catalogo_resumos_20261115 import identificador, ler_originais
from scripts.integrar_autoavaliacao_20261115 import EIXOS, anexar_tabela, indice_unico
from scripts.integrar_catalogo_lote2_20261115 import BRUTO, REVISOR
from scripts.integrar_teses_e_datas_uel_20261115 import (
    acrescentar, autores_comparaveis, instituicao_comparavel,
)
from scripts.preanalise_e_validacao_20261115 import cabecalhos, texto_normalizado

RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_catalogo_lote5_20261115.xlsx"
SAIDA = ANALISES / "triagem_fontes_cruzadas_20261115.xlsx"
DATA = datetime(2026, 11, 15)
PARES_REAPROVEITADOS = {
    "d0accc2b": "8e68ac12",
    "417d0d90": "fa78dc43",
    "8f150364": "969dc972",
}
ESTADOS_ESPERADOS = {
    "8e68ac12": ("Presente", "Não informado", "Não verificável"),
    "fa78dc43": ("Presente", "Presente", "Não informado"),
    "969dc972": ("Presente", "Não informado", "Presente"),
}


def texto_resumo(valor):
    return re.sub(r"\s+", " ", texto_normalizado(valor)).strip()


def instituicoes_compativeis(a, b):
    a, b = instituicao_comparavel(a), instituicao_comparavel(b)
    if not a or not b:
        return False
    return a == b or (a == "universidade estadual paulista"
                      and b.startswith("universidade estadual paulista julio de mesquita filho"))


def integrar(base, bruto, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    livro = load_workbook(base)
    triagem, eixos = livro["Triagem"], livro["Eixos de análise"]
    ct, ce = cabecalhos(triagem), cabecalhos(eixos)
    indices = indice_unico(triagem, ct["Código"], 1317)
    obter = lambda codigo, campo: triagem.cell(indices[codigo], ct[campo]).value

    grupos = defaultdict(list)
    for grupo, codigo, fonte, *_ in list(livro["Possíveis duplicatas"].values)[1:]:
        if codigo not in indices or obter(codigo, "Fonte") != fonte:
            raise ValueError(f"Inventário de candidatos divergente: {codigo}")
        grupos[grupo].append((codigo, fonte))
    cruzados = [(nome, v) for nome, v in grupos.items()
                if {fonte for _, fonte in v} in (
                    {"BDTD", "Catálogo CAPES"}, {"BDTD", "SciELO"})]
    composicao = Counter(tuple(sorted({fonte for _, fonte in grupo})) for _, grupo in cruzados)
    if composicao != {("BDTD", "Catálogo CAPES"): 35, ("BDTD", "SciELO"): 2}:
        raise ValueError("Seleção dos grupos entre fontes divergente.")

    capes = {codigo for _, grupo in cruzados for codigo, fonte in grupo if fonte == "Catálogo CAPES"}
    originais = ler_originais(bruto, {identificador(obter(c, "Link da fonte")) for c in capes})
    for codigo in capes:
        original = originais[identificador(obter(codigo, "Link da fonte"))]
        if any(obter(codigo, campo) != original[chave] for campo, chave in (
            ("Título", "NM_PRODUCAO"), ("Autoria", "NM_DISCENTE"), ("Resumo", "DS_RESUMO"),
            ("Link da fonte", "DS_URL_TEXTO_COMPLETO"),
        )):
            raise ValueError(f"Metadados CAPES divergentes: {codigo}")

    eixo_por_chave = {}
    for numero in range(2, eixos.max_row + 1):
        chave = (eixos.cell(numero, ce["Código"]).value, eixos.cell(numero, ce["Eixo"]).value)
        if chave in eixo_por_chave:
            raise ValueError(f"Eixo repetido: {chave}")
        eixo_por_chave[chave] = numero

    auditoria = livro.create_sheet("Comparação entre fontes")
    auditoria.append([
        "Grupo anterior", "Código BDTD", "Código outra fonte", "Outra fonte",
        "Autoria normalizada", "Tipos informados", "Anos informados",
        "Instituição", "Resumos preservados", "Links das fontes",
        "Tratamento e limites",
    ])
    pares_encontrados = set()
    for nome_grupo, grupo in cruzados:
        outro, fonte = next((codigo, fonte) for codigo, fonte in grupo if fonte != "BDTD")
        for codigo, origem in grupo:
            if origem != "BDTD":
                continue
            if (not obter(codigo, "Título") or
                    titulo_normalizado(obter(codigo, "Título")) != titulo_normalizado(obter(outro, "Título"))):
                raise ValueError(f"Títulos divergentes: {codigo}/{outro}")
            pares_encontrados.add((codigo, outro))
            autor_a, autor_b = obter(codigo, "Autoria"), obter(outro, "Autoria")
            autores = ("Concordam após normalização" if autor_a and autor_b
                       and autores_comparaveis(autor_a) == autores_comparaveis(autor_b)
                       else "Diferentes ou incompletas; não implica autores distintos")
            instituicao = ("Compatíveis pelos nomes" if instituicoes_compativeis(
                obter(codigo, "Instituição associada"), obter(outro, "Instituição associada"))
                else "Nomes diferentes ou não informados; não avaliado como conflito")
            res_a, res_b = texto_resumo(obter(codigo, "Resumo")), texto_resumo(obter(outro, "Resumo"))
            resumo = ("Iguais após normalização de caixa, acentos e espaços"
                      if len(res_a) >= 500 and res_a == res_b
                      else "Não iguais ou não comparáveis integralmente")
            tipo_a, tipo_b = obter(codigo, "Tipo de produção"), obter(outro, "Tipo de produção")
            ano_a, ano_b = obter(codigo, "Ano de defesa"), obter(outro, "Ano de defesa")
            pub_b = obter(outro, "Ano de publicação")
            link_a, link_b = obter(codigo, "Link da fonte"), obter(outro, "Link da fonte")
            links = ("Endereços iguais" if link_a and link_a == link_b
                     else "Endereços distintos ou ausentes; identidade comum não demonstrada")
            if fonte == "SciELO":
                tratamento = "Tese ou dissertação e artigo: produções relacionadas possíveis, não deduplicar por título."
            elif PARES_REAPROVEITADOS.get(codigo) == outro:
                tratamento = "Avaliação documental reaproveitada; duplicata entre fontes não confirmada."
            else:
                tratamento = "Candidato por título; identidade e equivalência não estabelecidas por esta comparação."
            auditoria.append([
                nome_grupo,
                codigo, outro, fonte, autores, f"BDTD: {tipo_a}; {fonte}: {tipo_b}",
                f"Defesa BDTD: {ano_a}; defesa {fonte}: {ano_b}; publicação {fonte}: {pub_b}",
                instituicao, resumo, links, tratamento,
            ])

    if len(pares_encontrados) != 38 or not set(PARES_REAPROVEITADOS.items()) <= pares_encontrados:
        raise ValueError("Pares candidatos divergentes.")

    for codigo, outro in PARES_REAPROVEITADOS.items():
        get_a = lambda campo: obter(codigo, campo)
        get_b = lambda campo: obter(outro, campo)
        if (autores_comparaveis(get_a("Autoria")) != autores_comparaveis(get_b("Autoria"))
                or get_a("Tipo de produção") != get_b("Tipo de produção")
                or not get_a("Ano de defesa") or get_a("Ano de defesa") != get_b("Ano de defesa")
                or not instituicoes_compativeis(get_a("Instituição associada"), get_b("Instituição associada"))
                or len(texto_resumo(get_a("Resumo"))) < 500
                or texto_resumo(get_a("Resumo")) != texto_resumo(get_b("Resumo"))):
            raise ValueError(f"Material ou metadados divergentes: {codigo}/{outro}")
        if (get_a("Relação com PIBID") != "Incerto" or get_a("Contexto de Goiás") != "Incerto"
                or get_a("Triagem de título e resumo") != "Pendente"
                or get_a("Decisão de elegibilidade") != "Não iniciada"
                or get_a("Duplicidade") != "Não verificada"
                or get_a("Revisor") is not None
                or get_b("Relação com PIBID") != "Tema central do estudo"
                or get_b("Contexto de Goiás") != "Sem evidência de contexto goiano"
                or get_b("Triagem de título e resumo") != "Pendente"
                or get_b("Decisão de elegibilidade") != "Pendente"
                or any((codigo, eixo) in eixo_por_chave for eixo in EIXOS.values())):
            raise ValueError(f"Estado anterior divergente: {codigo}/{outro}")
        fontes = [eixo_por_chave.get((outro, eixo)) for eixo in EIXOS.values()]
        if (not all(fontes) or tuple(eixos.cell(n, ce["Estado"]).value for n in fontes)
                != ESTADOS_ESPERADOS[outro]):
            raise ValueError(f"Extrações CAPES incompletas ou divergentes: {outro}")
        for campo in ("Relação com PIBID", "Contexto de Goiás"):
            triagem.cell(indices[codigo], ct[campo]).value = get_b(campo)
        triagem.cell(indices[codigo], ct["Decisão de elegibilidade"]).value = "Pendente"
        detalhes = (
            f"Avaliação preliminar reaproveitada de {outro}: título, autoria, tipo, ano de defesa "
            "e instituição compatíveis; resumo em português igual após normalização de caixa, "
            "acentos e espaços. Não confirma duplicidade nem substitui validação independente."
        )
        for campo, valor in {
            "Evidência do contexto": "Sem evidência de contexto goiano no material consultado; não prova ausência.",
            "Fontes das evidências": detalhes + " " + str(get_b("Fontes das evidências")),
            "Material consultado": f"Resumo BDTD e avaliação documental dos resumos do Catálogo CAPES ({outro}).",
            "Limitações e pendências": (
                "A leitura do resumo foi realizada; mantém-se a incerteza sobre publicação, afiliação "
                "e duplicidade. A instituição da tese não comprova afiliação. Elegibilidade final pendente."
            ),
            "Observações": detalhes,
        }.items():
            acrescentar(triagem.cell(indices[codigo], ct[campo]), valor)
        triagem.cell(indices[codigo], ct["Revisor"]).value = REVISOR
        triagem.cell(indices[codigo], ct["Data da triagem"]).value = DATA
        for numero_fonte in fontes:
            numero = eixos.max_row + 1
            for coluna in range(1, eixos.max_column + 1):
                eixos.cell(numero, coluna)._style = copy(eixos.cell(2, coluna)._style)
                eixos.cell(numero, coluna).value = eixos.cell(numero_fonte, coluna).value
            eixos.cell(numero, ce["Código"]).value = codigo
            eixos.cell(numero, ce["Título"]).value = get_a("Título")
            acrescentar(eixos.cell(numero, ce["Limites da evidência"]), detalhes)
    anexar_tabela(auditoria, "ComparacaoEntreFontes")
    tabela = eixos.tables["Eixos"]
    tabela.ref = f"A1:K{eixos.max_row}"
    tabela.autoFilter.ref = tabela.ref
    if len(eixos.data_validations.dataValidation) != 1:
        raise ValueError("Validação de eixos inesperada.")
    eixos.data_validations.dataValidation[0].sqref = f"D2:D{eixos.max_row}"
    livro["Limites da integração"].append([
        "Comparação de candidatos entre fontes e reaproveitamento de três avaliações; "
        "não houve confirmação de duplicata ou decisão final."
    ])
    livro.save(saida)
    livro.close()


if __name__ == "__main__":
    integrar(BASE, BRUTO, SAIDA)
    print(f"Base criada: {SAIDA}")
