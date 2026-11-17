# Diagnóstico inicial — planilha e dados disponíveis

**Data:** 15 de novembro de 2026  
**Etapa:** diagnóstico inicial; não constitui triagem, validação dos estudos nem resultado da pesquisa.

## 1. Procedimento e preservação

Foi inspecionada a estrutura e contado o preenchimento das células da [planilha original](../entregas/pacote_preliminar_20261112/Triagem%20e%20an%C3%A1lise.xlsx), sem alterá-la. Foi criada uma [cópia de diagnóstico](./triagem_base_diagnostico_20261115.xlsx), sem sobrescrever arquivos existentes. Original antes e depois da cópia e cópia apresentaram o mesmo SHA-256:

`3FFFF0FD78886E72592B9A95D1EDEF078FA1054B25C6BC7E7CA08B7EB6091BFE`

Foram consultados o [guia da entrega preliminar](../entregas/pacote_preliminar_20261112/LEIA-ME%20-%20orienta%C3%A7%C3%B5es%20para%20a%20pesquisadora.md), o [registro das buscas](../logs/execucoes.csv), o [manifesto de arquivos](../logs/arquivos.csv), o [registro de normalização](../logs/normalizacoes.csv), a [matriz de viabilidade](../../Matriz%20de%20viabilidade%20dos%20pilotos.md) e o [teste técnico do piloto](../triagem/relatorio_teste_piloto_pacote_20261112.md). A contagem de células verifica preenchimento, não a correção ou a suficiência do conteúdo. Não houve consulta atual aos links, leitura integral individual dos estudos ou teste interativo no Excel.

## 2. Estrutura e situação geral

| Aba | Linhas de dados | Estrutura e situação |
|---|---:|---|
| Triagem | 1.317 | 35 colunas, A–AI; 1.317 códigos distintos. São referências candidatas, não estudos incluídos. |
| Eixos de análise | 108 | 11 colunas; três eixos para cada um dos 36 códigos piloto. Todos os códigos constam em Triagem. As colunas de estado, achados e evidências estão vazias. |
| Possíveis duplicatas | 231 | Nove colunas, 114 grupos candidatos e 229 códigos distintos; todos constam em Triagem. As linhas não representam duplicatas confirmadas nem exaurem todas as possibilidades. |

As três abas contêm tabelas; há nove validações de dados em Triagem e uma em Eixos. Não foram encontradas fórmulas nem gráficos nas abas. A futura simplificação deverá reconstruir ou conferir tabelas e validações aplicáveis, além de testar a abertura e os gráficos no Excel.

Em Triagem, os campos de relação com PIBID, contexto goiano, período da revisão, produção acadêmica e afiliação goiana estão vazios em todos os registros. As 1.317 decisões de título e resumo constam como `Pendente`, as decisões de elegibilidade como `Não iniciada` e a duplicidade como `Não verificada`. Nenhuma dessas situações equivale a uma decisão científica.

## 3. Cobertura dos campos

Contagens de células preenchidas; os totais por fonte incluem registros potencialmente sobrepostos.

| Fonte | Referências | Ano de publicação | Ano de defesa | Resumo | Palavras-chave | Instituição associada | Afiliação de autoria |
|---|---:|---:|---:|---:|---:|---:|---:|
| BDTD | 1.060 | 0 | 1.060 | 1.037 | 937 | 1.060 | 0 |
| Portal CAPES | 103 | 103 | 0 | 0 | 0 | 0 | 0 |
| Catálogo CAPES | 78 | 0 | 78 | 78 | 78 | 78 | 0 |
| SciELO | 76 | 76 | 0 | 76 | 75 | 0 | 0 |
| **Total** | **1.317** | **179** | **1.138** | **1.191** | **1.090** | **1.138** | **0** |

