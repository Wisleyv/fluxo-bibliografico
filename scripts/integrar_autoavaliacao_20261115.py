"""Integra a autoavaliação à base técnica, preservando decisões anteriores."""

from copy import copy
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

from scripts.preanalise_e_validacao_20261115 import cabecalhos


RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_preanalise_local_20261115.xlsx"
AMOSTRA = ANALISES / "amostra_60_autoavaliacao_20261115.xlsx"
SAIDA = ANALISES / "triagem_integrada_autoavaliacao_20261115.xlsx"
DATA = datetime(2026, 11, 15)
EIXOS = {
    "Aprendizagem e identidade": "Aprendizagem da docência e identidade profissional",
    "Trajetórias profissionais": "Trajetórias profissionais",
    "Relações IES, escolas e comunidades": "Relações IES, escolas e comunidades; saberes e espaços híbridos",
}
CAMPOS = {
    "Relação com PIBID": "Relação com PIBID",
    "Contexto de Goiás": "Contexto de Goiás",
    "Afiliação em Goiás": "Afiliação em Goiás",
    "Publicação em 2020–2026": "Publicação em 2020–2026",
    "Produção acadêmica": "Produção acadêmica",
    "Triagem de título e resumo": "Triagem da autoavaliação",
}


def texto_anterior_e_novo(anterior, novo):
    return f"Anterior: {anterior}\nAutoavaliação: {novo}" if anterior else f"Autoavaliação: {novo}"


def indice_unico(aba, coluna_codigo, quantidade):
    indices = {}
    for numero in range(2, aba.max_row + 1):
        codigo = aba.cell(numero, coluna_codigo).value
        if not codigo or codigo in indices:
            raise ValueError(f"Código ausente ou repetido em {aba.title}: {codigo!r}")
        indices[codigo] = numero
    if len(indices) != quantidade:
        raise ValueError(f"Quantidade inesperada em {aba.title}: {len(indices)}")
    return indices


def anexar_tabela(aba, nome):
    tabela = Table(displayName=nome, ref=f"A1:{get_column_letter(aba.max_column)}{aba.max_row}")
    tabela.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
    aba.add_table(tabela)
    aba.freeze_panes = "C2"
    for coluna in range(1, aba.max_column + 1):
        aba.column_dimensions[get_column_letter(coluna)].width = 28 if coluna < 4 else 55
    for linha in aba:
        for celula in linha:
            celula.alignment = Alignment(vertical="top", wrap_text=True)
            if isinstance(celula.value, str):
                celula.data_type = "s"


