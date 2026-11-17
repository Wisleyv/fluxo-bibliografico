# Protocolo bibliométrico — v1.2 MINUTA

**Atualização posterior:** minuta aceita como referência operacional do Marco 1 conforme `Aceite do Marco 0.md`. As lacunas explícitas de definição nacional, tipos ambíguos e validação independente continuam para fechamento antes dos respectivos produtos. Preserva-se abaixo a redação histórica da minuta.

Data: 15/11/2026. Estado: pronta para aprovação; não substitui a versão 1.1 vigente em `Protocolo de busca bibliométrica.md`.

Esta minuta executa a preparação do Marco 0 do `Plano de ação - realinhamento da coleta e análise.md`. As aprovações e pendências estão em `Matriz de aprovação - Marco 0.md`; os insumos e verificações estão em `Inventário de insumos - Marco 0.md`. A concordância com a preparação do plano e a autorização desta rodada não são tomadas como aprovação formal das oito decisões metodológicas.

## Objetivos e unidades

Conservar os dois movimentos de `Vaneria.txt`: panorama brasileiro de 2007–2026 e revisão de escopo goiana de 2020–2026. Propõe-se obra acadêmica única como unidade final, com múltiplos registros de origem preservados. Linhas exportadas, registros OpenAlex e pares de correspondência são unidades técnicas diferentes; não representam automaticamente obras elegíveis únicas.

A definição operacional de produção brasileira ainda deve ser fechada antes da consolidação nacional: não confundir idioma, país do periódico, tema brasileiro, contexto da pesquisa e afiliação brasileira. A consulta executada não aplicou filtro de país. Propõe-se registrar essas dimensões e aprovar a regra nacional antes de classificar obras como brasileiras; não aplicar agora um filtro de afiliação que descarte silenciosamente obras com afiliação ausente.

## Busca executada e datas

A auditoria `dados/analises/openalex_busca_restrita_auditoria_20261115.json` e os parâmetros das 125 páginas preservam:

```text
search.title_abstract_keywords = PIBID OR "Programa Institucional de Bolsa de Iniciação à Docência"
filter = from_publication_date:2007-01-01,to_publication_date:2026-11-08
per_page = 100
```

O endpoint e o procedimento estão em `scripts/coletar_openalex_restrita_20261115.py`. O parâmetro pesquisou título, resumo e palavras-chave no índice da API; a recuperação não demonstra em qual campo original houve correspondência nem comprova pertinência substantiva. Não houve filtro de país ou tipo documental nessa consulta. Preservar a consulta literal, sem adaptá-la retroativamente.

O corte de publicação nacional é **08/11/2026 inclusive**: delimita as datas de publicação aceitas pela consulta, tornando 2026 parcial. A coleta efetiva ocorreu em **15/11/2026, de 19:33:58 a 19:37:22, UTC−03:00**. Ela observa o índice dessa execução, inclusive registros incorporados ou corrigidos depois de 08/11; não reconstrói o índice histórico daquela data. As duas datas devem acompanhar tabelas e metodologia. A admissibilidade final de registros recuperados posteriormente depende da decisão 6 da matriz.

## Fontes e comparabilidade propostas

Propõe-se OpenAlex como fonte operacional principal nacional. Portal de Periódicos CAPES permanece como fonte originalmente prevista, controle parcial e complemento. SciELO Brasil oferece controle de artigos; BDTD e Catálogo de Teses e Dissertações CAPES são essenciais para teses e dissertações, inclusive sem DOI. Google Scholar permanece complementar manual, sujeito a necessidade documentada. Nenhuma nova coleta é autorizada nesta rodada.

A mudança de fonte altera cobertura, campos pesquisáveis, tipos, metadados, datas de indexação e regras internas de agregação. Não há equivalência demonstrada entre a consulta OpenAlex e os 2.777 resultados nacionais relatados do Portal CAPES. A cobertura observada deve ser medida nos controles arquivados, por fonte, período e tipo, com denominador verificável; controles regionais ou de um único ano não estimam recuperação de toda a produção brasileira. Obras exclusivas das fontes complementares só serão incorporadas após conciliação e elegibilidade, com proveniência preservada.

