"""Conclui a leitura dos resumos disponíveis do inventário CAPES."""

from pathlib import Path

from openpyxl import load_workbook

from scripts.classificar_resumos_ausentes_20261115 import REDUZIDA
from scripts.conferir_catalogo_resumos_20261115 import identificador, ler_originais
from scripts.integrar_autoavaliacao_20261115 import indice_unico
from scripts.integrar_catalogo_lote2_20261115 import BRUTO
from scripts.integrar_catalogo_lote4_20261115 import ANTERIORES, integrar as integrar_leituras
from scripts.preanalise_e_validacao_20261115 import cabecalhos


RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_catalogo_lote4_20261115.xlsx"
DECISOES = ANALISES / "avaliacao_catalogo_lote5_20261115.csv"
SAIDA = ANALISES / "triagem_catalogo_lote5_20261115.xlsx"
SEM_RESUMO = {"53af6244": "15456992", "68880406": "15457639"}


def integrar(base, decisoes, bruto, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    originais = ler_originais(bruto, set(SEM_RESUMO.values()))
    livro = load_workbook(base)
    triagem = livro["Triagem"]
    col = cabecalhos(triagem)
    indices = indice_unico(triagem, col["Código"], 1317)
    inventario = {r[0]: r[1] for r in list(livro["Inventário inglês CAPES"].values)[1:]}
    for codigo, fonte_id in SEM_RESUMO.items():
        registro = originais[fonte_id]
        if (inventario.get(codigo) != fonte_id or codigo not in indices
                or triagem.cell(indices[codigo], col["Fonte"]).value != "Catálogo CAPES"
                or identificador(triagem.cell(indices[codigo], col["Link da fonte"]).value) != fonte_id
                or triagem.cell(indices[codigo], col["Título"]).value != registro["NM_PRODUCAO"]
                or triagem.cell(indices[codigo], col["Autoria"]).value != registro["NM_DISCENTE"]
                or triagem.cell(indices[codigo], col["Resumo"]).value != "EM CONSTRUÇÃO"
                or triagem.cell(indices[codigo], col["Qualidade documental do resumo"]).value != REDUZIDA
                or registro["DS_RESUMO"] != "EM CONSTRUÇÃO"
                or registro["DS_ABSTRACT"] != "EM CONSTRUÇÃO"):
            raise ValueError(f"Estado do resumo indisponível divergente: {codigo}")
    livro.close()
    integrar_leituras(
        base, decisoes, bruto, saida, quantidade=10, aba="CAPES bilíngue lote 5",
        anteriores=(*ANTERIORES, "CAPES bilíngue lote 4"), total_restantes=12,
        ignorar=tuple(SEM_RESUMO), nome_tabela="CAPESBilingueLote5",
        mensagem_limites="10 registros CAPES adicionais lidos nos dois resumos; 1 exclusão(ões) temática(s) "
        "preliminar(es) e reversível(is) por menção incidental. Sem validação independente nem decisão final.",
    )


if __name__ == "__main__":
    integrar(BASE, DECISOES, BRUTO, SAIDA)
    print(f"Base criada: {SAIDA}")
