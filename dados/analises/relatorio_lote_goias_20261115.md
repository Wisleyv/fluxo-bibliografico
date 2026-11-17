# Análise direcionada de registros com indícios de Goiás

**Data:** 15 de novembro de 2026  
**Produto:** [base de trabalho atualizada](./triagem_lote_goias_20261115.xlsx).

## Seleção e materiais

Foram priorizadas linhas que apresentavam indícios textuais de Goiás ou de instituições associadas ao estado, permaneciam com relação com o PIBID `Incerto` na base e não pertenciam ao piloto de 36 registros. O sinal foi usado para **priorização**, não como prova de contexto geográfico ou elegibilidade. Também foram examinadas abreviações e localidades presentes em título, resumo e palavras-chave de registros recentes ainda incertos. Esse levantamento não esgota nomes, municípios ou formas possíveis de referência ao estado.

Neste lote, foram analisadas **36 linhas**:

- 24 linhas de 12 pares BDTD com título, autoria, tipo, ano de defesa, instituição, resumo, palavras-chave e endereço de repositório coincidentes;
- uma linha correspondente a um registro da amostra já autoavaliado, com metadados e resumo locais idênticos ao par;
- 11 artigos cujos títulos indicam possível relação com o recorte regional, sem resumo disponível na planilha, com anos de publicação de 2015 a 2018.

As leituras utilizaram título, resumo e metadados locais quando disponíveis. Nos 12 pares de mesmo resumo, a síntese da leitura foi aplicada às duas linhas após a conferência da identidade bibliográfica e do conteúdo local. Não houve novas consultas externas nem leitura integral. As decisões e justificativas estão na aba **Lote prioritário GO** e no [registro do lote](./avaliacao_lote_goias_20261115.csv).

## Decisões provisórias do lote

| Triagem de título e resumo | Linhas |
|---|---:|
| Pendente | 25 |
| Excluir do recorte Goiás 2020–2026 por ano de publicação | 11 |
| **Total** | **36** |

Nas 25 linhas de teses e dissertações havia apenas ano de defesa. Mesmo quando anterior a 2020, ele **não foi convertido em ano de publicação nem usado como motivo de exclusão**. Os 11 artigos foram excluídos apenas do recorte goiano porque os respectivos metadados informam publicação anterior a 2020; podem ser pertinentes ao panorama nacional. As decisões de elegibilidade final continuam pendentes.

Quanto à relação com PIBID, 16 linhas foram classificadas como tema central, 13 como relação substantiva, duas como menção incidental e cinco como incertas. Quanto ao contexto, 23 linhas indicam contexto goiano e 13 permanecem incertas. Essas contagens incluem registros duplicados e **não representam estudos únicos**.

O contexto goiano foi identificado quando o material descreve a pesquisa em Goiás ou um objeto institucional goiano suficientemente localizado. Não se presumiu que o local de cada escola ou a afiliação de autoria seja conhecido a partir do nome da instituição. Nos estudos em que o PIBID aparece apenas como vínculo de participantes e sua função analítica não está clara, manteve-se a relação `Incerto`.

Foram adicionados **108 pares registro/eixo** referentes às 36 linhas. A extração foi limitada ao material disponível; nos artigos sem resumo e nos casos em que os efeitos específicos do PIBID não são verificáveis, os eixos foram marcados como `Não verificável`. As extrações incluem duplicatas e registros sem elegibilidade definida: não são contagens de resultados da revisão.

## Duplicidade e situação da base

Os 12 pares BDTD com o mesmo identificador de repositório e metadados bibliográficos coincidentes foram marcados como duplicatas confirmadas. A linha restante com par BDTD já pertencia a um par anteriormente confirmado. Nenhuma linha foi removida e não foi escolhido registro principal.

A base contém agora 34 linhas marcadas como duplicatas confirmadas, correspondentes aos **17 pares até aqui identificados**. Outras seis linhas continuam com duplicidade provável e os demais candidatos ainda precisam de conferência; isso não encerra a deduplicação da base.

| Triagem na base inteira | Linhas |
|---|---:|
| Avançar para avaliação | 18 |
| Excluir do recorte goiano por ano de publicação | 25 |
| Pendente | 1.274 |
| **Total** | **1.317** |

Esses números são de linhas, não de obras únicas. Na elegibilidade final, 135 linhas permanecem pendentes e 1.182 não iniciadas. A coleta nacional continua incompleta e não permite inferência sobre toda a produção brasileira.

## Verificação e limites

O [script](../../scripts/integrar_lote_goias_20261115.py) recusa aplicar uma síntese a um par sem coincidência dos metadados e do material local; também impede exclusão por simples ano de defesa e não sobrescreve o arquivo de entrada. Foram comparadas as versões: somente as 36 linhas previstas foram alteradas na triagem; as outras 1.281, os 1.317 alertas de qualidade e as abas históricas foram preservados. Os eixos anteriores, as listas de validação, a extensão da tabela e do filtro, a integridade ZIP e a ausência de fórmulas inesperadas foram conferidos. Passaram 20 testes focados. Não houve teste interativo no Excel.

A análise é preliminar e **não independente**. Sinais ausentes não comprovam que outros registros não tenham contexto goiano. A inconsistência título–resumo de **46baf45a**, datas incertas e os demais candidatos a duplicidade permanecem para revisão. Não foram atribuídos percentuais de confiança.

**Próximo passo:** continuar a leitura dos registros ainda não analisados semanticamente, inclusive os sem sinal regional explícito, e esclarecer duplicidades e datas quando o material disponível permitir. A seleção final, os gráficos e o relatório metodológico final ainda dependem da conclusão e conferência dessas etapas.
