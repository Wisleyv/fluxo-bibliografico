# Inventário de insumos e conferência local — Marco 0

**Atualização posterior:** base, controles e regras de medição aceitos pelo usuário; ver `Aceite do Marco 0.md`. Este inventário permanece o retrato dos insumos de partida, sem substituir as classificações produzidas no Marco 1.

Data: 15/11/2026. Caminhos relativos à raiz do workspace. Companheiros: `Protocolo de busca bibliométrica - v1.2 minuta.md` e `Matriz de aprovação - Marco 0.md`.

## Autoridade e escolha da base

Propõe-se `dados/analises/triagem_criterio_defesa_20261115.xlsx`, aba `Triagem`, como ponto de partida técnico. É a versão mais recente entre as bases de triagem locais; o plano de análise, atualização “Critério temporal aprovado”, a declara vigente, e as constantes BASE de `scripts/conciliar_openalex_20261115.py` e `scripts/conferir_identidades_openalex_20261115.py` apontam para ela. Seu relatório `dados/analises/relatorio_criterio_defesa_20261115.md` registra preservação das decisões e acréscimo do critério de defesa. A escolha técnica é sustentada; aguarda aceite operacional para o Marco 1, sem necessidade de refazer as análises anteriores.

Versões concorrentes são históricas: `dados/analises/triagem_portal_prioritario_20261115.xlsx` e `dados/analises/triagem_lote_consolidada_20261115.xlsx` antecedem o critério de defesa. A planilha `dados/entregas/pacote_preliminar_20261112/Triagem e análise.xlsx` é anterior às decisões de 15/11; produtos simplificados não são base técnica. A seção 6 do plano de automação ainda descreve a retomada de 12/11; esse estado histórico não prevalece sobre a cadeia de entradas dos scripts de 15/11. Não foram fundidas ou sobrescritas versões.

## Insumos do Marco 1

| Item | Caminho relativo e seleção | Data/versão | Unidade e observado | Identificadores / pendência |
|---|---|---|---|---|
| Base proposta | `dados/analises/triagem_criterio_defesa_20261115.xlsx`, aba Triagem | 15/11/2026 | 1.317 linhas; 1.317 códigos únicos | Código, DOI, Link OpenAlex, Link da fonte; aceite operacional pendente |
| Controle Portal CAPES | Mesma base, Fonte = Portal CAPES | 15/11, exportações 08/11 | 103 linhas = 102 regionais + 1 amostra nacional conforme manifesto | Código/DOI; conjunto parcial, não os 2.777 resultados nacionais |
| Controle SciELO | Mesma base, Fonte = SciELO | 15/11, exportação 08/11 | 76 linhas | Código/DOI/título; coleção Brasil |
| Controle BDTD | Mesma base, Fonte = BDTD | 15/11, exportações 08/11 | 1.060 linhas = 1.018 nacionais + 42 regionais conforme manifesto | Código/links/título/autoria; sobreposição de buscas, ano de defesa |
| Controle Catálogo CAPES | Mesma base, Fonte = Catálogo CAPES | 15/11, arquivo anual 2024 | 78 candidatos temáticos | Código/título/autoria/defesa; não confundir com 91.833 registros anuais brutos |
| OpenAlex consolidado | `dados/analises/openalex_busca_restrita_20261115.csv` | 15/11 | 12.431 linhas e IDs únicos | openalex_id, doi, pagina_origem; candidatos, sem elegibilidade nacional decidida |
| Auditoria/consulta | `dados/analises/openalex_busca_restrita_auditoria_20261115.json` | 15/11 | 125 hashes de página, parâmetros e horários | page_sha256, csv_sha256; não é manifesto legado |
| Páginas originais | `dados/brutos/openalex/busca-restrita-20261115/`, de `pagina_0001.json` a `pagina_0125.json` | 15/11 | 125 arquivos; 12.431 resultados | response.results[].id; request_cursor, request_parameters, retrieved_at |
| Conciliação inicial | `dados/analises/openalex_correspondencias_candidatas_20261115.csv` | 15/11 | 689 pares únicos | openalex_id + codigo_base; sem resolução nesta rodada |
| Classificação dos pares | `dados/analises/openalex_identidades_conferidas_20261115.csv` | 15/11 | 689 pares: 116 sustentados, 52 em revisão, 521 só título | Mesma chave composta; filtrar classificacao = Identificador concordante; metadados requerem revisão para obter os 52 prioritários |
| Auditoria de conciliação | `dados/analises/openalex_conciliacao_auditoria_20261115.json` | 15/11 | Totais históricos 12.431 / 1.317 / 689 | Usada para confronto, não para substituir recontagem |
| Auditoria de identidades | `dados/analises/openalex_identidades_auditoria_20261115.json` | 15/11 | Totais históricos 116 / 52 / 521 | Classificações operacionais preservadas |

Não foi encontrada uma tabela isolada obrigatória para os 52 pares: eles já estão na coluna `classificacao` da tabela de identidades. Não se criou cópia redundante nem se resolveu qualquer par. `codigo_base` corresponde a `Código` na base, `openalex_id` liga ao CSV e aos IDs das páginas. O DOI exige normalização pelo utilitário existente; título igual isoladamente não estabelece identidade. Os códigos curtos são únicos nesta base, mas não devem ser extrapolados para novas importações sem nova verificação.

## Proveniência dos controles e inventários existentes

