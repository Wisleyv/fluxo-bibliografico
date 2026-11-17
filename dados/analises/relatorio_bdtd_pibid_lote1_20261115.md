# Leitura de registros BDTD com PIBID no título

**Data:** 15 de novembro de 2026  
**Produto:** [base técnica atualizada](./triagem_bdtd_pibid_lote1_20261115.xlsx).

## Procedimento

Foram selecionadas, na ordem da base, as 20 primeiras linhas BDTD ainda não analisadas com termo do PIBID no título e resumo de pelo menos 500 caracteres. Foram lidos título, resumo e assuntos disponíveis e confrontados título, autoria, link e resumo com a exportação BDTD. A seleção é operacional e não representativa. A presença do termo no título orientou a seleção, mas a classificação foi baseada na leitura temática.

As sínteses, evidências de contexto e limitações individuais estão no [arquivo de avaliações](./avaliacao_bdtd_pibid_lote1_20261115.csv) e na aba **BDTD PIBID lote 1**. Não houve consulta externa nesta etapa.

## Resultado

| Relação identificada com o PIBID | Linhas |
|---|---:|
| Tema central do estudo | 19 |
| Relação substantiva com o programa | 1 |
| **Total** | **20** |

O caso `de544b6f` analisa conjuntamente estágio e PIBID; seus resultados não devem ser atribuídos isoladamente ao programa. Há outra linha com título correspondente, mas a duplicidade não foi confirmada. Em `9970113c`, o resumo descreve procedimentos sem achados específicos suficientes para extração temática.

Em 17 linhas não foi identificada evidência de contexto goiano no material consultado; isso **não comprova ausência** de contexto ou afiliação em Goiás. Em três (`1cd0fc3b`, `193ba189` e `f366cc08`), o contexto permaneceu `Incerto`, pois os estudos analisam trabalhos ou subprojetos de abrangência não suficientemente detalhada. Em todas, a afiliação de autoria continuou incerta.

A triagem e a elegibilidade continuam pendentes: os anos de defesa não foram convertidos em anos de publicação, e a duplicidade permanece não verificada. Não foram geradas extrações de eixos nesta etapa; elas permanecem pendentes para evitar tratar sínteses preliminares como resultados elegíveis da revisão goiana.

## Situação da base

| Triagem de título e resumo | Linhas |
|---|---:|
| Avançar para avaliação | 19 |
| Excluir preliminarmente por período | 112 |
| Excluir preliminarmente pelo critério de termos | 82 |
| Excluir preliminarmente por menção incidental | 3 |
| Pendente | 1.101 |
| **Total** | **1.317** |

Na elegibilidade final, 403 linhas estão pendentes e 914 não iniciadas, destas 874 BDTD e 40 Catálogo CAPES. Não há decisão final. Permanecem 80 linhas em 40 pares de duplicatas confirmadas e 1.237 linhas com duplicidade não verificada. São contagens de linhas, não de obras únicas. A base contém 714 pares registro/eixo, dos quais 633 têm estado preenchido; incluem duplicatas e casos sem elegibilidade definida.

## Verificação e limites

O [script](../../scripts/integrar_bdtd_pibid_lote1_20261115.py) impede sobrescrita e verifica os estados anteriores e a identidade com as exportações. Foram conferidos dados fora do escopo, validações, tabela e filtro dos eixos, fórmulas e integridade ZIP. Passaram **sete testes focados**, incluindo os do lote anterior; não houve teste interativo no Excel.

A leitura e a conferência são **não independentes**, não medem acurácia e não fundamentam percentuais de confiança. A coleta nacional permanece incompleta. Permanecem a análise dos demais registros, a conciliação de datas e duplicidades, as decisões finais e os produtos finais da pesquisa.
