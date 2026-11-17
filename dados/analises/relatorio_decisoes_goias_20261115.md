# Consolidação de decisões para a revisão goiana

**Data:** 15 de novembro de 2026  
**Base produzida:** [triagem com decisões do recorte goiano](./triagem_decisoes_goias_20261115.xlsx).

## Objetivo e procedimento

Para avançar com economia de processamento, foram consolidadas decisões sustentadas por dados já coletados, sem novas consultas ou leitura individual de arquivos ausentes. A decisão de elegibilidade desta etapa refere-se **à revisão de escopo sobre Goiás, de 2020 a 2026**; ela não decide automaticamente a participação no panorama nacional.

Foram retomados 19 registros que já avançavam para avaliação e 110 artigos com exclusão preliminar pelo ano de publicação. Os títulos, autorias, anos e DOIs disponíveis foram confrontados com os RIS originais. Para os registros do Portal candidatos à inclusão, foram também reaproveitados os resumos e metadados OpenAlex arquivados; para o artigo SciELO, a avaliação e os metadados da fonte já registrados.

Para os 11 registros incluídos, verificaram-se: relação substantiva com o PIBID, artigo acadêmico, publicação no período e até o corte de 08/11/2026, e contexto **ou** afiliação em Goiás. Os dez registros do Portal têm o termo do programa no título preservado; no registro SciELO, ele aparece no resumo preservado. As afiliações do Portal foram verificadas nos metadados OpenAlex, sujeitos às limitações dessa fonte. Para o registro de 2026 `22f73924`, a data OpenAlex é 01/06/2026; a [conferência anterior](./relatorio_conciliacao_pares_20261115.md) registrou a mesma data de publicação online na Crossref e a indisponibilidade da página do periódico consultada.

Antes das inclusões, foram comparados os DOIs e títulos dos 11 registros com os demais registros disponíveis: não houve candidato por DOI igual, similaridade normalizada de título de pelo menos 0,80 ou prefixo com pelo menos 20 caracteres. Essa busca não garante que não existam duplicatas e não altera o estado `Não verificada` da coluna de duplicidade. Os critérios e as decisões estão na aba **Decisões Goiás**.

## Decisões consolidadas

| Decisão para o recorte goiano | Linhas | Fundamentação |
|---|---:|---|
| Incluir | 11 | Dez do Portal CAPES e uma da SciELO, com os critérios acima sustentados pelo material disponível. |
| Excluir | 110 | Publicação anterior a 2020 conferida no campo `PY` dos RIS: 67 do Portal CAPES e 43 da SciELO. |

As 110 exclusões são **apenas temporais para a revisão goiana**: os registros continuam disponíveis para análise no panorama nacional. Os dois outros registros com exclusão preliminar por período são BDTD e não integraram a consolidação RIS desta etapa. As demais exclusões preliminares também não foram convertidas em decisões finais neste lote.

Os oito candidatos restantes entre os 19 que avançavam não foram objeto de nova decisão nesta etapa. Não se criou pendência nem se exigiu consulta individual apenas por falta de resumo preservado. O resumo atual consultado posteriormente, quando existente, não demonstra por si só o conteúdo histórico dos campos na data da coleta; esse limite é distinto da ausência documental e consta da [conferência anterior](./relatorio_campos_portal_20261115.md).

## Situação da base e limites

Das 1.317 linhas, a elegibilidade no recorte goiano está registrada como **11 inclusões**, **110 exclusões**, 343 pendentes e 853 não iniciadas. A triagem anterior permanece preservada: 19 avançam, 199 têm exclusão preliminar e 1.099 estão pendentes. Os estados de triagem descrevem a etapa anterior e não substituem a coluna de decisão de elegibilidade.

Dos 11 incluídos, dez têm qualidade documental reduzida no campo resumo da planilha; isso não significa ausência de resumo em fontes complementares. No outro registro, essa dimensão está marcada como não avaliada, não como validada. A documentação é qualitativa, sem percentual de confiança. Entre os 33 pares incluído/eixo, 12 têm estado preenchido e **21 ainda não foram extraídos**; campos vazios não são ausência de achado. As 11 linhas são decisões registradas, não uma estimativa do total definitivo de obras da revisão: restam registros por analisar e a deduplicação não está encerrada.

As decisões são rastreáveis e revisáveis, mas a análise não teve validação independente e não fundamenta taxas de acerto. Persistem incertezas sobre a cobertura das fontes e a coleta nacional incompleta. Valores antigos em campos de observações e limites foram mantidos como histórico, acompanhados de nota que informa a decisão atual.

## Verificação

O [integrador](../../scripts/consolidar_decisoes_goias_20261115.py) impede sobrescrita e exige correspondência com fontes e estados esperados; os [testes](../../tests/test_consolidar_decisoes_goias_20261115.py) verificaram decisões, preservação das demais células e abas, validações, tabela de auditoria, fórmulas, integridade ZIP e recusa de conflitos. Os três testes passaram. A base persistida foi aberta por biblioteca e seus totais e ZIP foram conferidos; não houve teste interativo no Excel.

**Próxima prioridade:** completar os 21 estados de eixo ainda vazios nos registros já incluídos, utilizando os resumos existentes e distinguindo ausência de informação de impossibilidade de avaliação; depois, consolidar resultados e gráficos com os denominadores e limitações explícitos, sem apresentar o conjunto ainda incompleto como revisão exaustiva.
