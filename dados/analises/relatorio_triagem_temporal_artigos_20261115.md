# Conferência temporal de registros de artigos

**Data:** 15 de novembro de 2026  
**Produto:** [base técnica atualizada](./triagem_temporal_artigos_20261115.xlsx).

## Procedimento

Foram selecionados os **85 registros** que ainda estavam pendentes na triagem e já apresentavam, na base anterior, ano de publicação fora de 2020–2026. Destes, 48 são do Portal CAPES e 37 da SciELO. A base identifica 84 como artigos e um como editorial; esse tipo foi preservado, sem presumir sua elegibilidade para o panorama nacional.

Para cada linha, título e autoria foram confrontados com os arquivos RIS originais locais, exigindo correspondência única. O ano de publicação informado no campo `PY` foi comparado com a planilha; quando havia data em `DA`, seu ano também foi conferido. DOIs foram comparados quando presentes nas duas fontes. Os anos conferidos vão de **2011 a 2019**.

As fontes, os valores anteriores e revisados e os campos de data consultados constam da aba **Triagem temporal artigos**. O [script](../../scripts/triagem_temporal_artigos_20261115.py) interrompe o processamento diante de correspondência ausente ou ambígua, ano ausente ou divergente, conflito de DOI, problema de leitura do RIS ou data anterior inconsistente. Não foram feitas novas consultas externas.

## Decisões e alcance

As 85 linhas receberam `Excluir` na **triagem de título e resumo**, com motivo `Fora do período`, exclusivamente para o recorte de Goiás 2020–2026. A elegibilidade final foi mantida `Pendente`; os registros continuam na base e disponíveis para avaliação no panorama nacional. Não foi feita análise semântica adicional dos títulos e resumos, nem verificação de duplicidade ou extração de eixos nesta etapa. As classificações anteriores nessas dimensões foram preservadas.

Não foram usados anos de defesa como substitutos de ano de publicação. Casos sem data suficiente, inclusive registros de 2026 sem data completa e teses ou dissertações com apenas ano de defesa, não integraram este lote.

## Situação da base

| Triagem de título e resumo | Linhas |
|---|---:|
| Avançar para avaliação | 19 |
| Excluir do recorte goiano por ano de publicação | 110 |
| Pendente | 1.188 |
| **Total** | **1.317** |

As 110 linhas abrangem as 85 desta etapa e 25 anteriormente classificadas; são contagens de registros, não de obras únicas. Na elegibilidade final, 248 linhas estão pendentes e 1.069 não iniciadas. Permanecem 80 linhas em 40 pares de duplicatas confirmadas e 1.237 linhas com duplicidade não verificada.

## Verificação e limites

Foram comparadas as células fora do escopo, as abas históricas, as validações, as tabelas, as fórmulas e a integridade ZIP. Passaram **15 testes focados**, incluindo os da integração anterior. Não houve teste interativo no Excel.

A comparação com os RIS confere a transcrição em relação aos arquivos originais disponíveis, mas não é validação independente nem prova de exatidão da data na fonte. Não foram atribuídos percentuais de confiança. A coleta nacional continua incompleta e não permite inferência sobre toda a produção brasileira.

O próximo passo é continuar a análise semântica dos registros pendentes, especialmente teses e dissertações com resumos disponíveis, mantendo em aberto o período quando houver somente ano de defesa e prosseguindo com a conferência das duplicidades.
