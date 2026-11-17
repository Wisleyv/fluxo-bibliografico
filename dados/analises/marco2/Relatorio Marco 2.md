# Marco 2 — consolidação nacional provisória

**Estado:** consolidação técnica e conferência local executadas; **corpus nacional provisório, ainda não fechado metodologicamente**. O aceite do Marco 0 aprovou o uso do OpenAlex, os controles e as regras propostas, conservando explicitamente lacunas sobre definição de produção brasileira, tipos ambíguos e validação independente. Esta rodada avança até esse limite e registra também a triagem temática ainda não concluída.

## Produtos

- [Corpus nacional provisório: 138 unidades com evidência de leitura](Corpus%20nacional%20provisorio.csv).
- [Proveniência: 13.748 registros ligados às unidades](Proveniencia.csv).
- [Registro completo: 13.226 unidades consolidadas pelas identidades sustentadas](Registro%20de%20unidades.csv).
- [Cobertura atualizada por fonte](Cobertura%20atualizada.csv).
- [Fila residual de pendências](Pendencias%20residuais.csv).
- [Conciliação: pares, justificativas e efeito residual](Conciliacao%20de%20identidades.csv).
- [Quatro complementares incorporados provisoriamente](Obras%20complementares%20incorporadas%20provisoriamente.csv).
- [Pré-corpus temático: 6.429 candidatos, não inclusões finais](Pre%20corpus%20tematico.csv).
- [Amostra estratificada e materiais consultados](Amostra%20para%20conferencia.csv), [conferência dos 30 casos](Conferencia%20amostral.csv) e [auditoria](Auditoria.json).

Todos os caminhos são relativos à pasta deste relatório. Os arquivos CSV preservam campos explícitos de estado e de identidade residual. O registro completo inclui casos que não podem entrar no corpus; não somar seus totais ao pré-corpus ou ao núcleo, pois são visões do mesmo universo.

## Insumos e decisões reaproveitados

Reutilizaram-se a base `dados/analises/triagem_criterio_defesa_20261115.xlsx`, a coleta `dados/analises/openalex_busca_restrita_20261115.csv`, suas 125 páginas JSON, a auditoria da coleta e os resultados do Marco 1. Foram conservados os 167 pares sustentados do Marco 1 — 116 anteriores e 51 revisados — e os 40 pares históricos confirmados na base.

A geração normalizada vigente `dados/normalizados/registros_normalizados__20261108T205625-0300__828bdff7.csv` foi lida uma vez em fluxo para recuperar, para cada Código da base, o UUID completo, identificador original, execução e caminho do bruto. Os 1.317 prefixos foram relacionados sem colisões ou ausências. A proveniência mantém o identificador da obra consolidada e cada registro de origem; para registros OpenAlex inclui página, ID, execução e horário efetivo. Os campos de ano/título/autoria da base representam a versão técnica vigente, não uma alegação de transcrição sem correções do bruto. Este último permanece localizável pelo caminho e UUID.

Reutilizaram-se as funções de normalização de texto/DOI, confirmação dos pares históricos e validação de páginas. Não houve coleta, visita a páginas externas, alteração da base técnica ou promoção de decisão regional para elegibilidade nacional.

## Período, tipo e tema

O filtro nacional aplicado é publicação entre **01/01/2007 e 08/11/2026 inclusive**. A coleta foi realizada em **15/11/2026** e seus horários individuais acompanham a proveniência. Datas de defesa permanecem separadas e não satisfazem automaticamente o critério nacional, mesmo quando autorizadas alternativamente para a revisão de Goiás.

As 12.431 datas OpenAlex passaram na validação local. Anos explícitos de publicação entre 2007 e 2025 nas fontes complementares têm suporte temporal; somente ano 2026 sem dia/mês não seria suficiente para comprovar o corte. Quando datas completas divergem, não escolher silenciosamente; conflito que atravesse o corte gera pendência. Nesta rodada nenhuma data completa ficou fora do corte. No conjunto consolidado, 12.437 unidades têm suporte temporal e **789 permanecem sem publicação nacional comprovada**, essencialmente nas fontes de teses/dissertações.

