"""Registra o novo critério temporal alternativo sem presumir elegibilidade."""

from collections import Counter
from copy import copy
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import TableColumn

from scripts.integrar_autoavaliacao_20261115 import anexar_tabela, indice_unico
from scripts.preanalise_e_validacao_20261115 import cabecalhos

RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_portal_prioritario_20261115.xlsx"
SAIDA = ANALISES / "triagem_criterio_defesa_20261115.xlsx"
CAMPO = "Critério alternativo por defesa"
TIPOS = {"Tese", "Dissertação"}
FONTES = {"BDTD", "Catálogo CAPES"}
LIMITE = (
    "Ano de defesa aceito como critério temporal alternativo para o recorte goiano, "
    "não como ano de publicação. A decisão de elegibilidade exige os demais critérios; "
    "a duplicidade e as exclusões já registradas não foram alteradas."
)
LIMITE_2026 = (
    " Defesa em 2026 informada apenas por ano; o arquivo BDTD foi capturado em 08/11/2026, "
    "mas a data individual completa não foi confirmada. Evidência temporal limitada."
)


def integrar(base, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    livro = load_workbook(base)
    try:
        triagem = livro["Triagem"]
        col = cabecalhos(triagem)
        if CAMPO in col or "Critério por defesa GO" in livro.sheetnames:
            raise ValueError("Critério temporal já está presente na base.")
        indices = indice_unico(triagem, col["Código"], 1317)
        registros = []
        for codigo, linha in indices.items():
            r = {campo: triagem.cell(linha, numero).value for campo, numero in col.items()}
            if r["Tipo de produção"] not in TIPOS or r["Fonte"] not in FONTES:
                continue
            ano = r["Ano de defesa"]
            if not ano or not str(ano).isdigit():
                raise ValueError(f"Ano de defesa ausente ou inválido: {codigo}")
            ano = int(ano)
            if 2020 <= ano <= 2026:
                registros.append((codigo, linha, ano, r))
        if (len(registros) != 417
                or Counter(r["Fonte"] for _, _, _, r in registros) != {"BDTD": 340, "Catálogo CAPES": 77}
                or Counter(ano for _, _, ano, _ in registros)[2026] != 15
                or any(ano == 2026 and r["Fonte"] != "BDTD" for _, _, ano, r in registros)):
            raise ValueError("Conjunto de registros com defesa 2020–2026 divergente.")

        nova_coluna = triagem.max_column + 1
        titulo = triagem.cell(1, nova_coluna, CAMPO)
        titulo._style = copy(triagem.cell(1, nova_coluna - 1)._style)
        triagem.column_dimensions[get_column_letter(nova_coluna)].width = 38
        auditoria = livro.create_sheet("Critério por defesa GO")
        auditoria.append(["Código", "Fonte", "Tipo", "Ano de defesa", "Ano de publicação",
                          "Critério alternativo", "Decisão de elegibilidade", "Relação com PIBID",
                          "Contexto de Goiás", "Afiliação em Goiás", "Limites"])
        for codigo, linha, ano, r in registros:
            estado = ("Defesa em 2026 — evidência limitada" if ano == 2026
                      else "Defesa em 2020–2025")
            celula = triagem.cell(linha, nova_coluna, estado)
            celula._style = copy(triagem.cell(linha, nova_coluna - 1)._style)
            auditoria.append([codigo, r["Fonte"], r["Tipo de produção"], ano, r["Ano de publicação"],
                              estado, r["Decisão de elegibilidade"], r["Relação com PIBID"],
                              r["Contexto de Goiás"], r["Afiliação em Goiás"],
                              LIMITE + (LIMITE_2026 if ano == 2026 else "")])
        tabela = triagem.tables["Triagem"]
        if (len(tabela.tableColumns) != nova_coluna - 1
                or max(c.id for c in tabela.tableColumns) != nova_coluna - 1):
            raise ValueError("Estrutura anterior da tabela Triagem divergente.")
        tabela.tableColumns.append(TableColumn(id=nova_coluna, name=CAMPO))
        referencia = f"A1:{get_column_letter(nova_coluna)}{triagem.max_row}"
        tabela.ref = referencia
        tabela.autoFilter.ref = referencia
        anexar_tabela(auditoria, "CriterioDefesaGO")
        livro["Limites da integração"].append([
            "Critério alternativo para teses e dissertações com defesa de 2020–2026; 2026 tem "
            "evidência limitada quando há apenas o ano. A coluna de publicação e as decisões de "
            "elegibilidade permanecem inalteradas; a aba Priorização lote é histórica."
        ])
        livro.save(saida)
    finally:
        livro.close()


if __name__ == "__main__":
    integrar(BASE, SAIDA)
    print(f"Base criada: {SAIDA}")
