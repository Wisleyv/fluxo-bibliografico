# Esquema de dados e estrutura de armazenamento

**Etapa:** 3 — Definir o esquema comum e a estrutura de armazenamento  
**Versão:** 1.8  
**Data:** 8 de novembro de 2026  
**Status:** aprovado; Etapa 5 executada e validada, com inconsistências de conteúdo sinalizadas para revisão.

## 1. Princípios

- Manter os arquivos originais de cada fonte sem alteração. A normalização gera novos arquivos e nunca substitui os brutos.
- Uma linha da tabela normalizada representa um registro recuperado de uma fonte. Registros que possam ser duplicatas permanecem separados até a Etapa 6.
- Registrar a execução que recuperou cada registro e o caminho relativo do arquivo bruto correspondente.
- Preservar campos originais específicos da fonte no arquivo bruto e, quando não couberem no esquema comum, no campo `source_metadata_json`.
- Não inferir valores ausentes. Distinguir ano de publicação de ano de defesa, e instituição de afiliação ou local onde o estudo foi realizado.
- O esquema não presume que todas as fontes forneçam todos os campos.

## 2. Arquivos e diretórios

Estrutura relativa à raiz do projeto:

```text
dados\
  brutos\
    portal-capes\
    bdtd\
    scielo\
    catalogo-capes\
  staging\
    catalogo-capes\
  normalizados\
  logs\
  triagem\
  analises\
```

