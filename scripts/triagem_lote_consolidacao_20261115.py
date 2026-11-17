"""Consolida leituras existentes e prioriza as linhas sem decisão."""

import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

from openpyxl import load_workbook

from scripts.confirmar_duplicatas_amostra_20261115 import validar_par
from scripts.conferir_catalogo_resumos_20261115 import identificador, ler_originais
from scripts.conferir_termos_e_resumos_20261115 import ler_exportacoes, tem_termo
from scripts.integrar_autoavaliacao_20261115 import anexar_tabela, indice_unico
from scripts.integrar_bdtd_termos_lote_20261115 import CAMPOS_BRUTOS, possivel_traducao
from scripts.integrar_catalogo_lote2_20261115 import BRUTO
from scripts.integrar_teses_e_datas_uel_20261115 import acrescentar
from scripts.preanalise_e_validacao_20261115 import cabecalhos

RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_eixos_incluidos_20261115.xlsx"
UNB = ANALISES / "conferencia_resumos_unb_20261115.json"
SAIDA = ANALISES / "triagem_lote_consolidada_20261115.xlsx"
ADICIONAIS = {
    "6fd8a46d": (
        "98fa066ebcbddd7d31425beb546841a91f5ee5882e0a08bea17b202872357534",
        "O estudo examina supervisão de estágio; o PIBID é citado como possibilidade de estudos futuros.",
    ),
    "6af837ea": (
        "af1e61990e850e717b9eef9bcc1cf547b102e369f45580db58e5b300df106d10",
        "O estudo analisa livros didáticos; experiências no PIBID e na residência pedagógica são motivação.",
    ),
}
PAR_UNB = ("a3e7321c", "69c845eb")
HISTORICO_BDTD = ("Conferência termos e UnB", "BDTD termos lote", "BDTD termos lote 2")
HISTORICO_CAPES = (
    "Resumos Catálogo CAPES", "Revisão bilíngue CAPES",
    "CAPES bilíngue lote 2", "CAPES bilíngue lote 4", "CAPES bilíngue lote 5",
)


def categoria(periodo, contexto, afiliacao, relacao, triagem, decisao):
    if decisao == "Excluir":
        return "Exclusão temática consolidada"
    if triagem == "Excluir":
        return "Exclusão preliminar não consolidada"
    go = contexto == "Pesquisa realizada em Goiás" or afiliacao == "Sim"
    dentro = periodo == "Publicação 2020–2026 confirmada"
    if dentro and go:
        if relacao in {"Tema central do estudo", "Relação substantiva com PIBID"}:
            return "Critérios indicados; conferir evidências"
        return "Período e vínculo GO indicados; pertinência não estabelecida"
    if go:
        return "Vínculo GO indicado; período não confirmado"
    if dentro:
        return "Período indicado; vínculo GO não estabelecido"
    return "Período e vínculo GO não estabelecidos"