## Recorte regional e elegibilidade

Manter a consulta regional de referência `(PIBID OR "Programa Institucional de Bolsa de Iniciação à Docência") AND ("Goiás" OR "goiano" OR "goiana")` e a complementação por IES/contextos prevista em `Vaneria.txt`. Os sinais são instrumentos de recuperação e priorização, não decisões de elegibilidade nem universo exaustivo.

A regra contexto **ou** afiliação goiana está documentada no plano de análise, seção 7, como decisão informada em 15/11. Preservar campos separados: contexto em Goiás não prova afiliação; instituição associada à tese não prova afiliação da autoria. Essa regra regional não resolve a atribuição de coautoria nem o denominador nacional.

Para a revisão goiana, conservar publicação de 2020 até 08/11/2026 e o critério alternativo aprovado na v1.1: defesa em 2020–2026 para teses e dissertações, identificada separadamente. Para defesa em 2026 com somente ano, registrar evidência temporal limitada; não converter defesa, depósito ou atualização em publicação. Esse critério não se estende automaticamente a novas obras OpenAlex sem evidência de defesa.

Conservar todos os idiomas e tipos acadêmicos previstos na v1.1, pertinência substantiva ao PIBID e justificativas rastreáveis de exclusão. O mapeamento final dos tipos OpenAlex, especialmente dataset, paratext, peer-review e outros formatos ambíguos, permanece pendente; nenhum será excluído nesta etapa por rótulo isolado. Ausência de resumo ou afiliação não é exclusão automática.

Os três eixos — aprendizagem da docência, trajetórias profissionais e relações IES–escolas–comunidades — orientam a extração após seleção; identidade profissional, saberes e espaços híbridos são aspectos de análise. Registrar material, localização, síntese e limites; distinguir presente, não informado, não verificável e pendente.

## Identidade, validação e indicadores

Propor uma obra por unidade consolidada, preservando seus registros de origem. Reutilizar DOI normalizado, identificador OpenAlex e comparação bibliográfica. Os 116 pares sustentados são classificações operacionais existentes, não novas decisões desta rodada; os 52 pares com identificador concordante continuam em revisão e os 521 por título continuam candidatos. Tese e artigo não são fundidos apenas por título.

A conferência computacional não constitui validação científica independente. Há autoavaliação de 60 linhas e segunda conferência por regras documentadas; não atribuir taxas de acerto ou faixas de confiança sem referência independente. O alcance final da validação é decisão aberta.

Antes de indicadores, aprovar contagem inteira ou fracionada, múltiplas afiliações, definição nacional e tratamento de desconhecidos. Propor contagem inteira de obras únicas com ao menos uma afiliação goiana confirmada, com cobertura de afiliação reportada; manter essa proposta suspensa até aprovação. Numerador e denominador deverão compartilhar corpus, período e tipos. O recorte por defesa será apresentado separadamente da série por publicação quando os denominadores não forem equivalentes.

## Congelamento e sequência

Base de trabalho proposta: `dados/analises/triagem_criterio_defesa_20261115.xlsx`, aba `Triagem`, pelas evidências do inventário. Preservar originais e decisões históricas. Novas coletas amplas ficam suspensas nesta rodada; eventual retomada segue a regra de parada do plano de realinhamento.

O Marco 1 está tecnicamente preparado para medir correspondência bibliográfica nos quatro controles existentes. Essa medição descritiva não exige decisões finais de elegibilidade, contagem regional ou indicadores; requer aceite operacional dos insumos e das regras de identidade/denominador descritas na matriz. A apresentação do OpenAlex como fonte principal aprovada permanece condicionada à decisão 1. Encerrar o Marco 0 como preparação para aprovação enquanto houver essas decisões abertas.

Histórico: v1.1 preservada; v1.2 minuta adiciona proposta de mudança de fonte, datas executadas, controles e limites de aprovação. Esta rodada não resolveu pares, não decidiu elegibilidade e não alterou produtos históricos.
