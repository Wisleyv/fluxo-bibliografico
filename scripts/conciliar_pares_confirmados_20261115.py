"""Concilia divergências documentadas entre duplicatas já confirmadas."""

from pathlib import Path

from openpyxl import load_workbook

from scripts.integrar_autoavaliacao_20261115 import anexar_tabela, indice_unico
from scripts.integrar_teses_e_datas_uel_20261115 import acrescentar
from scripts.preanalise_e_validacao_20261115 import cabecalhos


RAIZ = Path(__file__).resolve().parents[1]
ANALISES = RAIZ / "dados" / "analises"
BASE = ANALISES / "triagem_bdtd_pibid_lote2_20261115.xlsx"
SAIDA = ANALISES / "triagem_pares_conciliados_20261115.xlsx"

AJUSTES = (
    ("2e073f75", "5dbf2cee", "Relação com PIBID",
     "Relação substantiva com PIBID", "Tema central do estudo",
     "O resumo identifica o PIBID como objeto de estudo; o mesmo material consta em ambas as linhas."),
    ("2e073f75", "5dbf2cee", "Publicação em 2020–2026",
     "Só ano de defesa disponível", "Incerto",
     "O repositório informa emissão em 25/08/2021, mas sua equivalência a publicação permanece incerta."),
    ("361dd6b1", "f1d6e487", "Contexto de Goiás",
     "Incerto", "Sem evidência de contexto goiano",
     "O resumo descreve pesquisa em Pedro Canário/ES; não identifica contexto goiano."),
    ("5f5259e7", "3ee25c3e", "Contexto de Goiás",
     "Incerto", "Sem evidência de contexto goiano",
     "O resumo descreve intervenção remota com estudantes do CAp-UERJ; não identifica contexto goiano."),
)


def pares_confirmados(livro, triagem, colunas, indices):
    pares = set()
    for nome in ("Duplicatas conferidas", "Pares recentes conferidos"):
        for linha in list(livro[nome].values)[1:]:
            pares.add(tuple(sorted(linha[:2])))
    for linha in list(livro["Lote prioritário GO"].values)[1:]:
        codigo, par = linha[:2]
        if par in indices:
            estado = lambda c: triagem.cell(indices[c], colunas["Duplicidade"]).value
            if estado(codigo) == estado(par) == "Duplicata confirmada":
                pares.add(tuple(sorted((codigo, par))))
    pares.add(tuple(sorted(("83224e28", "387c5254"))))
    codigos = [codigo for par in pares for codigo in par]
    confirmados = {
        codigo for codigo, numero in indices.items()
        if triagem.cell(numero, colunas["Duplicidade"]).value == "Duplicata confirmada"
    }
    if len(pares) != 40 or len(set(codigos)) != 80 or set(codigos) != confirmados:
        raise ValueError("Pares confirmados não reconciliam com as 80 linhas da triagem.")
    return pares


def integrar(base, saida):
    if saida.exists():
        raise FileExistsError(f"Não será sobrescrito: {saida}")
    livro = load_workbook(base)
    triagem = livro["Triagem"]
    colunas = cabecalhos(triagem)
    indices = indice_unico(triagem, colunas["Código"], 1317)
    pares = pares_confirmados(livro, triagem, colunas, indices)
    auditoria = livro.create_sheet("Conciliação pares confirmados")
    auditoria.append(["Código", "Par confirmado", "Campo", "Anterior", "Conciliado", "Evidência e limites"])

    def celula(codigo, campo):
        return triagem.cell(indices[codigo], colunas[campo])

    campos_iguais = ("Fonte", "Tipo de produção", "Título", "Autoria", "Ano de defesa",
                     "Resumo", "Palavras-chave", "Instituição associada", "Link da fonte")
    for codigo, par, campo, anterior, novo, evidencia in AJUSTES:
        if tuple(sorted((codigo, par))) not in pares:
            raise ValueError(f"Par não confirmado: {codigo}/{par}")
        for nome in campos_iguais:
            a, b = celula(codigo, nome).value, celula(par, nome).value
            if a != b or (nome in {"Título", "Autoria", "Resumo", "Link da fonte"} and not a):
                raise ValueError(f"Material ou identidade divergente: {codigo}/{par}, {nome}")
        if celula(codigo, campo).value != anterior or celula(par, campo).value != novo:
            raise ValueError(f"Estado anterior inesperado: {codigo}/{par}, {campo}")
        celula(codigo, campo).value = novo
        limite = (
            evidencia + " A afiliação e a elegibilidade final permanecem pendentes; "
            "a conciliação não é validação independente."
        )
        if campo == "Contexto de Goiás":
            acrescentar(celula(codigo, "Evidência do contexto"), evidencia)
        if campo == "Publicação em 2020–2026":
            acrescentar(celula(codigo, "Fontes das evidências"),
                       "Repositório IF Goiano: https://repositorio.ifgoiano.edu.br/handle/prefix/2162; "
                       "consulta anterior registrada na autoavaliação do par 5dbf2cee.")
        acrescentar(celula(codigo, "Limitações e pendências"), "Conciliação 15/11/2026: " + limite)
        auditoria.append([codigo, par, campo, anterior, novo, limite])

    anexar_tabela(auditoria, "ConciliacaoParesConfirmados")
    livro["Limites da integração"].append([
        "Quatro divergências em três pares confirmados conciliadas; sem exclusão de linhas, "
        "escolha de principal, novas extrações ou decisão final. Ver Conciliação pares confirmados."
    ])
    livro.save(saida)
    livro.close()


if __name__ == "__main__":
    integrar(BASE, SAIDA)
    print(f"Base criada: {SAIDA}")
