# Etapa 4 — delta de elegibilidade e metadados CAPES

**Estado: concluída até o limite das evidências locais.** Não houve coleta nova, recálculo dos indicadores ou alteração da entrega anterior. Esta etapa prepara os corpora e as proveniências para a etapa de cálculo. O [manifesto de execução](Manifesto%20de%20execucao.json) identifica os caminhos vigentes e os destinos propostos das próximas etapas.

## Resultado nacional

Foram avaliados os **648 componentes herdados** alcançados pelos 665 registros CAPES conciliados: 509 incluídos, 129 pendentes e dez elegíveis com identidade pendente. Seus estados foram preservados. Não foi encontrado título novo que resolvesse a pertinência de um componente pendente, e o RIS não trouxe resumos ou conteúdo adicional capaz de alterar esse fundamento. Repetir o rótulo “Editorial” também não resolve a natureza/conteúdo acadêmico ainda pendentes nas duas obras com esse título.

A recuperação na fonte CAPES não é um critério de inclusão. Mantiveram-se decisões fundamentadas anteriormente, sem rebaixá-las por título abreviado, e sem promover pendências por frequência de recuperação. Os dez componentes herdados já elegíveis continuam fora da contagem confirmada porque a nova recuperação não resolveu suas relações de identidade residuais.

As **dez ocorrências sem identidade confirmada** passaram a componentes provisórios identificáveis, sem serem somadas ao corpus de obras únicas: três têm candidatos por metadados com divergência de autoria e sete não têm identidade local sustentada. Um componente provisório tem sinais suficientes de tema, tipo e ano, mas identidade pendente; os outros nove permanecem pendentes também por critérios não sustentados. O registro 0674, de 2026, não tem data completa para demonstrar publicação até 08/11/2026. Títulos genéricos não foram convertidos em exclusões por falta de resumo.

| Unidade | Antes desta etapa | Depois |
|---|---:|---:|
| Registros CAPES ligados a identidade conciliada | 665 | 665 |
| Registros CAPES representados em componentes provisórios | 0, em fila separada | 10 |
| Registros de proveniência no inventário nacional | 14.413 vinculados | **14.423**, incluindo dez provisórios |
| Componentes técnicos no registro nacional | 13.221 | **13.231**, incluindo dez provisórios |
| Obras nacionais incluídas | 7.779 | **7.779** |
| Novas obras confirmadas ou promoções a inclusão nesta etapa | — | **0** |
| Novas exclusões nacionais nesta etapa | — | **0** |

As 14.423 ocorrências reconciliam com 13.748 originais + 675 CAPES. O registro final contém 7.779 incluídas, 286 elegíveis com identidade pendente e 5.166 pendentes. Os dois últimos grupos não são obras confirmadas. “Componente provisório” não significa que se provou a existência de uma obra distinta daquelas já incluídas.

A única redução desde a entrega de 7.780 é a fusão bibliográfica concluída na etapa anterior para “Quero ser professora”. Esta etapa não promoveu nem excluiu obras; acrescentou representação rastreável e avaliação de critérios para as ocorrências ainda sem identidade.

## Metadados e evidências reaproveitados

Foram registrados **198 casos de variantes/divergências de metadados**, em [tabela própria](Divergencias%20de%20metadados.csv). Uma variante não é necessariamente um erro: nomes abreviados, ordens de sobrenomes e subtítulos podem representar o mesmo objeto. A tabela preserva títulos, autoria literal na proveniência, anos e DOIs por fonte; os nomes canônicos e créditos anteriores não foram substituídos a partir de AU concatenado.

“Práticas de leitura” conserva publicação sustentada em 2013. O ano 2019 do RIS permanece no campo de origem e no conjunto de anos observados, sem alterar silenciosamente o ano usado para os indicadores. Os demais conjuntos de anos do corpus anterior, inclusive suas divergências já documentadas, também foram preservados. A nova coluna `anos_publicacao_observados` não substitui `anos_publicacao`, que continua sendo a entrada temporal sustentada das obras.

No registro Cury 0134, o DOI com prefixo repetido continua em `doi_original_normalizado`; o valor sustentado pelo título e pelo snapshot foi explicitado em `doi_para_correspondencia`, com justificativa em `ajuste_de_chave`. DOI adicional não é considerado válido apenas porque a identidade da obra foi vinculada. As três divergências de autoria da fila permanecem como alertas também nos componentes candidatos, sem mudança dos créditos ou da elegibilidade anterior.

