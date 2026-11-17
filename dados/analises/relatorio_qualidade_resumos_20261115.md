# Tratamento documental dos resumos não preservados

**Atualização posterior:** a etapa seguinte identificou mais 64 campos com marcadores ou outros metadados em vez de resumo substantivo. A marcação foi corrigida em nova cópia, totalizando 273 linhas. Os números de 209 e 1.108 abaixo registram a situação histórica desta etapa; consultar o [relatório posterior](./relatorio_catalogo_lote3_20261115.md) e a [base vigente](./triagem_catalogo_lote3_20261115.xlsx).

## Decisão operacional

A ausência de resumo substantivo no campo da base é limitação documental e não gera, isoladamente, pendência nem consulta individual para recuperá-lo. Quando a ocorrência do termo está demonstrada, essa limitação deve acompanhar os resultados como qualidade documental reduzida. Dúvidas independentes sobre pertinência substantiva, período, contexto, afiliação, natureza acadêmica ou duplicidade continuam distintas. A marcação documental não decide inclusão ou exclusão.

Essa orientação substitui recomendações anteriores de pendência ou consulta motivadas **apenas** pela ausência do resumo. As observações anteriores foram preservadas como histórico e receberam nota explícita sobre a regra atual. Os estados anteriores de triagem e elegibilidade não foram alterados: sua persistência não deve ser interpretada como pendência criada pela falta de resumo, nem como indicação de que todas as dúvidas foram resolvidas.

## Procedimento e resultados

A partir da [base anterior](./triagem_portal_campos_20261115.xlsx), foi criada a [nova base técnica](./triagem_qualidade_resumos_20261115.xlsx), sem alterar a entrada. Foram examinados os campos `Resumo`, `Título` e `Palavras-chave`, com identificação literal da sigla ou da expressão do programa e reaproveitamento da conferência anterior das oito páginas do Portal. A classificação do conteúdo do campo resumo empregou as regras existentes para vazio, possível orientação e possível referência bibliográfica. Não houve consulta individual adicional.

| Fonte | Campo vazio | Possível orientação | Possível referência | Total de linhas |
|---|---:|---:|---:|---:|
| Portal CAPES | 103 | 0 | 0 | 103 |
| BDTD | 23 | 50 | 33 | 106 |
| Total | 126 | 50 | 33 | 209 |

As 209 linhas receberam `Reduzida — campo sem resumo substantivo` na coluna **Qualidade documental do resumo** e constam da aba filtrável **Qualidade dos resumos**, com as evidências separadas. A classificação se refere ao campo da base, não assegura ausência de resumo em outras fontes e não mede a precisão das demais informações. As 1.108 linhas restantes foram marcadas `Não avaliada nesta etapa`; isso não significa que seus resumos ou extrações tenham sido validados. As contagens são de linhas, não de obras únicas.

Entre as 209 linhas, o termo foi identificado por regra no título de 137: 68 do Portal CAPES e 69 da BDTD. Nas outras 72:

- oito do Portal têm o termo nos resumos das páginas consultadas anteriormente, mas não nos títulos; essas páginas, consultadas após o corte de 08/11/2026, não comprovam o que estava visível na coleta;
- duas da BDTD têm termo nas palavras-chave, mas não no título; palavras-chave não demonstram ocorrência histórica no título ou resumo;
- 27 do Portal e 35 da BDTD não apresentaram termo literal no título ou nas palavras-chave pela regra aplicada. A recuperação por assunto ou em todos os campos não comprova, por si, ocorrência em título ou resumo. A ausência de identificação literal tampouco prova ausência do termo em outras fontes já consultadas ou ausência de relação substantiva.

A aba conserva o material anteriormente consultado por registro; em particular, existem evidências anteriores em repositórios para alguns casos sem termo literal nos campos examinados nesta etapa. Essas evidências não foram apagadas nem reanalisadas aqui. A regra literal não esgota variantes linguísticas e não substitui leitura temática dos materiais disponíveis.

## Limites para resultados e gráficos

A categoria é qualitativa e documental, não equivale a porcentagem de confiança, probabilidade de acerto ou validação independente. Ela identifica uma limitação relevante mesmo em linhas que não sejam elegíveis. Para resultados e gráficos futuros, considerar somente registros efetivamente selecionados, após resolver os demais critérios e duplicidades, e informar a quantidade com qualidade documental reduzida e o denominador correspondente. Não multiplicar contagens por valores de confiança inventados.

## Verificação

Os testes focalizados conferiram a seleção, a distinção entre título, palavras-chave e resumo atual, a preservação dos estados e dos demais campos, a recusa de sobrescrita e de divergência na identidade dos oito registros conferidos. Também foram verificados fórmulas, validações, dimensões e filtros das tabelas, integridade ZIP e preservação do arquivo de entrada. Não houve teste interativo no Excel.