- Entre os 179 anos de publicação, 69 estão em 2020–2026 e 110 fora desse intervalo; 1.138 registros não apresentam ano de publicação. Ano de defesa não deve ser automaticamente convertido em ano de publicação.
- A coluna de programa de pós-graduação tem 536 células preenchidas; DOI, 173; link da fonte, 1.146; e link OpenAlex, 36. A disponibilidade e o conteúdo atual dos links não foram verificados.
- Os 103 registros do Portal CAPES não têm resumo na planilha, inclusive os 36 do piloto. A avaliação deles pode exigir fontes complementares. O pacote preliminar não contém textos integrais, segundo o guia.
- Os 95 alertas em AI compreendem 17 indicações de caracteres a conferir no próprio registro e 78 alertas de problemas em outros registros da mesma fonte, não necessariamente no registro sinalizado. Preservar essa distinção no registro técnico.
- A contagem de instituições associadas não comprova afiliação de autoria, nem a de afiliações comprova o contexto geográfico da pesquisa.

## 4. Fontes e limites da coleta

O manifesto registra nove arquivos brutos: dois da BDTD, cinco do Portal CAPES, um do Catálogo CAPES e um da SciELO. A execução de normalização concluída em 8 de novembro registra 93.072 linhas normalizadas; esse total inclui o arquivo anual amplo do Catálogo e **não** significa 93.072 estudos elegíveis sobre o PIBID. As versões anteriores dessa normalização constam como substituídas.

- **BDTD:** o registro de coleta informa 1.018 resultados exportados na busca nacional e 42 na regional. A matriz aponta que o filtro da interface é chamado ano de publicação, enquanto o campo exportado é ano de defesa; a diferença requer verificação.
- **Portal CAPES:** o registro da busca nacional informa 2.777 resultados exibidos, mas apenas um exportado naquela execução. A busca regional teve 102 resultados exportados em quatro lotes. Portanto, a exportação nacional não está completa.
- **Catálogo CAPES:** o arquivo anual de 2024 contém 91.833 registros, segundo o registro de coleta; a matriz relata 78 candidatos com termos temáticos. A cobertura aberta de 2025–2026 não foi confirmada.
- **SciELO:** a exportação registra 76 referências da coleção Brasil. O protocolo geral inclui 2007–2026; a busca e o filtro efetivamente usados devem ser descritos conforme as evidências, sem presumir um filtro temporal que não foi comprovado.
- **Google Scholar:** previsto apenas como busca complementar exploratória manual e documentada na matriz de viabilidade, não como coleta automatizada ou cobertura exaustiva.

Totais de buscas diferentes não devem ser somados como quantidade de estudos únicos. Buscas por instituições e contextos goianos permanecem pendentes segundo o guia. A existência de scripts de captura, normalização e auditoria de caracteres permite avaliar seu reaproveitamento, mas sua adequação a novas etapas ainda deve ser testada.

## 5. Destinação proposta das colunas

**Resultado** significa candidato a permanecer na entrega final se efetivamente utilizado em tabela, gráfico ou identificação do resultado; **técnico** significa preservar na base de trabalho/auditoria e omitir da planilha final. Esta proposta não altera nem exclui colunas agora. A forma final depende dos resultados e da validação dos critérios.

### Aba Triagem

