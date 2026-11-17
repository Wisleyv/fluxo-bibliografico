# Plano de ação para o levantamento quantitativo e bibliométrico

## Objetivo

Executar, de forma reproduzível e auditável, os dois movimentos complementares previstos em [Vaneria.txt](./Vaneria.txt): mapear a produção científica sobre o PIBID no Brasil em 2007–2026 e situar a participação de Goiás nesse cenário; e apoiar a revisão de escopo da produção referente a Goiás em 2020–2026. A revisão de escopo pode ser priorizada operacionalmente, sem substituir o levantamento nacional. A automação deve apoiar a coleta, a organização e o processamento dos registros sem substituir a validação metodológica e a triagem humana.

Este plano operacionaliza o documento canônico e complementa [Projeto Bibliométrico.md](./Projeto%20Bibliom%C3%A9trico.md), [Fase técnica.md](./Fase%20t%C3%A9cnica.md) e [Automação de coleta.md](./Automa%C3%A7%C3%A3o%20de%20coleta.md), observadas as decisões de viabilidade e uso responsável registradas aqui. Os ajustes metodológicos propostos em 12 de novembro de 2026 não alteram retroativamente o [protocolo aprovado para os pilotos](./Protocolo%20de%20busca%20bibliom%C3%A9trica.md); devem ser discutidos com a pesquisadora e, quando confirmados, incorporados a uma nova versão do protocolo antes de conclusões finais.

### Interpretação do objetivo e limites da evidência

- A comparação nacional situa a produção com autoria vinculada a instituições goianas **dentro** da produção nacional sobre o PIBID; não pressupõe comparar apenas artigos ou somente estudos realizados em Goiás. O protocolo vigente inclui todos os tipos de produção acadêmica disponíveis. Apresentar também resultados por tipo documental, evitando comparar conjuntos heterogêneos como se fossem apenas artigos.
- A revisão de escopo de 2020–2026 trata da produção **referente ao contexto de Goiás**. Afiliação goiana e contexto do estudo são dimensões distintas, que podem coincidir ou não; sua relação exata com a elegibilidade da revisão deve ser definida com a pesquisadora, sem presumir que uma implique a outra.
- O documento canônico prevê leitura de títulos, resumos e palavras-chave após a recuperação e não estabelece texto integral disponível como critério obrigatório de inclusão. Tampouco garante que resumos bastem para responder a todas as perguntas qualitativas. Metadados podem sustentar indicadores com cobertura adequada; título, resumo e palavras-chave podem apoiar triagem e descrição temática, mas normalmente não permitem verificar de modo completo métodos, contexto, resultados ou ausência de evidências.
- Não excluir automaticamente por paywall, ausência de texto integral, resumo ou sinal geográfico. Registrar informação insuficiente e decidir com a pesquisadora se o texto integral ou outra fonte confiável é necessário para cada caso ou pergunta. Na ausência de evidência suficiente, manter a questão ou decisão pendente, sem transformar ausência de informação em ausência do fenômeno.
- RAG é um recurso opcional, não exigido pelo documento canônico nem pré-requisito da entrega. Qualquer uso deverá identificar a versão e o trecho-fonte, distinguir resumo de texto integral e exigir conferência humana; acesso, processamento e compartilhamento dependem das permissões e condições aplicáveis. Não contornar paywalls nem presumir autorização para distribuir arquivos ou enviar conteúdo a serviços externos.

## Princípios de execução

1. **Validar antes de automatizar:** confirmar disponibilidade, cobertura, campos, filtros, paginação e condições de uso de cada fonte por meio de um piloto.
2. **Separar fontes e coletores:** cada fonte terá um procedimento independente; os resultados serão integrados somente depois da coleta.
3. **Preservar os dados de origem:** manter arquivos brutos imutáveis e registrar a transformação que produziu cada conjunto tratado.
4. **Manter o processo reproduzível:** registrar consultas, filtros, datas, versões de ferramentas e decisões de inclusão/exclusão.
5. **Usar automação responsável:** preferir APIs, protocolos e exportações oficiais. Não contornar controles de acesso, autenticação, CAPTCHA, limites técnicos ou termos de uso.
6. **Separar recuperação de seleção:** preservar a busca nacional e as buscas regionais complementares como procedimentos distintos; a revisão goiana pode avançar primeiro, sem tomar seus resultados por um corpus nacional completo.
7. **Manter revisão humana:** validar duplicatas ambíguas, pertinência temática, afiliação institucional e classificação dos documentos.

