# Conferência dos resumos do Catálogo CAPES

**Data:** 15 de novembro de 2026  
**Produto:** [base técnica atualizada](./triagem_catalogo_resumos_20261115.xlsx).

## Procedimento

Foram examinados 11 registros do Catálogo CAPES ainda não avaliados e sem sinal literal do PIBID nos campos disponíveis da planilha. Foram lidos seus títulos, resumos em português e inglês, palavras-chave e projetos associados no arquivo anual original de 2024. Os títulos, autorias e identificadores foram confrontados com a base de trabalho. As leituras individuais estão no [arquivo de avaliações](./avaliacao_catalogo_resumos_20261115.csv) e na aba **Resumos Catálogo CAPES**.

Como a normalização anterior incorporou `DS_RESUMO`, mas não `DS_ABSTRACT`, foi criado também o **Inventário inglês CAPES** para os 78 registros dessa fonte na base. O inventário verifica a presença literal da sigla ou da expressão em português no resumo inglês e nos campos locais; não é uma análise semântica completa nem detecta necessariamente traduções ou variantes.

## Resultados do lote

| Tratamento de triagem | Registros |
|---|---:|
| Exclusão preliminar pelo critério de termos | 9 |
| Pendente por menção ao PIBID no resumo em inglês | 1 |
| Pendente por possível vínculo com projeto de temática próxima | 1 |
| **Total** | **11** |

Nos nove registros marcados para exclusão preliminar, os dois resumos e as palavras-chave não identificam o programa como parte do estudo descrito. O campo `NM_PROJETO` contém referência ao PIBID, mas não demonstra por si só relação substantiva com cada pesquisa. A exclusão é **reversível** se outra evidência demonstrar pertinência; não comprova ausência no texto integral. Na planilha, o motivo é `Outro`, detalhado em evidências e limitações.

Os dois casos mantidos pendentes são:

- **11047151:** o resumo em inglês informa que seis dos sete licenciandos em Física participavam ou haviam participado do PIBID, dado que não aparece no resumo em português. A função do programa na análise não está suficientemente clara; não foram atribuídos seus resultados ao PIBID.
- **598f4ee2:** o projeto cadastrado menciona PIBID, drogas na escola e redução de danos; o resumo aborda intervenção sobre drogas na escola. A proximidade temática justifica cautela, mas não confirma que a intervenção tenha ocorrido no PIBID.

Foram acrescentadas seis extrações `Não verificável` para os dois registros pendentes. Não foram geradas extrações de eixos para os nove excluídos preliminarmente. Ano de defesa não foi convertido em ano de publicação; nenhuma duplicata foi decidida nesta etapa.

## Alcance da lacuna

Os 78 registros do Catálogo têm conteúdo em `DS_ABSTRACT` no arquivo original. Em **um**, o 11047151, a sigla ou a expressão em português aparece nesse resumo, mas não nos campos locais da planilha. Outros 67 registros não tiveram seus resumos ingleses lidos nesta etapa, incluindo 17 que já haviam recebido análise anterior: a ausência de novo sinal literal não garante que os detalhes semânticos coincidam entre idiomas. A avaliação deles deve ser complementada antes da consolidação dos resultados.

O projeto associado é um sinal de possível vínculo, não prova de que a pesquisa trate do PIBID. Da mesma forma, a ausência literal nos metadados examinados não prova ausência no texto integral. Os 78 registros são linhas recuperadas do arquivo anual de 2024, não representam a cobertura completa do Catálogo e podem incluir duplicatas.

## Situação da base

| Triagem de título e resumo | Linhas |
|---|---:|
| Avançar para avaliação | 19 |
| Excluir preliminarmente por período | 112 |
| Excluir preliminarmente pelo critério de termos | 37 |
| Pendente | 1.149 |
| **Total** | **1.317** |

Na elegibilidade final, 328 linhas estão pendentes e 989 não iniciadas. Permanecem 80 linhas em 40 pares de duplicatas confirmadas e 1.237 linhas com duplicidade não verificada. São contagens de linhas, não de obras únicas. A base contém 687 pares registro/eixo, dos quais 606 têm estado preenchido; incluem duplicatas e casos sem elegibilidade definida.

## Verificação e limites

O [script](../../scripts/conferir_catalogo_resumos_20261115.py) confere os identificadores e metadados com o arquivo original e impede exclusão quando o termo é identificado em algum dos resumos ou palavras-chave examinados. Células fora do lote, abas e eixos históricos, validações, tabela e filtro, fórmulas e integridade ZIP foram verificados. Passaram **10 testes focados**, incluindo os testes da etapa anterior; não houve teste interativo no Excel.

A conferência é documental e computacional **não independente**, não mede acurácia e não fundamenta percentuais de confiança. A coleta nacional continua incompleta. Permanecem a análise dos demais registros, a revisão dos resumos ingleses, a deduplicação, as datas e as decisões finais.