As regras temáticas da v1.3 foram reaproveitadas, com o [adendo v1.4](../../../../Protocolo%20de%20busca%20bibliom%C3%A9trica%20-%20v1.4%20integra%C3%A7%C3%A3o%20CAPES.md) registrando a execução. Os filtros Artigo/Editorial e produção nacional da consulta CAPES não foram aplicados retroativamente ao corpus inteiro. As datas de coleta CAPES (16/11/2026) e OpenAlex (15/11/2026) permanecem separadas do corte de publicação (08/11/2026).

## Revisão goiana

Foram preservadas **97 inclusões, 291 extrações e 871 pendências regionais**. Os 62 componentes regionais com recuperação CAPES já estavam no universo regional examinado. A varredura de novos sinais por título e instituições não encontrou candidato goiano adicional entre os demais registros vinculados.

A ponte da fusão de “Quero ser professora” remapeou um componente regional excluído por publicação anterior a 2020, sem mudar seu resultado. Foram acrescentados **65 registros de proveniência regional**: 64 recuperações CAPES e um registro OpenAlex anteriormente separado da entrada SciELO agora conciliada. O total regional passou de 2.053 para **2.118 registros**, com os mesmos 1.529 componentes e 97 inclusões.

Uma [fila adicional de transferência](Fila%20de%20transferencia%20regional.csv) conserva as dez ocorrências provisórias: quatro têm ano de publicação anterior a 2020 e seis ficam pendentes para exame regional. Isso não equivale a dez obras novas, nem a dez pendências adicionadas às 871. O vínculo goiano não foi comprovado nesses registros. As quatro inclusões anteriores por defesa e a dúvida artigo/capítulo permanecem com seus estados e limitações anteriores.

As três extrações por obra foram copiadas sem nova leitura ou mudança de estado. Falta de informação continua distinta de evidência insuficiente; nenhuma informação ausente foi tratada como ausência do fenômeno.

## Arquivos e conferências

- [Corpus nacional](Corpus%20nacional.csv), [registro de decisões](Registro%20de%20decisoes.csv) e [proveniência completa](Proveniencia.csv).
- [Delta de elegibilidade](Delta%20de%20elegibilidade.csv), [componentes provisórios](Componentes%20provisorios%20CAPES.csv) e [pendências CAPES](Pendencias%20CAPES.csv).
- [Corpus goiano](Corpus%20goiano.csv), [decisões regionais](Decisoes%20regionais.csv), [proveniência regional](Proveniencia%20regional.csv) e [três eixos](Tres%20eixos.csv).
- [Verificações e hashes](Verificacoes.json) e [manifesto para a próxima etapa](Manifesto%20de%20execucao.json).

As verificações executáveis confirmaram as 675 ocorrências CAPES inventariadas, 14.423 identificadores únicos de proveniência, soma de registros por componente, 13.231 componentes, 7.779 inclusões, preservação das 97 inclusões regionais e das 291 combinações obra/eixo/estado, 871 pendências regionais e ausência de novo sinal regional não tratado. Os insumos foram reconferidos por SHA-256; o RIS original coincide com a cópia arquivada e com o hash da primeira fase. Passaram **sete testes específicos do delta e 31 testes anteriores dos marcos**. As conferências são internas, não validação independente.

Reprodução: `python -m scripts.avaliar_delta_capes_20261116`. O script recusa sobrescrita; `--atualizar` refaz somente os produtos desta etapa, a partir da conciliação e dos dados regionais preservados. Os documentos de interpretação são versionados separadamente.

## Encaminhamento

O próximo trabalho é recalcular a cobertura, os indicadores e as respostas afetadas usando o manifesto, mantendo a entrega anterior intacta. As frações 196/7.780 e 67/3.459 continuam sendo a linha de base anterior, não resultados recalculados para o corpus incremental. A participação total continua não estimável; contexto e afiliação precisam permanecer separados.

O relatório metodológico substituto deverá distinguir: 647 coincidências nominais de ID no snapshot, 665 vínculos bibliográficos de recuperação, dez ocorrências provisórias e a sobreposição por obras elegíveis a ser calculada. Esses números não compartilham a mesma unidade. Não foram geradas novas planilhas/gráficos nem um novo pacote final nesta etapa.
