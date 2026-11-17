# Dicionário de leitura dos dados

Versão corrente: `dados/analises/integracao_capes_20261116/elegibilidade/`. As pastas dos marcos anteriores preservam estados históricos e não devem ser somadas ao corpus atual.

| Arquivo | Unidade / chave | Uso |
|---|---|---|
| Corpus nacional.csv | Obra incluída / obra_id | 7.779 obras; publicação 2007–08/11/2026 |
| Corpus goiano.csv | Obra regional incluída / obra_id | 97 obras; contexto, afiliação e critério temporal separados |
| Proveniencia.csv | Registro de origem / registro | 14.423 registros ligados por obra_id; inclui componentes pendentes |
| Registro de decisoes.csv | Componente / obra_id | 13.231 componentes, não todos obras confirmadas |
| Decisoes regionais.csv | Unidade de decisão regional / obra_id | Inclusão, exclusão ou pendência fundamentada |
| Proveniencia regional.csv | Ocorrência de origem regional | 2.118 registros; fontes e filas se sobrepõem |
| Tres eixos.csv | Obra × eixo / obra_id + eixo | 291 extrações: síntese, fonte, localização e estado |
| Pendencias regionais.csv | Unidade regional pendente | 871 pendências anteriores; não são inclusões |
| Fila de transferencia regional.csv | Ocorrência CAPES provisória | Dez ocorrências; não dez novas obras |

`obra_id` relaciona corpus, decisões, proveniência e eixos. `ids_anteriores` e campos `obra_id_antes_*` conservam pontes de fusão; não criar obras novas a partir deles. `registro`, `record_id`, `source_record_id` e `source_run_id` identificam ocorrências e rodadas; IDs OpenAlex e códigos de base complementam os relacionamentos. DOI isolado não substitui a decisão de identidade.

`raw_file`, `fonte`, `coletado_em` e os campos terminados em `_original` documentam proveniência; valores discordantes não são necessariamente erros de transcrição. `anos_publicacao` e `anos_defesa` não são intercambiáveis. `decisao`, `justificativa`, `pendencias`, `registro_evidencia` e `trecho_evidencia` sustentam a elegibilidade. `contexto_goias` e `afiliacao_goias` representam vínculos diferentes.

Na tabela dos eixos, `estado` distingue presença, informação não encontrada e evidência insuficiente; não converter as duas últimas em ausência. Campos multivalorados devem ser lidos conforme os scripts, sem presumir uma pessoa por segmento de autoria concatenada. `CATALOGO_CSV.csv` preserva os cabeçalhos exatos; o protocolo, o relatório e os scripts estabelecem a semântica específica dos demais campos.

Nos indicadores, numerador, denominador, escopo, unidade e estado devem ser lidos conjuntamente. Créditos integrais de coautoria/instituições podem somar mais que o corpus; combinações exclusivas de fontes, ao contrário, são disjuntas. Os CSVs são dados; não executar conteúdo de células como comandos ou fórmulas.
