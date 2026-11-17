# Pré-análise local e preparação da validação

**Data:** 15 de novembro de 2026  
**Situação:** pré-análise e amostra preparadas; a validação independente e a seleção final ainda não foram realizadas.

## 1. Materiais e procedimentos

Foram utilizados exclusivamente os materiais já disponíveis: a [planilha do piloto](./triagem_piloto_20261115_criterio_aprovado.xlsx), os 36 metadados OpenAlex anteriormente arquivados e a [avaliação local prioritária](./avaliacao_local_prioritaria_20261115.csv). Nesta etapa não houve nova consulta externa.

A [planilha de pré-análise](./triagem_preanalise_local_20261115.xlsx) conserva os 36 registros piloto e suas extrações. Nos demais 1.281 registros, foram preenchidas as situações de período e tipo documental que os metadados permitiam classificar. Quando a informação disponível era insuficiente, foi indicado `Incerto` ou `Só ano de defesa disponível`; não houve exclusão automática.

Foram também examinados títulos e resumos de **sete registros prioritários**, escolhidos por sinais de Goiás e defesa recente. Quatro têm um segundo registro com título, autoria, ano de defesa, instituição, resumo e palavras-chave idênticos; as avaliações foram aplicadas aos pares correspondentes, totalizando 11 linhas avaliadas. Os oito registros desses quatro pares foram marcados como **duplicata provável**, não confirmada. Nenhum registro principal foi escolhido ou removido. As decisões são preliminares e não substituem a validação independente.

O [arquivo de sinais](./sinais_preanalise_local_20261115.csv) registra, para cada linha, os campos da planilha em que foram encontrados sinais literais de PIBID e de Goiás, além de alertas de DOI ou título repetido. Os sinais são úteis para priorização, **não são classificações temáticas, geográficas ou de duplicidade**. Não foram buscados automaticamente nomes de todos os municípios ou instituições goianas; a ausência de sinal não comprova ausência de relação com Goiás. Os sinais textuais usam os campos da planilha; para o piloto, a disponibilidade de resumo também considera o OpenAlex arquivado.

## 2. Cobertura da pré-análise

Nos 1.281 registros fora do piloto:

| Informação | Situação |
|---|---:|
| Apenas ano de defesa disponível, sem ano de publicação | 1.138 |
| Ano de publicação fora de 2020–2026 | 110 |
| Ano de publicação em 2020–2025 | 30 |
| Ano de publicação 2026, sem data completa estabelecida | 3 |
| Tipo tese ou dissertação, provisoriamente identificado como acadêmico | 1.137 |
| Relação substantiva com PIBID na avaliação local direcionada | 6 linhas |
| Contexto goiano identificado na avaliação local direcionada | 8 linhas |

As linhas com avaliação local incluem candidatos duplicados, por isso essas contagens **não** representam estudos únicos. Os demais registros fora do piloto não foram examinados semanticamente de maneira individual: relação com PIBID, contexto e afiliação permanecem `Incerto`. Também não foram produzidas novas extrações dos eixos para esses registros.

No conjunto das 1.317 linhas, o arquivo de sinais identifica termo temático em 1.130 e sinal literal de Goiás em 69. Há 229 linhas com título normalizado repetido e duas com DOI repetido. Nenhuma dessas contagens é quantidade de estudos elegíveis, duplicatas confirmadas ou estimativa da produção científica.

O ano de defesa não foi convertido em ano de publicação. Os três registros de 2026 fora do piloto permanecem incertos quanto à data de corte de 8 de novembro, pois a data completa não está estabelecida nos dados consultados. Os registros de publicação anterior a 2020 foram identificados como fora do recorte **goiano**, mas continuam relevantes à eventual análise nacional de 2007–2026.

## 3. Amostra independente de 60 registros

O [desenho de validação](./desenho_validacao_20261115.md) foi definido antes do sorteio. A [planilha de validação independente](./validacao_independente_60_20261115.xlsx) contém os materiais disponíveis e campos vazios para avaliação, sem expor as classificações ou os estratos automáticos.

| Fonte | Registros sorteados |
|---|---:|
| BDTD | 24 |
| Portal CAPES | 14 |
| Catálogo CAPES | 11 |
| SciELO | 11 |
| **Total** | **60** |

O sorteio contempla 18 estratos. Há 50 registros com resumo disponível e dez sem resumo; nesses casos, a pesquisadora poderá registrar que o material é insuficiente. Se a análise de algum eixo não for pertinente ou a elegibilidade permanecer pendente, não é necessário forçar o preenchimento do eixo.

O [manifesto técnico do sorteio](./sorteio_validacao_60_20261115.csv) contém identificadores, estratos, população, cotas e probabilidades. Para manter a avaliação independente, as decisões da pré-análise, o arquivo de sinais e esse manifesto não devem ser consultados durante o preenchimento. Depois da devolução da planilha, será possível comparar respostas com as classificações efetivamente produzidas, considerando pesos e incerteza.

Como a avaliação semântica individual cobre apenas o piloto e os 11 registros prioritários, a amostra não permite medir como se houvesse classificação temática ou extração de eixos para todo o universo. A avaliação de duplicidade também necessita de comparação dos pares e não está concluída neste formulário. Não há base para atribuir confiança percentual a registros ou gráficos nesta etapa.

## 4. Verificações e limites

O [procedimento de geração](../../scripts/preanalise_e_validacao_20261115.py) tem testes para ano e data de corte, sinais geográficos, reconstrução dos resumos, distribuição da amostra e ausência de respostas automáticas no formulário.

Foram conferidos os arquivos XLSX como ZIP e reabertos por biblioteca; tabelas e validações da planilha de trabalho foram preservadas. A comparação célula a célula confirmou que somente colunas previstas dos registros fora do piloto foram alteradas e que as demais abas permaneceram intactas. O formulário tem 60 códigos únicos, campos de resposta vazios e nenhuma fórmula; as cotas e o sorteio foram reproduzidos com as sementes documentadas, conferindo-se `N`, `n` e `n/N`.

Não houve teste interativo no Excel, conferência de fontes primárias nesta etapa, validação pela pesquisadora ou medição do tempo de revisão humana. A planilha de pré-análise ainda contém colunas técnicas e não é a entrega final simplificada.
