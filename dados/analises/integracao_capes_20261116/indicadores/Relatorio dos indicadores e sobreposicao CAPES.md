# Etapa 5 da integração CAPES — cobertura, indicadores e respostas

**Estado: etapa executada.** Os cálculos usam os corpora da etapa de elegibilidade, sem nova coleta ou decisão de inclusão. Foram atualizadas as tabelas e a [síntese das seis subquestões](Sintese%20das%20seis%20subquestoes.md). Não foi gerada nova entrega Excel nem substituído o relatório metodológico do Marco 5; esses produtos pertencem à etapa seguinte.

## Resultados nacionais e comparação com Goiás

| Medida | Versão anterior | Versão incremental | Estado |
|---|---:|---:|---|
| Obras nacionais incluídas | 7.780 | **7.779** | Consolidado no corpus operacional; universo completo não demonstrado |
| Obras regionais incluídas | 97 | **97** | Consolidado no corpus observado |
| Fração de afiliação goiana identificada, publicação 2007–08/11/2026 | 196/7.780 | **196/7.779 = 2,52%** | Parcial: fração observada, não participação total |
| Fração identificada, publicação 2020–08/11/2026 | 67/3.459 | **67/3.459 = 1,94%** | Parcial: mesmo corpus/período em numerador e denominador |
| Participação total Goiás–Brasil | Não estimável | **Não estimável** | Recuperação, afiliação e decisões incompletas |

A fusão de “Quero ser professora”, sustentada na fase bibliográfica, elimina uma inclusão duplicada de 2016. Não houve novas obras confirmadas na etapa de elegibilidade. Consequentemente, a série de 2016 passa de 575 para 574; artigos passam de 5.968 para 5.967. O total de obras com autoria informada passa de 7.753 para 7.752, e a categoria de uma autoria observada passa de 1.555 para 1.554. O componente duplicado de origem SciELO não deve continuar gerando um crédito separado. Isso não constitui nova investigação de autoria.

O numerador goiano não mudou: 196 obras no período nacional e 67 no período comum. O arredondamento a duas casas decimais mantém 2,52% no primeiro caso, mas o denominador efetivo mudou e deve aparecer como 7.779. A primeira proporção exata é 2,5196040622%; a anterior era 2,5192802057%. Não apresentar a igualdade dos percentuais arredondados como ausência de alteração do corpus. Ver [frações nacionais](Participacao%20e%20contexto%20Goias.csv), [período comum](Participacao%20periodo%20comum.csv) e [antes/depois](Comparacao%20antes%20depois.csv).

O cruzamento regional mantém 78 das 97 obras incluídas também presentes no corpus nacional. As outras 19 não foram promovidas ao nacional pela nova proveniência. Não calcular 97/7.779. A contagem de contexto permanece separada: 56 contextos locais/institucionais documentados, dois objetos goianos sem local escolar confirmado, 32 não verificáveis, seis nacionais/múltiplos e um explicitamente fora de Goiás. A afiliação goiana identificada na revisão continua em 80/97. Ver [correspondência](Correspondencia%20Goias%20Brasil.csv) e [contextos](Contexto%20Goias%20separado.csv).

## Sobreposição: três níveis com unidades diferentes

| Nível | Resultado | O que mede |
|---|---:|---|
| IDs CAPES presentes no snapshot OpenAlex | **647/675 = 95,85%** | Coincidência nominal de identificadores; não valida todas as identidades |
| Recuperações CAPES ligadas a componentes conciliados | **665/675** | Vínculos bibliográficos com o acervo, incluindo obras ainda pendentes |
| Mesma obra confirmada em relação ao snapshot OpenAlex | **664 registros** | Um dos 665 vínculos é com controle sem OpenAlex na consulta arquivada |
| Casos de cobertura em revisão | **3 registros** | Divergências de autoria; excluídos do denominador verificável |
| Não recuperados na consulta arquivada | **7 registros** | Seis sem candidato confirmado e um controle sem OpenAlex; não inexistência no índice completo |
| Não verificável para o corte | **1 registro** | Ano 2026 sem data completa para demonstrar publicação até 08/11 |

