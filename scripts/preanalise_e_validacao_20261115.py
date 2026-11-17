"""Prepare conservative local screening and a blinded validation sample."""

import csv
import json
import random
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo


ROOT = Path(__file__).resolve().parent.parent
ANALISES = ROOT / "dados" / "analises"
BASE = ANALISES / "triagem_piloto_20261115_criterio_aprovado.xlsx"
METADADOS = ANALISES / "openalex_piloto_20261115.json"
REVISOES = ANALISES / "avaliacao_local_prioritaria_20261115.csv"
SAIDA = ANALISES / "triagem_preanalise_local_20261115.xlsx"
SINAIS = ANALISES / "sinais_preanalise_local_20261115.csv"
SORTEIO = ANALISES / "sorteio_validacao_60_20261115.csv"
VALIDACAO = ANALISES / "validacao_independente_60_20261115.xlsx"
COTAS = {"BDTD": 24, "Portal CAPES": 14, "Catálogo CAPES": 11, "SciELO": 11}
SEMENTE = 20261115
SEMENTE_ORDEM = 20261116
PADRAO_TEMA = re.compile(
    r"\bpibid(?:ian[oa]s?)?\b|"
    r"\bprograma institucional de bolsa(?:s)? de iniciacao a docencia\b"
)
PADRAO_GO = re.compile(r"\b(?:goias|goian[oa]s?)\b")
LOCALIZACOES = ("Título", "Resumo", "Palavras-chave", "Instituição associada", "Afiliações de autoria")


def texto_normalizado(valor):
    return "".join(
        char
        for char in unicodedata.normalize("NFKD", str(valor or "").casefold())
        if not unicodedata.combining(char)
    )


def sinal(campos, padrao):
    return [nome for nome, valor in campos.items() if padrao.search(texto_normalizado(valor))]


def ano(valor):
    if valor is None or str(valor).strip() == "":
        return None
    texto = str(valor).strip()
    if not re.fullmatch(r"\d{4}", texto):
        raise ValueError(f"Ano inválido: {valor!r}")
    return int(texto)


def periodo(ano_publicacao, ano_defesa):
    publicacao = ano(ano_publicacao)
    defesa = ano(ano_defesa)
    if publicacao is not None:
        if 2020 <= publicacao <= 2025:
            return "Publicação 2020–2026 confirmada"
        if publicacao == 2026:
            return "Incerto"
        return "Publicação fora de 2020–2026"
    return "Só ano de defesa disponível" if defesa is not None else "Ano ausente"


def categoria_temporal(registro):
    if registro["Piloto CAPES"] == "Sim":
        if registro["Triagem de título e resumo"] == "Avançar para avaliação":
            return "piloto_avancar"
        return "piloto_pendente"
    publicacao = ano(registro["Ano de publicação"])
    defesa = ano(registro["Ano de defesa"])
    if publicacao is not None:
        if 2020 <= publicacao <= 2025:
            return "publicacao_2020_2025"
        return "publicacao_2026_data_pendente" if publicacao == 2026 else "publicacao_fora"
    if defesa is not None:
        return "so_defesa_2020_2026" if 2020 <= defesa <= 2026 else "so_defesa_fora"
    return "ano_ausente"


def reconstruir_resumo(indice):
    if not indice:
        return ""
    posicoes = {}
    for palavra, indices in indice.items():
        for posicao in indices:
            if not isinstance(posicao, int) or posicao < 0 or posicao in posicoes:
                raise ValueError("Índice de resumo inválido ou com posição repetida")
            posicoes[posicao] = palavra
    if set(posicoes) != set(range(len(posicoes))):
        raise ValueError("Índice de resumo contém lacunas")
    return " ".join(posicoes[i] for i in range(len(posicoes)))


def distribuir(grupos, cota):
    if len(grupos) > cota or sum(len(v) for v in grupos.values()) < cota:
        raise ValueError("Cota incompatível com os estratos")
    alocacao = {chave: 1 for chave in grupos}
    for _ in range(cota - len(grupos)):
        candidatos = [chave for chave in sorted(grupos) if alocacao[chave] < len(grupos[chave])]
        if not candidatos:
            raise ValueError("Não há registros suficientes para completar a cota")
        # Cross multiplication gives an exact comparison and deterministic tie-breaking.
        melhor = candidatos[0]
        for chave in candidatos[1:]:
            if len(grupos[chave]) * (alocacao[melhor] + 1) > (
                len(grupos[melhor]) * (alocacao[chave] + 1)
            ):
                melhor = chave
        alocacao[melhor] += 1
    return alocacao


