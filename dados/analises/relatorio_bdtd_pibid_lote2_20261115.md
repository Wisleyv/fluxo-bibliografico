# Leitura de registros BDTD recentes com PIBID no título

**Data:** 15 de novembro de 2026  
**Produto:** [base técnica atualizada](./triagem_bdtd_pibid_lote2_20261115.xlsx).

## Procedimento

Das 874 linhas BDTD ainda não iniciadas na elegibilidade, 221 tinham ano de defesa a partir de 2020, resumo local com pelo menos 500 caracteres e termo literal do PIBID nos campos locais. Foram selecionadas as primeiras 20 na ordem da base; todas também apresentavam o termo no título. O ano de defesa foi usado para priorização, **não como ano de publicação**. A seleção é operacional e não representativa.

Foram lidos título, resumo e assuntos disponíveis. Título, autoria, link e resumo foram confrontados com as exportações BDTD; em `7324cc85`, o separador de autoria havia sido normalizado na base e foi conciliado. Não houve consulta externa nesta etapa. Não apareceram candidatos na comparação de títulos normalizados exatos ou com similaridade de pelo menos 0,90, links e DOIs; isso não comprova ausência de duplicatas.

As evidências e os limites de cada registro constam no [arquivo de avaliações](./avaliacao_bdtd_pibid_lote2_20261115.csv) e na aba **BDTD PIBID recentes**.

## Resultado

| Relação identificada com o PIBID | Linhas |
|---|---:|
| Tema central do estudo | 18 |
| Relação substantiva com o programa | 1 |
| Incerta | 1 |
| **Total** | **20** |

O caso `01d34bae` examina os saberes de um ex-bolsista e discute sua iniciação no programa, sem isolar a origem de seus saberes. Em `fbe0a70f`, a pesquisa envolve bolsistas e uma intervenção com gamificação, mas o resumo não esclarece se a intervenção integrou ações do PIBID; seus resultados não devem ser atribuídos ao programa sem esclarecimento.

Em 15 linhas não foi identificada evidência de contexto goiano no material consultado; isso **não comprova ausência** de contexto ou afiliação em Goiás. Em cinco (`28de0b69`, `b66fff4f`, `fbe0a70f`, `9da923d6` e `42007bfd`) o contexto permanece incerto: os recortes são nacionais, institucionais ou não suficientemente localizados. A afiliação de autoria continua incerta nas 20 linhas.

O resumo de `cf7c0ce8` termina abruptamente e não há palavras-chave locais; os limites permanecem registrados. A defesa em 2026 de `44752b85` não confirma publicação até o corte de **08/11/2026**. Todas as decisões de elegibilidade continuam pendentes, assim como a conciliação de data de publicação e duplicidade. Os eixos não foram extraídos neste lote: adiamento não significa ausência de achado.

## Situação da base

| Triagem de título e resumo | Linhas |
|---|---:|
| Avançar para avaliação | 19 |
| Excluir preliminarmente por período | 112 |
| Excluir preliminarmente pelo critério de termos | 82 |
| Excluir preliminarmente por menção incidental | 3 |
| Pendente | 1.101 |
| **Total** | **1.317** |

Na elegibilidade final, 423 linhas estão pendentes e 894 não iniciadas, destas 854 BDTD e 40 Catálogo CAPES. Não há decisão final. Permanecem 80 linhas em 40 pares de duplicatas confirmadas e 1.237 linhas com duplicidade não verificada. São contagens de linhas, não de obras únicas. A base contém 714 pares registro/eixo, dos quais 633 têm estado preenchido; incluem duplicatas e casos sem elegibilidade definida.

## Verificação e limites

O [integrador](../../scripts/integrar_bdtd_pibid_lote2_20261115.py) reutiliza o processamento do lote anterior, impede sobrescrita e verifica os estados anteriores e a correspondência com as exportações. Foram conferidos dados fora do escopo, validações, tabela e filtro dos eixos e da auditoria, fórmulas e integridade ZIP. Passaram seis testes focados dos dois lotes; não houve teste interativo no Excel.

A leitura e a conferência são **não independentes**, não medem acurácia e não fundamentam percentuais de confiança. A coleta nacional permanece incompleta. Permanecem a análise dos demais registros, a leitura dos 40 resumos ingleses CAPES ainda não contemplados nas etapas bilíngues, a conciliação de datas e duplicidades, as decisões finais e os produtos finais da pesquisa.