As quatro categorias reconciliam: **664 + 3 + 7 + 1 = 675**. O denominador verificável é **675 − 3 − 1 = 671**; a fração confirmada é **664/671 = 98,96%**. Sobre todos os registros, são **664/675 = 98,37%**. Os denominadores excluídos estão explícitos, sem apagar registros ou tratá-los como negativos.

O caso de 2026 não verificável não foi simplesmente classificado como ausente: a consulta CAPES cobre o ano inteiro, enquanto o snapshot OpenAlex foi limitado por publicação até 08/11. Os demais anos e as datas arquivadas permitem a comparação operacional descrita. A matriz não mede cobertura de todos os índices nem compara buscas com escopo perfeitamente equivalente.

Fontes: [matriz por período, ano e tipo](Matriz%20de%20cobertura%20CAPES.csv), [classificação individual](Cobertura%20CAPES%20por%20registro.csv) e [níveis de sobreposição](Niveis%20de%20sobreposicao%20CAPES%20OpenAlex.csv). Os anos nessa matriz são os do RIS; não substituem os anos canônicos da evolução bibliométrica. Os 17 grupos de títulos repetidos e os aliases bibliográficos explicam por que registros e obras não são intercambiáveis.

## Sobreposição por obras elegíveis e por fonte

O novo lote recuperou **509 obras já incluídas**. Dessas, 21 tinham recuperação Portal CAPES anterior. A união das rodadas é **83 + 509 − 21 = 571 obras elegíveis com proveniência Portal CAPES**. Assim, 488 obras passaram a ter essa proveniência adicional. Não são 488 novas inclusões nacionais.

Nas 7.779 obras nacionais, a partição OpenAlex–Portal CAPES é:

| Recuperação observada | Obras |
|---|---:|
| Ambas as fontes | 571 |
| Somente OpenAlex entre essas duas fontes | 7.206 |
| Somente Portal CAPES entre essas duas fontes | 0 |
| Outras fontes, sem recuperação nas duas | 2 |
| Total | 7.779 |

“Somente OpenAlex entre essas duas fontes” não significa exclusividade em relação a BDTD, Catálogo ou SciELO. As [combinações exclusivas de todas as fontes](Combinacoes%20exclusivas%20de%20fontes.csv) mostram a partição completa, enquanto [interseções entre fontes](Sobreposicao%20fontes%20corpus%20elegivel.csv) podem se sobrepor e não devem ser somadas. Há estratos de período e tipo no arquivo [OpenAlex–CAPES](OpenAlex%20CAPES%20por%20periodo%20e%20tipo.csv).

Esses resultados mostram recuperação em comum neste corpus, não equivalência entre o Portal e o OpenAlex, nem dispensam fontes complementares. O conjunto CAPES mantém os filtros de Artigo/Editorial e produção nacional da interface, e a concatenação de 23 páginas é declarada, sem comprovação individual de paginação. A matriz histórica dos 1.317 controles do Marco 1 foi preservada; não foi reescrita com a nova consulta.

## Cobertura de campos e demais indicadores

A cobertura de afiliação nacional é **3.024 conhecidas, 1.485 parciais e 3.270 desconhecidas**, somando 7.779. “Conhecida” significa todas as autorias pessoais observadas com instituição mapeada; não certifica a completude real da lista ou a solução de divergências de autoria entre fontes. Os dois alertas CAPES em obras incluídas foram acrescentados, mantendo os créditos do material arquivado e os 22 rótulos institucionais já sinalizados.

As instituições e os países permanecem mapeados em 4.228 obras; o percentual no corpus passa a **54,35%**. Os tópicos principais OpenAlex continuam disponíveis em 7.777 obras, agora **99,97%**. Disponibilidade não valida a classificação temática. As palavras-chave e os tópicos continuam identificados como algorítmicos; nenhuma categoria foi inventada a partir do RIS sem resumo ou palavras-chave. Autoria, instituições, países, coautoria e créditos fracionários foram recalculados com as mesmas regras, sem separar pessoas por vírgulas do AU.