- `brutos\{fonte}\`: exportações originais exatamente como obtidas, inclusive ZIP, CSV, RIS, BibTeX e arquivos de dados abertos. Quando uma exportação vier compactada, preservar o ZIP; extrações para inspeção são derivadas e não substituem o bruto.
- `staging\catalogo-capes\`: arquivos recebidos ainda não registrados e parciais de downloads interrompidos; não usar como entrada analítica. `register` preserva o arquivo de entrada no lugar e cria uma cópia bruta; o comando de download direto remove seu parcial somente depois de arquivar com sucesso a cópia bruta.
- `normalizados\`: tabelas comuns derivadas dos brutos; cada geração deve ser identificada por execução ou versão e não sobrescrever a anterior.
- `logs\execucoes.csv`: manifesto das consultas e importações executadas.
- `logs\arquivos.csv`: inventário dos arquivos brutos, seus caminhos, formatos e, quando calculado, checksum SHA-256.
- `logs\normalizacoes.csv`: histórico das gerações normalizadas, estado, entradas e saídas.
- `triagem\`: decisões humanas por registro, separadas dos metadados bibliográficos.
- `analises\`: tabelas agregadas e produtos analíticos derivados; não são fonte de verdade para os registros.

Nomear arquivos brutos como `{fonte}__{consulta-id}__{data-hora-com-fuso}__{formato}.{ext}`. Exemplo: `portal-capes__busca-nacional__20261108T112000-0300__RIS.ris`. Registrar a consulta completa no manifesto, não no nome do arquivo. Um novo download ou uma nova execução recebe um novo arquivo; nunca sobrescrever uma exportação anterior.

## 3. Tabela normalizada de registros

Arquivo de intercâmbio: CSV UTF-8 sem BOM, delimitado por vírgula e com cabeçalho. Seguir o escape CSV para vírgulas, aspas e quebras de linha. Campos que contêm listas usam JSON válido em uma única célula, evitando separadores ambíguos. Valores não disponíveis ficam vazios; não usar textos como `N/A` como substitutos.

Os nomes dos campos normalizados usam identificadores técnicos estáveis; as descrições e os valores do estudo permanecem em português.

| Campo | Tipo/forma | Definição e regra |
|---|---|---|
| `record_id` | UUID | Identificador interno persistente atribuído na primeira importação; preservar em reprocessamentos do mesmo registro de origem. |
| `source` | texto controlado | Fonte de coleta: `portal-capes`, `bdtd`, `scielo`, `catalogo-capes` ou `google-scholar`. Scholar só poderá registrar buscas exploratórias manuais e não implica inclusão no corpus principal. |
| `source_record_id` | texto | Identificador original fornecido pela fonte, se houver; não criar identificador com aparência de identificador da fonte. |
| `source_run_id` | texto | Chave para a execução registrada em `logs\execucoes.csv`. |
| `raw_file` | caminho relativo | Caminho para o arquivo bruto que contém o registro. |
| `document_type_original` | texto | Tipo documental tal como informado pela fonte. |
| `document_type_normalized` | texto controlado | Tipo harmonizado, mantendo `document_type_original`; usar um valor validado (`article`, `thesis`, `dissertation`, `conference_paper`, `book`, `book_chapter`, `other_academic` ou `unknown`). |
| `title` | texto | Título transcrito da fonte, sem alteração editorial. |
| `authors_json` | array JSON de textos | Autores na ordem e forma de apresentação da fonte. Não reduzir a um campo de texto separado por vírgulas. |
| `publication_year` | inteiro de quatro dígitos | Ano de publicação indicado pela fonte. Não preencher com ano de defesa, depósito, processamento ou coleta. |
| `defense_year` | inteiro de quatro dígitos | Ano de defesa/titulação, quando fornecido. Manter separado de `publication_year`. |
| `abstract` | texto | Resumo disponível, preservando o conteúdo e idioma originais. |
| `keywords_json` | array JSON de textos | Palavras-chave conforme a fonte; vazio se ausentes, sem completar por inferência. |
| `language` | texto | Idioma informado pela fonte, preservando o código ou rótulo original quando possível. |
| `institution_original` | texto | Instituição associada ao registro acadêmico conforme a fonte (por exemplo, IES que oferece o curso); não presumir que seja afiliação dos autores. |
| `institution_normalized` | texto | Forma harmonizada por tabela de correspondência validada; vazio até existir correspondência confirmada. |
| `author_affiliations_json` | array JSON de textos | Afiliações de autores explicitamente informadas pela fonte; não inferir a partir da instituição do registro. |
| `program` | texto | Programa de pós-graduação, quando fornecido. |
| `venue` | texto | Periódico, evento ou veículo de publicação informado pela fonte. |
| `volume` | texto | Volume, se disponível. |
| `issue` | texto | Número/fascículo, se disponível. |
| `pages` | texto | Paginação original, se disponível; não presumir intervalo quando a fonte fornecer apenas uma página. |
| `doi` | texto | DOI conforme informado pela fonte. |
| `url` | texto | URL do registro ou do texto completo, mantendo a distinção na origem bruta. |
| `collected_at` | data/hora ISO 8601 | Momento da coleta/importação, com fuso horário. Não confundir com data de publicação. |
| `source_metadata_json` | objeto JSON | Campos originais adicionais sem correspondência no esquema comum; chaves devem manter os nomes da fonte. |

O registro original não deve ser reconstruído somente a partir desta tabela: `raw_file` e `source_record_id` garantem a rastreabilidade ao arquivo e ao item de origem.

## 4. Manifesto de execuções

`logs\execucoes.csv` registra uma linha por busca ou importação. Campos mínimos:

| Campo | Definição |
|---|---|
| `source_run_id` | Identificador único da execução. |
| `source` | Fonte/interface utilizada. |
| `query_id` e `query_literal` | Nome curto da consulta e expressão exata submetida. |
| `searched_fields` | Campos pesquisados conforme interface ou procedimento. |
| `filters_json` | Período, tipos e demais filtros efetivamente aplicados. |
| `method` | Busca manual, exportação assistida, importação de dados abertos ou outro método permitido. |
| `started_at`, `completed_at` | Data/hora ISO 8601 com fuso; conclusão vazia se a execução falhar ou for interrompida. |
| `source_reported_count` | Total exibido pela fonte, quando disponível. |
| `records_exported`, `records_imported` | Contagens observadas em cada etapa, sem tratá-las como equivalentes automaticamente. |
| `output_files` | Caminhos relativos dos arquivos resultantes. |
| `status`, `notes` | Estado e limitações/erros observados. Falhas devem permanecer explícitas. |

## 5. Coleta incremental das exportações

O comando `scripts\capture_collection.py register` arquiva uma exportação local recebida da interface oficial ou dos dados abertos. Ele não faz requisições web, não automatiza navegador/login e não transforma os metadados. O arquivo de entrada permanece no lugar; uma cópia byte a byte é guardada em `dados\brutos\{fonte}\`.

Modelos de consulta disponíveis no comando `queries`:

```powershell
python .\scripts\capture_collection.py queries
```

O comando exibe a consulta nacional e a consulta regional complementar do protocolo. A busca regional combina o bloco temático com `("Goiás" OR "goiano" OR "goiana")`. Trate-a como modelo para adaptação por fonte, não como sintaxe universal; submeta a variante efetivamente aceita e registre-a sem alterar no manifesto. Consultas de IES/contextos goianos validados também podem ser registradas com `query-id` próprio. A coleta/triagem regional complementa e nunca substitui o conjunto nacional.

Exemplo PowerShell para um RIS já baixado:

```powershell
python .\scripts\capture_collection.py register `
  --source portal-capes `
  --query-id busca-nacional `
  --query 'PIBID OR "Programa Institucional de Bolsa de Iniciação à Docência"' `
  --file '.\Periodicos-CAPES-RIS.ris' `
  --method assisted_export `
  --fields 'busca de assunto' `
  --filters-json '{"publication_year":"2007:2026"}' `
  --reported-count 2777 `
  --exported-count 1
```

