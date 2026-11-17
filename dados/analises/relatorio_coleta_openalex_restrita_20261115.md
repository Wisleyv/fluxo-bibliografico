# Coleta complementar OpenAlex — busca restrita

**Coleta:** 15/11/2026, das 19h33min58s às 19h37min22s, horário local.  
**Situação:** coleta concluída para a consulta descrita; registros ainda não selecionados, deduplicados entre fontes ou incorporados aos resultados da pesquisa.

## Consulta e procedimento

Após o [piloto](./relatorio_busca_piloto_openalex_20261115.md), foi escolhida a busca em título, resumo e palavras-chave do OpenAlex, com a expressão:

```text
PIBID OR "Programa Institucional de Bolsa de Iniciação à Docência"
```

O filtro `from_publication_date:2007-01-01,to_publication_date:2026-11-08` foi aplicado à data de publicação informada pelo OpenAlex. Utilizou-se a pesquisa padrão de obras da API, sem filtro de país ou de tipo de produção. A busca também pode recuperar obras por palavras-chave indexadas, e os termos pesquisados não garantem relevância substantiva. Não foi utilizado filtro que reconstitua o estado do índice em 08/11.

Foram recebidas **125 páginas**, com até 100 registros por página. A primeira e a última resposta, assim como as intermediárias, informaram 12.431 resultados; a última retornou 31 registros e cursor seguinte nulo. Foram conferidos os encadeamentos de cursores, a unicidade dos identificadores, a data de publicação e a contagem em relação ao total informado. Isso confirma a consistência da paginação desta consulta, não a ausência de mudanças no índice durante a coleta ou sua cobertura completa do tema.

As [páginas de resposta arquivadas](../brutos/openalex/busca-restrita-20261115/) preservam os objetos retornados pela API, os parâmetros, os horários e os cabeçalhos de limite, sem a chave. O [CSV consolidado](./openalex_busca_restrita_20261115.csv) apresenta uma linha por identificador OpenAlex, com título, data, tipo, autores, instituições identificadas, DOI, fonte, palavras-chave e resumo reconstruído quando disponível; a coluna `pagina_origem` remete à página arquivada. A [auditoria estruturada](./openalex_busca_restrita_auditoria_20261115.json) registra contagens e hashes SHA-256 das páginas e do CSV. Não houve download de textos integrais.

## Caracterização dos registros recuperados

| Indicador | Registros |
|---|---:|
| Identificadores OpenAlex distintos | 12.431 |
| Com DOI informado | 6.349 |
| Com resumo indexado | 10.911 |
| Com pelo menos uma instituição informada em autoria | 6.371 |
| Tipo `article` informado | 8.996 |
| Tipo `book-chapter` informado | 1.234 |
| Tipo `conference-paper` informado | 1.027 |
| Tipo `dissertation` informado | 718 |

As contagens de campos se sobrepõem e a tipologia é a informada pelo OpenAlex, não uma classificação validada. A auditoria discrimina todos os tipos. Resumos e afiliações ausentes reduzem a informação disponível; não são evidência de ausência de vínculo ou pertinência e, por si sós, não geram pendência nem busca individual.

As 125 solicitações concluídas registraram **US$ 0,125 de uso da API**, não de créditos do Copilot; a coleta foi executada com a chave disponibilizada localmente, sem registrá-la. O arquivo consolidado foi reaberto e conferido, incluindo contagem, identificadores e hash. Passaram testes focados de encadeamento, duplicidade e datas. Essas verificações são técnicas e não validam a seleção científica.

## Limites e continuidade

O OpenAlex é uma fonte distinta do Portal de Periódicos CAPES. Os **12.431 candidatos** não são equivalentes aos 2.777 resultados exibidos pelo Portal em 08/11, nem são o total da produção brasileira sobre o PIBID. A busca não foi limitada ao Brasil; presença de instituição brasileira ou goiana, quando disponível, não comprova o contexto do estudo, e a falta de afiliação não comprova ausência de vínculo.

As datas de publicação filtradas não são anos de defesa e não demonstram que os registros já estivessem indexados em 08/11. Coleta em 15/11 pode incluir atualizações posteriores. A pesquisa restrita pode deixar de fora obras recuperáveis apenas em outros campos. Metadados incompletos, pertinência temática e possíveis duplicatas entre fontes requerem tratamento posterior com evidências disponíveis; diferenças de tipo documental impedem fundir automaticamente uma tese e um artigo sobre o mesmo estudo. Não se alteraram as decisões da base técnica ou os gráficos preliminares.

A próxima etapa é preparar e conciliar os candidatos em lote com as fontes já arquivadas, separando identificação bibliográfica de elegibilidade e preservando proveniência. A completude da busca no OpenAlex não resolve a exportação incompleta da busca nacional no Portal CAPES nem autoriza, por si só, a estimativa da participação de Goiás no Brasil.