As duas divergências anuais canônicas anteriores continuam em categoria própria, com limites por ano não aditivos. O metadado CAPES 2019 de “Práticas de leitura” não substituiu a publicação sustentada de 2013; a divergência literal permanece na proveniência. O ano 2026 é incompleto. A distribuição integral por UF/região, grupos e redes consolidadas continua não estimável. Ver [cobertura](Cobertura%20de%20campos.csv), [estado dos indicadores](Estado%20dos%20indicadores.csv) e [divergências anuais](Divergencias%20de%20ano.csv).

## Respostas canônicas e limites regionais

As respostas 1 e 2 foram atualizadas nos totais nacionais, cobertura e participação observada, com descrição explícita da contribuição CAPES. As frequências e evidências regionais que sustentam as respostas 3 a 6 foram preservadas: 97 obras, 291 pares obra/eixo, aprendizagem/identidade 66/24/7, trajetórias 6/87/4 e relações 51/34/12, respectivamente Presente/Não informado/Não verificável. A redação qualitativa foi reaproveitada com suas referências, sem apresentar objetivos como resultados ou informação ausente como ausência do fenômeno.

As 871 pendências regionais continuam separadas das dez ocorrências CAPES provisórias. Na fila regional adicional dessas ocorrências, quatro estão fora do período por publicação e seis permanecem pendentes, sem vínculo goiano comprovado. As quatro inclusões por defesa e a dúvida artigo/capítulo continuam limitando comparações e interpretações; nenhuma foi resolvida pela simples inclusão de proveniência CAPES.

## Verificação e reprodução

Passaram **25 verificações internas dos indicadores** e **13 da integração**, incluindo totais, pesos fracionários, identidade do corpus, nove frequências de estados dos eixos, correspondência regional, numeradores/denominadores, quatro categorias CAPES, união de rodadas, estratos e partição das fontes. Os produtos históricos do Marco 4 foram conferidos contra os hashes de seu inventário e permaneceram idênticos; os insumos da rodada também foram reconferidos. Ver [verificações gerais](Verificacoes%20internas.csv), [da integração](Verificacoes%20da%20integracao.csv) e [auditoria](Auditoria%20da%20integracao.json).

A parametrização dos três scripts de indicadores foi limitada a caminhos por manifesto, denominadores calculados dos corpora e material qualitativo arquivado. Os padrões antigos foram mantidos. Os resultados desta rodada ficam em diretório próprio; não foram substituídos os arquivos de `dados/analises/marco4/` ou `dados/entregas/marco5/`.

Passaram **48 testes relevantes**: dez novos sobre a classificação de cobertura, denominadores verificáveis, estratos e proteção dos caminhos históricos; sete da etapa de elegibilidade; e 31 anteriores dos marcos. Uma execução isolada, sem `--atualizar`, em saída nova, reproduziu **38 tabelas CSV byte a byte idênticas**. O inventário não foi comparado byte a byte porque contém caminhos da saída temporária. O teste não envolve a futura entrega Excel e está em [Teste de reproducao por manifesto.json](Teste%20de%20reproducao%20por%20manifesto.json).

Reprodução a partir da raiz, sem rede:

```text
python -m scripts.recalcular_cobertura_capes_20261116 --recalcular --atualizar
```

Sem `--recalcular`, o comando confere e produz a cobertura, a comparação e a síntese usando os indicadores já calculados. `--atualizar` substitui somente os produtos da nova rodada. Esta conferência é interna e não fornece acurácia ou validação científica independente.

O [manifesto de saída](Manifesto%20de%20saida.json) registra os caminhos e hashes do código desta etapa. O inventário dos indicadores inclui os produtos quantitativos, a documentação e as verificações, mantendo o manifesto de entrada da etapa anterior preservado.

## Próxima etapa

Os indicadores e a síntese estão prontos para regerar a planilha e os gráficos numa entrega paralela, atualizar a base técnica e a matriz, substituir o relatório metodológico pela versão que explicita a recuperação CAPES e sua sobreposição, e montar/conferir o novo pacote reproduzível. O [subsídio metodológico](Subsidios%20para%20o%20relatorio%20metodologico%20substituto.md) registra os pontos que devem acompanhar essa redação. Nenhuma dessas tarefas de entrega final é declarada concluída nesta etapa.
