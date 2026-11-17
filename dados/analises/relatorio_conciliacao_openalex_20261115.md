# Conciliação inicial do OpenAlex com a base anterior

**Data:** 15/11/2026. **Situação:** identificação de candidatos e sinais para priorização; não é deduplicação concluída nem triagem de elegibilidade.

## Procedimento

Foram comparados os 12.431 registros do [CSV OpenAlex](./openalex_busca_restrita_20261115.csv) com as 1.317 linhas da [base técnica vigente](./triagem_criterio_defesa_20261115.xlsx). A comparação cruzou DOI normalizado, identificador OpenAlex já associado e título exato após normalização de caixa, acentos e pontuação. Valores ausentes não foram comparados entre si.

Cada par com pelo menos um sinal foi registrado em [correspondências candidatas](./openalex_correspondencias_candidatas_20261115.csv), com fontes, sinais, títulos, tipos e anos conforme cada origem. Uma obra pode corresponder a várias linhas e uma linha pode ter vários candidatos. **Nenhum par foi automaticamente confirmado, fundido ou removido.** Títulos iguais, isoladamente, não demonstram identidade; artigos e teses relacionados podem ser produções distintas. DOI ou identificador concordante também requerem verificação de conflitos bibliográficos antes do tratamento definitivo.

Em paralelo, o [inventário de sinais](./openalex_sinais_triagem_20261115.csv) registra ocorrência textual do PIBID no título, resumo e palavras-chave, e de Goiás/goiano/goiana nesses campos ou nos nomes de instituições disponíveis. Esses sinais servem para priorização, não comprovam relevância, local da pesquisa ou afiliação em Goiás. Os critérios literais não abrangem todos os nomes institucionais ou contextos possíveis. Ausência de sinal ou resumo **não é exclusão** nem gera, por si só, pendência ou busca individual.

## Resultados

| Indicador | Quantidade |
|---|---:|
| Pares candidatos OpenAlex–base | 689 |
| Identificadores OpenAlex com pelo menos um candidato | 642 |
| Linhas da base com pelo menos um candidato | 665 |
| Pares com coincidência de título normalizado | 681 |
| Pares com coincidência de DOI | 168 |
| Pares com identificador OpenAlex coincidente | 36 |
| Pares com títulos divergentes ou não comparáveis | 8 |
| Registros OpenAlex com sinal textual de Goiás **ou** sinal no nome institucional | 333 |

Os sinais em um par se sobrepõem, portanto suas contagens não devem ser somadas. Os 689 pares correspondem a 479 linhas de comparação com BDTD, 121 com Portal CAPES, 73 com SciELO e 16 com Catálogo CAPES; são pares, não obras distintas. Entre eles há, por exemplo, 45 pares com tipo `article` no OpenAlex e tese ou dissertação na base, que não devem ser fundidos apenas pelo título. Quarenta e seis identificadores OpenAlex têm candidatos em duas ou mais linhas da base, que por sua vez podem se sobrepor.

Entre os 12.431 registros, 201 têm sinal geográfico nos campos textuais e 258 em nomes de instituições; 333 têm um ou ambos. Os 12.390 com sinal textual do PIBID são ocorrências literais, não confirmações de pertinência; os demais não foram excluídos. A busca original da API também pode ter recuperado candidatos por palavras-chave indexadas, sem que a regra literal encontre o termo nos campos preservados.

## Verificação e limites

O [script](../../scripts/conciliar_openalex_20261115.py) usa os normalizadores já existentes e recusou sobrescrita. A [auditoria estruturada](./openalex_conciliacao_auditoria_20261115.json) registra as contagens. Foram reabertos os dois CSVs, conferidas suas dimensões, unicidade dos pares e identificadores, e o número de correspondências por registro; testes focados verificaram sinais, campos ausentes e tipos diferentes. Os arquivos de entrada não foram alterados. Isso não constitui validação científica independente.

A comparação por título e identificadores existentes não encontra necessariamente todas as duplicatas nem resolve títulos divergentes. Não houve consulta externa ou análise individual de documentos. As decisões anteriores, as 19 inclusões operacionais, os 1.099 casos sem decisão na base anterior e os gráficos permanecem inalterados. Os registros OpenAlex ainda não foram integrados à elegibilidade nem contados como resultados nacionais ou goianos; a coleta incompleta do Portal continua uma limitação.

## Continuidade

Priorizar, com as evidências arquivadas, os pares com identificadores concordantes e os 333 registros com sinais geográficos, sem interpretar esse conjunto como todos os trabalhos goianos. Retomar também os três pares já confirmados por ano de defesa e as duas dúvidas temáticas previamente identificadas. Depois de conciliar e triar de forma documentada, atualizar os resultados possíveis, os gráficos e o relatório, explicitando o material ainda não avaliado e a cobertura incompleta.
