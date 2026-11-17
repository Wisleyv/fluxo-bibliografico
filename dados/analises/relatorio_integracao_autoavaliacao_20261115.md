# Integração da autoavaliação à base de trabalho

**Data:** 15 de novembro de 2026  
**Produto:** [base técnica integrada](./triagem_integrada_autoavaliacao_20261115.xlsx).

## Procedimento

As decisões da [autoavaliação de 60 registros](./amostra_60_autoavaliacao_20261115.xlsx) foram incorporadas a uma cópia da [pré-análise](./triagem_preanalise_local_20261115.xlsx), usando o código como identificador. Os dois arquivos de entrada e a amostra cega foram preservados.

Para cada registro da amostra foram integradas as avaliações de relação com PIBID, contexto, afiliação, período, natureza acadêmica e triagem, com evidências e limites. A aba **Alterações da amostra** registra valores anteriores e novos. As notas anteriores foram mantidas, identificadas como históricas, junto às informações da autoavaliação.

O ano de publicação de **06792f41** foi acrescentado com base no repositório indicado na evidência. A divergência de datas de **c3920958** permanece registrada, sem substituição silenciosa dos dados de origem. O par **83224e28/387c5254** foi marcado como duplicata confirmada, mas nenhum registro principal foi escolhido; ambos permanecem na base. O par não deve ser contabilizado como duas obras.

No registro **796dae04**, a pré-análise havia mantido o contexto `Incerto`, enquanto a autoavaliação o classificou como goiano. Como o resumo identifica o subprojeto da UFG, mas não explicita a localização das escolas, a divergência foi registrada e o contexto integrado permaneceu `Incerto`. O avanço desse registro também é fundamentado na afiliação goiana informada pelo OpenAlex; contexto e afiliação continuam separados.

A aba **Eixos de análise** recebeu três avaliações para cada um dos 60 registros da amostra, incluindo os que estão pendentes ou fora do recorte. Foram preservadas as nove avaliações anteriores do piloto; ao todo há **189 pares registro/eixo preenchidos** e 81 ainda vazios. As novas avaliações expressam o que foi encontrado no material consultado, não o resultado definitivo da revisão de escopo.

## Situação da triagem

| Triagem de título e resumo na base inteira | Linhas |
|---|---:|
| Avançar para avaliação | 18 |
| Excluir do recorte de Goiás por ano de publicação fora do intervalo | 14 |
| Pendente | 1.285 |
| **Total** | **1.317** |

As três linhas da amostra que avançam já pertenciam às 18 do piloto; não devem ser somadas novamente. As 14 exclusões se aplicam somente ao recorte goiano de 2020–2026 e não eliminam essas referências do panorama nacional. Os totais são de **registros**, não de obras únicas. Na coluna de elegibilidade final, 99 linhas estão pendentes e 1.218 não iniciadas: nenhuma inclusão ou exclusão final foi afirmada.

Os 1.257 registros fora da amostra não receberam alterações nesta integração; isso não significa que todos estejam sem pré-análise, pois parte já havia sido avaliada no piloto ou na análise prioritária. Não foi feita análise semântica adicional do restante da base nesta etapa.

## Limites e verificações

- A integração **não é validação independente**. A mesma assistência participou da pré-análise e da autoavaliação; não há fundamento para estimar acurácia ou atribuir faixas de confiança.
- Os eixos incluem registros sem elegibilidade definida e registros fora do recorte; suas contagens não representam resultados finais. A coleta nacional permanece incompleta.
- A divergência de contexto de 796dae04, as datas não confirmadas, a inconsistência título–resumo de 46baf45a, a conferência de outras duplicatas e as demais pendências permanecem em aberto. Não se ampliou a pesquisa externa nesta etapa.
- Foram conferidos os 60 códigos e a identidade bibliográfica básica, as listas de validação, a extensão da tabela e do filtro dos eixos, o ZIP e a ausência de fórmulas inesperadas. Os 1.257 registros fora da amostra, os 1.317 alertas originais e a aba de possíveis duplicatas foram comparados com a pré-análise e permaneceram intactos.
- Os dez testes focados de integração, preenchimento e pré-análise passaram. A abertura e a edição interativas no Excel não foram testadas.

**Próximas ações:** prosseguir com a análise dos demais registros usando evidências disponíveis e resolver pendências prioritárias; solicitar avaliação independente da amostra cega antes de calcular desempenho ou apresentar confiabilidade. A simplificação da planilha, os gráficos e o relatório metodológico final dependem da conclusão e conferência dessas etapas.
