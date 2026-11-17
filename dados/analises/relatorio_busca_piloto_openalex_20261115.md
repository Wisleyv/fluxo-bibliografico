# Piloto de busca no OpenAlex

**Data:** 15 de novembro de 2026, aproximadamente 19h25 (horário local).  
**Objetivo:** testar busca temática, paginação básica e metadados para uma possível coleta complementar; não constituir o corpus final.

## Procedimento

Foram feitas quatro solicitações anônimas à API de obras do OpenAlex, sem chave, utilizando:

- Expressão: `PIBID OR "Programa Institucional de Bolsa de Iniciação à Docência"`.
- Filtro informado à API: data de publicação de 01/01/2007 a 08/11/2026, inclusive.
- Duas modalidades: `search` (busca ampla) e `search.title_abstract_keywords` (título, resumo e palavras-chave).
- Duas páginas de dez resultados para cada modalidade, ordenadas pela relevância padrão da API.

As [respostas integrais](./openalex_busca_piloto_20261115.json) incluem parâmetros, horários, status HTTP, cabeçalhos de limite e dados retornados. Foram obtidas com o [script do piloto](../../scripts/piloto_busca_openalex_20261115.py), sem modificar o exemplo original. O SHA-256 do arquivo de respostas é `9cf82ae164ce65e2896d9e2e65e34054353904dec4bbe979e003c012ca3b3b21`.

## Resultados

| Busca | Total informado pela API | Registros obtidos no piloto |
|---|---:|---:|
| Ampla | 31.638 | 20 |
| Título, resumo e palavras-chave | 12.431 | 20 |

As quatro respostas tiveram HTTP 200. Cada modalidade retornou dez registros em cada página, sem repetição de identificadores entre as duas páginas da mesma modalidade. Quinze identificadores apareceram nas duas modalidades; portanto, foram obtidos **25 registros distintos no piloto**, não 40 obras distintas. As contagens são fotografias da API nessa data, não estimativas de estudos elegíveis.

Na amostra ampla, 16 registros tinham tipo `article`, dois `dissertation` e dois `conference-paper`; dez tinham DOI, 18 tinham resumo indexado e 15 tinham ao menos uma instituição registrada em alguma autoria. Na busca restrita, eram 17 `article`, uma `dissertation` e dois `conference-paper`; nove tinham DOI, 18 tinham resumo indexado e 15 tinham ao menos uma instituição registrada. Esses campos não foram validados independentemente; afiliação presente não comprova contexto da pesquisa, e afiliação ausente não comprova ausência de vínculo.

Os 40 retornos tinham data de publicação informada dentro do intervalo solicitado. Verificou-se a ocorrência literal da sigla ou expressão nos títulos ou nas palavras do índice de resumos de todos os retornos da amostra; isso não comprova pertinência substantiva de todos os registros. A amostra de conveniência ordenada por relevância não estima a qualidade nem a composição dos conjuntos completos.

## Interpretação e limites

- O OpenAlex é fonte distinta do Portal de Periódicos CAPES. Os **2.777 resultados** exibidos pelo Portal em 08/11 não são o total da busca OpenAlex nem garantem o mesmo conjunto. As modalidades OpenAlex também pesquisam campos diferentes dos utilizados no Portal.
- A busca ampla também pode recuperar ocorrências no texto integral e palavras-chave; a busca restrita reduz o escopo pesquisado, mas não garante pertinência nem cobertura completa. Nenhuma foi limitada geograficamente ao Brasil. Os totais exigem triagem, critérios geográficos e deduplicação antes de interpretação bibliométrica.
- O filtro é de data de publicação do OpenAlex. Não equivale ao ano de defesa da BDTD, nem comprova que um registro estivesse indexado em 08/11. Coleta em 15/11 pode refletir alterações posteriores; registros sem data compatível podem não ser recuperados por esse filtro.
- A paginação básica funcionou anonimamente nas duas primeiras páginas. Segundo a [documentação](https://help.openalex.org/api/paging/), ela alcança até os primeiros 10.000 resultados; para percorrer conjuntos maiores por cursor é necessária uma chave gratuita após a primeira página. A execução integral e o cursor com chave **não foram testados**.
- As quatro chamadas custaram US$ 0,004 em uso da API, dentro da franquia anônima compartilhada; isso não é medida dos créditos do Copilot. À tarifa documentada de US$ 0,001 por busca e com 100 resultados por página, estimam-se cerca de 317 chamadas/US$ 0,317 para a busca ampla e 125 chamadas/US$ 0,125 para a restrita, antes de verificações ou repetição. Totais, limites, saldo e tarifas podem mudar. A [franquia gratuita com chave](https://help.openalex.org/access/pricing/) é de US$ 1 diário; pode haver limites de ritmo para contas novas.
- O piloto não fez download de textos integrais, revisão independente, triagem completa, confronto com as demais fontes nem estimativa de participação goiana.

## Próximo passo possível

Decidir a modalidade de busca e seu alcance antes de uma coleta integral. Para percorrer por cursor qualquer um dos totais observados, seria necessária uma chave configurada localmente, sem envio pelo chat. O coletor precisaria preservar respostas e proveniência, tratar erros e interrupções, conferir paginação e dados, manter tipo e afiliações, e não rotular automaticamente todos os itens como artigos. A coleta permaneceria complementar e não resolveria, por si só, a exportação incompleta do Portal CAPES.
