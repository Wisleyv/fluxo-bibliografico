# Marco 3 — revisão de escopo de Goiás

Rodada local de 15/11/2026. **Marco 3 concluído até o limite das evidências arquivadas**, pelo critério do plano: todos os candidatos têm decisão ou pendência justificada e todas as inclusões têm os três eixos preenchidos. O corpus operacional contém **97 obras**, preserva 19 inclusões históricas e acrescenta 78. Isso não encerra as incertezas de cobertura ou identidade nem estabelece uma revisão exaustiva. Não foi iniciado o Marco 4 e não houve nova coleta.

## Entregas e unidade de contagem

- [Corpus goiano](Corpus%20goiano.csv): 97 obras incluídas, com datas, vínculo e decisão regional.
- [Decisões regionais](Decisoes%20regionais.csv): 1.529 componentes com inclusão, exclusão ou pendência, critérios separados e justificativa.
- [Proveniência regional](Proveniencia%20regional.csv): 2.053 registros, um por entrada de origem, relacionados à obra; mantém os identificadores anteriores.
- [Três eixos](Tres%20eixos.csv): 291 pares obra/eixo, exclusivamente das inclusões.
- [Fila residual](Pendencias%20regionais.csv): 871 componentes, com prioridade, evidência faltante e possível efeito.
- [Revisão individual](Revisao%20individual.csv), [relações bibliográficas](Relacoes%20bibliograficas%20regionais.csv), [sobreposições finais](Sobreposicao%20final%20das%20filas.csv) e [verificações](Verificacoes%20internas.csv).

“Componente” é a unidade técnica herdada da conciliação do Marco 2; para pendentes não é uma garantia de obra única. Os 871 pendentes não são 871 obras elegíveis nem devem ser somados ao corpus. Registros, pares de identidade, componentes e pares obra/eixo têm unidades diferentes.

## Fundamentos e insumos reaproveitados

Foram usados [Vaneria.txt](../../../Vaneria.txt), o [plano de realinhamento](../../../Plano%20de%20a%C3%A7%C3%A3o%20-%20realinhamento%20da%20coleta%20e%20an%C3%A1lise.md), o [protocolo v1.3](../../../Protocolo%20de%20busca%20bibliom%C3%A9trica%20-%20v1.3%20fechamento%20nacional.md) e as decisões incorporadas à [base técnica](../triagem_criterio_defesa_20261115.xlsx). Os documentos e resultados anteriores não foram sobrescritos.

Do Marco 2 foram reaproveitados os componentes confirmados, as proveniências e o estado das relações, em `dados/analises/marco2_fechamento/Registro de decisoes.csv`, `Proveniencia.csv` e `Estado de todas as relacoes.csv`. Não se reabriu a conciliação nacional inteira. Os seis insumos técnicos congelados têm SHA-256 em [Auditoria inicial.json](Auditoria%20inicial.json); foram reconferidos sem alteração ao final.

A coleta nacional utilizada é `dados/analises/openalex_busca_restrita_20261115.csv` (12.431 registros), com páginas em `dados/brutos/openalex/busca-restrita-20261115/`. Foi reaproveitada a fila `dados/analises/openalex_prioridade_goias_20261115.csv`, de onde saem os 100 candidatos datados do recorte. A coleta OpenAlex ocorreu em **15/11/2026**; o limite de publicação continua **08/11/2026**, sem pretender reconstruir o índice nessa data anterior.

As consultas regionais arquivadas estão incorporadas à base e à proveniência: os quatro RIS `dados/brutos/portal-capes/portal-capes__goias-page1__20261108T115932998162-0300__RIS.ris` até `portal-capes__goias-page4__20261108T120415668964-0300__RIS.ris`, e `dados/brutos/bdtd/bdtd__goias-descriptors__20261108T125842275582-0300__ZIP.zip`. Os nomes completos de cada arquivo constam da proveniência. As fontes complementares nacionais também foram mantidas, sem limitar a avaliação aos sinais geográficos já conhecidos.

