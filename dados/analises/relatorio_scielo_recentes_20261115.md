# Leitura de artigos recentes e conferência de duplicatas

**Data:** 15 de novembro de 2026  
**Produto:** [base técnica atualizada](./triagem_scielo_recentes_20261115.xlsx).

## Seleção e materiais

Foram examinados 28 artigos SciELO de 2020 a 2026 que permaneciam com relação com o PIBID incerta na base anterior. A seleção não dependeu de sinal regional explícito. Para cada artigo, foram lidos o título e o resumo disponível na planilha, registrando-se decisões, síntese e limites no [arquivo de avaliações](./avaliacao_scielo_recentes_20261115.csv) e na aba **Lote SciELO recente**.

Como o arquivo RIS local não apresentava afiliações, foram consultados os metadados das páginas SciELO dos próprios artigos já coletados, sem ampliar a busca bibliográfica. As consultas foram registradas em [metadados](./metadados_scielo_recentes_20261115.json). Três endereços retornaram erro HTTP 502; seus endereços canônicos foram consultados separadamente, com resultados em [complemento](./metadados_scielo_recentes_complemento_20261115.json). DOI, autoria e ano foram confrontados com a base antes da integração.

As instituições listadas nos metadados foram registradas sem atribuir uma instituição específica a cada autor. Mesmo quando não listam instituição goiana, esses metadados não comprovam que não haja vínculo não informado. Contexto da pesquisa e afiliação de autoria foram tratados separadamente.

No registro **910fa3c6**, o resumo local não informava o local da escola. A seção inicial do [texto SciELO](https://doi.org/10.1590/1984-6398202549948) situa a experiência em Anápolis, Goiás; os metadados listam afiliações à Universidade Estadual de Goiás. Com publicação em 2025 e relação substantiva com o PIBID, o artigo passou a **avançar para avaliação**, não a inclusão final. A seção consultada não equivale à leitura integral do artigo.

Para os dois artigos de 2026, a SciELO e a Crossref apresentaram o ano de publicação sem data completa nos metadados consultados em 15/11/2026: [4264db79](https://api.crossref.org/works/10.1590%2Frbce.48.e20250074) e [cee52e9a](https://api.crossref.org/works/10.1590%2Fs0104-40362026003405141). Datas de criação ou depósito dos metadados não foram tratadas como data de publicação. Assim, a conformidade com o corte de **08/11/2026** permanece incerta.

## Situação do lote

| Triagem de título e resumo | Linhas |
|---|---:|
| Avançar para avaliação | 1 |
| Pendente | 27 |
| Excluir | 0 |
| **Total** | **28** |

O PIBID foi classificado como tema central em 23 linhas e como relação substantiva em cinco. Um registro tem contexto goiano e afiliação goiana identificados; sete têm `Sem evidência de contexto goiano` e 20 permanecem com contexto `Incerto`. A afiliação goiana permanece `Incerto` em 27 linhas. A ausência de informação regional não foi usada como exclusão. As 28 decisões finais de elegibilidade continuam pendentes, e a duplicidade dos artigos deste lote ainda não foi verificada.

Foram acrescentados **84 pares registro/eixo**: 34 `Presente`, 47 `Não informado` no material consultado e três `Não verificável`. Por exemplo, resultados sobre aprendizagem de estudantes escolares ou dificuldades cognitivas de tarefas não foram convertidos automaticamente em aprendizagem docente; permanência na licenciatura não foi confundida com trajetória profissional posterior. Os eixos são extrações provisórias de resumos, abrangem registros ainda não elegíveis e não constituem resultados finais da revisão.

## Duplicatas

Foram confirmados **23 pares adicionais**, listados em [pares conferidos](./pares_repositorio_recentes_20261115.csv) e na aba **Pares recentes conferidos**: 20 pares antes não verificados e três antes prováveis. A confirmação exigiu coincidência de título, autoria, tipo, ano de defesa, instituição e identificador de repositório, além de ausência de conflito em DOI ou ano de publicação quando ambos informados. Grupos maiores com os mesmos dados básicos foram deixados para conciliação.

Em um dos pares, o campo de link continha referência bibliográfica, endereço do repositório e DOI separados por `||`; o endereço de repositório foi identificado e validado separadamente, sem alterar o campo original nem usar o ano presente no DOI como ano de publicação. Nenhuma linha foi removida e não foi escolhido registro principal.

Um grupo de quatro linhas com o mesmo título, autoria, ano de defesa e identificador de repositório, mas com instituições associadas divergentes, permanece não verificado: **cc9255f4**, **03f41e0d**, **f2e72aea** e **14bf350a**. Outros candidatos ainda precisam ser avaliados.

## Situação da base

| Triagem de título e resumo | Linhas |
|---|---:|
| Avançar para avaliação | 19 |
| Excluir do recorte goiano por ano de publicação | 25 |
| Pendente | 1.273 |
| **Total** | **1.317** |

Na elegibilidade final, 163 linhas estão pendentes e 1.154 não iniciadas. A base contém 80 linhas em 40 pares de duplicatas confirmadas e 1.237 linhas com duplicidade não verificada. São contagens de **linhas**, não de obras únicas. Há 462 pares registro/eixo, dos quais 381 têm estado preenchido; incluem duplicatas e casos ainda sem elegibilidade definida.

## Verificação e limites

O [script de integração](../../scripts/integrar_scielo_recentes_20261115.py) preserva a base de entrada, confere os metadados das consultas e impede avanço sem os requisitos registrados. Os testes compararam as células fora do escopo, abas históricas e eixos anteriores; também verificaram validações, tabela e filtro dos eixos, fórmulas e integridade ZIP. Passaram 12 testes focados. Não houve teste interativo no Excel.

A leitura e a conferência computacional **não são independentes**, não medem acurácia e não fundamentam percentuais de confiança. A coleta nacional continua incompleta. Permanecem pendentes a análise de grande parte dos registros, a resolução das datas e duplicidades, a seleção final, os gráficos e o relatório metodológico final.