def ler_csv(caminho):
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        registros = list(csv.DictReader(arquivo))
    if not registros or any(None in r or None in r.values() for r in registros):
        raise ValueError(f"CSV vazio ou malformado: {caminho}")
    return registros


def cabecalhos(aba):
    nomes = [celula.value for celula in aba[1]]
    if len(nomes) != len(set(nomes)):
        raise ValueError(f"Cabeçalhos repetidos: {aba.title}")
    return {nome: indice for indice, nome in enumerate(nomes, 1)}


def salvar_csv(caminho, colunas, registros):
    with caminho.open("x", encoding="utf-8-sig", newline="") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=colunas, extrasaction="raise")
        writer.writeheader()
        writer.writerows(registros)


def criar_formulario(registros, resumos):
    workbook = Workbook()
    instrucoes = workbook.active
    instrucoes.title = "Instruções"
    for linha in [
        "Validação independente — 60 registros",
        "Preencha sem consultar decisões, sinais ou justificativas da análise automática.",
        "Use apenas os materiais já disponíveis. A ausência de informação não prova ausência no estudo.",
        "Ano de defesa não equivale automaticamente a ano de publicação; 2026 exige data até 08/11/2026.",
        "A elegibilidade admite contexto ou afiliação em Goiás; registre essas dimensões separadamente.",
        "Registre pendência quando o material não permitir decidir. Nos eixos, não informado refere-se ao material consultado.",
        "As afiliações OpenAlex podem estar incompletas e a instituição associada não prova afiliação de autoria.",
        "Os resumos do piloto foram reconstruídos dos metadados OpenAlex já arquivados; nenhuma busca adicional foi feita.",
        "Informe justificativa e localização da evidência, data e revisor; devolva esta planilha preenchida para comparação.",
    ]:
        instrucoes.append([linha])
    instrucoes.column_dimensions["A"].width = 110
    for row in instrucoes:
        row[0].alignment = Alignment(wrap_text=True, vertical="top")
    instrucoes["A1"].font = Font(bold=True, size=14)

    aba = workbook.create_sheet("Avaliação independente")
    campos = [
        "Código", "Fonte", "Tipo de produção", "Título", "Autoria",
        "Ano de publicação", "Ano de defesa", "Resumo disponível", "Resumo",
        "Palavras-chave", "Instituição associada", "Afiliações de autoria", "DOI",
        "Link da fonte", "Link OpenAlex", "Relação com PIBID", "Contexto de Goiás",
        "Afiliação em Goiás", "Publicação em 2020–2026", "Produção acadêmica",
        "Triagem independente", "Aprendizagem e identidade", "Trajetórias profissionais",
        "Relações IES, escolas e comunidades", "Evidência e localização",
        "Limites e pendências", "Data da avaliação", "Avaliador",
    ]
    aba.append(campos)
    for registro in registros:
        codigo = registro["Código"]
        resumo = resumos.get(codigo) or registro["Resumo"] or ""
        if len(resumo) > 32767:
            raise ValueError(f"Resumo excede limite de célula do Excel: {codigo}")
        valores = [
            registro["Código"], registro["Fonte"], registro["Tipo de produção"],
            registro["Título"], registro["Autoria"], registro["Ano de publicação"],
            registro["Ano de defesa"], "Sim" if resumo else "Não", resumo,
            registro["Palavras-chave"], registro["Instituição associada"],
            registro["Afiliações de autoria"], registro["DOI"], registro["Link da fonte"],
            registro["Link OpenAlex"],
        ] + [None] * (len(campos) - 15)
        aba.append(valores)
        for celula in aba[aba.max_row]:
            if isinstance(celula.value, str):
                celula.data_type = "s"
            celula.alignment = Alignment(vertical="top", wrap_text=True)
    listas = {
        "P": "Tema central do estudo,Relação substantiva com PIBID,Menção incidental,Outro significado para a sigla,Incerto",
        "Q": "Pesquisa realizada em Goiás,Afiliação em Goiás apenas,Sem evidência de contexto goiano,Incerto",
        "R": "Sim,Não (confirmado),Não informado,Incerto",
        "S": "Publicação 2020–2026 confirmada,Publicação fora de 2020–2026,Ano ausente,Só ano de defesa disponível,Incerto",
        "T": "Sim,Não,Incerto",
        "U": "Avançar para avaliação,Excluir,Pendente",
        "V": "Presente,Não informado,Não verificável,Pendente",
        "W": "Presente,Não informado,Não verificável,Pendente",
        "X": "Presente,Não informado,Não verificável,Pendente",
    }
    for coluna, opcoes in listas.items():
        validacao = DataValidation(type="list", formula1=f'"{opcoes}"', allow_blank=True)
        validacao.showErrorMessage = True
        validacao.errorTitle = "Valor inválido"
        validacao.error = "Selecione uma opção da lista."
        aba.add_data_validation(validacao)
        validacao.add(f"{coluna}2:{coluna}{len(registros) + 1}")
    tabela = Table(displayName="ValidacaoIndependente", ref=f"A1:AB{len(registros) + 1}")
    tabela.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2", showFirstColumn=False, showLastColumn=False,
        showRowStripes=True, showColumnStripes=False,
    )
    aba.add_table(tabela)
    aba.freeze_panes = "D2"
    for i, nome in enumerate(campos, 1):
        aba.column_dimensions[get_column_letter(i)].width = (
            65 if nome == "Resumo" else 45 if nome in {"Título", "Evidência e localização", "Limites e pendências"} else 23
        )
    return workbook