Métodos aceitos: `assisted_export`, `open_data_download`, `manual_capture` e `manual_search`. O Scholar só aceita `manual_search`. Formatos de entrada: ZIP, RIS, BibTeX, CSV e XLSX. O manifesto distingue `source_reported_count` do número efetivamente exportado; o número importado permanece vazio nesta etapa.

Cada tentativa recebe um `source_run_id`. Arquivos idênticos da mesma fonte são registrados como `duplicate_skipped` e apontam para o bruto já preservado; conteúdo idêntico recebido de fontes distintas continua armazenado separadamente. Erros de validação/cópia ficam registrados como `failed` e também são reportados no terminal. Uma nova consulta ou novo conteúdo produz outro bruto, sem sobrescrita.

Para registrar uma consulta executada sem exportação disponível (inclusive uma tentativa interrompida após busca), use `record-search`. Isso registra a expressão literal, campos, filtros, total informado, estado e observações; não cria um falso arquivo nem converte o total mostrado em contagem exportada:

```powershell
python .\scripts\capture_collection.py record-search `
  --source bdtd `
  --query-id goias-descriptors `
  --query '(PIBID OR "Programa Institucional de Bolsa de Iniciação à Docência") AND ("Goiás" OR "goiano" OR "goiana")' `
  --fields 'todos os campos' `
  --filters-json '{"publication_year":"2007:2026"}' `
  --status export_unavailable `
  --notes 'Registrar o motivo observado na interface.'
```

`--reported-count` e `--exported-count` são opcionais, permitindo registrar explicitamente contagens desconhecidas. Os estados `search_completed` e `export_unavailable` não afirmam que houve exportação. O Google Scholar permanece limitado a procedimento manual e não pode ser automatizado por este utilitário.

Para baixar diretamente um recurso oficial do Catálogo CAPES, use `download-capes-open-data`. O comando aceita somente URLs HTTPS de `dadosabertos.capes.gov.br`, grava o arquivo em staging, aplica o limite obrigatório de bytes e valida o tamanho esperado se informado. Em caso de interrupção, mantém o parcial e tenta retomá-lo com `Range` na próxima execução usando a mesma URL e consulta. Se o servidor responder sem suporte à retomada, o download reinicia do começo; erros ficam registrados como `download_incomplete`.

O arquivo anual de 2024 foi obtido via navegador e registrado com `register`; a tentativa de transferência direta expirou por timeout antes de receber conteúdo. O bruto está em `dados\brutos\catalogo-capes\`. A leitura em streaming confirmou 91.833 registros, 59 colunas e separador `;`. UTF-8 falhou e Windows-1252 estrito encontrou byte indefinido. Na Etapa 5, o arquivo foi processado como Windows-1252 com substituição explícita; 79 substituições em 12 registros estão sinalizadas para revisão, sem alterar o bruto. Consulte a seção 8 para os detalhes e ressalvas.

Para registrar um CSV que já foi baixado manualmente:

```powershell
python .\scripts\capture_collection.py register `
  --source catalogo-capes `
  --query-id catalogo-2024 `
  --query 'Dados abertos CAPES: Catálogo de Teses e Dissertações Brasil, arquivo anual 2024' `
  --file '.\dados\staging\catalogo-capes\br-capes-btd-2024-2025-12-01.csv' `
  --method manual_capture `
  --fields 'arquivo anual integral; 59 colunas; verificação streaming com delimitador ponto e vírgula' `
  --filters-json '{"dataset_id":"2021-a-2024-catalogo-de-teses-e-dissertacoes-brasil","publication_year":"2024"}' `
  --exported-count 91833