Artigo, livro, capítulo, trabalho em anais e tese/dissertação têm tipos compatíveis com o escopo já aprovado; `review` foi tratado como revisão acadêmica compatível, mantendo o rótulo original. Isso é suporte documental, não prova isolada de pertinência. Preprint, resumo de evento, editorial, paratexto, dataset e demais rótulos ambíguos ficam pendentes de enquadramento, sem exclusão automática: **223 unidades** têm tipo ainda pendente. No OpenAlex, `dissertation` foi usado como classe ampla compatível com tese ou dissertação, sem converter doutorado em mestrado.

Para o tema, foram reaproveitadas leituras anteriores que registravam tema central ou relação substantiva; novas leituras locais e a amostra complementam essa evidência. A mera presença de PIBID no título ou sua recuperação pela API gera uma fila de candidatos, **não inclusão final**. Ausência de resumo ou de sigla no título também não exclui. Os 6.429 candidatos do pré-corpus continuam identificados conforme o nível da evidência, incluindo candidatos que ainda exigem triagem substantiva. O corpus provisório de 138 é o subconjunto com suporte de leitura, tipo compatível e publicação no intervalo. Ainda depende da definição nacional e, em cinco unidades, de pendências de identidade que podem afetar a contagem.

## Deduplicação e os 522 pares inconclusivos

Identificadores OpenAlex foram conferidos quanto à unicidade; não há DOI normalizado repetido entre os 12.431 registros originais OpenAlex. DOI idêntico não foi usado isoladamente para fundir obras.

Para correspondências novas, exigiu-se tipo compatível, ausência de conflito entre DOIs informados, título normalizado exato com ao menos seis tokens e autoria completa concordante. Além disso, exigiu-se identificador de repositório coincidente ou resumo concordante (Jaccard de tokens distintos ≥0,90, com pelo menos 30 tokens distintos em cada resumo). Para artigos e outros tipos não classificados como tese/dissertação, a concordância explícita de ano de publicação também fornece corroboração adicional. Ausência de autoria ou `et al.` não é concordância completa. Essas regras são de identidade bibliográfica e não de validação temática.

Diferença entre artigo e tese foi mantida como ambiguidade: pode ser produção derivada ou classificação errada da fonte. A comparação não funde essas obras pelo título. Os identificadores de repositório são extraídos dos caminhos handle das localizações arquivadas, não inferidos da universidade.

| Origem das relações | Confirmadas | Pendentes na regra direta | Total de pares |
|---|---:|---:|---:|
| Pares históricos internos | 40 | 0 | 40 |
| Sustentados no Marco 1 | 167 | 0 | 167 |
| Inconclusivos do Marco 1 | **295** | **227** | **522** |
| Comparações adicionais por título exato | 43 | 587 | 630 |
| **Total** | **545** | **814** | **1.359** |

As 43 confirmações adicionais são 38 relações entre controles e cinco relações dentro do OpenAlex. Três relações diretamente pendentes já pertencem ao mesmo componente por outras evidências confirmadas; portanto a fila de relações com possível efeito residual tem **811 pares**. Não são 811 obras nem 811 exclusões.

As 545 arestas confirmadas reduzem 522 registros: algumas arestas corroboram conexões já existentes e não reduzem novamente a contagem. O resultado é uma partição dos registros por identidades sustentadas, não garantia de que nenhuma duplicata residual exista. Títulos genéricos, nomes insuficientes, DOIs conflitantes e tipos incompatíveis conservam justificativas na tabela de conciliação. O par de DOI atípico `4348c88f` permanece entre os não resolvidos.

## Reconciliação das unidades

| Medida | Quantidade | Unidade |
|---|---:|---|
| OpenAlex original | 12.431 | registros/IDs |
| Fontes complementares | 1.317 | linhas da base técnica |
| Entradas totais | **13.748** | registros |
| Redução por identidades sustentadas | 522 | registros redundantes no componente |
| Registro consolidado | **13.226** | unidades provisórias |
| Unidades com OpenAlex | 12.426 | componentes, após cinco fusões internas |
| Unidades somente complementares | 800 | componentes |
| Corpus provisório com evidência de leitura | **138** | subconjunto das unidades |
| Dessas, sem OpenAlex | **4** | unidades complementares incorporadas provisoriamente |

