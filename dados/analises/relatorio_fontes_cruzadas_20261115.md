# Comparação de candidatos entre BDTD, Catálogo CAPES e SciELO

**Data:** 15 de novembro de 2026  
**Base produzida:** [triagem com comparação entre fontes](./triagem_fontes_cruzadas_20261115.xlsx).

## Procedimento e resultados

Foram retomados os grupos de títulos normalizados exatos já registrados na aba **Possíveis duplicatas**, sem nova coleta. Há 35 grupos entre BDTD e Catálogo CAPES e dois entre BDTD e SciELO. Um dos grupos BDTD/CAPES tem três linhas, duas delas BDTD; por isso, os 37 grupos originam 38 comparações BDTD–outra fonte, e não 38 obras nem 38 duplicatas. A aba **Comparação entre fontes** registra os códigos, tipos, anos, comparação de autoria, instituição, resumos e endereços.

Nos 36 confrontos BDTD/CAPES, a autoria concorda após normalização em 32; quatro apresentam diferenças de nome ou informações adicionais no campo de autoria, que não demonstram por si só pessoas diferentes. Em dois confrontos, o tipo informado diverge: dissertação versus tese em `DUP-0044`; dissertação versus produto, processo ou técnica em `DUP-0081`. Oito confrontos têm resumos preservados de pelo menos 500 caracteres iguais após normalização de caixa, acentos e espaços. Os demais não apresentaram igualdade integral sob essa regra ou não eram comparáveis por ela; isso não prova que sejam obras distintas.

Os endereços de texto completo preservados nos registros CAPES examinados apontam para as respectivas páginas Sucupira. Não se identificou endereço comum com as linhas BDTD nesses confrontos; a comparação não esgota todos os identificadores possíveis. Apesar das correspondências bibliográficas, **nenhuma nova duplicata foi confirmada**, nenhum registro principal foi escolhido e nenhuma linha foi removida. Os dois grupos BDTD/SciELO combinam tese ou dissertação com artigo: o mesmo título e eventual relação entre pesquisas não justificam fundir essas produções.

O grupo Portal CAPES/SciELO identificado por DOI e por título já integra a conciliação anterior e não foi recontado aqui. A comparação por título exato limita-se aos candidatos existentes e não demonstra ausência de outras duplicatas.

## Reaproveitamento de avaliações

Três registros BDTD ainda não iniciados foram associados a avaliações CAPES já existentes:

| BDTD | Catálogo CAPES | Aproveitamento preliminar |
|---|---|---|
| `d0accc2b` | `8e68ac12` | Tema central; formação inclusiva e proposta de jogo digital de Geografia. |
| `417d0d90` | `fa78dc43` | Tema central; percepção de egressos do PIBID de História da UECE. |
| `8f150364` | `969dc972` | Tema central; formação docente e relações universidade–escola no PIBID/UEAP. |

Em cada par, conferiram-se título, autoria, tipo de produção, ano de defesa e instituição compatíveis, além de igualdade do resumo completo em português após normalização. Nos dois casos UNESP, o nome abreviado na BDTD é compatível com o nome institucional expandido no Catálogo. A avaliação foi reaproveitada como análise do material, **não** como confirmação de identidade por identificador comum. Os três registros receberam a classificação de tema central e ausência de evidência de contexto goiano no material consultado, além dos três estados de eixo já registrados no Catálogo. As evidências e os limites das extrações apontam para a avaliação de origem.

Esses estados são preliminares, não representam validação independente nem exclusão definitiva. Não identificar Goiás no material não demonstra ausência de contexto ou afiliação; a instituição da tese não comprova afiliação. Ano de defesa não foi convertido em ano de publicação. Os casos com resumo não preservado não geram pendência ou busca individual por esse motivo, conforme a regra vigente. Outras questões, como data, afiliação e duplicidade, permanecem separadas.

## Situação da base e verificações

A base contém **1.317 linhas**: 19 avançam à avaliação, 199 têm exclusão preliminar e 1.099 estão pendentes na triagem. Na elegibilidade final, 464 estão pendentes e 853 não iniciadas; não há decisão final. Permanecem 80 linhas em 40 pares de duplicatas confirmadas e 1.237 linhas com duplicidade não verificada. São contagens de linhas, não de obras únicas.

Há 831 pares registro/eixo, dos quais 750 com estado preenchido. Incluem duplicatas e casos sem elegibilidade definida e não constituem resultados finais. A qualidade documental permanece reduzida para 273 linhas e não avaliada nessa dimensão para 1.044.

O [integrador](../../scripts/conciliar_fontes_catalogo_bdtd_20261115.py) preserva a base de entrada, recusa sobrescrita e interrompe a execução se os candidatos, metadados, material ou estados esperados divergirem. Passaram três [testes](../../tests/test_conciliar_fontes_catalogo_bdtd_20261115.py) de reaproveitamento, preservação, estrutura e recusa de conflitos. As células das abas da cópia persistida coincidiram com as da reprodução de teste; foram verificadas tabelas, filtros, validações, fórmulas e integridade ZIP. Não houve teste interativo no Excel.

Persistem análise dos demais registros, conciliação de datas e duplicidades, decisões finais, planilha simplificada, gráficos e relatório metodológico. Os percentuais de confiança não foram estimados, pois não há referência independente para validá-los; a coleta nacional continua incompleta.
