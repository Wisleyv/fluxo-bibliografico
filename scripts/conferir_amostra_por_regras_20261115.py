"""Compara sinais reproduzíveis da amostra cega com a autoavaliação."""

import re
from collections import Counter, defaultdict
from pathlib import Path

from openpyxl import Workbook, load_workbook

from scripts.integrar_autoavaliacao_20261115 import anexar_tabela, indice_unico
from scripts.preanalise_e_validacao_20261115 import (
    PADRAO_GO,
    PADRAO_TEMA,
    cabecalhos,
    periodo,
    sinal,
    texto_normalizado,
)
from scripts.preparar_piloto_20261115 import normalizar_doi


RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
CEGA = ANALISES / "validacao_independente_60_20261115.xlsx"
AUTO = ANALISES / "amostra_60_autoavaliacao_20261115.xlsx"
BASE = ANALISES / "triagem_integrada_autoavaliacao_20261115.xlsx"
SAIDA = ANALISES / "conferencia_por_regras_60_20261115.xlsx"
PARECERES = {
    "Relação com PIBID": "Relação com PIBID",
    "Contexto de Goiás": "Contexto de Goiás",
    "Afiliação em Goiás": "Afiliação em Goiás",
    "Publicação em 2020–2026": "Publicação em 2020–2026",
    "Produção acadêmica": "Produção acadêmica",
    "Triagem da autoavaliação": "Triagem de título e resumo",
}


def titulo_normalizado(valor):
    return re.sub(r"\W+", " ", texto_normalizado(valor)).strip()


def tipo_resumo(valor):
    texto = texto_normalizado(valor).strip()
    if not texto:
        return "Campo vazio"
    if re.match(r"^orientador(?:a)?\s*:", texto):
        return "Possível informação de orientação"
    if re.match(r"^(?:dissertacao|tese)\s*\([^)]*\)\s*[-—]", texto):
        return "Possível referência bibliográfica"
    return "Texto preenchido; conteúdo não verificado por regra"


def coerencia_triagem(registro):
    decisao = registro["Triagem da autoavaliação"]
    if decisao == "Avançar para avaliação":
        valido = (
            registro["Relação com PIBID"] in {"Tema central do estudo", "Relação substantiva com PIBID"}
            and (registro["Contexto de Goiás"] == "Pesquisa realizada em Goiás"
                 or registro["Afiliação em Goiás"] == "Sim")
            and registro["Publicação em 2020–2026"] == "Publicação 2020–2026 confirmada"
            and registro["Produção acadêmica"] == "Sim"
        )
        return "Requisitos declarados compatíveis" if valido else "Requisitos declarados incompatíveis"
    if decisao == "Excluir":
        return (
            "Exclusão temporal declarada compatível"
            if registro["Publicação em 2020–2026"] == "Publicação fora de 2020–2026"
            else "Exclusão sem período fora do recorte"
        )
    if decisao == "Pendente":
        return "Pendente; regra de avanço não aplicada"
    raise ValueError(f"Triagem desconhecida: {decisao!r}")


def registros(aba, tamanho):
    colunas = cabecalhos(aba)
    indices = indice_unico(aba, colunas["Código"], tamanho)
    return {
        codigo: {nome: aba.cell(numero, coluna).value for nome, coluna in colunas.items()}
        for codigo, numero in indices.items()
    }