Reutilizar `dados/logs/arquivos.csv` (nove arquivos brutos), `dados/logs/execucoes.csv` (consultas, filtros e execuções) e `dados/logs/normalizacoes.csv` (geração concluída 828bdff7 e gerações substituídas). Este documento complementa esses manifestos, que permanecem intactos. OpenAlex tem auditoria própria com parâmetros, horários e hashes e não está automaticamente registrado no manifesto legado.

Arquivos brutos de controle registrados no inventário existente:

- `dados/brutos/portal-capes/portal-capes__busca-nacional__20261108T113709100047-0300__RIS.ris`;
- `dados/brutos/portal-capes/portal-capes__goias-page1__20261108T115932998162-0300__RIS.ris`;
- `dados/brutos/portal-capes/portal-capes__goias-page2__20261108T120049708295-0300__RIS.ris`;
- `dados/brutos/portal-capes/portal-capes__goias-page3__20261108T120216735525-0300__RIS.ris`;
- `dados/brutos/portal-capes/portal-capes__goias-page4__20261108T120415668964-0300__RIS.ris`;
- `dados/brutos/scielo/scielo__national-pibid-brazil__20261108T200222874859-0300__RIS.ris`;
- `dados/brutos/bdtd/bdtd__busca-nacional__20261108T113708926870-0300__CSV.csv`;
- `dados/brutos/bdtd/bdtd__goias-descriptors__20261108T125842275582-0300__ZIP.zip`;
- `dados/brutos/catalogo-capes/catalogo-capes__catalogo-2024__20261108T150417015445-0300__CSV.csv`.

A geração normalizada vigente está em `dados/normalizados/registros_normalizados__20261108T205625-0300__828bdff7.csv`; o log registra 93.072 linhas, incluindo o Catálogo anual integral. Nesta rodada não se releu o CSV de 648 MB: os quatro controles foram contados diretamente na base técnica, e a quantidade normalizada é identificada aqui como valor de log, não recontagem. Os manifestos preservam UUID record_id/source_run_id, IDs de origem e caminhos; para a conciliação operacional usar Código, não procurar uma junção direta inexistente entre rótulos de fonte e IDs OpenAlex.

## Conferência efetivamente executada

| Medida | Referência do plano | Observado local | Origem / método |
|---|---:|---:|---|
| Linhas base | 1.317 | 1.317 | Leitura somente de valores de Triagem e contagem das linhas com Código |
| BDTD / Portal / Catálogo / SciELO | 1.060 / 103 / 78 / 76 | 1.060 / 103 / 78 / 76 | Agrupamento do campo Fonte da mesma aba |
| Elegibilidade incluir / excluir / pendente / não iniciada | 19 / 199 / 247 / 852 | 19 / 199 / 247 / 852 | Campo Decisão de elegibilidade; sem decisão = 1.099 |
| Registros OpenAlex CSV | 12.431 | 12.431, todos com ID único | csv.DictReader no consolidado |
| Páginas / resultados | 125 / 12.431 | 125 / 12.431 | JSONs locais; validate_page reutilizada de scripts/coletar_openalex_restrita_20261115.py |
| Pares candidatos únicos | 689 | 689 | Chave openalex_id + codigo_base na conciliação |
| Sustentados / revisão / título | 116 / 52 / 521 | 116 / 52 / 521 | Agrupamento de classificacao na tabela de identidades |

Checagens adicionais: os IDs das páginas coincidem com os IDs do consolidado; o cursor inicial é `*`, a sequência é consistente e o final é nulo; as datas dos resultados passam no validador existente; todos os parâmetros de página coincidem com PARAMS do coletor; a API informa 12.431 em todas as páginas. Todos os 125 hashes e o hash do CSV coincidem com a auditoria. As chaves dos 689 pares coincidem entre conciliação e identidades e todas ligam a códigos existentes na base e IDs existentes no CSV.

Consulta literal e horários observados na auditoria e confirmados nas páginas: `search.title_abstract_keywords` = `PIBID OR "Programa Institucional de Bolsa de Iniciação à Docência"`; filtro `from_publication_date:2007-01-01,to_publication_date:2026-11-08`; per_page = 100; coleta de 2026-11-15T19:33:58.117641-03:00 a 2026-11-15T19:37:22.842919-03:00. Não foi acessado o endpoint externo: a função validate_page foi importada sem executar o coletor.

## Divergências, limites e prontidão

Nenhuma divergência numérica foi encontrada nos totais recontados. Há divergência documental de vigência: o plano de automação descreve estados de 12/11 e o plano de análise contém atualizações sucessivas; a seleção da base de 15/11 acima resolve o ponto de partida técnico, preservando o histórico. O estado OpenAlex principal é proposta do realinhamento, enquanto o protocolo 1.1 e decisões anteriores ainda o tratam como complemento; a minuta registra essa transição sem substituir a aprovação.

Não faltam arquivos obrigatórios para começar a medição local de cobertura. Faltam aprovações metodológicas discriminadas na matriz. Os controles são linhas recuperadas com sobreposição, não amostra representativa da produção nacional; a BDTD combina duas buscas e o Catálogo cobre apenas 2024. Não se pode inferir completude nacional a partir desses controles. A definição operacional de produção brasileira permanece adicionalmente aberta antes do corpus nacional, pois a consulta OpenAlex é global.

Próxima ação após aceite: iniciar o Marco 1 pelos 52 pares filtrados na tabela de identidades e medir cobertura nos quatro controles com denominadores explícitos. Esta rodada encerra na preparação: não houve resolução de pares, triagem semântica, nova coleta ou alteração das decisões históricas.