## Escopo das fontes

| Fonte | Papel no levantamento | Procedimento inicial |
|---|---|---|
| SciELO | Base principal de artigos, conforme a cobertura disponível | Piloto para verificar API, sintaxe de busca, campos, paginação e limites; automatizar somente após validação |
| BDTD | Base de teses e dissertações | Piloto OAI-PMH para verificar endpoint, conjuntos, metadados e cobertura; filtrar localmente se não houver busca temática adequada |
| Catálogo de Teses e Dissertações da CAPES | Fonte distinta para teses e dissertações | Testar busca e exportação próprias; não presumir que o procedimento do Portal de Periódicos também se aplique ao catálogo |
| Portal de Periódicos CAPES | Fonte de artigos e outros documentos cobertos pelo Portal | Priorizar busca e exportação oficial; avaliar automação de navegador apenas para tarefas estáveis e permitidas |
| Google Scholar | Busca complementar para localizar registros não encontrados nas fontes principais | Busca complementar documentada, sem depender de raspagem que contorne bloqueios; registrar limitações e procedimento utilizado |

## Etapas de execução

### Etapa 1 — Congelar o protocolo de busca

**Status: concluída em 8 de novembro de 2026.** O protocolo aprovado para orientar os pilotos está em [Protocolo de busca bibliométrica.md](./Protocolo%20de%20busca%20bibliom%C3%A9trica.md), versão 1.0. A sintaxe literal, os campos efetivamente pesquisáveis e os filtros de cada interface serão confirmados na Etapa 2, sem alterar silenciosamente o escopo aprovado.

**Ações**

- Confirmar o período de publicação (2007–2026) e registrar a data-limite da coleta. Como 2026 está em andamento, identificar explicitamente a cobertura parcial desse ano.
- Definir uma consulta nacional baseada em `PIBID OR "Programa Institucional de Bolsa de Iniciação à Docência"` e adaptar sua sintaxe aos recursos de cada fonte.
- Definir quais campos serão pesquisados em cada fonte (título, resumo e palavras-chave quando disponíveis).
- Planejar consultas complementares para Goiás, incluindo `Goiás`, `goiano` e `goiana`, nomes de IES e contextos goianos. Essas consultas complementam — não substituem — a busca nacional.
- Registrar critérios de inclusão e exclusão: todos os tipos de produção acadêmica e idiomas disponíveis nas fontes; pertinência substantiva ao PIBID; exclusão de registros fora do período, duplicatas (preservando a proveniência) e materiais não acadêmicos.

**Entregável:** protocolo versionado com consultas por fonte, filtros, critérios e data de corte.

**Critério de conclusão:** outra pessoa consegue repetir a consulta temática de referência, compreender como adaptá-la por fonte e identificar período, campos pretendidos, escopo documental, idiomas, critérios e limitações pendentes de validação técnica.

### Etapa 2 — Executar pilotos de viabilidade por fonte

**Status: concluída em 8 de novembro de 2026.** A avaliação e as decisões para as cinco fontes estão registradas em [Matriz de viabilidade dos pilotos.md](./Matriz%20de%20viabilidade%20dos%20pilotos.md). A BDTD teve busca, filtro temporal e CSV assistido validados; no Portal CAPES, consulta booleana, filtro temporal e arquivo RIS de amostra foram validados, mas o limite de exportação e o fluxo completo com CAFe devem ser verificados antes da coleta integral. SciELO e Google Scholar ficam sem coleta automatizada; os dados abertos da CAPES ficam como fonte auxiliar, condicionados a leitura local e harmonização. As condições operacionais ainda não verificadas são pré-requisitos para cada coleta, não pressupostos de um coletor de produção.

**Ações**

- Executar e registrar uma busca pequena por fonte, distinguindo as duas interfaces CAPES e mantendo a consulta literal.
- Validar exportação CSV da BDTD, consulta/filtro e geração amostral RIS/BIBTEX no Portal CAPES, busca assistida SciELO, amostra de esquema dos arquivos abertos do Catálogo CAPES e restrições do Google Scholar.
- Atribuir a cada fonte um procedimento explícito (automatizado, exportação/importação assistida ou complementar/excluída do corpus principal) e registrar as verificações ainda necessárias antes de qualquer lote.

**Entregável:** matriz de viabilidade, uma linha por fonte, com método confirmado, metadados, limitações e decisão (automatizar, exportar assistidamente ou não utilizar).