def integrar(base, bruto, unb, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    fontes = defaultdict(list)
    for origem, registros in zip(("nacional", "regional"), ler_exportacoes()):
        for registro in registros:
            chave = (registro["Título"], registro["Autor(a)"].replace("||", " | "), registro["Link de acesso"])
            fontes[chave].append((origem, registro))
    dados_unb = json.loads(unb.read_text(encoding="utf-8"))
    consulta = next(x for x in dados_unb["registros"] if x["codigo"] == PAR_UNB[0])
    if (dados_unb["data_consulta"] != "2026-11-15" or consulta["par"] != PAR_UNB[1]
            or consulta["data_emissao"] != "2017-05-26"
            or not consulta["data_incorporacao"].startswith(consulta["data_emissao"])
            or consulta["ano_na_referencia"] != 2017):
        raise ValueError("Metadados temporais UnB divergentes.")

    livro = load_workbook(base)
    triagem = livro["Triagem"]
    col = cabecalhos(triagem)
    indices = indice_unico(triagem, col["Código"], 1317)
    registros = {codigo: {campo: triagem.cell(numero, coluna).value for campo, coluna in col.items()}
                 for codigo, numero in indices.items()}
    pendentes = {codigo for codigo, r in registros.items()
                 if r["Decisão de elegibilidade"] in {"Pendente", "Não iniciada"}}
    if len(pendentes) != 1196:
        raise ValueError("Quantidade de linhas sem decisão divergente.")
    selecionados = {
        codigo for codigo in pendentes
        if registros[codigo]["Decisão de elegibilidade"] == "Pendente"
        and registros[codigo]["Triagem de título e resumo"] == "Excluir"
        and registros[codigo]["Motivo da exclusão"] in {"Outro", "Sem relação substantiva com PIBID"}
    }
    if (len(selecionados) != 87
            or Counter(registros[c]["Fonte"] for c in selecionados) != {"BDTD": 72, "Catálogo CAPES": 15}):
        raise ValueError("Seleção das leituras anteriores divergente.")
    historicos = {}
    for nome in HISTORICO_BDTD + HISTORICO_CAPES:
        historicos[nome] = {r[0] for r in list(livro[nome].values)[1:]}
    historico_bdtd = set().union(*(historicos[n] for n in HISTORICO_BDTD))
    historico_capes = set().union(*(historicos[n] for n in HISTORICO_CAPES))
    ids_capes = {identificador(registros[c]["Link da fonte"]) for c in selecionados
                 if registros[c]["Fonte"] == "Catálogo CAPES"}
    capes = ler_originais(bruto, ids_capes)

    def conferir_bdtd(codigo):
        r = registros[codigo]
        link = r["Link da fonte"] or "Não informado pela instituição"
        candidatos = fontes[(r["Título"], r["Autoria"], link)]
        if not candidatos or len({origem for origem, _ in candidatos}) != len(candidatos):
            raise ValueError(f"Exportação BDTD ausente ou ambígua: {codigo}")
        if any(x["Resumo"] != r["Resumo"] for _, x in candidatos):
            raise ValueError(f"Resumo BDTD divergente: {codigo}")
        return candidatos

    for codigo in selecionados:
        r = registros[codigo]
        if r["Fonte"] == "BDTD":
            if codigo not in historico_bdtd or len(r["Resumo"] or "") < 500:
                raise ValueError(f"Leitura BDTD não comprovada: {codigo}")
            for _, item in conferir_bdtd(codigo):
                if any(tem_termo(item[campo]) or possivel_traducao(item[campo]) for campo in CAMPOS_BRUTOS):
                    raise ValueError(f"Termo ou possível tradução encontrado: {codigo}")
        else:
            if codigo not in historico_capes:
                raise ValueError(f"Leitura CAPES não comprovada: {codigo}")
            item = capes[identificador(r["Link da fonte"])]
            if (r["Título"] != item["NM_PRODUCAO"] or r["Autoria"] != item["NM_DISCENTE"]
                    or r["Resumo"] != item["DS_RESUMO"]
                    or min(len(item["DS_RESUMO"]), len(item["DS_ABSTRACT"])) < 500):
                raise ValueError(f"Material CAPES divergente: {codigo}")
            if r["Motivo da exclusão"] == "Outro" and any(
                tem_termo(item[campo]) for campo in
                ("NM_PRODUCAO", "DS_RESUMO", "DS_ABSTRACT", "DS_PALAVRA_CHAVE", "DS_KEYWORD")
            ):
                raise ValueError(f"Termo encontrado em CAPES: {codigo}")
            if r["Motivo da exclusão"] == "Sem relação substantiva com PIBID" and r["Relação com PIBID"] != "Menção incidental":
                raise ValueError(f"Relação CAPES divergente: {codigo}")

    for codigo, (hash_esperado, _) in ADICIONAIS.items():
        r = registros[codigo]
        conferir_bdtd(codigo)
        if (r["Fonte"] != "BDTD" or r["Triagem de título e resumo"] != "Pendente"
                or r["Decisão de elegibilidade"] not in {"Pendente", "Não iniciada"}
                or r["Relação com PIBID"] not in {"Incerto", "Menção incidental"}
                or r["Motivo da exclusão"] is not None
                or hashlib.sha256(r["Resumo"].encode("utf-8")).hexdigest() != hash_esperado
                or not tem_termo(r["Resumo"])):
            raise ValueError(f"Leitura adicional divergente: {codigo}")

    n1, n2 = (indices[codigo] for codigo in PAR_UNB)
    validar_par(triagem, col, n1, n2, *PAR_UNB)
    for codigo in PAR_UNB:
        r = registros[codigo]
        link, link_consulta = urlsplit(r["Link da fonte"]), urlsplit(consulta["url"])
        if (r["Título"] != consulta["titulo"] or r["Autoria"] != consulta["autoria"]
                or link.scheme not in {"http", "https"} or link_consulta.scheme not in {"http", "https"}
                or (link.netloc, link.path) != (link_consulta.netloc, link_consulta.path)
                or str(r["Ano de publicação"]) != "2017"
                or r["Publicação em 2020–2026"] != "Publicação fora de 2020–2026"
                or r["Triagem de título e resumo"] != "Excluir"
                or r["Motivo da exclusão"] != "Fora do período"
                or r["Decisão de elegibilidade"] != "Pendente"):
            raise ValueError(f"Estado temporal UnB divergente: {codigo}")

    for codigo in sorted(selecionados | set(ADICIONAIS)):
        campo = lambda nome: triagem.cell(indices[codigo], col[nome])
        if codigo in ADICIONAIS:
            campo("Relação com PIBID").value = "Menção incidental"
            campo("Triagem de título e resumo").value = "Excluir"
            campo("Motivo da exclusão").value = "Sem relação substantiva com PIBID"
            if campo("Revisor").value is None:
                campo("Revisor").value = "Análise computacional e documental preliminar não independente"
            if campo("Data da triagem").value is None:
                campo("Data da triagem").value = datetime(2026, 11, 15)
            acrescentar(campo("Fontes das evidências"), ADICIONAIS[codigo][1]
                       + " Fonte: resumo da exportação BDTD; leitura de 15/11/2026.")
            acrescentar(campo("Material consultado"), "Título e resumo da exportação BDTD.")
        campo("Decisão de elegibilidade").value = "Excluir"
        limite = (
            "Exclusão operacional e reversível do recorte goiano pela leitura temática e pelos campos "
            "disponíveis; não comprova ausência do PIBID no texto integral. A análise não é independente. "
            "Esta decisão não substitui avaliação específica para o panorama nacional."
        )
        acrescentar(campo("Limitações e pendências"),
                   "Consolidação: elegibilidade do recorte goiano decidida. " + limite)
        acrescentar(campo("Observações"), "Exclusão temática consolidada em 15/11/2026. " + limite)

    for codigo in PAR_UNB:
        campo = lambda nome: triagem.cell(indices[codigo], col[nome])
        campo("Ano de publicação").value = None
        campo("Publicação em 2020–2026").value = "Incerto"
        campo("Triagem de título e resumo").value = "Pendente"
        campo("Motivo da exclusão").value = None
        texto = (
            "Reavaliação temporal: a data de emissão de 2017 coincide com a incorporação ao repositório; "
            "a referência também traz 2017, mas não confirma publicação distinta. Ano de publicação e "
            "período permanecem incertos; não se exclui apenas pelo ano de defesa ou incorporação."
        )
        acrescentar(campo("Limitações e pendências"), texto)
        acrescentar(campo("Observações"), texto)

    auditoria = livro.create_sheet("Priorização lote")
    auditoria.append([
        "Código", "Fonte", "Decisão anterior", "Decisão atual", "Triagem atual",
        "Relação PIBID", "Período", "Contexto de Goiás", "Afiliação em Goiás",
        "Qualidade documental do resumo", "Prioridade operacional",
    ])
    for codigo in sorted(pendentes):
        r = registros[codigo]
        campo = lambda nome: triagem.cell(indices[codigo], col[nome]).value
        auditoria.append([
            codigo, r["Fonte"], r["Decisão de elegibilidade"], campo("Decisão de elegibilidade"),
            campo("Triagem de título e resumo"), campo("Relação com PIBID"),
            campo("Publicação em 2020–2026"), campo("Contexto de Goiás"), campo("Afiliação em Goiás"),
            campo("Qualidade documental do resumo"), categoria(
                campo("Publicação em 2020–2026"), campo("Contexto de Goiás"), campo("Afiliação em Goiás"),
                campo("Relação com PIBID"), campo("Triagem de título e resumo"), campo("Decisão de elegibilidade")),
        ])
    anexar_tabela(auditoria, "PriorizacaoLote")
    livro["Limites da integração"].append([
        "Triagem em lote de 1.196 linhas sem decisão: 89 exclusões temáticas consolidadas; "
        "dois registros UnB retornaram à incerteza temporal. A priorização usa estados existentes e "
        "não substitui leitura temática nem cria pendência por ausência de resumo."
    ])
    livro.save(saida)
    livro.close()


if __name__ == "__main__":
    integrar(BASE, BRUTO, UNB, SAIDA)
    print(f"Base criada: {SAIDA}")
