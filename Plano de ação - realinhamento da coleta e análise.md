# Plano de ação — realinhamento da coleta e análise

**Versão:** 1.0  
**Data:** 15 de novembro de 2026  
**Situação:** proposta para aprovação metodológica e execução  
**Documento canônico:** [Vaneria.txt](./Vaneria.txt)

## 1. Finalidade

Realinhar o projeto aos dois movimentos previstos no documento canônico:

1. mapear a produção científica sobre o PIBID no Brasil, de 2007 a 2026, e situar Goiás nesse cenário;
2. realizar uma revisão de escopo da produção referente a Goiás, de 2020 a 2026, segundo os três eixos canônicos.

O realinhamento deve permitir a conclusão dos entregáveis no menor tempo possível, com uso prioritário dos dados, scripts e decisões já existentes. Processamento semântico ou consulta individual será reservado aos casos que possam alterar a elegibilidade, a deduplicação ou os resultados.

Este plano complementa o [protocolo vigente](./Protocolo%20de%20busca%20bibliom%C3%A9trica.md), o [plano de automação](./Plano%20de%20a%C3%A7%C3%A3o%20-%20automa%C3%A7%C3%A3o%20da%20coleta.md) e o [plano de análise](./Plano%20de%20a%C3%A7%C3%A3o%20-%20an%C3%A1lise%20e%20metodologia.md). Depois de aprovado pela pesquisadora, deverá fundamentar uma nova versão do protocolo. Não altera retroativamente as consultas ou decisões já executadas.

## 2. Decisão de realinhamento

### 2.1 Papel do OpenAlex

O OpenAlex passa de fonte complementar exploratória a **fonte operacional principal do panorama nacional**, em razão da impossibilidade prática de exportar integralmente os resultados nacionais do Portal de Periódicos CAPES.

Essa decisão não pressupõe que:

- o OpenAlex reproduza o índice, a consulta ou os resultados do Portal CAPES;
- os dados do Portal CAPES sejam diretamente distribuídos ao OpenAlex;
- todo registro presente em uma das fontes esteja presente na outra;
- a coleta OpenAlex, realizada em 15/11, reconstrua o estado dos índices em 08/11;
- a recuperação automática comprove elegibilidade temática ou identidade bibliográfica.

O OpenAlex agrega registros provenientes de Crossref, DataCite, PubMed, DOAJ, repositórios e outras fontes. A integração institucional recente documentada entre CAPES e OpenAlex utiliza a base OpenAlex para localizar publicações de pesquisadores na Plataforma Sucupira. Há sobreposição relevante entre os acervos: apresentação institucional da CAPES informou que 28.778 dos 40.216 títulos do Portal, ou 71,55%, estavam indexados no OpenAlex. Essa medida é de títulos de periódicos, não de obras recuperadas por uma consulta específica.

Fontes externas de referência:

- [OpenAlex — How it's built](https://help.openalex.org/data/how-its-built/);
- [RNP — integração da Plataforma Sucupira com o OpenAlex](https://www.rnp.br/2026/07/13/nova-integracao-da-plataforma-sucupira-reduz-em-ate-80-o-tempo-de-registro-da-producao-cientifica/);
- [CAPES/euroCRIS — uso de ORCID e OpenAlex e sobreposição de títulos](https://dspacecris.eurocris.org/bitstream/11366/2751/1/Portella_euroCRIS_MM2025_AI-CAPES_apresenta%C3%A7%C3%A3o.pdf).

### 2.2 Papel das demais fontes

| Fonte | Papel após o realinhamento |
|---|---|
| OpenAlex | Espinha dorsal reproduzível da recuperação nacional e apoio à deduplicação, afiliação e complementação de metadados. |
| Portal de Periódicos CAPES | Fonte originalmente prevista, conjunto parcial de controle e fonte complementar para obras não recuperadas no OpenAlex. |
| BDTD | Fonte essencial de teses e dissertações, especialmente documentos sem DOI ou com cobertura incompleta no OpenAlex. |
| Catálogo de Teses e Dissertações CAPES | Fonte complementar de teses e dissertações e de campos acadêmicos específicos. |
| SciELO | Fonte complementar e conjunto de controle para artigos da coleção Brasil. |
| Google Scholar | Busca manual residual, somente quando necessária para localizar obra já identificada ou verificar lacuna específica; não integra o corpus por recuperação automatizada. |

O panorama nacional será denominado **panorama nacional baseado no OpenAlex, complementado e avaliado por registros do Portal CAPES, SciELO, BDTD e Catálogo CAPES**. Não será descrito como reprodução ou exportação substituta do Portal CAPES.

## 3. Estado de partida

| Componente | Estado em 15/11/2026 |
|---|---|
| Protocolo | Versão 1.1, anterior à definição do OpenAlex como fonte operacional principal. |
| Base técnica anterior | 1.317 linhas: 1.060 BDTD, 103 Portal CAPES, 78 Catálogo CAPES e 76 SciELO. |
| Elegibilidade goiana anterior | 19 inclusões, 199 exclusões e 1.099 linhas sem decisão. |
| Duplicidade anterior | 40 pares confirmados; busca não encerrada. |
| Coleta OpenAlex | 12.431 registros em 125 páginas, com consulta e arquivos arquivados. |
| Conciliação OpenAlex | 689 pares candidatos com a base anterior. |
| Identidades sustentadas | 116 pares como mesma obra por DOI e metadados concordantes: 71 com Portal CAPES e 45 com SciELO. |
| Identidades em revisão | 52 pares com identificador concordante e metadados que exigem revisão; 521 pares apenas por título. |
| Prioridade goiana OpenAlex | 333 registros com sinais geográficos, dos quais 100 têm publicação informada em 2020–2026. |
| Casos goianos prioritários | Três pares com suporte preliminar aos critérios e duas dúvidas temáticas ainda não integrados. |
| Produtos | Planilha e relatório preliminares; não constituem corpus ou resultados finais. |

As bases, relatórios e produtos existentes permanecem preservados. Antes da retomada, será declarada uma única base técnica vigente e os demais arquivos serão tratados como históricos ou auxiliares.

## 4. Princípios de economia e qualidade

1. **Reutilizar antes de coletar.** Não executar nova busca ampla enquanto os conjuntos existentes não forem conciliados e triados segundo este plano.
2. **Automatizar somente regras objetivas.** Filtros temporais, identificadores, correspondências exatas, contagens e validações estruturais serão executados localmente.
3. **Reservar análise semântica.** Leitura ou processamento semântico será aplicado somente a candidatos regionais, identidades ambíguas, inclusões potenciais e casos capazes de alterar indicadores.
4. **Deduplicar antes de extrair.** Os três eixos serão extraídos por obra única incluída, evitando analisar versões duplicadas.
5. **Não processar individualmente os 12.431 registros.** O conjunto OpenAlex será filtrado, conciliado e agregado por regras; revisão individual será limitada às filas definidas neste plano.
6. **Evitar microlotes de código.** Decisões serão registradas em tabelas declarativas e integradas por fluxo reutilizável. Não criar um novo script e uma nova planilha para cada pequeno lote sem necessidade técnica real.
7. **Regenerar produtos por marco.** Planilha simplificada, gráficos e relatório serão atualizados depois do fechamento de cada corpus, não após cada decisão intermediária.
8. **Preservar incerteza.** Ausência de resumo, afiliação, termo geográfico ou correspondência não será convertida automaticamente em exclusão.
9. **Usar o mesmo denominador.** Qualquer proporção Goiás–Brasil usará o mesmo corpus, período, tipos documentais e regras de inclusão no numerador e no denominador.
10. **Não atribuir confiança não calibrada.** Verificações técnicas não serão apresentadas como validação científica independente.

## 5. Fluxo de execução

### Marco 0 — Aprovar e congelar o desenho

**Ações**

- aprovar o OpenAlex como fonte operacional principal do panorama nacional;
- versionar o protocolo, registrando consulta, campos, data de corte, data de coleta e diferenças em relação ao Portal CAPES;
- confirmar a unidade de análise como obra acadêmica única;
- confirmar que contexto em Goiás ou afiliação de autoria a instituição goiana qualificam o registro para exame regional, mantendo as duas dimensões separadas;
- declarar a base técnica vigente e os arquivos auxiliares;
- congelar novas coletas amplas até o Marco 4.

**Critério de conclusão:** regras, corpus de partida, fonte principal, fontes complementares e limitações estão aprovados e versionados.

### Marco 1 — Medir a cobertura observada do OpenAlex

Usar os conjuntos já arquivados como controles, sem nova coleta:

| Conjunto de controle | Universo disponível |
|---|---:|
| Portal CAPES regional e amostra nacional | 103 linhas |
| SciELO Brasil | 76 linhas |
| BDTD nacional e regional | 1.060 linhas |
| Catálogo CAPES temático de 2024 | 78 candidatos |

**Ações**

- resolver prioritariamente os 52 pares com identificador concordante;
- classificar cada registro de controle como `mesma obra confirmada`, `candidato em revisão`, `não recuperado no OpenAlex` ou `não verificável`;
- calcular a recuperação observada por fonte, período e tipo documental apenas sobre registros verificáveis;
- listar obras exclusivas das fontes complementares;
- não generalizar cobertura de títulos de periódicos para cobertura de obras ou da consulta temática.

**Entregável:** matriz de cobertura e sobreposição OpenAlex–fontes de controle, com denominadores e casos exclusivos.

**Critério de conclusão:** todas as correspondências por DOI ou identificador estão resolvidas ou justificadamente pendentes, e as lacunas observadas estão quantificadas.

### Marco 2 — Construir o corpus nacional baseado no OpenAlex

**Ações automáticas ou determinísticas**

- conferir unicidade dos identificadores e integridade das 125 páginas;
- aplicar o período de publicação de 01/01/2007 a 08/11/2026;
- preservar a data de coleta de 15/11 e a ressalva de que ela não reproduz o índice de 08/11;
- manter tipos acadêmicos previstos no protocolo e sinalizar tipos cuja natureza exija decisão;
- registrar ocorrência do PIBID no título, resumo e palavras-chave sem tratar a ocorrência isolada como elegibilidade final;
- deduplicar registros OpenAlex por identificador canônico e DOI;
- conciliar com as 116 identidades sustentadas e demais correspondências resolvidas;
- incorporar obras exclusivas confirmadas de Portal CAPES, SciELO, BDTD e Catálogo CAPES, preservando todas as proveniências.

**Revisão humana ou semântica limitada**

- tipos documentais ambíguos;
- ocorrências incidentais ou homônimas de PIBID;
- divergências bibliográficas que alterem a contagem de obras;
- uma amostra estratificada das decisões automáticas para verificar as regras.

Não será feita leitura qualitativa individual de todos os registros nacionais. Indicadores bibliométricos serão produzidos a partir de metadados do corpus elegível e da cobertura documentada.

**Entregável:** corpus nacional deduplicado, tabela de proveniência, relatório de cobertura e fila residual de casos não verificáveis.

**Critério de conclusão:** cada obra contabilizada possui identidade única, pertinência sustentada pelas regras aprovadas e origem rastreável; pendências residuais não são contadas silenciosamente como incluídas ou excluídas.

### Marco 3 — Fechar a revisão de escopo de Goiás

**Universo prioritário**

- registros recuperados pelas consultas regionais já executadas;
- registros das fontes existentes com sinais de contexto ou afiliação goiana;
- os 100 registros OpenAlex sinalizados com publicação em 2020–2026;
- registros identificados por nomes e variantes validadas de IES e contextos goianos;
- três pares com suporte preliminar e duas dúvidas temáticas já documentadas;
- obras exclusivas das fontes complementares identificadas no Marco 1.

**Ações**

1. deduplicar o universo regional e escolher tratamento único por obra;
2. aplicar os critérios de tema, natureza acadêmica, período e vínculo com Goiás separadamente;
3. distinguir publicação de ano de defesa; manter o critério alternativo aprovado para teses e dissertações;
4. classificar contexto goiano e afiliação goiana em campos distintos;
5. atribuir a cada obra `incluir`, `excluir` ou `pendente justificada`;
6. extrair, somente para obras incluídas, os três eixos:
   - aprendizagem da docência e identidade profissional;
   - trajetórias profissionais;
   - relações entre IES, escolas e comunidades, incluindo saberes e espaços híbridos;
7. registrar fonte consultada, síntese, trecho ou localização, estado da evidência e limites;
8. conferir todas as inclusões, duplicatas que alterem contagens e exclusões de maior risco.

**Entregável:** corpus goiano deduplicado, decisões rastreáveis e tabela completa dos três eixos para as obras incluídas.

**Critério de conclusão:** todo candidato regional tem decisão ou pendência justificada; toda obra incluída possui evidência de tema, período e vínculo com Goiás; os três eixos estão preenchidos sem transformar `não informado` em ausência do fenômeno.

### Marco 4 — Produzir indicadores e responder às questões

**Panorama nacional**

- evolução anual;
- tipos documentais;
- autorias e instituições, conforme cobertura dos campos;
- distribuição geográfica;
- redes de coautoria e colaboração somente se a qualidade e a cobertura permitirem;
- temáticas por palavras-chave ou tópicos, identificando quando a classificação for produzida pelo OpenAlex.

**Participação de Goiás**

- número e proporção de obras com afiliação goiana no corpus nacional;
- número de obras com contexto goiano, apresentado separadamente;
- instituições e autorias que se destacam, com regra explícita para coautoria e múltiplas afiliações;
- cobertura de afiliação conhecida, parcial e desconhecida.

**Revisão goiana**

- distribuição temporal, documental e institucional;
- resultados dos três eixos;
- tendências, contribuições, ausências no material consultado e lacunas investigativas;
- limites decorrentes de metadados, resumos, texto integral, data de coleta e validação.

**Regra de interpretação:** a participação de Goiás somente será calculada quando numerador e denominador derivarem do mesmo corpus nacional consolidado e das mesmas regras. Caso isso não seja possível, serão apresentados números absolutos e a limitação, sem proporção nacional.

### Marco 5 — Conferir e entregar

**Produtos mínimos**

1. planilha final simplificada com obras únicas, resultados e gráficos editáveis;
2. base técnica separada, com proveniência, decisões, evidências e pendências;
3. matriz de cobertura e sobreposição entre fontes;
4. relatório metodológico com procedimentos efetivamente realizados;
5. síntese dos resultados alinhada às seis subquestões do documento canônico;
6. pacote reproduzível com protocolo, consultas, scripts, logs e inventário dos arquivos.

**Conferências**

- reconciliar contagens entre base técnica, planilha simplificada, gráficos e relatório;
- verificar fórmulas, tabelas, filtros e integridade dos arquivos;
- conferir visualmente cada gráfico e sua nota metodológica;
- executar os testes existentes relevantes;
- registrar pendências e cobertura sem convertê-las em resultados;
- distinguir explicitamente resultados finais, parciais e não estimáveis.

**Critério de conclusão:** os produtos podem ser reconstruídos a partir dos dados e decisões arquivados, e nenhuma conclusão excede a cobertura demonstrada.

## 6. Regras de parada e de nova coleta

Nova coleta somente será autorizada quando uma lacuna:

- puder alterar materialmente uma resposta ou indicador previsto;
- não puder ser resolvida com os arquivos já arquivados;
- tiver fonte, consulta, custo e resultado esperado definidos;
- puder ser incorporada sem reiniciar todo o fluxo.

Não constituem motivo suficiente para nova coleta:

- ausência isolada de resumo;
- falta de termo geográfico literal;
- desejo de melhorar campo que não integra os entregáveis;
- disponibilidade de nova ferramenta sem lacuna metodológica correspondente;
- tentativa de alcançar completude abstrata sem denominador ou critério verificável.

Ferramentas como Zotero, Bibliometrix/Biblioshiny, VOSviewer e RAG são opcionais. Serão utilizadas somente se reduzirem trabalho necessário para um entregável já definido. Não são pré-requisitos do fechamento.

## 7. Controle do consumo de processamento

| Tipo de tarefa | Método preferencial |
|---|---|
| Integridade, filtros, datas e contagens | Scripts locais determinísticos |
| DOI, identificadores e títulos exatos | Conciliação automática com auditoria |
| Registros nacionais sem ambiguidade | Processamento em lote, sem leitura individual |
| Candidatos goianos | Regras em lote seguidas de revisão semântica direcionada |
| Duplicatas ambíguas | Revisão bibliográfica limitada aos pares candidatos |
| Extração dos eixos | Somente obras incluídas e deduplicadas |
| Síntese e redação | Depois do congelamento das contagens |
| Gráficos e planilha final | Uma geração por marco de entrega |

Qualquer etapa que proponha processar novamente todo o corpus deverá justificar qual decisão ou entregável será alterado. Resultados intermediários válidos serão reutilizados.

## 8. Riscos e salvaguardas

| Risco | Salvaguarda |
|---|---|
| Tratar OpenAlex como réplica do Portal CAPES | Descrever a mudança de fonte e medir sobreposição com conjuntos de controle. |
| Perder teses ou produção sem DOI | Manter BDTD e Catálogo CAPES como fontes complementares essenciais. |
| Contar a mesma obra várias vezes | Deduplicar antes dos indicadores e preservar todas as proveniências. |
| Usar afiliação como prova de contexto | Classificar contexto e afiliação separadamente. |
| Interpretar tópicos OpenAlex como categorias dos autores | Identificar a origem algorítmica da classificação e conferir sua adequação. |
| Comparar Goiás com denominador incompatível | Aplicar as mesmas regras e o mesmo corpus ao numerador e denominador. |
| Transformar ausência de metadado em exclusão | Usar estados `não informado`, `não verificável` e `pendente`. |
| Consumir recursos em tarefas periféricas | Aplicar as regras de parada e produzir somente indicadores ligados às questões canônicas. |

## 9. Decisões que exigem aprovação da pesquisadora

1. adoção formal do OpenAlex como fonte operacional principal do panorama nacional;
2. denominação do produto nacional e forma de relatar a substituição do Portal CAPES;
3. critérios finais de tipos acadêmicos elegíveis no OpenAlex;
4. regra para contexto ou afiliação goiana na revisão e na comparação nacional;
5. critério alternativo por ano de defesa para teses e dissertações;
6. tratamento de registros obtidos após a data de corte;
7. regra de contagem para coautoria e múltiplas afiliações;
8. alcance da validação humana ou independente antes da entrega final.

Após essas decisões, o protocolo deverá ser atualizado antes da apresentação dos resultados como finais.

## 10. Resultado esperado do realinhamento

Ao final, o projeto deverá dispor de:

- um panorama nacional reproduzível, baseado no OpenAlex e complementado pelas fontes brasileiras previstas;
- uma medida documentada da sobreposição e das lacunas entre as fontes;
- um corpus goiano deduplicado e integralmente decidido ou justificadamente pendente;
- uma análise dos três eixos canônicos restrita às evidências disponíveis;
- indicadores e gráficos com denominadores compatíveis;
- um relatório que distinga desenho pretendido, execução efetiva, cobertura e limites;
- produtos finais sem depender da exportação integral do Portal CAPES e sem atribuir ao OpenAlex equivalência não demonstrada com esse Portal.