| Coluna | Campo | Destinação proposta e vínculo |
|---|---|---|
| A | Código | Resultado: identificador para vincular estudo e resultados. |
| B | Fonte | Resultado se compuser apresentação da cobertura ou identificação da referência; caso contrário, técnico. |
| C | Tipo de produção | Resultado: distribuição por tipo. |
| D | Título | Resultado: identificação do estudo e dos achados. |
| E | Autoria | Resultado: identificação e análise de autorias. |
| F | Ano de publicação | Resultado: evolução temporal, quando confirmado. |
| G | Ano de defesa | Resultado apenas se usado como indicador distinto; nunca substituir automaticamente F. Caso contrário, técnico. |
| H | Resumo | Técnico: material de análise, não resultado em si. |
| I | Palavras-chave | Resultado se usadas para apresentar temáticas; caso contrário, técnico. |
| J | Instituição associada | Resultado para distribuição institucional, com identificação correta do vínculo. |
| K | Afiliações de autoria | Resultado para distribuição e colaboração, se obtidas e verificadas. |
| L | Programa de pós-graduação | Resultado se houver análise de programas. |
| M | DOI | Resultado para identificação e localização das publicações. |
| N | Link da fonte | Resultado para identificação e acesso às referências. |
| O | Link OpenAlex | Técnico: apoio de consulta; preservar a fonte efetivamente usada. |
| P | Piloto CAPES | Técnico: marcador de triagem. |
| Q | Relação com PIBID | Técnico: critério de seleção; preservá-lo com evidência. |
| R | Contexto de Goiás | Resultado se usado para apresentar o recorte geográfico; preservar evidência técnica. |
| S | Publicação em 2020–2026 | Técnico: critério de seleção; ano confirmado em F sustenta o resultado temporal. |
| T | Produção acadêmica | Técnico: critério de seleção. |
| U | Triagem de título e resumo | Técnico: fluxo de seleção e rastreabilidade. |
| V | Decisão de elegibilidade | Técnico: seleção e denominadores do fluxo. |
| W | Motivo da exclusão | Técnico: justificativa e fluxo de seleção. |
| X | Duplicidade | Técnico: deduplicação e fluxo de seleção. |
| Y | Código do registro principal | Técnico: vínculo entre duplicatas e fontes. |
| Z | Evidência do contexto | Técnico: fundamentação da classificação geográfica. |
| AA | Afiliação em Goiás | Resultado se usado na análise geográfica, separado do contexto da pesquisa. |
| AB | Evidência da afiliação | Técnico: fundamentação da afiliação. |
| AC | Fontes das evidências | Técnico: rastreabilidade das decisões e extrações. |
| AD | Material consultado | Técnico: limite do material efetivamente examinado. |
| AE | Limitações e pendências | Técnico: preservar limites e sintetizá-los nas notas dos resultados. |
| AF | Observações | Técnico, salvo eventual achado relevante extraído para coluna específica de resultado. |
| AG | Revisor | Técnico; excluir da planilha final conforme solicitado. |
| AH | Data da triagem | Técnico; excluir da planilha final conforme solicitado. |
| AI | Alerta de qualidade | Técnico; preservar os alertas e sua distinção antes de excluir da planilha final. |

### Aba Eixos de análise

São candidatas a resultado as colunas **A Código**, **B Título**, **C Eixo**, **D Estado** e **E Achado ou observação**, na medida em que componham a apresentação. As colunas **F Trecho ou localização**, **G Tipo de fonte**, **H Link ou referência consultada** e **I Limites da evidência** devem permanecer no registro técnico para auditoria; limites relevantes devem aparecer nas notas dos resultados. **J Revisor** e **K Data** são técnicos. A atual aba contém somente os 36 registros piloto: expandir aos demais estudos elegíveis antes de apresentar o conjunto como completo.

### Aba Possíveis duplicatas

As colunas **A Grupo**, **B Código**, **C Fonte**, **D Título**, **E Autoria**, **F Ano de publicação**, **G Ano de defesa**, **H DOI** e **I Critério de comparação** são uma lista técnica de conferência, não uma tabela final de resultados. Preservar a lista e as decisões em registro separado; o fluxo final poderá apresentar contagens agregadas após verificação.

## 6. Pendências para a próxima etapa

1. Acordar a regra para afiliação goiana com contexto fora do estado ou desconhecido, sem confundir afiliação e local da pesquisa.
2. Definir e testar critérios de triagem e extração nos 36 registros piloto; estimar tempo e necessidade de complementação antes de processar todos os registros.
3. Definir a amostra de validação e verificar se os dados sustentam as faixas de desempenho pretendidas; não atribuir percentuais por suposição.
4. Avaliar o esforço de coleta complementar e as fontes efetivamente acessíveis no prazo; preservar limitações se não for possível concluí-la.
5. Confirmar a destinação condicional das colunas após definir os resultados e preservar os dados de auditoria antes de produzir uma versão simplificada.
