# Revisão bilíngue de avaliações anteriores do Catálogo CAPES

**Data:** 15 de novembro de 2026  
**Produto:** [base técnica revisada](./triagem_revisao_bilingue_catalogo_20261115.xlsx).

## Procedimento e alcance

Foram relidos os resumos em português (`DS_RESUMO`) e inglês (`DS_ABSTRACT`) de 17 registros CAPES que já haviam recebido análise anterior. Os identificadores, títulos, autorias e resumos em português foram confrontados com o arquivo anual original de 2024. Para o registro `401f22b2`, também foram examinados título, palavras-chave e projeto associado. As decisões individuais e seus limites estão no [arquivo de revisão](./revisao_bilingue_catalogo_20261115.csv) e na aba **Revisão bilíngue CAPES**, que preserva os estados anteriores e revisados.

Esta etapa complementa a leitura dos 11 registros descritos no [relatório anterior](./relatorio_catalogo_resumos_20261115.md). Ao todo, 28 dos 78 registros CAPES tiveram seus resumos em inglês lidos nessas duas etapas; **50 ainda não foram lidos dessa forma**. O **Inventário inglês CAPES** foi mantido como registro histórico da etapa anterior. Sua busca literal não substitui leitura semântica nem garante equivalência entre idiomas.

## Decisões revisadas

Três registros passaram de pendentes a **exclusão preliminar**, reversível mediante evidência adicional:

| Código | Motivo da decisão |
|---|---|
| `5dec546a` | O PIBID aparece como possibilidade de estudos futuros; o estudo descrito trata de supervisão de estágio em Química. Menção incidental. |
| `16954ac9` | A experiência da autora no PIBID motiva a pesquisa, mas o objeto descrito é a análise de livros didáticos. Menção incidental. |
| `401f22b2` | Não há termo do programa no título, nos dois resumos ou nas palavras-chave; o projeto mais amplo o menciona entre várias atividades, sem demonstrar relação com a pesquisa descrita. Exclusão preliminar pelo critério de termos. |

Essas decisões resultam de leitura temática, não de uma exclusão automática por palavra. A ausência nos metadados examinados não prova ausência no texto integral, e o projeto associado não comprova, por si só, a relação da pesquisa individual com o programa. A decisão final de elegibilidade continua pendente.

Em `011e7d10`, a relação com o PIBID passou de substantiva para **Incerto**: os participantes pertencem ao programa, mas os resumos não esclarecem se os encontros relatados integraram suas ações. Para evitar atribuições indevidas, os três eixos passaram a `Não verificável`.

Em `bebf73ba`, os três eixos passaram de `Presente` a `Não verificável`, pois os resumos apresentam objetivos e resultados pretendidos, sem achados específicos suficientes. Em `fe0ff0a0`, o primeiro e o terceiro eixos passaram de `Presente` a `Não verificável`; o segundo permaneceu `Não informado`. Ao todo, foram alterados oito estados de eixo: seis de `Presente` e dois de `Não informado` para `Não verificável`. As extrações anteriores permanecem no histórico e acompanhadas das ressalvas.

Foram registradas duas inconsistências sem escolher uma interpretação:

- `223fc435`: os dois resumos informam “vinte e sete (30)” participantes.
- `401f22b2`: o resumo em português diz que a ação foi desenvolvida, enquanto o inglês usa futuro.

Os outros 11 registros mantiveram suas decisões anteriores, com notas de leitura e limitações. Nenhuma duplicidade ou data de publicação foi decidida nesta etapa.

## Situação da base

| Triagem de título e resumo | Linhas |
|---|---:|
| Avançar para avaliação | 19 |
| Excluir preliminarmente por período | 112 |
| Excluir preliminarmente pelo critério de termos | 38 |
| Excluir preliminarmente por menção incidental | 2 |
| Pendente | 1.146 |
| **Total** | **1.317** |

Na elegibilidade final, 328 linhas estão pendentes e 989 não iniciadas; não há decisão final. Permanecem 80 linhas em 40 pares de duplicatas confirmadas e 1.237 linhas com duplicidade não verificada. São contagens de linhas, não de obras únicas. A base contém 687 pares registro/eixo, dos quais 606 têm estado preenchido: 169 `Presente`, 190 `Não informado` e 247 `Não verificável`. Incluem duplicatas e casos sem elegibilidade definida e não constituem resultados finais.

## Verificação e limites

O [script de integração](../../scripts/revisar_bilingue_catalogo_20261115.py) impede sobrescrever a entrada ou uma saída existente, confronta os registros com a fonte e exige estados anteriores compatíveis. Foram comparadas as alterações com a base anterior; verificaram-se preservação dos dados fora do escopo, validações, tabela e filtro dos eixos, fórmulas e integridade ZIP. Passaram **10 testes focados**, incluindo os da etapa anterior; não houve teste interativo no Excel.

A conferência é documental e computacional **não independente**: não mede acurácia nem fundamenta percentuais de confiança. A coleta nacional permanece incompleta, e ano de defesa não equivale automaticamente a publicação. Ainda são necessárias a análise dos demais registros, a revisão dos resumos ingleses restantes, a conciliação de duplicidades e datas, as decisões finais e os produtos finais da pesquisa.
