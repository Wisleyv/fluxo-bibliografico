# Terceiro lote de leituras do Catálogo CAPES

**Atualização posterior:** os 28 registros com resumos disponíveis que ainda restavam foram lidos. Os dois outros têm marcador de resumo indisponível. Consultar a [base vigente](./triagem_catalogo_lote5_20261115.xlsx) e o [relatório dos lotes seguintes](./relatorio_catalogo_lotes4e5_20261115.md); os totais abaixo são históricos.

## Procedimento

Foram lidos os dez primeiros registros ainda não examinados nas etapas bilíngues anteriores, na ordem do inventário. Para cada um, foram consultados título, campos `DS_RESUMO` e `DS_ABSTRACT` e palavras-chave do arquivo anual CAPES de 2024, comparando identificador, título, autoria e resumo em português com a base. A seleção é operacional, não uma amostra representativa; não houve consulta externa.

Embora o inventário histórico chame o segundo campo de resumo inglês, em `bc0f1ea5` ele contém texto **em espanhol**. A leitura considerou essa língua e a ressalva foi registrada. As [avaliações individuais](./avaliacao_catalogo_lote3_20261115.csv) e a aba **CAPES bilíngue lote 3** da [base atualizada](./triagem_catalogo_lote3_20261115.xlsx) documentam evidências e limites.

## Resultado

Em cinco registros, o PIBID é tema central; em três, apresenta relação substantiva com o estudo; em dois, a relação permanece incerta. Os dez continuam com triagem pendente por outros critérios e sem decisão final. Não houve exclusão neste lote.

- Em `2fda2cb6` e `9f3cb0ea`, o programa identifica participantes de cursos, mas os resumos não estabelecem que os cursos fossem ações do PIBID; os resultados não foram atribuídos automaticamente ao programa.
- Em `634b7e49` e `bb48b0d9`, os achados reúnem o PIBID e outros espaços ou programas formativos; não se presume contribuição exclusiva do PIBID.
- Em `8e68ac12`, o jogo digital é uma proposta conceitual, não uma aplicação comprovada. Em `c7fd8559`, as percepções de ex-bolsistas incluem obstáculos ao ingresso profissional, sem estabelecer causalidade.
- Em `16fa7013`, os achados de desenvolvimento profissional referem-se a professores supervisores, e não necessariamente a licenciandos ou a trajetórias ocupacionais posteriores.

Não foi identificada evidência de contexto goiano no título e nos resumos dos dez registros; isso não comprova ausência de contexto ou afiliação em Goiás. Ano de defesa não foi convertido em ano de publicação. Duplicidade e elegibilidade final não foram decididas.

Foram acrescentadas 30 extrações provisórias dos eixos: oito `Presente`, oito `Não informado` e 14 `Não verificável`. As sínteses e os limites por registro acompanham as extrações; elas não são contagens de estudos elegíveis.

## Correção documental ligada à etapa anterior

Na conferência do inventário, foram encontrados dois campos `DS_RESUMO` e `DS_ABSTRACT` com o marcador **EM CONSTRUÇÃO**, que a regra anterior não havia identificado como ausência de resumo substantivo. Uma verificação adicional dos campos curtos da base identificou mais 62 linhas BDTD que continham apenas marcadores ou metadados, como referência bibliográfica, orientação, financiamento ou descrição de material acompanhante.

Essas 64 linhas foram acrescentadas à aba de qualidade documental e marcadas como `Reduzida — campo sem resumo substantivo`. O total passou de 209 para **273 linhas**; as demais **1.044** seguem como `Não avaliada nesta etapa`. A correção diz respeito ao campo da base, não garante inexistência de resumo em outras fontes, não comprova ocorrência do termo nem altera decisões de triagem ou elegibilidade. Não se criou pendência nem busca individual pela falta do resumo. Não se afirma que todos os campos não avaliados sejam resumos substantivos.

## Situação da base

As quatro etapas de leitura examinaram 48 dos 78 registros do inventário histórico. Restam 30 sem leitura nessas etapas, dos quais dois têm `EM CONSTRUÇÃO` em ambos os campos de resumo. Eles não exigem busca individual para suprir essa falta; dúvidas independentes continuam distintas.

| Indicador | Linhas |
|---|---:|
| Triagem: avançar para avaliação | 19 |
| Triagem: excluir preliminarmente | 197 |
| Triagem: pendente | 1.101 |
| Elegibilidade: pendente | 433 |
| Elegibilidade: não iniciada | 884 |
| Duplicidade confirmada | 80, correspondentes a 40 pares |
| Duplicidade não verificada | 1.237 |

A base contém 744 pares registro/eixo, dos quais 663 têm estado preenchido. Esses dados incluem duplicatas e casos sem elegibilidade definida; não são resultados finais nem quantidades de obras únicas. A coleta nacional permanece incompleta.

## Verificação e limites

O [integrador](../../scripts/integrar_catalogo_lote3_20261115.py) impede sobrescrita e verifica identidade, resumos, histórico e estados anteriores. Foram testadas a preservação fora do escopo, a correção documental, as validações, filtros e tabelas, fórmulas e integridade ZIP. A análise e sua conferência não são independentes, não medem acurácia e não fundamentam percentuais de confiança. Não houve teste interativo no Excel.