def integrar(base, amostra, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    livro = load_workbook(base)
    fonte = load_workbook(amostra, data_only=True)
    triagem = livro["Triagem"]
    eixos = livro["Eixos de análise"]
    avaliacao = fonte["Autoavaliação"]
    ct, ca, ce = map(cabecalhos, (triagem, avaliacao, eixos))
    indices = indice_unico(triagem, ct["Código"], 1317)
    sorteados = indice_unico(avaliacao, ca["Código"], 60)
    if not set(sorteados).issubset(indices):
        raise ValueError("Há códigos da amostra que não constam na base.")

    linhas_eixos = {}
    for numero in range(2, eixos.max_row + 1):
        chave = (eixos.cell(numero, ce["Código"]).value, eixos.cell(numero, ce["Eixo"]).value)
        if chave in linhas_eixos:
            raise ValueError(f"Par registro/eixo repetido: {chave}")
        linhas_eixos[chave] = numero

    auditoria = livro.create_sheet("Alterações da amostra")
    auditoria.append(["Código", "Campo", "Anterior", "Autoavaliação", "Valor integrado", "Observação"])

    def alterar(codigo, campo, valor, observacao=""):
        celula = triagem.cell(indices[codigo], ct[campo])
        anterior = celula.value
        if anterior != valor:
            auditoria.append([codigo, campo, anterior, valor, valor, observacao])
            celula.value = valor

    for codigo, numero_amostra in sorteados.items():
        linha = indices[codigo]
        valor = lambda campo: avaliacao.cell(numero_amostra, ca[campo]).value
        for campo in ("Título", "Fonte", "Tipo de produção"):
            if triagem.cell(linha, ct[campo]).value != valor(campo):
                raise ValueError(f"Identificação divergente em {codigo}: {campo}")
        if not all(valor(campo) for campo in list(CAMPOS.values()) + [
            "Evidência e localização", "Limites e pendências", *EIXOS
        ]):
            raise ValueError(f"Autoavaliação incompleta: {codigo}")

        for destino, origem in CAMPOS.items():
            novo = valor(origem)
            if codigo == "796dae04" and destino == "Contexto de Goiás":
                anterior = triagem.cell(linha, ct[destino]).value
                if anterior != "Incerto" or novo != "Pesquisa realizada em Goiás":
                    raise ValueError("Divergência de contexto esperada mudou; revisar manualmente.")
                auditoria.append([
                    codigo, destino, anterior, novo, anterior,
                    "Divergência preservada: UFG identificada, local das escolas não explicitado; "
                    "avanço fundamentado também na afiliação.",
                ])
                continue
            alterar(codigo, destino, novo)

        if codigo == "06792f41":
            if triagem.cell(linha, ct["Ano de publicação"]).value is not None or valor("Ano de publicação") != 2024:
                raise ValueError("Ano de publicação inesperado em 06792f41")
            alterar(codigo, "Ano de publicação", 2024, "Fonte primária indicada na evidência.")
        if valor("Triagem da autoavaliação") == "Excluir":
            alterar(codigo, "Motivo da exclusão", "Fora do período", "Somente no recorte goiano.")
        alterar(codigo, "Decisão de elegibilidade", "Pendente", "Sem decisão final de elegibilidade.")
        if codigo in {"83224e28", "387c5254"}:
            outro = "387c5254" if codigo == "83224e28" else "83224e28"
            par = sorteados[outro]
            for campo in ("Título", "Ano de publicação", "DOI"):
                if valor(campo) != avaliacao.cell(par, ca[campo]).value:
                    raise ValueError(f"Dados do par duplicado divergentes em {campo}")
            alterar(codigo, "Duplicidade", "Duplicata confirmada", f"Mesmo estudo do registro {outro}.")

        evidencia = valor("Evidência e localização")
        limites = valor("Limites e pendências")
        for campo, novo in {
            "Evidência do contexto": evidencia,
            "Evidência da afiliação": evidencia if valor("Afiliação em Goiás") == "Sim" else "Afiliação não confirmada.",
            "Fontes das evidências": evidencia,
            "Material consultado": "Conferir evidência da autoavaliação; fonte local e eventual consulta pontual.",
            "Limitações e pendências": limites,
            "Observações": (
                "Autoavaliação computacional não independente; não é inclusão final nem valida confiança. "
                "Veja a aba Alterações da amostra e a amostra preenchida."
            ),
        }.items():
            celula = triagem.cell(linha, ct[campo])
            novo_valor = texto_anterior_e_novo(celula.value, novo)
            if len(novo_valor) > 32767:
                raise ValueError(f"Texto excede limite do Excel: {codigo}, {campo}")
            alterar(codigo, campo, novo_valor)
        alterar(codigo, "Revisor", "Autoavaliação computacional não independente")
        alterar(codigo, "Data da triagem", DATA)

        for campo_origem, eixo in EIXOS.items():
            chave = (codigo, eixo)
            if chave in linhas_eixos:
                linha_eixo = linhas_eixos[chave]
                if eixos.cell(linha_eixo, ce["Estado"]).value:
                    raise ValueError(f"Extração anterior preenchida requer conciliação: {chave}")
            else:
                linha_eixo = eixos.max_row + 1
                for coluna in range(1, eixos.max_column + 1):
                    eixos.cell(linha_eixo, coluna)._style = copy(eixos.cell(2, coluna)._style)
                eixos.cell(linha_eixo, ce["Código"]).value = codigo
                eixos.cell(linha_eixo, ce["Título"]).value = valor("Título")
                eixos.cell(linha_eixo, ce["Eixo"]).value = eixo
                linhas_eixos[chave] = linha_eixo
            preenchimento = {
                "Estado": valor(campo_origem),
                "Achado ou observação": evidencia,
                "Trecho ou localização": "Síntese e localização no campo de evidência; consultar amostra.",
                "Tipo de fonte": "Material local e eventuais fontes adicionais indicadas na evidência",
                "Link ou referência consultada": "Ver evidência e amostra autoavaliada por código.",
                "Limites da evidência": limites + " Extração provisória; registro pode não ser elegível.",
                "Revisor": "Autoavaliação computacional não independente",
                "Data": DATA,
            }
            for campo, conteudo in preenchimento.items():
                eixos.cell(linha_eixo, ce[campo]).value = conteudo

    tabela_eixos = eixos.tables["Eixos"]
    tabela_eixos.ref = f"A1:K{eixos.max_row}"
    if tabela_eixos.autoFilter is not None:
        tabela_eixos.autoFilter.ref = tabela_eixos.ref
    if len(eixos.data_validations.dataValidation) != 1:
        raise ValueError("Validação de eixos inesperada.")
    eixos.data_validations.dataValidation[0].sqref = f"D2:D{eixos.max_row}"
    anexar_tabela(auditoria, "AlteracoesAmostra")

    orientacoes = livro.create_sheet("Limites da integração", 0)
    for texto in [
        "Base de trabalho — integração da autoavaliação de 60 registros",
        "NÃO é validação independente nem planilha final de resultados.",
        "Amostra selecionada por registro, com cotas por fonte e possíveis duplicatas; não extrapolar contagens.",
        "As alterações anteriores e novas constam da aba Alterações da amostra; fontes e limites acompanham os registros.",
        "Triagem Excluir por ano refere-se apenas a Goiás 2020–2026; a elegibilidade final continua pendente.",
        "Os eixos da amostra incluem registros pendentes ou fora do recorte; não são contagens de estudos incluídos.",
        "A divergência de contexto do código 796dae04 permanece Incerto na base; o avanço tem suporte na afiliação.",
        "Par 83224e28/387c5254 confirmado como duplicata; nenhum registro principal foi escolhido.",
        "A amostra cega, a autoavaliação e a pré-análise originais permanecem separadas e preservadas.",
        "Demais registros não foram analisados semanticamente por este procedimento; não atribuir confiança percentual.",
    ]:
        orientacoes.append([texto])
    orientacoes.column_dimensions["A"].width = 110
    for linha in orientacoes:
        linha[0].alignment = Alignment(wrap_text=True, vertical="top")
    orientacoes["A1"].font = Font(bold=True, size=14)
    livro.save(saida)


if __name__ == "__main__":
    integrar(BASE, AMOSTRA, SAIDA)
    print(f"Base integrada criada: {SAIDA}")
