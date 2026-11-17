"""Confirma pares com identificador de repositório e metadados coincidentes."""

from pathlib import Path
from urllib.parse import urlparse

from openpyxl import load_workbook

from scripts.integrar_autoavaliacao_20261115 import anexar_tabela, indice_unico
from scripts.preanalise_e_validacao_20261115 import cabecalhos


RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_integrada_autoavaliacao_20261115.xlsx"
SAIDA = ANALISES / "triagem_duplicatas_conferidas_20261115.xlsx"
PARES = (
    ("dca33e23", "740184cf"),
    ("3ee25c3e", "5f5259e7"),
    ("f1d6e487", "361dd6b1"),
    ("5dbf2cee", "2e073f75"),
)
IDENTIDADE = ("Título", "Autoria", "Tipo de produção", "Ano de defesa",
              "Instituição associada", "Link da fonte")


def validar_par(triagem, col, n1, n2, codigo1, codigo2):
    for campo in IDENTIDADE:
        v1 = triagem.cell(n1, col[campo]).value
        v2 = triagem.cell(n2, col[campo]).value
        if not v1 or v1 != v2:
            raise ValueError(f"Dados diferentes ou ausentes para {codigo1}/{codigo2}: {campo}")
    link = triagem.cell(n1, col["Link da fonte"]).value
    url = urlparse(link)
    if url.scheme not in {"http", "https"} or not url.netloc or not url.path.strip("/"):
        raise ValueError(f"Identificador de repositório inválido: {codigo1}")
    return link


def confirmar(base, saida, pares=PARES):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    livro = load_workbook(base)
    triagem = livro["Triagem"]
    col = cabecalhos(triagem)
    indices = indice_unico(triagem, col["Código"], 1317)
    if len({codigo for par in pares for codigo in par}) != len(pares) * 2:
        raise ValueError("Os pares devem conter códigos distintos.")
    auditoria = livro.create_sheet("Duplicatas conferidas")
    auditoria.append([
        "Código 1", "Código 2", "Título", "Autoria", "Ano de defesa",
        "Identificador de repositório", "Estado anterior 1", "Estado anterior 2",
        "Situação", "Limites",
    ])
    for codigo1, codigo2 in pares:
        if codigo1 not in indices or codigo2 not in indices:
            raise ValueError(f"Código ausente no par {codigo1}/{codigo2}")
        n1, n2 = indices[codigo1], indices[codigo2]
        link = validar_par(triagem, col, n1, n2, codigo1, codigo2)
        anteriores = [triagem.cell(n, col["Duplicidade"]).value for n in (n1, n2)]
        if any(estado not in {"Não verificada", "Duplicata provável"} for estado in anteriores):
            raise ValueError(f"Estado anterior inesperado para {codigo1}/{codigo2}: {anteriores}")
        auditoria.append([
            codigo1, codigo2, triagem.cell(n1, col["Título"]).value,
            triagem.cell(n1, col["Autoria"]).value, triagem.cell(n1, col["Ano de defesa"]).value,
            link, *anteriores, "Duplicata confirmada",
            "Mesmo identificador e metadados locais; não foi escolhido registro principal nem alterada elegibilidade.",
        ])
        for numero, outro in ((n1, codigo2), (n2, codigo1)):
            triagem.cell(numero, col["Duplicidade"]).value = "Duplicata confirmada"
            observacao = triagem.cell(numero, col["Observações"])
            novo = (
                f"Conferência 15/11/2026: mesmo identificador de repositório, título, autoria, "
                f"tipo, ano de defesa e instituição do registro {outro}; sem escolha de principal."
            )
            texto = f"{observacao.value}\n{novo}" if observacao.value else novo
            if len(texto) > 32767:
                raise ValueError(f"Observação excede limite do Excel: {outro}")
            observacao.value = texto
    anexar_tabela(auditoria, "DuplicatasConferidas")
    livro["Limites da integração"].append([
        "Quatro pares adicionais confirmados por identificador de repositório e metadados locais; "
        "ver aba Duplicatas conferidas. Sem escolha de registro principal."
    ])
    livro.save(saida)


if __name__ == "__main__":
    confirmar(BASE, SAIDA)
    print(f"Base criada: {SAIDA}")