O Marco 1 apresentava 626 grupos provisórios exclusivos, correspondentes a 652 linhas. Reprojetados após a conciliação, esses mesmos códigos ocupam **602 unidades**, ainda sem OpenAlex. A redução decorre da conciliação entre controles; não transforma ausência de candidato na busca em inexistência no índice completo. Os 800 componentes exclusivamente complementares incluem também obras oriundas de pares anteriormente candidatos que continuaram sem identidade OpenAlex confirmada. Assim, 626, 602 e 800 têm universos e estágios diferentes e não devem ser somados.

A cobertura por fonte está no CSV: 1.060 linhas BDTD representam 994 unidades (269 com OpenAlex); 78 linhas Catálogo representam 78 unidades (cinco com OpenAlex); 103 linhas Portal representam 103 unidades (101 com OpenAlex); 76 linhas SciELO representam 76 unidades (69 com OpenAlex). Os totais por fonte se sobrepõem e não somam o total de obras. A relação linha→obra está integralmente na proveniência.

## Complementares e divergências de ano

Quatro unidades sem registro OpenAlex têm suporte temático de leitura, documental e temporal e foram acrescentadas **provisoriamente**:

- `223fc435` / `fe0699e5`: Plataforma Inglês Paraná — duas linhas conciliadas; participantes do PIBID integram a investigação. Publicação 2024 explícita na base, separada da defesa.
- `7ef41aa6`: Um esboço crítico sobre parceria na formação de professores — resumo analisa documentos e ações do PIBID.
- `b0560bbc`: Quero ser professora — resumo analisa sentidos da docência construídos por bolsistas.
- `ebceb9d5`: Práticas de leitura no ensino médio: o Pibid de Letras — suporte de leitura anterior reaproveitado; identidade residual ainda pode alterar a contagem.

Não se incorporaram todas as 800 unidades somente complementares por simples recuperação. As outras 796 permanecem no registro e na fila, por data, pertinência, natureza documental, identidade ou combinações dessas condições. São preservadas também as obras com defesa elegível para Goiás, mesmo sem publicação nacional comprovada.

A divergência original `5c2ab78c` continua registrada como **2014 no OpenAlex e 2015 na SciELO**, dentro de uma única unidade já sustentada por identidade. Não houve preferência silenciosa de ano. A consolidação identificou mais três unidades com anos discordantes: 2013/2014, 2011/2012 e 2022/2025. Os quatro conflitos não atravessam as faixas 2007–2019/2020–2026 nem o corte nacional, mas alteram séries anuais. Datas e anos de cada origem estão na proveniência, e a coluna `divergencia_ano` permite localizar os quatro casos. Não foi escolhido um ano canônico para indicadores.

## Conferência amostral e testes

A amostra local foi sorteada com semente 20261115, dez unidades por estrato operacional: núcleo com leitura, sinal no título e demais pendentes. São 30 casos de conferência de regras, não uma amostra independente de desempenho. O CSV da amostra guarda título, resumo disponível, tipo, estado temporal e caminho da fonte. O CSV de conferência registra o parecer individual.

Resultados: dez compatíveis com leituras anteriores, 15 com pertinência sustentada no material amostral e cinco mantidos pendentes. A leitura integral dos resumos especiais mostrou que temas sem PIBID no título podem ser pertinentes: não se excluiu por ausência de sigla. Os cinco casos pendentes incluem resumo ausente, metadado de evento no lugar de resumo e papel ainda incerto do PIBID. Das 15 novas evidências positivas, 13 satisfizeram também tipo e data e foram incorporadas ao núcleo: **125 antes da conferência → 138 depois**. Uma dissertação continua sem publicação comprovada e um resumo de evento depende de decisão documental; não foram incluídos apenas por tema.

Conferências técnicas realizadas:

1. Hashes e parâmetros das 125 páginas, cursores, IDs únicos e intervalo de todas as datas OpenAlex; sequência terminada e IDs coincidentes com o CSV.
2. Relação sem colisões dos 1.317 códigos com UUID e bruto na geração normalizada; existência dos caminhos da proveniência.
3. Reutilização e reconciliação dos 40 pares históricos e 167 pares Marco 1; registro separado dos 522 reavaliados.
4. Partição dos 13.748 registros com cada registro ligado exatamente a uma unidade; somas de proveniência e cobertura por registro reconciliadas.
5. Hashes das seis entradas principais idênticos antes/depois; nenhum dado histórico foi sobrescrito.
6. **13 testes focados aprovados**, incluindo seis novos: fronteira de data, ano parcial de 2026, falta de publicação, DOI conflitante, tese versus artigo e necessidade de evidência adicional à igualdade de título/autoria. Os demais cobrem identidade e denominadores reaproveitados.

Reprodução: executar `python -m scripts.construir_corpus_marco2` para a primeira consolidação; preservar/preencher o registro da conferência de 30 casos; executar `python -m scripts.integrar_conferencia_marco2` para integrar suas decisões. A primeira etapa recusa diretório existente e a segunda recusa integração repetida. Não se deve apagar uma rodada para reexecutar: escolher novo destino/versionamento e conservar a presente. A auditoria registra os totais antes e depois da conferência.

## Decisões para fechar o corpus e efeito prático

| Decisão/pendência | Proposta ou providência necessária | Efeito |
|---|---|---|
| Definição de produção brasileira | Escolher entre vínculo/contexto brasileiro documentado e regra estritamente por afiliação; a mera recuperação temática não decide isso. | Todo o corpus permanece provisório. Das 138 unidades do núcleo, 93 têm BR explícito nas afiliações OpenAlex e 45 não têm esse sinal ou não têm metadado de afiliação. Ausência de BR não prova origem estrangeira. |
| Tipos ambíguos | Aprovar mapeamento dos 223 componentes com tipo pendente, inclusive resumo de evento, preprint, editorial e dataset. | Pode acrescentar obras pertinentes; não excluí-los automaticamente e não confundir natureza acadêmica com tipo da API. |
| Triagem temática remanescente | Rever prioritariamente candidatos do pré-corpus com potencial de alterar resultados; a amostra não autoriza generalizar inclusão aos demais. | As 6.429 unidades do pré-corpus incluem as 138 com leitura; 6.291 ainda não têm o mesmo suporte de tema/data/tipo exigido para o núcleo. Obras sem sinal no título também permanecem no registro completo. |
| Identidade residual | Resolver os pares de maior impacto ou adotar explicitamente limites de contagem; não somar ambas as pontas como obras finais. | 811 relações podem reduzir contagens; cinco unidades do núcleo ainda têm relações residuais. |
| Publicação das complementares | Usar apenas publicação documentalmente sustentada; defesa alternativa vale para Goiás. | 789 unidades têm data nacional pendente; muitas podem seguir para exame regional pelo critério de defesa sem entrar no panorama por publicação. |
| Ano canônico | Definir regra e fonte preferencial antes de série anual, mantendo ambas as datas. | Quatro unidades têm conflito de ano; sem impacto no corte amplo atual, mas com impacto nos anos individuais. |
| Validação independente | Definir responsável, referência e amostra antes de alegar desempenho. | Não impede inspeção de dados, mas impede apresentar acurácia, confiança calibrada ou revisão validada independentemente. |

As pendências têm linhas próprias por unidade, prioridade e vínculos aos registros; as evidências de pares estão em arquivo separado. A definição brasileira é comum a todas e não foi ocultada por uma inclusão automática. **Não há contagem nacional final aprovada nesta rodada.** O núcleo de 138 oferece material auditável com pertinência sustentada, enquanto o pré-corpus e o registro completo permitem continuar sem refazer a coleta ou a consolidação.

Para o Marco 3, preservar os critérios de contexto e afiliação separados, o critério alternativo de defesa e os códigos da base. As 789 pendências de publicação nacional não excluem automaticamente da revisão goiana. Identidades entre tese e artigo, afiliações ausentes e as cinco unidades com identidade residual no núcleo podem alterar a seleção e a contagem regional; devem ser tratadas antes de gráficos finais. Esta rodada não executou a revisão goiana nem alterou as 19 inclusões históricas.