```

Exemplo de download direto para uma futura repetição (não necessário para o arquivo já arquivado):

```powershell
python .\scripts\capture_collection.py download-capes-open-data `
  --url 'https://dadosabertos.capes.gov.br/dataset/dbb9b83e-7779-4b99-89d2-1ff8099f36f6/resource/87133ba7-ac99-4d87-966e-8f580bc96231/download/br-capes-btd-2024-2025-12-01.csv' `
  --query-id catalogo-2024 `
  --dataset-id 2021-a-2024-catalogo-de-teses-e-dissertacoes-brasil `
  --max-bytes 550000000 `
  --expected-bytes 506649988
```

Substitua o placeholder pela URL direta do recurso no portal oficial. Não aumente o limite nem inicie a transferência de um arquivo grande sem confirmar o recurso, o tamanho esperado e a necessidade de coletá-lo. Um download concluído é copiado para `brutos\catalogo-capes\`, registrado no inventário e no manifesto; o staging é então removido. A importação, a leitura do CSV e a harmonização de esquemas continuam fora do escopo desse comando.

## 6. Tabelas de revisão posteriores

As decisões de triagem não alteram a tabela bibliográfica. A partir da Etapa 6, manter em `triagem\decisoes.csv` no mínimo `record_id`, `decision` (`included`, `excluded` ou `pending`), `reason`, `reviewer` e `reviewed_at`. O vínculo entre registros duplicados e fontes de origem deve ser preservado em uma tabela própria, não resolvido pela exclusão de linhas brutas/normalizadas.

O recorte de Goiás será registrado separadamente na Etapa 7. A instituição/afiliação do autor não equivale a local de realização do estudo; registrar a classificação do estudo, sua evidência e a regra aplicada sem inferir localização a partir da IES.

## 7. Mapeamento inicial dos formatos validados

- **Portal CAPES RIS:** `ID` → `source_record_id`; `TY` → tipo original; `TI` → título; `PY` → `publication_year`; `JO` → `venue`; `VL` → `volume`; `IS` → `issue`; `SP`/`EP` → `pages`; `DO` → `doi`. A amostra do Portal reúne os autores em uma única linha `AU`, separados por vírgula e espaço; só separar essa lista após validar o delimitador em cada arquivo, mantendo o valor original acessível no RIS bruto. Preservar o `.ris` original. O formato não traz status de acesso aberto; registrar essa classificação em observação de execução separada, indicando que foi conferida manualmente. A validação regional confirmou lotes de 30/30/30/12 (102 IDs únicos); `Periodicos-CAPES-RIS-5.ris` é cópia binária do lote 1 e não adiciona registros.
- **BDTD CSV:** importar respeitando o cabeçalho e a codificação UTF-8 observados. O campo “Ano de defesa” alimenta `defense_year`; não preencher `publication_year` apenas porque o filtro da interface foi chamado “Ano da publicação”.
- **Dados abertos CAPES:** respeitar o delimitador e o esquema do arquivo bruto. O CSV de 2024 tem 59 campos, delimitador `;` e 91.833 registros; a execução da Etapa 5 usou Windows-1252 com substituição explícita para 79 bytes indefinidos, sinalizados em 12 registros. Campos como `DT_TITULACAO`, `NM_PRODUCAO`, `DS_PALAVRA_CHAVE`, `DS_RESUMO`, `SG_UF_IES` e `NM_UF_IES` não autorizam inferir ano de publicação ou local de estudo; verificar os metadados de cada período antes de mapear.
- **SciELO RIS:** `ID` → `source_record_id`; `TY` → tipo original; `TI` → título; linhas repetidas `AU` → autores na ordem de origem; `PY` → ano de publicação; `JO`/`J2` → periódico; `DO` → DOI; linhas repetidas `AB` → resumos em idiomas disponíveis; linhas repetidas `KW` → palavras-chave. O RIS manual da coleção Brasil contém 76 registros, sem IDs ou títulos duplicados, e deve ser preservado sem alteração. Há seis registros sem DOI. O ano exportado varia de 2012 a 2026. Por decisão do usuário, aplicar o período geral do protocolo (2007–2026); os oito registros de 2025–2026 permanecem incluídos. A ausência de registros anteriores a 2012 descreve apenas o intervalo desta exportação.

## 8. Normalização e relatório de qualidade

Execute `python .\scripts\normalize_collection.py` na raiz do projeto. O script lê apenas arquivos listados em `logs\arquivos.csv`, relaciona cada registro ao `source_run_id` original e grava quatro arquivos versionados em `normalizados\`: `registros_normalizados__*.csv`, `relatorio_qualidade__*.csv`, `inconsistencias__*.csv` e `mapeamento_instituicoes__*.csv`. A execução é registrada em `logs\normalizacoes.csv`. Uma falha gera estado explícito no log e não substitui arquivos brutos. IDs internos são determinísticos para o mesmo registro na mesma exportação, permitindo comparar reprocessamentos sem confundi-los com IDs fornecidos pela fonte.

O processamento usa `csv` da biblioteca padrão em streaming; essa escolha evita carregar o catálogo CAPES de 506 MB inteiro em memória e não adiciona dependência de pandas. Para CSV, tenta decodificar estritamente em UTF-8 e Windows-1252. Se ambos falharem porque há bytes indefinidos em Windows-1252, usa esse codec com substituição explícita e contabiliza `U+FFFD` no relatório; assim, pontuação tipográfica como aspas curvas não vira caracteres de controle C1, como ocorreria com Latin-1. A contagem de substituições explicita a perda localizada e o bruto permanece imutável. RIS é lido como UTF-8 e o ZIP BDTD é preservado, sendo apenas o CSV interno processado.

O mapeamento mantém `publication_year` separado de `defense_year`: o CSV BDTD usa “Ano de defesa”; no Catálogo CAPES, `DT_TITULACAO` preenche apenas ano de defesa e `AN_BASE` permanece em `source_metadata_json`, sem ser tratado como ano de publicação. O ARK/identificador persistente da BDTD, quando não informado pela fonte, fica vazio; não é criado identificador com aparência de ID da fonte. O RIS CAPES fornece autores em uma linha agrupada, que é preservada como um único elemento de `authors_json` para não separar nomes por uma vírgula ambígua. `institution_normalized` permanece vazio até haver tabela de correspondência validada.

O relatório de qualidade é por arquivo bruto, compara registros processados com `records_exported` quando conhecido e registra campos esperados ausentes, campos fonte não mapeados, títulos/anos/autores/IDs ausentes, anos inválidos e anos fora do período 2007–2026. Também informa caracteres de controle C1 e caracteres `U+FFFD` introduzidos na decodificação. `inconsistencias__*.csv` detalha os registros que precisam de revisão e quantifica os caracteres especiais por código Unicode. Nenhuma inconsistência causa exclusão automática; deduplicação e triagem permanecem nas etapas seguintes.

A geração validada `20261108T205625-0300__828bdff7` contém 93.072 registros (BDTD 1.060, Portal CAPES 103, Catálogo CAPES 91.833, SciELO 76), com 93.072 `record_id` únicos e listas/objetos JSON válidos. As nove entradas de arquivo conferem com suas contagens exportadas conhecidas; não há título/ano ausente, ano inválido ou ano fora do período. O relatório aponta 1.004 itens BDTD sem ARK/identificador persistente (962 nacionais e 42 regionais), sem inventar IDs da fonte. A exportação nacional BDTD em UTF-8 contém 42 caracteres C1 em 17 registros: 41 em resumos e um no título de um desses registros; esses caracteres permanecem no derivado e estão detalhados para revisão. No CSV CAPES, UTF-8 e Windows-1252 estritos falham; Windows-1252 com substituição explícita resulta em 79 `U+FFFD` em 12 registros. O CSV bruto segue intacto e deve ser consultado em caso de revisão desses trechos.

O arquivo `mapeamento_instituicoes__*.csv` reúne as grafias observadas, ocorrências por fonte, campo para a forma normalizada e estado `pending`. A geração validada lista 606 nomes distintos. Nenhuma equivalência foi presumida; preencher `institution_normalized` somente após validação. O tipo RIS `Editorial` é classificado como `other_academic`; autores CAPES RIS agrupados em uma linha continuam como um único elemento para evitar separação ambígua por vírgulas.

Para localizar os caracteres sinalizados na geração concluída, execute:

```powershell
python .\scripts\audit_character_issues.py --run-id 828bdff7-5b9b-4111-9e85-a430f4d62a73
```

O comando verifica o SHA-256 dos brutos envolvidos e confronta os IDs, posições e contagens do relatório original antes de gravar uma nova auditoria em `dados\triagem\`. Cada linha representa uma ocorrência, com campo da fonte, posição de caractere no campo (base 1; não é deslocamento em bytes), código original, contexto e decisão pendente. Para CAPES, `original_code` é o byte indefinido e o contexto vizinho usa Windows-1252 com substituição: é uma representação auxiliar, não confirmação de codificação nem reconstrução do texto. Para BDTD, os controles Unicode são exibidos como marcadores. Nenhum conteúdo bruto ou normalizado é modificado; a auditoria não define correções nem decisões de triagem.

A [auditoria de 12/11/2026](./dados/triagem/auditoria_caracteres__20261112T103440254440-0300__e08ff020.csv) localizou 121 ocorrências: 42 C1 em 17 registros BDTD e 79 bytes indefinidos em 12 registros CAPES. Os 17 registros BDTD constam da planilha corrigida de revisão de escopo Goiás; os 12 CAPES não constam dos 1.317 candidatos nessa planilha. Uma inspeção por registro não deve confundir o alerta genérico aplicado aos 78 candidatos CAPES com evidência de substituição em cada um.

## 9. Controle de versões

| Versão | Data | Alterações |
|---|---|---|
| 1.0 | 08/11/2026 | Define campos comuns, formatos de intercâmbio, rastreabilidade, manifesto de execuções, diretórios e regras de preservação/normalização. |
| 1.1 | 08/11/2026 | Documenta staging e download retomável/limitado dos recursos oficiais de dados abertos CAPES. |
| 1.2 | 08/11/2026 | Inclui preservação de exportações ZIP sem modificar o original. |
| 1.3 | 08/11/2026 | Registra aquisição e validação em streaming do CSV CAPES de 2024 e as ressalvas de codificação e filtragem. |
| 1.4 | 08/11/2026 | Documenta preservação e mapeamento inicial do RIS manual SciELO, incluindo a divergência de anos 2025–2026. |
| 1.5 | 08/11/2026 | Registra a decisão de aplicar à SciELO o período geral aprovado de 2007–2026 e manter no escopo os oito registros de 2025–2026. |
| 1.6 | 08/11/2026 | Documenta o normalizador em streaming, os mapeamentos por fonte, o fallback de codificação e os relatórios/logs gerados na Etapa 5. |
| 1.7 | 08/11/2026 | Evita corrupção de pontuação no CSV CAPES: após falha do decodificador Windows-1252 estrito, usa substituição explícita e relata a contagem em vez de Latin-1. |
| 1.8 | 08/11/2026 | Registra a execução validada da Etapa 5, diagnósticos de caracteres por registro e a geração de candidatos a mapeamento institucional. |
