# Lote de teses e conferência de datas da UEL

**Data:** 15 de novembro de 2026  
**Produto:** [base técnica atualizada](./triagem_teses_datas_uel_20261115.xlsx).

## Leitura dos registros

Foram analisadas **35 linhas** de teses e dissertações pendentes, usando os resumos e metadados locais:

- sete linhas com indícios regionais identificados em título, resumo, palavras-chave ou instituição, incluindo dois pares de duplicatas já confirmadas;
- 20 linhas BDTD cujo título mencionava PIBID e cuja data de defesa originalmente informada era 2024, sem exigir sinal regional;
- oito linhas de quatro pares BDTD–Catálogo CAPES com títulos, autorias, tipos, anos de defesa informados, instituições e resumos compatíveis. Para esses pares, os resumos coincidiam após normalização de caixa e espaços.

O ano originalmente informado serviu apenas para priorização, não como prova de publicação ou elegibilidade. A conferência posterior mostrou que parte dos anos de defesa era incorreta. Sinais regionais também foram usados apenas para priorizar, não para excluir os demais registros. As leituras, evidências e limites estão no [arquivo de avaliações](./avaliacao_teses_lote_20261115.csv) e na aba **Lote teses recente**.

| Relação com PIBID no lote | Linhas |
|---|---:|
| Tema central | 21 |
| Relação substantiva | 4 |
| Menção incidental | 3 |
| Incerto | 7 |
| **Total** | **35** |

Sete linhas apresentam contexto de pesquisa goiano, 16 não apresentam evidência de contexto goiano no material consultado e 12 permanecem com contexto incerto. Essas contagens incluem duplicatas e não equivalem a estudos únicos. Em particular, o vínculo de participantes ao PIBID, sem esclarecimento da função do programa na pesquisa, não foi tratado automaticamente como efeito do programa.

As 35 linhas continuam com triagem e elegibilidade final pendentes. Foram acrescentados **105 pares registro/eixo**: 32 `Presente`, 37 `Não informado` no material consultado e 36 `Não verificável`. A extração é preliminar; resultados de aprendizagem de estudantes escolares não foram convertidos em aprendizagem docente.

Os dois pares do mesmo repositório já estavam confirmados. Os quatro pares entre fontes permanecem **candidatos**, pois não foi estabelecido identificador compartilhado suficiente para confirmação. Nenhuma linha foi removida e não foi escolhido registro principal. Artigos e teses relacionados, inclusive os de título semelhante, não foram automaticamente tratados como duplicatas.

## Divergência de datas no repositório UEL

Durante a leitura, foram identificados resumos de registros UEL com números aparentemente truncados e anos de defesa de 2024 que exigiam conferência. Após autorização de consulta, foram examinados os metadados públicos do repositório para os **31 registros BDTD** da base que tinham endereço UEL e ano de defesa originalmente informado como 2024. Os títulos, autorias e identificadores foram confrontados antes da integração; as consultas estão em [metadados UEL](./datas_uel_20261115.json) e as alterações na aba **Datas UEL conferidas**.

| Resultado da conferência | Registros |
|---|---:|
| Data de defesa explícita na UEL entre 2012 e 2020; ano de defesa corrigido na cópia de trabalho | 30 |
| Defesa não informada na UEL; data de emissão de 28/03/2024 identificada | 1 |
| **Total** | **31** |

Nos 30 registros corrigidos, 2024 coincide com o ano de incorporação informado pelo repositório; essa coincidência sugere um possível problema de origem ou mapeamento, mas não estabelece seu mecanismo. A data de incorporação **não foi usada como data de defesa ou publicação**. A base original e os valores anteriores foram preservados.

No registro **fe0699e5**, o campo `dc.date.issued` da UEL informa 28/03/2024. O ano de publicação foi registrado como 2024; a defesa de 2024 informada na BDTD foi mantida com ressalva de que não foi confirmada nos metadados UEL. Para os outros 30, não havia `dc.date.issued` nos metadados consultados: seus anos de defesa corrigidos não foram convertidos em anos de publicação, nem usados isoladamente para excluir obras do recorte.

A verificação não abrangeu todos os repositórios nem todos os demais anos. Também não se pode generalizar que outros registros com ano de defesa 2024 estejam incorretos. O total de 446 registros com defesa originalmente informada entre 2020 e 2026, mencionado no levantamento anterior, deve ser lido com essa ressalva; após estas correções, o total informado na base passou a **418**, ainda sem validação integral das datas restantes.

## Situação da base

| Triagem de título e resumo | Linhas |
|---|---:|
| Avançar para avaliação | 19 |
| Excluir do recorte goiano por ano de publicação | 110 |
| Pendente | 1.188 |
| **Total** | **1.317** |

Na elegibilidade final, 279 linhas permanecem pendentes e 1.038 não iniciadas. Permanecem 80 linhas em 40 pares de duplicatas confirmadas e 1.237 linhas com duplicidade não verificada. Os 567 pares registro/eixo incluem duplicatas e registros sem elegibilidade definida; 486 têm estado preenchido. Essas contagens não são resultados finais nem contagens de obras únicas.

## Verificação e limites

O [script de integração](../../scripts/integrar_teses_e_datas_uel_20261115.py) impede reaproveitamento da análise entre pares com metadados ou resumo divergentes, registra as datas anteriores e recusa converter incorporação em defesa. As células fora do escopo, abas históricas, eixos anteriores, validações, tabela e filtro, fórmulas e integridade ZIP foram conferidos. Passaram **23 testes focados**; não houve teste interativo no Excel.

A leitura e a conferência computacional **não são independentes** e não medem acurácia. Não foram atribuídos percentuais de confiança. A coleta nacional permanece incompleta; a análise semântica restante, a deduplicação, as decisões finais, os gráficos e o relatório metodológico final ainda dependem de conclusão.