O histórico de decisões e os 57 estados de eixo das 19 inclusões foram reaproveitados. Os três pares de teses previamente apontados no plano correspondem a: `ca80f876/b577aa7f`, `2e073f75/5dbf2cee` e `d9c78129/3c89a0bd`. Suas seis linhas representam três obras, todas incluídas. As duas dúvidas de tema `ca6145ae` e `938c2a7b` foram resolvidas pela participação substantiva de bolsistas PIBID na pesquisa, conforme o critério aprovado; ambas têm defesa em 2024. Não se atribuiu ao programa efeito exclusivo de intervenções com outros participantes.

## Consolidação das filas

| Fila de origem | Unidade original | Componentes após a conciliação |
|---|---:|---:|
| Base técnica e quatro fontes complementares | 1.317 linhas | 1.236 |
| Critério alternativo por defesa | 417 linhas, contidas na base | 382 |
| Inclusões históricas | 19 linhas/obras, contidas na base | 19 |
| OpenAlex sinalizado com publicação no período | 100 registros | 100 |
| Varredura local de título, resumo e instituições | Registros OpenAlex com nomes de IES/localidades | 359 |

A união tinha 1.530 componentes e 2.053 registros. Uma fusão adicional reduziu a união a **1.529**, preservando todos os registros. Depois da fusão, os 100 OpenAlex compartilham 24 obras com a base técnica, 19 com as inclusões históricas, uma com a fila de defesa e 96 com a varredura local. A base compartilha 70 com a varredura. A fila de defesa é subconjunto da base; não se somam 417 linhas aos 1.317 registros. As interseções par a par estão na tabela final; ausências de linha representam interseção zero.

A varredura usou as variantes institucionais e localidades explícitas no script, incluindo UFG, UEG, IFG, IF Goiano, UFJ, UFCAT, PUC Goiás, UniRV e UniEVANGÉLICA. Trata-se de complementação interna dos arquivos, sem alegação de exaustividade de nomes ou municípios. Sinais só priorizam leitura; não comprovam elegibilidade.

## Critérios aplicados e revisão individual

Tema: o PIBID, suas ações, experiências, participantes ou resultados precisam integrar o objeto/contexto investigado. Metadado de evento, biografia ou referência incidental não bastam. Natureza: formatos acadêmicos previstos no protocolo; os tipos originais, veículos e identificadores permanecem na proveniência e nas páginas arquivadas. Não houve exigência nova de revisão por pares.

Período regional: publicação de 01/01/2020 a 08/11/2026, ou defesa em 2020–2026 para tese/dissertação, pela alternativa aprovada. As datas de publicação e defesa continuam em campos próprios. Ano de publicação 2026 isolado não confirma o dia do corte. Defesa 2026 só com ano continua evidência limitada, como aprovado, sem conversão em data de publicação.

Foram corrigidas, durante a preparação, 474 exclusões que uma regra inicial indevidamente produziria por defesa antiga sem publicação conhecida: passaram a período incerto. Essa regra incorreta não foi usada no fechamento. As exclusões temporais finais requerem publicação antiga para documentos sem a alternativa de defesa, ou publicação e defesa explicitamente antigas para teses/dissertações.

Vínculo: contexto/objeto goiano **ou** afiliação de autoria a instituição goiana, documentados separadamente. Instituição associada ao depósito de uma tese não foi convertida automaticamente em afiliação nem em local da pesquisa. Uma escola denominada “Norte Goiano”, em Araguaína/TO, não foi confundida com contexto em Goiás. Referências bibliográficas goianas e metadados genéricos de eventos não comprovaram vínculo. Esses casos ficaram pendentes quando a via alternativa de afiliação continuava desconhecida.

O registro individual tem **109 entradas**: 87 da fila prioritária congelada, incluindo 19 inclusões históricas conferidas/reaproveitadas e os dois lados da fusão, mais 22 casos com período e vínculo forte que a regra temática não priorizara. Entre os 22 adicionais, 16 foram incluídos, dois excluídos e quatro ficaram pendentes. A revisão desses casos recuperou obras com participação substantiva do PIBID e evitou transformar falha da regra lexical em exclusão.

Todas as inclusões foram objeto de conferência individual ou reaproveitamento explícito da leitura histórica, com os resumos e metadados locais vinculados em [Materiais locais.csv](Materiais%20locais.csv). Não houve acesso novo a textos integrais. Aprendizagem de escolares não foi recodificada como aprendizagem docente; história de projeto não foi tomada como trajetória profissional; objetivos e expectativas não foram apresentados como resultados demonstrados.

