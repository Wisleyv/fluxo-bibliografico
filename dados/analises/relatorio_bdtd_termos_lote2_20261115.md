# Segundo lote BDTD sem termo literal

**Data:** 15 de novembro de 2026  
**Produto:** [base técnica atualizada](./triagem_bdtd_termos_lote2_20261115.xlsx).

## Procedimento

Foram conferidas 24 linhas com resumo substantivo sem a sigla ou a expressão portuguesa do PIBID nos metadados locais. Destas, 21 ainda não haviam sido analisadas; três tinham leitura anterior: duas pertencem a pares confirmados e uma aguardava conferência da UFS. Foram lidos título, resumo e assuntos disponíveis, comparados com as exportações BDTD nacional e regional. A ausência literal foi combinada com leitura temática, não usada como decisão automática.

Para evitar trabalho repetido, aproveitou-se a leitura de resumos e palavras-chave iguais, após confronto dos conteúdos. A mesma decisão foi aplicada às duas linhas de cada par já confirmado: `361dd6b1`/`f1d6e487` e `5f5259e7`/`3ee25c3e`. Outras linhas têm conteúdo igual ou títulos correspondentes, inclusive uma tese com resumos em português e inglês; seus vínculos de duplicidade **não foram confirmados**. Não foram escolhidos registros principais.

As justificativas constam do [arquivo de avaliações](./avaliacao_bdtd_termos_lote2_20261115.csv) e da aba **BDTD termos lote 2**. A busca original BDTD foi executada em todos os campos; o critério de termos é uma triagem posterior dos metadados visíveis disponíveis.

## Resultado

| Tratamento de triagem | Linhas |
|---|---:|
| Exclusão preliminar pelo critério de termos e leitura temática | 22 |
| Pendente com vínculo ao PIBID confirmado na UFS | 1 |
| Pendente por possível tradução inglesa | 1 |
| **Total** | **24** |

As 22 exclusões são **preliminares e reversíveis** se surgirem evidências adicionais; não demonstram ausência no texto integral. Na planilha, o motivo é `Outro`, detalhado nas evidências. As linhas não devem compor contagens temáticas sem reavaliar o critério e a evidência; a elegibilidade final continua pendente.

- **`9d2082d5`:** a [consulta à UFS](https://ri.ufs.br/jspui/handle/riufs/14672), concluída em 15/11/2026 após o erro de acesso anterior, confirma no resumo português a participação de bolsistas do PIBID e da residência pedagógica em oficina de ações integradas. A relação passou de `Incerto` para substantiva, mas a triagem permanece pendente. Os achados não foram atribuídos a um programa isoladamente. A página informa emissão e referência em 2021; não se estabeleceu nesta etapa publicação distinta da defesa. A consulta está registrada no [arquivo de fonte](./consulta_ufs_bdtd_lote2_20261115.json).
- **`52ecb111`:** o resumo inglês menciona programa de iniciação à docência e residência pedagógica, sem sigla que permita identificação segura. A consulta à UFS retornou erro 503; a relação permanece `Incerto` e a triagem pendente.

Não foram geradas extrações de eixos nem alteradas datas ou classificações de duplicidade. Os dois pares já confirmados continuam identificados como tais, e os demais candidatos não foram transformados em obras únicas.

## Situação da base

| Triagem de título e resumo | Linhas |
|---|---:|
| Avançar para avaliação | 19 |
| Excluir preliminarmente por período | 112 |
| Excluir preliminarmente pelo critério de termos | 82 |
| Excluir preliminarmente por menção incidental | 3 |
| Pendente | 1.101 |
| **Total** | **1.317** |

Na elegibilidade final, 383 linhas estão pendentes e 934 não iniciadas; não há decisão final. Permanecem 80 linhas em 40 pares de duplicatas confirmadas e 1.237 linhas com duplicidade não verificada. São contagens de linhas, não de obras únicas. Os 40 resumos ingleses CAPES remanescentes continuam por ler.

Entre os registros BDTD ainda não analisados, 52 não apresentam o termo literal nos campos locais: 51 têm resumo com menos de 500 caracteres e um tem resumo mais longo. O tamanho, sozinho, não determina se há resumo substantivo. Em particular, resumos ausentes, bibliográficos ou incompletos não autorizam exclusão sumária; também é necessário considerar possíveis traduções.

## Verificação e limites

O [script](../../scripts/integrar_bdtd_termos_lote2_20261115.py) verifica identidade e estados anteriores, confere os pares já confirmados e exige igualdade de conteúdo antes de reaproveitar leituras. Também impede exclusão quando identifica uma formulação inglesa sinalizadora; essa salvaguarda não esgota as traduções possíveis. Foram verificados dados fora do escopo, validações, tabela e filtro dos eixos, fórmulas e integridade ZIP. Passaram **oito testes focados**, incluindo os do lote anterior; não houve teste interativo no Excel.

A conferência é **não independente** e não mede acurácia nem fundamenta percentuais de confiança. A coleta nacional permanece incompleta.
