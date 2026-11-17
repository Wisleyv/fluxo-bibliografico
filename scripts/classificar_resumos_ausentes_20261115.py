"""Registra a qualidade documental dos campos de resumo, sem decidir elegibilidade."""

from collections import Counter
from copy import copy
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import TableColumn

from scripts.conferir_amostra_por_regras_20261115 import tipo_resumo
from scripts.conferir_campos_portal_20261115 import ler_decisoes, texto
from scripts.conferir_termos_e_resumos_20261115 import tem_termo
from scripts.integrar_autoavaliacao_20261115 import anexar_tabela, indice_unico
from scripts.integrar_teses_e_datas_uel_20261115 import acrescentar
from scripts.preanalise_e_validacao_20261115 import cabecalhos


RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_portal_campos_20261115.xlsx"
CONFERENCIA = ANALISES / "conferencia_portal_campos_20261115.csv"
SAIDA = ANALISES / "triagem_qualidade_resumos_20261115.xlsx"
ABA = "Qualidade dos resumos"
COLUNA = "Qualidade documental do resumo"
REDUZIDA = "Reduzida — campo sem resumo substantivo"
NAO_AVALIADA = "Não avaliada nesta etapa"
NOTA = (
    "Regra atual: a falta de resumo substantivo neste campo é limitação documental, "
    "não gera pendência nem consulta individual por si só. Recomendações anteriores "
    "de consulta apenas por essa falta ficam superadas; dúvidas de outros critérios "
    "permanecem distintas. Ver aba Qualidade dos resumos."
)
TEXTOS = {
    "Campo vazio": "Campo resumo vazio",
    "Possível informação de orientação": "Campo contém possível informação de orientação",
    "Possível referência bibliográfica": "Campo contém possível referência bibliográfica",
}


def classificar(valor):
    return TEXTOS.get(tipo_resumo(valor))


def integrar(base, conferencia, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    conferidos = {item["codigo"]: item for item in ler_decisoes(conferencia)}
    livro = load_workbook(base)
    triagem = livro["Triagem"]
    col = cabecalhos(triagem)
    indices = indice_unico(triagem, col["Código"], 1317)
    if ABA in livro.sheetnames or COLUNA in col or triagem.max_column != 35:
        raise ValueError("Estrutura anterior inesperada.")
    if not set(conferidos).issubset(indices):
        raise ValueError("Registros conferidos no Portal ausentes da base.")

    registros = []
    for codigo, numero in indices.items():
        valor = lambda campo: triagem.cell(numero, col[campo]).value
        tipo = classificar(valor("Resumo"))
        if codigo in conferidos:
            item = conferidos[codigo]
            if (valor("Fonte") != "Portal CAPES" or tipo != "Campo resumo vazio"
                    or texto(valor("Título")) != texto(item["titulo"])
                    or texto(valor("DOI")) != texto(item["doi"])
                    or item["evidencia"] not in (valor("Fontes das evidências") or "")):
                raise ValueError(f"Conferência anterior divergente: {codigo}")
        if tipo:
            registros.append((codigo, numero, tipo))

    totais = Counter(triagem.cell(numero, col["Fonte"]).value for _, numero, _ in registros)
    tipos = Counter(tipo for _, _, tipo in registros)
    if totais != {"Portal CAPES": 103, "BDTD": 106} or tipos != {
        "Campo resumo vazio": 126,
        "Campo contém possível informação de orientação": 50,
        "Campo contém possível referência bibliográfica": 33,
    }:
        raise ValueError(f"Universo anterior divergente: {totais}; {tipos}")

    nova_coluna = triagem.max_column + 1
    cabecalho = triagem.cell(1, nova_coluna, COLUNA)
    cabecalho._style = copy(triagem.cell(1, nova_coluna - 1)._style)
    triagem.column_dimensions[get_column_letter(nova_coluna)].width = 45
    tabela = triagem.tables["Triagem"]
    if tabela.ref != "A1:AI1318" or tabela.autoFilter.ref != tabela.ref:
        raise ValueError("Tabela de triagem inesperada.")
    tabela.ref = f"A1:AJ{triagem.max_row}"
    tabela.autoFilter.ref = tabela.ref
    tabela.tableColumns.append(TableColumn(id=nova_coluna, name=COLUNA))
    for numero in indices.values():
        triagem.cell(numero, nova_coluna, NAO_AVALIADA)

    auditoria = livro.create_sheet(ABA)
    auditoria.append([
        "Código", "Fonte", "Título", "Estado do campo resumo",
        "Termo no título", "Termo nas palavras-chave",
        "Resumo atual do Portal já conferido", "Material consultado anteriormente",
        "Qualidade documental", "Limites de interpretação",
    ])
    for codigo, numero, tipo in registros:
        valor = lambda campo: triagem.cell(numero, col[campo]).value
        triagem.cell(numero, nova_coluna, REDUZIDA)
        acrescentar(triagem.cell(numero, col["Limitações e pendências"]), NOTA)
        item = conferidos.get(codigo)
        atual = item["evidencia"] if item else "Não identificado nesta conferência"
        limite = (
            "Qualidade do campo da base, não medida de acurácia ou decisão de inclusão. "
            "A recuperação por assunto/todos os campos não prova termo em título ou resumo; "
            "fontes já consultadas podem conter outras evidências. Sem busca individual adicional."
        )
        if item:
            limite += " O resumo do Portal foi consultado após o corte e não comprova o conteúdo histórico."
        auditoria.append([
            codigo, valor("Fonte"), valor("Título"), tipo,
            "Sim" if tem_termo(valor("Título")) else "Não identificado por regra",
            "Sim" if tem_termo(valor("Palavras-chave")) else "Não identificado por regra",
            atual, valor("Material consultado") or "Não registrado",
            REDUZIDA, limite,
        ])
    anexar_tabela(auditoria, "QualidadeResumos")
    livro["Limites da integração"].append([
        "Regra vigente: ausência de resumo substantivo no campo da base é limitação "
        "documental, não pendência nem motivo de busca individual por si só; dúvidas "
        "de outros critérios permanecem distintas. Classificação qualitativa não mede acurácia."
    ])
    livro.save(saida)
    livro.close()


if __name__ == "__main__":
    integrar(BASE, CONFERENCIA, SAIDA)
    print(f"Base criada: {SAIDA}")