def main():
    for saida in (SAIDA, SINAIS, SORTEIO, VALIDACAO):
        if saida.exists():
            raise FileExistsError(f"Arquivo já existe; não será sobrescrito: {saida}")

    dados = json.loads(METADADOS.read_text(encoding="utf-8"))
    obras = {obra["id"]: obra for obra in dados["response"]["results"]}
    if len(obras) != 36:
        raise ValueError("Metadados do piloto não contêm 36 identificadores únicos")
    avaliacoes = ler_csv(REVISOES)
    revisoes = {linha["codigo"]: linha for linha in avaliacoes}
    if len(revisoes) != len(avaliacoes):
        raise ValueError("Avaliação prioritária contém códigos duplicados")
    workbook = load_workbook(BASE)
    aba = workbook["Triagem"]
    col = cabecalhos(aba)
    registros = []
    linhas = {}
    for linha in range(2, aba.max_row + 1):
        registro = {nome: aba.cell(linha, coluna).value for nome, coluna in col.items()}
        codigo = registro["Código"]
        if not codigo or codigo in linhas:
            raise ValueError(f"Código ausente ou repetido: {codigo}")
        registros.append(registro)
        linhas[codigo] = linha
    if len(registros) != 1317 or not set(revisoes).issubset(linhas):
        raise ValueError("Universo ou códigos da avaliação prioritária divergentes")
    resumos = {}
    for registro in registros:
        if registro["Piloto CAPES"] == "Sim":
            obra = obras[registro["Link OpenAlex"]]
            resumos[registro["Código"]] = reconstruir_resumo(obra["abstract_inverted_index"])
    if len(resumos) != 36:
        raise ValueError("O piloto não contém 36 resumos")

    for codigo, revisao in revisoes.items():
        outro = revisao["par_candidato"]
        if outro:
            if outro not in revisoes or revisoes[outro]["par_candidato"] != codigo:
                raise ValueError(f"Par não recíproco: {codigo}")
            campos_iguais = ("Título", "Autoria", "Ano de defesa", "Instituição associada", "Resumo", "Palavras-chave")
            if any(aba.cell(linhas[codigo], col[campo]).value != aba.cell(linhas[outro], col[campo]).value for campo in campos_iguais):
                raise ValueError(f"Campos do par candidato divergem: {codigo}, {outro}")

    campos_sinais = [
        "codigo", "fonte", "sinal_pibid_campos", "sinal_goias_campos",
        "doi_repetido", "titulo_normalizado_repetido", "situacao_temporal",
        "resumo_disponivel", "revisao_local_prioritaria",
    ]
    dois = Counter(texto_normalizado(r["DOI"]).removeprefix("https://doi.org/").strip() for r in registros if r["DOI"])
    titulos = Counter(re.sub(r"\W+", " ", texto_normalizado(r["Título"])).strip() for r in registros)
    sinais = []
    grupos = defaultdict(list)
    por_codigo = {r["Código"]: r for r in registros}
    for registro in registros:
        codigo = registro["Código"]
        numero = linhas[codigo]
        campos = {nome: registro[nome] for nome in LOCALIZACOES}
        tema = sinal({nome: campos[nome] for nome in ("Título", "Resumo", "Palavras-chave")}, PADRAO_TEMA)
        go = sinal(campos, PADRAO_GO)
        resumo_disponivel = bool(registro["Resumo"] or resumos.get(codigo))
        estado_amostra = categoria_temporal(registro)
        chave = (registro["Fonte"], estado_amostra, "com_sinal" if go else "sem_sinal", "com_resumo" if resumo_disponivel else "sem_resumo")
        grupos[chave].append(codigo)
        doi = texto_normalizado(registro["DOI"]).removeprefix("https://doi.org/").strip()
        titulo = re.sub(r"\W+", " ", texto_normalizado(registro["Título"])).strip()
        sinais.append({
            "codigo": codigo, "fonte": registro["Fonte"],
            "sinal_pibid_campos": "; ".join(tema), "sinal_goias_campos": "; ".join(go),
            "doi_repetido": "Sim" if doi and dois[doi] > 1 else "Não",
            "titulo_normalizado_repetido": "Sim" if titulos[titulo] > 1 else "Não",
            "situacao_temporal": estado_amostra,
            "resumo_disponivel": "Sim" if resumo_disponivel else "Não",
            "revisao_local_prioritaria": "Sim" if codigo in revisoes else "Não",
        })
        if registro["Piloto CAPES"] == "Sim":
            continue
        tipo = registro["Tipo de produção"]
        valores = {
            "Relação com PIBID": "Incerto",
            "Contexto de Goiás": "Incerto",
            "Publicação em 2020–2026": periodo(registro["Ano de publicação"], registro["Ano de defesa"]),
            "Produção acadêmica": "Sim" if tipo in {"Tese", "Dissertação"} else "Incerto",
            "Afiliação em Goiás": "Incerto",
            "Fontes das evidências": f"Metadados da planilha; fonte {registro['Fonte']}.",
            "Material consultado": "Metadados e sinais textuais; sem revisão semântica integral.",
            "Limitações e pendências": "Classificação automática preliminar; verificar conteúdo, afiliações, data e duplicidade.",
            "Observações": "Pré-análise local; sinais textuais não são decisão de elegibilidade.",
        }
        if codigo in revisoes:
            revisao = revisoes[codigo]
            valores["Relação com PIBID"] = {
                "substantiva": "Relação substantiva com PIBID", "incerto": "Incerto"
            }[revisao["pibid"]]
            valores["Contexto de Goiás"] = {
                "go": "Pesquisa realizada em Goiás", "incerto": "Incerto"
            }[revisao["contexto"]]
            valores["Evidência do contexto"] = revisao["nota"]
            valores["Material consultado"] = "Título e resumo da planilha; avaliação preliminar."
            valores["Decisão de elegibilidade"] = "Pendente"
            if revisao["par_candidato"]:
                valores["Duplicidade"] = "Duplicata provável"
                valores["Observações"] = f"Par candidato {revisao['par_candidato']}; não é duplicata confirmada."
        for nome, valor in valores.items():
            aba.cell(numero, col[nome]).value = valor

    alocacoes = {}
    for fonte, cota in COTAS.items():
        estratos = {k: v for k, v in grupos.items() if k[0] == fonte}
        alocacoes.update(distribuir(estratos, cota))
    if set(grupos) != set(alocacoes):
        raise ValueError("Há fonte sem cota definida")
    rng = random.Random(SEMENTE)
    amostra = []
    manifestos = []
    for chave in sorted(grupos):
        codigos = sorted(grupos[chave])
        n = alocacoes[chave]
        for codigo in rng.sample(codigos, n):
            amostra.append(por_codigo[codigo])
            manifestos.append({
                "codigo": codigo, "fonte": chave[0], "situacao_temporal": chave[1],
                "sinal_goias": chave[2], "resumo": chave[3], "N": len(codigos), "n": n,
                "probabilidade_n_sobre_N": f"{n}/{len(codigos)}",
            })
    if len(amostra) != 60 or len({r["Código"] for r in amostra}) != 60:
        raise ValueError("A amostra não contém 60 códigos únicos")
    random.Random(SEMENTE_ORDEM).shuffle(amostra)
    formulario = criar_formulario(amostra, resumos)

    with SAIDA.open("xb") as arquivo:
        workbook.save(arquivo)
    salvar_csv(SINAIS, campos_sinais, sinais)
    salvar_csv(SORTEIO, [
        "codigo", "fonte", "situacao_temporal", "sinal_goias", "resumo", "N", "n",
        "probabilidade_n_sobre_N",
    ], manifestos)
    with VALIDACAO.open("xb") as arquivo:
        formulario.save(arquivo)
    print(f"Registros pré-analisados: {len(registros)}; revisões locais: {len(revisoes)}")
    print(f"Estratos: {len(grupos)}; amostra: {len(amostra)}")
    print("Cotas:", dict(Counter(r["Fonte"] for r in amostra)))
    print("Saídas:", SAIDA, SINAIS, SORTEIO, VALIDACAO, sep="\n")


if __name__ == "__main__":
    main()