**Critério de conclusão:** cada fonte possui uma decisão e um procedimento reprodutível, com limitações e pré-condições explícitas; nenhum coletor de produção é iniciado com pressupostos não verificados sobre API, endpoint, filtros ou exportação.

### Etapa 3 — Definir o esquema comum e a estrutura de armazenamento

**Status: concluída em 8 de novembro de 2026.** O dicionário de dados, as regras de rastreabilidade e a estrutura de diretórios estão documentados em [Esquema de dados e estrutura de armazenamento.md](./Esquema%20de%20dados%20e%20estrutura%20de%20armazenamento.md); as pastas base em `dados\` também foram criadas. A validação dos dois arquivos RIS do Portal CAPES confirmou que são cópias idênticas de um único registro; a matriz de viabilidade foi atualizada com essa evidência. A criação dos coletores e o processamento integral dos dados continuam reservados às Etapas 4 e 5.

**Ações**

- Definir campos comuns: fonte, identificador original, tipo de documento, título, autores, ano de publicação, resumo, palavras-chave, instituição/afiliação, programa de pós-graduação, URL/DOI e data da coleta.
- Preservar campos específicos de cada fonte e o registro bruto original, mesmo quando não houver correspondência no esquema comum.
- Estabelecer diretórios separados para dados brutos, dados normalizados, resultados de triagem e saídas analíticas.
- Adotar nomes de arquivos previsíveis que identifiquem fonte, consulta e data da coleta; não sobrescrever arquivos brutos.
- Definir um formato tabular de intercâmbio (CSV em UTF-8 ou formato equivalente validado no piloto) e manter exportações RIS/BibTeX originais quando fornecidas.

**Entregável:** dicionário de dados e estrutura de arquivos documentados.

**Critério de conclusão:** todos os campos têm significado e formato definidos, e cada registro pode ser rastreado até sua fonte e arquivo bruto.

### Etapa 4 — Implementar a coleta incremental

**Status: em andamento.** A ferramenta [capture_collection.py](./scripts/capture_collection.py) registra exportações oficiais, preserva os arquivos brutos, calcula SHA-256, registra execução/inventário e sinaliza duplicatas e falhas. Os quatro lotes regionais RIS do Portal CAPES foram arquivados: 30/30/30/12 registros, totalizando 102 registros com identificadores RIS e sem IDs repetidos entre páginas. O usuário confirmou que a sessão do Portal estava autenticada via CAFe e que conferiu os resultados exportados com a interface; informou também que 101 dos 102 resultados são de acesso aberto. Essa classificação foi registrada como observação manual, pois o RIS não contém campo que a permita validar automaticamente. O arquivo adicional `Periodicos-CAPES-RIS-5.ris` tem 30 registros e SHA-256 idêntico ao lote da página 1 já arquivado; foi registrado como duplicata, não como lote adicional nem como exportação dos 102 resultados completos. A paginação de 30/30/30/12 e os 102 IDs únicos continuam cobrindo os resultados regionais. A exportação regional da BDTD foi recebida e arquivada byte a byte como ZIP; a integridade do arquivo foi confirmada e o CSV interno contém 42 linhas e 25 colunas, sem linhas integralmente duplicadas. O CSV regional permanece sujeito à triagem: há um título repetido e o campo ARK está como “Não informado pela instituição” nos 42 registros. O CSV anual CAPES de 2024 também foi recebido via navegador, arquivado byte a byte (506.649.988 bytes; SHA-256 registrado no inventário) e percorrido em streaming: 59 colunas, delimitador `;` e 91.833 registros. A leitura exploratória encontrou 78 registros com termos temáticos e 3 com sinal regional combinado; na Etapa 5, o arquivo foi processado como `cp1252-replace`; 79 bytes indefinidos foram sinalizados em 12 registros, sem alterar o bruto. A filtragem por termos geográficos combinada ao tema é útil para priorizar, mas não será usada para excluir automaticamente os demais registros temáticos. Na SciELO, a exportação manual RIS da coleção Brasil foi arquivada: 76 registros, IDs únicos, 68 de 2012–2024 e 8 de 2025–2026. O usuário confirmou aplicar o protocolo geral de 2007–2026; os oito registros recentes permanecem no escopo. A exportação não contém registros anteriores a 2012, intervalo observado nesta busca, sem alterar o bruto. A validação do encoding e a extração/normalização local foram concluídas na Etapa 5; permanecem pendentes a decisão sobre exportar a busca nacional do Portal CAPES e, se necessário, testar limite superior a 30 por lote.

**Ações**

- Usar `python .\scripts\capture_collection.py register` para arquivar cada exportação aprovada, passando fonte, consulta literal, filtros, contagens observadas e arquivo recebido.
- Obter os modelos com `python .\scripts\capture_collection.py queries`; executar primeiro a busca nacional e, em seguida, a consulta complementar regional (ou variantes validadas por fonte), preservando a consulta literal efetivamente aceita.
- Usar `python .\scripts\capture_collection.py record-search` para registrar resultados da interface e tentativas sem exportação; manter campos de contagem vazios quando desconhecidos e nunca confundir total da interface com quantidade exportada.
- Manter busca/exportação CAPES assistida pelo navegador institucional; a sessão CAFe e a correspondência da busca regional foram confirmadas pelo usuário. O utilitário arquiva os arquivos, não autentica nem dispara consultas no site.
- Continuar usando CSV assistido da BDTD; não usar o endpoint OAI testado, que respondeu 404.
- Manter SciELO como coleta manual assistida: o RIS já foi exportado e arquivado. Não automatizar a fonte. Na normalização, manter os 76 registros no período geral aprovado de 2007–2026, incluindo os oito de 2025–2026; registrar que a exportação observada começa em 2012.
- Para dados abertos CAPES, usar `download-capes-open-data` somente com URL HTTPS oficial, limite explícito `--max-bytes` e tamanho esperado conhecido quando disponível; validar amostra, formato e esquema antes de baixar outros períodos. O CSV de 2024 já está preservado; em sua leitura local, filtrar em streaming por termos do PIBID combinados a descritores geográficos textuais ou `SG_UF_IES=GO`. Usar esse resultado para priorizar revisão, não para excluir automaticamente registros temáticos sem sinal geográfico.
- Para viabilizar a comparação nacional, completar a exportação da busca nacional do Portal CAPES por lotes oficiais conferidos, conforme disponibilidade e condições de uso; registrar totais da interface, lotes recebidos, lacunas e data. Avaliar e documentar, para as demais fontes e anos, a cobertura efetivamente obtida e a viabilidade de coleta complementar, sem presumir cobertura nacional integral a partir do arquivo CAPES de 2024 ou da busca SciELO restrita à coleção Brasil. Registrar como limitação qualquer lacuna não resolvida.
- Complementar a identificação goiana com buscas documentadas por nomes e variantes de IES e contextos, inclusive estudos sem descritores geográficos nos metadados; usar o Google Scholar apenas como busca manual complementar.
- Registrar cada tentativa, inclusive falha e conteúdo duplicado; não sobrescrever brutos e conferir o inventário para retomar sem perder arquivos. Na consulta regional do Portal, registrar a classificação de acesso aberto separadamente dos metadados RIS; a observação atual é 101/102 segundo conferência manual do usuário.

**Entregável:** arquivos brutos por fonte e logs de execução.

**Critério de conclusão:** o fluxo suportado por cada fonte pode ser repetido ou retomado, resultados parciais e falhas são identificáveis, e os arquivos brutos permanecem imutáveis. O download auxiliar CAPES pode ser retomado quando o servidor aceita `Range`, respeita limite configurado e registra a falha mantendo o parcial em `dados\staging\`; uma resposta sem suporte a `Range` reinicia o arquivo desde o início. Coletores automáticos específicos só são acrescentados após validar a via oficial correspondente.

### Etapa 5 — Normalizar e validar os metadados

**Status: concluída tecnicamente em 8 de novembro de 2026; inconsistências de conteúdo permanecem para revisão.** Foi implementado [normalize_collection.py](./scripts/normalize_collection.py), que percorre os arquivos registrados no inventário e gera CSVs novos em `dados\normalizados\`, sem modificar os brutos. A rotina usa a biblioteca padrão do Python e processamento em streaming; não requer pandas. A geração final `20261108T205625-0300__828bdff7` normalizou 93.072 registros: BDTD 1.060, Portal CAPES 103, Catálogo CAPES 91.833 e SciELO 76. As nove entradas de arquivo tiveram contagens exportadas correspondentes quando conhecidas; não há registros sem título/ano nem anos inválidos/fora de 2007–2026. A geração é reproduzível por arquivo/registro, preserva campos não mapeados em `source_metadata_json` e mantém ano de publicação separado de ano de defesa.

O CSV CAPES foi lido como `cp1252-replace`: 79 bytes indefinidos do codec foram representados por `U+FFFD` em 12 registros e sinalizados por registro; o bruto não foi alterado. O BDTD nacional decodifica como UTF-8, mas contém 42 caracteres de controle C1 em 17 registros: 41 em resumos e um no título de um desses registros; também foram sinalizados sem correção automática. Há 1.004 registros BDTD sem identificador persistente/ARK informado (962 na exportação nacional e 42 na regional). A tabela `mapeamento_instituicoes__20261108T205625-0300__828bdff7.csv` lista 606 nomes institucionais distintos como candidatos, todos pendentes de validação; por isso `institution_normalized` continua vazio. A conferência final confirmou 93.072 IDs internos únicos, JSON válido, integridade dos nove arquivos brutos e zero divergências de contagem.

**Ações**

- Executar `python .\scripts\normalize_collection.py` para processar os arquivos do inventário; cada geração produz registros normalizados, relatório de qualidade, inconsistências por registro e candidatos a correspondência institucional, todos com o mesmo identificador de geração.
- Preservar os arquivos brutos sem alteração. O processamento usa CSV em streaming e lê cada membro CSV do ZIP BDTD como derivação, sem substituir o ZIP.
- Uniformizar codificação, espaços externos, campos vazios, listas e formatos de ano, sem inferir valores ausentes. Para o CSV CAPES, se UTF-8 e Windows-1252 estrito falharem por bytes indefinidos, usar Windows-1252 com substituição explícita e revisar a contagem de caracteres substituídos; não aplicar Latin-1, que converte pontuação Windows em caracteres de controle.
- Conferir a contagem processada contra `records_exported` quando essa contagem estiver registrada; examinar registros sem título/ano, ano inválido/fora do período e campos originais não mapeados.
- Criar uma tabela inicial de correspondência para variantes de nomes institucionais; manter o valor original e o valor normalizado. A saída da Etapa 5 contém 606 nomes únicos com normalização pendente, sem presumir equivalências.
- Manter `institution_normalized` vazio até validar uma correspondência; produzir relatório de qualidade por arquivo e inconsistências por registro, sem excluir itens.
- Manter os tipos documentais diferenciados (artigo, tese, dissertação e outros).

**Entregável:** [registros normalizados](./dados/normalizados/registros_normalizados__20261108T205625-0300__828bdff7.csv), [relatório de qualidade](./dados/normalizados/relatorio_qualidade__20261108T205625-0300__828bdff7.csv), [inconsistências por registro](./dados/normalizados/inconsistencias__20261108T205625-0300__828bdff7.csv) e [candidatos de mapeamento institucional](./dados/normalizados/mapeamento_instituicoes__20261108T205625-0300__828bdff7.csv). A execução está registrada em `dados\logs\normalizacoes.csv`.

**Critério de conclusão:** transformações são reproduzíveis, valores originais continuam disponíveis e inconsistências não são descartadas sem registro. As contagens foram reconciliadas e os problemas residuais estão identificados para revisão. A geração final é a autoridade; gerações anteriores foram mantidas para auditoria e marcadas como substituídas. A normalização não realiza deduplicação nem triagem temática; a próxima etapa é a Etapa 6.

### Etapa 6 — Deduplicar e realizar a triagem temática

**Retomada em 12 de novembro de 2026 — em andamento:** o usuário determinou priorizar a revisão de escopo de Goiás para 2020–2026 no trabalho a seguir. As planilhas de 10 de novembro em `dados\triagem\` foram preservadas sem alterações: a [versão corrigida](./dados/triagem/triagem_revisao_escopo_goias__revisao_capES_36__20261110_corrigido.xlsx) contém 1.317 candidatos, pré-triagem, 114 grupos candidatos de duplicatas e revisão informativa de 36 registros CAPES. As decisões de título/resumo continuam `Pendente` e as duplicidades `Não verificada`; os sinais não são decisões. O levantamento bibliométrico nacional e o protocolo geral 2007–2026 permanecem preservados; a priorização da revisão de escopo não altera retroativamente seu período.

Como primeiro incremento, [audit_character_issues.py](./scripts/audit_character_issues.py) localiza as ocorrências sinalizadas nos arquivos de origem, verifica seus hashes e identificadores e produz uma [auditoria para revisão](./dados/triagem/auditoria_caracteres__20261112T103440254440-0300__e08ff020.csv), sem corrigir texto automaticamente. Os 17 registros BDTD afetados estão na planilha de 1.317 candidatos; os 12 registros CAPES com substituições não estão nessa planilha. O aviso genérico presente nos 78 candidatos CAPES da planilha não significa que cada candidato sofreu substituição. A auditoria conserva também os 12 casos fora da planilha para a qualidade do levantamento geral.

A [cópia com filtros e painéis ajustados](./dados/triagem/triagem_revisao_escopo_goias__revisao_capES_36__20261110_filtros_paineis_20261112.xlsx) preserva a planilha anterior e a cópia recuperada pelo Excel. Foram removidos os filtros de nível de planilha sobrepostos aos filtros das tabelas nas abas `Triagem Goiás` e `Revisão CAPES 36`, e o congelamento da aba principal passou a abranger somente o cabeçalho. A sobreposição é uma hipótese para o reparo informado pelo Excel, não uma causa confirmada. A integridade do arquivo, os valores e fórmulas e as três tabelas foram verificados; uma abertura em Excel em leitura preservou as três tabelas, e o filtro da tabela principal retornou 1.060 registros BDTD. Essa verificação não confirma a ausência de todos os possíveis avisos de reparo, pois os alertas estavam desativados.

**Ações**

- Importar os registros para o Zotero para apoiar a revisão humana e a deduplicação, mantendo os arquivos brutos e a tabela normalizada como registros mestres.
- Deduplicar primeiro por identificadores persistentes quando disponíveis e, em seguida, por combinação de título, autoria e ano.
- Revisar manualmente correspondências incertas; preservar a relação entre o registro consolidado e todas as fontes de origem.
- Triar títulos, resumos e palavras-chave segundo os critérios do protocolo; registrar decisão e motivo de exclusão.
- Distinguir falta de informação de exclusão: registrar a evidência consultada e manter pendentes os casos que não permitam decidir. A indisponibilidade de texto integral, por si só, não é motivo automático de exclusão.
- Consolidar a amostra nacional e manter separadamente os registros incluídos, excluídos e pendentes de decisão.

**Entregável:** corpus nacional deduplicado e planilha de triagem com decisões rastreáveis.

**Critério de conclusão:** cada registro tem estado de triagem, duplicatas são justificáveis e registros de origem permanecem recuperáveis.

### Etapa 7 — Identificar e validar o recorte de Goiás

**Ações**

- Aplicar descritores regionais aos registros do corpus nacional.
- Identificar IES e afiliações goianas por meio de uma tabela de nomes e variantes institucionais validada.
- Revisar o texto disponível (resumo, palavras-chave e, quando necessário, documento) para localizar estudos sobre Goiás que não indiquem o estado em campos bibliográficos.
- Registrar separadamente, com evidência, fonte e estado confirmado/negativo/não informado ou não verificável, a afiliação dos autores a IES goianas e o contexto de realização do estudo em Goiás. Permitir ambas as dimensões e múltiplas afiliações; não inferir afiliação a partir do contexto nem contexto a partir da afiliação, do endereço da editora ou de uma menção isolada.
- Para a comparação, definir com a pesquisadora a regra de atribuição de afiliação e o tratamento de coautoria, múltiplos vínculos, vínculos ausentes e variação temporal. Para a revisão de escopo, acordar a regra de elegibilidade do contexto e como tratar casos com vínculo goiano, mas contexto fora do estado ou desconhecido. Registrar decisões e justificativas sem excluir automaticamente casos ambíguos.
- Manter consultas regionais complementares e registrar quais registros foram encontrados por elas.

**Entregável:** classificações separadas de afiliação e contexto, regras acordadas e lista rastreável de casos resolvidos e pendentes.

**Critério de conclusão:** a classificação regional é consistente, justificável e não depende exclusivamente da presença da palavra “Goiás” nos metadados.

### Etapa 8 — Classificar variáveis e preparar a análise bibliométrica

**Ações**

- Consolidar ano, tipo documental, autoria, instituição, UF/região, programa de pós-graduação e palavras-chave.
- Documentar unidade de análise e regras de contagem, especialmente para coautoria, múltiplas instituições e registros sem afiliação. Para a participação institucional goiana, usar como denominador o corpus nacional elegível e deduplicado no mesmo período; informar também número e proporção com afiliação completa, parcial ou desconhecida, conforme a informação verificável, e evitar tratar desconhecido como não goiano. Definir contagem inteira ou fracionada antes de comparar; explicitar que totais por instituição ou UF podem se sobrepor.
- Apresentar separadamente a comparação 2007–2026 e a revisão de escopo 2020–2026; quando comparar períodos ou tipos documentais, usar denominadores equivalentes e reportar lacunas de fontes e campos. Grupos de pesquisa e redes só serão descritos quando houver dados suficientes e vínculos verificáveis; não inferir grupo de pesquisa apenas de coautoria ou instituição.
- Preparar arquivos de entrada para Bibliometrix/Biblioshiny, mapeando explicitamente os campos para as tags esperadas (por exemplo, autores, título, ano, resumo e palavras-chave).
- Verificar uma amostra da conversão antes de gerar indicadores.
- Utilizar VOSviewer como complemento de visualização quando o formato de entrada e a análise proposta forem compatíveis.

**Entregável:** conjunto analítico documentado, tabelas de indicadores e arquivos de entrada validados.

**Critério de conclusão:** contagens e campos importados são conferidos contra a amostra triada e as regras de análise estão registradas.

### Etapa 9 — Produzir resultados e fechar a coleta

**Ações**

- Gerar volume e evolução temporal (2007–2026), produtividade de autores e instituições, distribuição geográfica e tipos documentais.
- Construir redes de coautoria e colaboração institucional e análises de coocorrência de palavras-chave quando a qualidade dos metadados permitir.
- Produzir gráficos e mapas do corpus nacional e do recorte goiano, indicando denominadores e limitações.
- Registrar a data final da coleta, cobertura incompleta de 2026, lacunas das fontes, decisões manuais e limitações de comparabilidade.
- Distinguir resultados provisórios dos finais e relatar cobertura de ano, autoria, afiliação, resumo e palavras-chave, além de decisões pendentes. Não apresentar contagem de registros recuperados como quantidade de estudos únicos ou produção nacional total.
- Arquivar protocolo, consultas, arquivos brutos, dados tratados, scripts, logs e produtos analíticos.

**Entregável:** pacote de resultados reproduzível e relatório metodológico de cobertura e limitações.

**Critério de conclusão:** os resultados podem ser reconstruídos a partir dos dados e das decisões arquivados.

### Etapa 10 — Preparar a entrega e apoiar a revisão de escopo

**Status: em andamento em 12 de novembro de 2026; nenhum pacote final ou corpus elegível foi constituído.** O [pacote preliminar](./dados/entregas/pacote_preliminar_20261112/LEIA-ME%20-%20orienta%C3%A7%C3%B5es%20para%20a%20pesquisadora.md) foi simplificado a pedido do usuário: contém o guia vinculado a `Vaneria.txt`, o documento canônico e uma única planilha de triagem e análise. A planilha mantém 1.317 candidatos, 36 sinalizados para o piloto, os três eixos e candidatos a duplicidade, sem expor IDs de execução, caminhos de arquivos brutos ou planilhas técnicas. Para identificar cada registro usa os oito primeiros caracteres do UUID da planilha de origem; os prefixos foram conferidos como únicos no conjunto atual, preservando a correspondência com a versão completa em `dados\triagem\`. Os arquivos brutos, logs, auditoria, protocolo e matriz continuam no projeto, fora da entrega.

A [verificação técnica anterior do piloto](./dados/triagem/relatorio_teste_piloto_pacote_20261112.md) registrou os 36 IDs e o fluxo fictício na primeira versão. A versão simplificada foi comparada aos registros e decisões anteriores, inclusive os 36 candidatos e 108 linhas de eixos; tabelas, listas e preenchimento fictício foram conferidos programaticamente. Nenhuma verificação substitui a revisão humana dos estudos ou teste interativo desta nova cópia no Excel. A comparação anterior identificou divergência entre dois sinais históricos de outros estados (3 no resumo de status e 2 por registro), pendente de revisão. Os resumos e textos integrais dos 36 não acompanham o pacote. A pesquisadora ainda precisa testar o material e registrar suas decisões; as regras propostas também aguardam acordo e eventual atualização do protocolo.

**Ações**

- Preparar uma versão identificada e datada do pacote, com sumário acessível para a pesquisadora: objetivo dos dois movimentos, conteúdo e finalidade de cada arquivo, origem e data de corte, instruções de abertura, filtros e preenchimento, significados dos estados e campos, exemplos de decisões e como registrar justificativas e dúvidas. Preservar os códigos dos registros e os arquivos originais ao trabalhar em cópia.
- Incluir somente o necessário à pesquisadora; manter auditoria de caracteres, inventário, consultas, linhagem, dados normalizados e protocolo no projeto para rastreabilidade. Indicar na entrega a cobertura, as limitações e as contagens de registros, não de estudos únicos.
- Informar que os 1.317 candidatos atuais não são um corpus selecionado, que os 114 grupos são candidatos a duplicidade e que os 36 registros CAPES são apenas um lote piloto, não uma amostra representativa. A cobertura nacional está incompleta, inclusive no Portal CAPES e no Catálogo CAPES aberto; faltam buscas por IES e contextos. Esclarecer que o ano de defesa/titulação não substitui automaticamente o ano de publicação e que 2026 é parcial.
- Definir com a pesquisadora um formulário ou tabela de extração por estudo para os três eixos canônicos — aprendizagem da docência, trajetórias profissionais e relações entre IES, escolas e comunidades — contemplando identidade profissional, saberes e espaços híbridos. Para cada achado, registrar fonte consultada, trecho ou localização, tipo de evidência, interpretação e limites; usar estados como presente, não informado, não verificável e pendente, sem inferir ausência a partir de resumo incompleto.
- Registrar separadamente disponibilidade do resumo, localização e acesso autorizado ao texto integral e adequação da evidência a cada pergunta. Quando o resumo for suficiente para uma decisão ou descrição, registrar a base dessa decisão; quando não for, buscar acesso legal institucional ou outra fonte confiável e manter pendente o que não puder ser verificado. Não prometer nem incluir textos integrais que não tenham sido localizados ou cuja distribuição não esteja autorizada.
- Se a pesquisadora optar por RAG, preparar somente depois um conjunto autorizado, identificar documentos e nível de acesso, registrar método e versão da indexação e exigir citações verificáveis e conferência humana. Explicitar que respostas baseadas apenas em resumos não equivalem à análise do texto integral.
- Testar o pacote e suas instruções com um lote piloto dos 36 registros CAPES, sem supor sua elegibilidade: revisar duplicatas, ano, pertinência ao PIBID, afiliação, contexto e suficiência da evidência. Registrar dificuldades e decisões, ajustar o fluxo e então aplicá-lo aos demais candidatos, preservando o processo nacional em paralelo.

**Entregável:** pacote preliminar versionado para triagem e orientação; posteriormente, conjunto revisado e documentação de extração e limitações, mediante as decisões da pesquisadora.

**Critério de conclusão:** a pesquisadora consegue localizar e compreender os materiais, registrar e devolver decisões rastreáveis e distinguir candidatos, evidências disponíveis e pendências. A conclusão do pacote não implica corpus final nem validação de todas as perguntas qualitativas.

## Sequência recomendada para as próximas ações

1. Discutir com a pesquisadora as regras propostas de afiliação e contexto, evidência suficiente e extração; versionar o protocolo quando aprovadas, preservando o histórico.
2. Preparar e testar um pacote preliminar acessível com a planilha existente e suas limitações; conduzir o piloto dos 36 registros CAPES com decisões humanas rastreáveis.
3. Ajustar o procedimento e avançar na triagem e nas buscas complementares por IES e contextos goianos, sem excluir automaticamente registros com informações ausentes.
4. Em paralelo, completar ou delimitar e documentar a coleta nacional por fonte e período, incluindo a exportação nacional do Portal CAPES; normalizar e integrar novos lotes sem sobrescrever os dados anteriores.
5. Deduplicar e validar os corpora e campos, calcular indicadores somente com denominadores e cobertura explícitos e apoiar a extração qualitativa conforme a evidência disponível.
6. Entregar versões atualizadas do pacote, com instruções e limitações; declarar resultados finais somente após revisão e documentação das lacunas remanescentes.

## Registro mínimo por execução de coleta

Para cada fonte e consulta, registrar:

- identificador da execução;
- fonte e interface utilizada;
- consulta exata e campos pesquisados;
- filtros aplicados e período de publicação;
- data e hora da coleta;
- formato e nome dos arquivos brutos;
- quantidade de registros obtidos;
- erros, páginas/lotes incompletos e limitações observadas;
- versão do script ou procedimento manual;
- responsável pela validação e observações.
