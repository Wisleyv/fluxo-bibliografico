# Aplicação do critério temporal alternativo por defesa

**Data:** 15 de novembro de 2026  
**Base produzida:** [triagem com critério por defesa](./triagem_criterio_defesa_20261115.xlsx).

## Decisão e procedimento

Foi aprovado o uso do **ano de defesa de 2020–2026** como critério temporal alternativo para teses e dissertações no recorte goiano. O ano de defesa não é ano de publicação. Para registros de 2026 com apenas o ano informado, a captura em 08/11/2026 demonstra que o registro estava na exportação, mas não confirma a data individual completa da defesa; o critério é aceito operacionalmente com evidência limitada. Não houve consulta individual para suprir datas.

Na base técnica, acrescentou-se a coluna **Critério alternativo por defesa** e uma aba de auditoria. As datas de publicação, a coluna específica sobre publicação e as decisões anteriores de elegibilidade foram preservadas. A presença do critério temporal não significa inclusão automática: continuam necessários pertinência ao PIBID, natureza acadêmica, contexto **ou** afiliação em Goiás e tratamento de duplicidade. A escolha de defesa como critério alternativo modifica a definição operacional da revisão, e a distinção precisa acompanhar os resultados.

## Alcance

| Indicador | Linhas |
|---|---:|
| Teses e dissertações com defesa de 2020–2025 | 402 |
| Teses e dissertações com defesa de 2026 e evidência temporal limitada | 15 |
| **Total com critério alternativo** | **417** |

Essas 417 linhas compreendem 340 da BDTD e 77 do Catálogo CAPES; são linhas, não obras únicas. A seleção respeita o tipo de produção: um registro de outro tipo com ano de defesa não foi automaticamente classificado como tese ou dissertação. Entre as 417 linhas, 53 já haviam sido excluídas por critério temático; as outras 364 permanecem sem decisão de elegibilidade. Duas linhas já tinham publicação de 2024 confirmada; a nova coluna também registra a defesa sem apagar essa evidência.

Oito das 417 linhas já tinham contexto goiano indicado. Seis são três pares de duplicatas confirmadas com relação substantiva ao PIBID previamente indicada; duas apresentam pertinência temática incerta. Essas indicações orientam a próxima avaliação, mas não substituem a conferência das evidências e a escolha do tratamento dos pares.

As decisões globais permanecem **19 inclusões, 199 exclusões e 1.099 linhas sem decisão**. As abas anteriores de priorização registram estados históricos e não incorporam a nova coluna; consultar **Triagem** e **Critério por defesa GO** para o critério atual. A ausência da marcação por defesa não prova que a publicação esteja fora do período.

## Verificação

O [integrador](../../scripts/aplicar_criterio_defesa_20261115.py) impede sobrescrita, confere o número de linhas e fontes esperados e não modifica os campos anteriores. Os [testes](../../tests/test_aplicar_criterio_defesa_20261115.py) conferiram as 417 marcações, o tratamento de 2026, tipo documental, dados anteriores, fórmulas, validações, tabela e filtro, integridade ZIP e recusa de conflitos. A base persistida foi aberta no Excel, que reconheceu as 1.317 linhas da tabela e as 417 linhas da auditoria. A verificação técnica não valida a interpretação temática nem elimina duplicatas.