def analisar(cega, auto, base):
    if set(cega) != set(auto) or not set(cega).issubset(base):
        raise ValueError("Os códigos das planilhas não são compatíveis.")
    por_doi, por_titulo = defaultdict(list), defaultdict(list)
    for codigo, linha in base.items():
        doi = normalizar_doi(linha["DOI"])
        titulo = titulo_normalizado(linha["Título"])
        if doi:
            por_doi[doi].append(codigo)
        if titulo:
            por_titulo[titulo].append(codigo)

    linhas, alertas = [], []
    for codigo, bruto in cega.items():
        avaliado = auto[codigo]
        integrado = base[codigo]
        for campo in ("Título", "Fonte", "Tipo de produção", "DOI"):
            if bruto[campo] != avaliado[campo] or bruto[campo] != integrado[campo]:
                raise ValueError(f"Identificação divergente: {codigo}, {campo}")

        per = periodo(bruto["Ano de publicação"], bruto["Ano de defesa"])
        per_auto = avaliado["Publicação em 2020–2026"]
        comparacao = "Igual" if per == per_auto else "Diferente; consultar fontes e limites"
        locais = {"Título": bruto["Título"], "Resumo": bruto["Resumo"]}
        pibid = ", ".join(sinal(locais, PADRAO_TEMA)) or "Nenhum sinal literal identificado"
        go = ", ".join(sinal(locais, PADRAO_GO)) or "Nenhum sinal literal identificado"
        tipo = tipo_resumo(bruto["Resumo"])
        doi = normalizar_doi(bruto["DOI"])
        titulo = titulo_normalizado(bruto["Título"])
        outros_dois = sorted(x for x in por_doi.get(doi, []) if x != codigo) if doi else []
        outros_titulos = sorted(x for x in por_titulo.get(titulo, []) if x != codigo) if titulo else []
        consistencia = coerencia_triagem(avaliado)
        diferencas = [
            f"{campo}: auto={avaliado[campo]}; base={integrado[destino]}"
            for campo, destino in PARECERES.items()
            if avaliado[campo] != integrado[destino]
        ]
        linhas.append([
            codigo, bruto["Fonte"], bruto["Título"], per, per_auto, comparacao,
            pibid, go, tipo, ", ".join(outros_dois) or "Nenhum candidato por DOI",
            ", ".join(outros_titulos) or "Nenhum candidato por título exato",
            consistencia, " | ".join(diferencas) or "Sem diferença nos seis campos",
            avaliado["Evidência e localização"], avaliado["Limites e pendências"],
        ])

        def alerta(categoria, detalhe):
            alertas.append([codigo, categoria, detalhe, avaliado["Evidência e localização"],
                            avaliado["Limites e pendências"]])

        if per != per_auto:
            alerta("Período entre versões", f"Dados cegos: {per}; autoavaliação: {per_auto}.")
        if tipo.startswith("Possível"):
            alerta("Campo resumo", f"{tipo}; não presumir resumo substantivo.")
        if (avaliado["Relação com PIBID"] in {"Tema central do estudo", "Relação substantiva com PIBID"}
                and pibid == "Nenhum sinal literal identificado"):
            alerta("PIBID sem sinal literal", "A verificação não encontrou o termo no título ou no resumo local; "
                   "isso não prova erro nem ausência de relação.")
        if (avaliado["Contexto de Goiás"] == "Pesquisa realizada em Goiás"
                and go == "Nenhum sinal literal identificado"):
            alerta("Contexto sem sinal literal", "A verificação não encontrou Goiás/goiano no título ou no resumo; "
                   "instituições, municípios ou outras fontes podem sustentar o contexto.")
        if outros_dois:
            alerta("DOI repetido", "Outros códigos com DOI normalizado igual: " + ", ".join(outros_dois)
                   + ". Conferir dados bibliográficos; não deduplicar automaticamente.")
        if outros_titulos:
            alerta("Título repetido", "Outros códigos com título normalizado exato: " + ", ".join(outros_titulos)
                   + ". Não presumir duplicidade.")
        if "incompatíveis" in consistencia or "sem período" in consistencia:
            alerta("Inconsistência lógica", consistencia)
        if diferencas:
            alerta("Diferença na integração", " | ".join(diferencas))
        if codigo == "46baf45a":
            alerta("Inconsistência previamente documentada",
                   "A divergência título–resumo foi identificada anteriormente; esta regra não a detecta semanticamente.")
    return linhas, alertas


def gerar(cega_path, auto_path, base_path, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    wb_cega = load_workbook(cega_path, data_only=True)
    wb_auto = load_workbook(auto_path, data_only=True)
    wb_base = load_workbook(base_path, data_only=True)
    cega = registros(wb_cega["Avaliação independente"], 60)
    auto = registros(wb_auto["Autoavaliação"], 60)
    base = registros(wb_base["Triagem"], 1317)
    linhas, alertas = analisar(cega, auto, base)
    livro = Workbook()
    guia = livro.active
    guia.title = "Limites e regras"
    for texto in [
        "Conferência computacional por regras — não é análise independente validada.",
        "Sinais e períodos são gerados dos campos A–O da amostra cega; a autoavaliação é comparada depois.",
        "Não se leu o texto integral nem se verificou se os metadados originais são corretos.",
        "Sinais literais de PIBID e Goiás são incompletos; sua presença ou ausência não decide conteúdo nem localização.",
        "Períodos diferentes podem refletir fontes adicionais; exigir conferência de evidência, não assumir erro.",
        "A lógica de avanço verifica somente coerência entre respostas, não a verdade das respostas.",
        "DOI e título repetidos são candidatos para revisão, não confirmação automática.",
        "Alertas são acionamentos de regra, podem se sobrepor e não representam erros ou taxas de acerto.",
        "A conferência não valida eixos, interpretação semântica, acurácia ou faixas de confiança.",
    ]:
        guia.append([texto])
    guia.column_dimensions["A"].width = 110
    tabela = livro.create_sheet("Conferência por registro")
    tabela.append([
        "Código", "Fonte", "Título", "Período nos dados cegos", "Período na autoavaliação",
        "Comparação do período", "Sinal PIBID em título ou resumo", "Sinal Goiás em título ou resumo",
        "Campo resumo local", "Outros códigos com mesmo DOI", "Outros códigos com mesmo título",
        "Coerência da triagem declarada", "Diferenças com base integrada",
        "Evidência da autoavaliação", "Limites da autoavaliação",
    ])
    for linha in linhas:
        tabela.append(linha)
    anexar_tabela(tabela, "ConferenciaRegistros")
    aba_alertas = livro.create_sheet("Alertas")
    aba_alertas.append(["Código", "Regra acionada", "Descrição", "Evidência anterior", "Limites anteriores"])
    for linha in alertas:
        aba_alertas.append(linha)
    if alertas:
        anexar_tabela(aba_alertas, "AlertasConferencia")
    livro.save(saida)
    print("Registros:", len(linhas))
    print("Alertas por regra:", dict(Counter(linha[1] for linha in alertas)))
    print("Registros com pelo menos um alerta:", len({linha[0] for linha in alertas}))


if __name__ == "__main__":
    gerar(CEGA, AUTO, BASE, SAIDA)
    print(f"Conferência criada: {SAIDA}")
