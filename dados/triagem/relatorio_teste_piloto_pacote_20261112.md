# Teste técnico do pacote — lote piloto CAPES

**Data:** 12 de novembro de 2026. **Natureza:** verificação operacional e inventário da evidência já registrada; não é uma revisão de elegibilidade ou análise qualitativa. Este relatório descreve a primeira versão do pacote, posteriormente simplificada; os nomes de abas e arquivos a seguir são históricos.

## Resultados

- Os **36 IDs** da aba `Revisão CAPES 36` são únicos, estão presentes em `Triagem Goiás` e correspondem à fonte Portal CAPES. A ficha complementar contém os mesmos 36 IDs e três linhas de eixos por ID, totalizando 108 linhas.
- Os 36 registros têm ano CAPES informado entre 2020 e 2026, DOI, link DOI e link OpenAlex preenchidos. A planilha registra coincidência do ano com o OpenAlex em 36 casos. Esses sinais não confirmam, por si sós, elegibilidade ou acesso atual.
- No campo de resumo e no campo de afiliações da aba principal, há **36 vazios em cada**. A aba histórica informa que os resumos estavam disponíveis no OpenAlex em 10 de novembro, mas eles não foram reproduzidos integralmente no pacote. Assim, a pesquisadora precisará consultar as fontes; os links e os resumos não foram revalidados neste teste.
- A aba informativa registra 17 sinais de Goiás em resumos, 17 sem sinal identificado e dois com sinal de outro estado. São sinais históricos, não classificação do contexto ou da afiliação. A síntese de status anterior indica três resumos com sinal de outro estado, enquanto a coluna por registro indica dois; a diferença **não foi reconciliada**. Conferir os registros e não usar essas contagens como decisão ou resultado.
- Nenhum dos 36 IDs aparece nos 114 grupos candidatos já listados na aba de duplicatas. Isso não comprova ausência de duplicatas: a lista resulta de critérios automáticos limitados.
- As 36 decisões de título/resumo estão `Pendente`, as decisões de elegibilidade `Não iniciada` e os estados de duplicidade `Não verificada`. A ficha complementar não contém decisões ou trechos preenchidos.
- A checagem programática conferiu integridade ZIP/XML, cabeçalhos, tabelas, listas, IDs, links relativos do guia e identidade das cópias documentais. Um preenchimento **fictício** foi salvo e reaberto em cópias temporárias, depois removidas; nenhum dado de teste foi gravado nas planilhas entregues. A versão original foi preservada.

## Limitações e encaminhamento

Não houve teste interativo desta cópia no Excel, nem teste com a pesquisadora, nem leitura individual dos 36 resumos para decidir pertinência, contexto, duplicidade ou extração qualitativa. O teste estrutural não garante ausência de avisos de reparo no Excel. É necessário fazer o piloto humano conforme o [guia atualizado](../entregas/pacote_preliminar_20261112/LEIA-ME%20-%20orienta%C3%A7%C3%B5es%20para%20a%20pesquisadora.md), registrar dificuldades e acordar as regras de decisão antes de expandir o procedimento.