## Identidades e reconciliação

A tese de Paula Junqueira da Silva Rezende, representada em `M2-f1063b9800fa3a1b` e `M2-4bae42ee3741323e`, foi fundida nesta última: mesmo DOI `10.14393/ufu.te.2022.620`, handle `123456789/37389`, autoria e conteúdo concordantes. Os códigos BDTD e o registro OpenAlex continuam relacionados à obra. Essa decisão resolve regionalmente a identidade ainda assinalada no estado nacional herdado; o arquivo nacional não foi modificado.

Artigo português `M2-6fc274039407a243` e capítulo inglês `M2-f5ac63d543e7078a` têm autores e resumos equivalentes, com DOIs próprios e publicação próxima. Ambos foram retirados da contagem e mantidos pendentes: a distinção obra/versão requer conteúdo específico não disponível localmente. Podem acrescentar **uma ou duas obras**, não duas automaticamente.

Foram preservados como publicações relacionadas distintas o relato em anais e o artigo sobre o barquinho, o artigo Poliges e o resumo sobre democracia escolar, e os relatos sucessivos de espaços híbridos. Têm evidências bibliográficas e conteúdos/formas diferentes registrados na tabela de relações. Não equivalem a intervenções, amostras ou participantes independentes. Tese, artigo derivado e capítulo não foram fundidos só por tratarem do mesmo projeto.

| Decisão | Componentes/obras | Registros de origem |
|---|---:|---:|
| Incluir | 97 obras | 123 |
| Excluir | 561 componentes | 906 |
| Pendente | 871 componentes | 1.024 |
| Total | 1.529 componentes | 2.053 |

As 561 exclusões são 297 por publicação anterior ao recorte, 201 por publicação **e** defesa antigas, 61 exclusões temáticas históricas sem evidência positiva conflitante e duas exclusões temáticas novas (PIBIC-EM, programa distinto; e direito registral com PIBID só no nome de evento). Exclusões regionais temporais não são exclusões nacionais.

Das 97 inclusões, 93 têm suporte por publicação completa e quatro por defesa alternativa: duas defesas de 2024, uma de 2022 e uma de 2021. Nenhuma inclusão depende só do ano de defesa 2026. Há 93 registros OpenAlex, 21 Portal CAPES, seis BDTD, dois Catálogo CAPES e um SciELO entre os 123 registros das inclusões. Quatro obras não têm registro OpenAlex neste conjunto observado. Essas contagens de proveniência não são parcelas disjuntas de obras.

## Extração dos eixos

Foram preservadas 57 extrações históricas e produzidas 234 novas, totalizando 291. Os 100 estados novos “Presente” têm trechos exatamente recuperáveis por campo e índices de caracteres. Em 11 relações IES–escola, a confirmação dependia de múltiplas frases; o localizador foi corrigido para citar o resumo integral, conforme [registro de correções](Correcoes%20de%20extracao.csv), sem confundir falha lexical com ausência de evidência.

| Eixo | Presente | Não informado | Não verificável | Denominador |
|---|---:|---:|---:|---:|
| Aprendizagem da docência e identidade profissional | 66 | 24 | 7 | 97 obras |
| Trajetórias profissionais | 6 | 87 | 4 | 97 obras |
| Relações IES–escolas–comunidades, saberes e espaços híbridos | 51 | 34 | 12 | 97 obras |

“Presente” caracteriza abordagem, objetivo, expectativa ou relato no material consultado, conforme o trecho; não é comprovação de eficácia nem causalidade. “Não informado” significa não identificado nesse material, sem afirmar ausência do fenômeno. “Não verificável” indica material insuficiente, por exemplo título sem resumo específico ou apresentação de livro inteiro que não descreve o capítulo. Não se usou o resumo genérico do livro para atribuir resultados ao capítulo. Não houve codificação de ausência comprovada do fenômeno.

Comunidades, saberes escolares/comunitários e espaços híbridos possuem campos de menção específicos no terceiro eixo. Uma parceria IES–escola não prova, por si, participação comunitária nem espaço híbrido; os campos preservam as menções efetivamente encontradas. As sínteses não autorizam inferência sobre o texto integral ou generalização para toda a produção goiana.

## Conferência interna e reprodução

Foram executadas **15 verificações internas**, todas aprovadas: hashes de seis insumos; partição; proveniência única; existência de 139 caminhos; contagem de registros por componente; quatro critérios das inclusões; preservação das 19 obras históricas; três eixos apenas para incluídas; preservação dos 57 estados históricos; reprodução exata dos 100 trechos novos “Presente”; preenchimento de fonte/localização/síntese/limite; recálculo das 498 exclusões temporais; fusão da tese; retenção das versões ambíguas; varredura dos 4.656 pares internos do corpus, sem DOI compartilhado entre componentes ou título com similaridade ≥ 0,88. Traduções exigem a revisão individual e não são detectadas por essa comparação lexical.

A [amostra de exclusões](Amostra%20de%20exclusoes.csv), semente `20261117`, contém dez exclusões temáticas históricas e seis temporais. A conferência de objeto e decisão histórica nos títulos/resumos, e das datas de origem, manteve as 16 decisões operacionais; não prova ausência de PIBID no texto integral nem mede acurácia. As duas exclusões temáticas novas e os falsos sinais geográficos foram revistos individualmente. Os seis testes de regressão focalizados passaram, cobrindo defesa antiga sem publicação, alternativa por defesa, datas antigas, corte, nome geográfico falso e localização exata de evidência.

Reprodução a partir da raiz, sem rede: `python -m scripts.executar_marco3 --atualizar`, depois `python -m scripts.fechar_marco3 --atualizar` e `python -m scripts.verificar_marco3 --atualizar`. A primeira etapa recompõe os preparatórios; o fechamento usa a fila congelada de 87 casos e verifica os identificadores da fusão. Os scripts recusam sobrescrita sem `--atualizar`; esta opção substitui somente os produtos da própria rodada. Testes: `python -m unittest discover -s tests -p test_marco3.py`. Não houve validação científica independente, nova consulta ou teste interativo em planilha.

A conferência conjunta dos testes dos marcos (`python -m unittest discover -s tests -p 'test_*marco*.py'`) também passou: **21 testes**, incluindo os seis regionais.

## Residual e limites para o Marco 4

As 871 pendências estão ordenadas: duas de identidade com tema/período/contexto sustentados, 11 com vínculo sustentado e outro critério incompleto, 858 com vínculo regional e/ou outros critérios sem comprovação. Não são uma estimativa de perdas de cobertura. As duas versões podem acrescentar uma ou duas obras; as demais só entram após comprovar todos os critérios e conferir identidade. O material específico ausente é uma limitação documental, sem impedir a conclusão das partes verificáveis. Não é necessária nova decisão geral de método para usar o corpus operacional.

Entre as inclusões, 80 têm afiliação goiana (41 também com contexto/objeto), 17 entram só por contexto/objeto. O contexto está documentado local/institucionalmente em 56, é objeto goiano com local da escola não confirmado em duas, não verificável em 32, nacional/múltiplo em seis e explicitamente fora de Goiás em uma (UNIFESSPA/Pará, incluída por afiliação UFCAT). Não se pode apresentar as 97 como 97 pesquisas realizadas em escolas goianas.

No estado nacional herdado, 78 dessas obras constam incluídas, 18 pendentes e uma elegível com identidade pendente — a tese fundida nesta rodada. As inclusões regionais não promovem automaticamente o arquivo nacional: a alternativa por defesa é regional e a nova leitura temática deve ser propagada explicitamente se a comparação exigir. Não se deve dividir 97 pelo total nacional vigente. A comparação Goiás–Brasil precisa reconciliar identidades/decisões, usar o mesmo período e regra de publicação, e separar o numerador por afiliação do recorte por contexto. Manter separadas as quatro inclusões por defesa até haver publicação comprovada para comparações baseadas em publicação.

Os indicadores futuros devem declarar o corpus observado e as pendências, a cobertura desigual das fontes, a dependência de afiliações OpenAlex, os resumos/textos específicos ausentes, a sobreposição de publicações de uma pesquisa e o alcance interno da conferência. Frequência de “Não informado” é lacuna de informação no material consultado; não é frequência de ausência do fenômeno. Nenhum indicador do Marco 4 foi produzido nesta rodada.
