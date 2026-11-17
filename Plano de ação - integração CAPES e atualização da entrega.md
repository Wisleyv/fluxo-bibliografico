# Plano de ação — integração CAPES e atualização da entrega

**Data: 16/11/2026. Estado: proposta de execução, fundamentada em diagnóstico local concluído.** A integração científica e a atualização da entrega ainda não foram executadas. A versão concluída do Marco 5 permanece preservada em `dados/entregas/marco5/`.

## Objetivo e abordagem

Integrar o [novo RIS CAPES](dados/CAPES-concatenado.ris) à pesquisa prevista em [Vaneria.txt](Vaneria.txt), preservando identidades, decisões, proveniências e análises já sustentadas. Adotar **integração incremental por obra**, com o OpenAlex e as demais fontes existentes mantidos no acervo, e o Portal CAPES registrado como fonte própria de recuperação.

Não substituir o corpus nacional pelos resultados CAPES, não restringir o corpus à interseção CAPES–OpenAlex e não somar registros como novas obras. A CAPES já era fonte prevista e utilizada parcialmente; a novidade é uma rodada de recuperação mais ampla, não uma mudança geral dos critérios acadêmicos ou temáticos.

O [diagnóstico detalhado](dados/analises/capes_20261116_avaliacao/Avaliacao%20da%20integracao%20CAPES.md) encontrou 675 registros, 673 artigos e dois editoriais, 675 IDs W e 633 DOIs distintos. Não há resumos, palavras-chave, afiliações ou datas completas em campos próprios. Há 658 títulos normalizados e 17 grupos repetidos; isso não é deduplicação de obras.

## Base demonstrada para dimensionar o trabalho

| Resultado preliminar | Unidade | Consequência |
|---|---|---|
| 647 IDs já no snapshot OpenAlex | Registros RIS | Reaproveitar metadados e decisões; não afirmar independência de cobertura |
| 601 correspondências por identificador sem divergência detectada nos campos comparados | Registros | Caminho prioritário de conciliação em lote, com controles |
| 51 com divergência | Registros | 45 títulos, cinco DOIs e um ano; priorizar efeito material |
| 25 das 45 diferenças de título são prefixos/subtítulos com ID, DOI, ano e autoria concordantes | Registros | Regra objetiva em lote, com amostra; evitar 25 releituras sem necessidade |
| 15 somente por título | Registros | Não fundir sem suporte; reaproveitar aliases e pareceres anteriores |
| 8 sem correspondência estrita | Registros | Um recupera candidato por limpeza de DOI anexado ao título; sete continuam sem candidato nesse exame adicional |
| 651 componentes candidatos alcançados | Componentes atuais | 512 incluídos, 129 pendentes, dez elegíveis com identidade pendente; não são 651 confirmações |
| 26 dos 103 controles CAPES anteriores com candidato na nova consulta | Registros de controle | Preservar os 77 restantes; filtros/data distintos não invalidam o histórico |
| 62 componentes regionais alcançados | Componentes atuais | 12 incluídos, 11 pendentes, 39 excluídos; reaproveitar estados e rever somente evidência relevante |

Os grupos não são todos aditivos: 25 é subconjunto de 51, e os 62 regionais estão no acervo já comparado. O [arquivo por registro](dados/analises/capes_20261116_avaliacao/Registros%20e%20correspondencias.csv) é a referência para executar e reconciliar o trabalho.

## Premissas e decisões para a execução

1. **Corte de publicação:** manter 08/11/2026 na atualização recomendada; anotar CAPES coletada em 16/11 e OpenAlex em 15/11. Se for desejada publicação até 16/11, aprovar outra versão de corte e atualizar os dois lados da comparação; não alterar apenas CAPES.
2. **Escopo da busca CAPES:** a URL tem Artigo/Editorial e `national_production=1`. Registrar esses filtros literalmente. Eles não provam completude do Portal nem autorizam retirar do corpus obras sem afiliação brasileira. Verificar se houve escolha intencional dos filtros; se a meta for declarar busca CAPES sem essas restrições, é necessária evidência adicional ou uma recuperação específica autorizada. Isso não impede integrar o lote fornecido como conjunto filtrado.
3. **Paginação:** registrar 23 páginas como declaração do fornecedor. Não atribuir automaticamente cada grupo de 30 registros a uma página comprovada. Se houver exportações individuais, manifesto, total exibido ou capturas já disponíveis, anexá-los; se não houver, manter a limitação de cobertura da paginação.
4. **Unidade e critérios:** conservar obra acadêmica única, pertinência substantiva, tipos já aprovados e período nacional/regional; edição de metadado não é autorização para mudar elegibilidade. Editorial é formato acadêmico possível, mas não inclusão por rótulo.
5. **Geografia:** separar contexto e afiliação goiana; o filtro de produção nacional da interface não comprova afiliação brasileira ou goiana. Ausência de campo não é exclusão.
6. **Histórico e validação:** preservar o Marco 5 como versão anterior; produzir revisão paralela. Conferência interna não é validação independente. Nenhuma coleta ampla é condição inicial deste plano.

Os itens 1–3 precisam constar do manifesto e do protocolo atualizado. Só há decisão metodológica nova indispensável se se pretender mudar o corte ou declarar um escopo de coleta diferente do realmente documentado. As regras já aprovadas não precisam ser submetidas novamente à aprovação.

## Etapa 1 — Congelar a versão anterior e registrar a rodada CAPES

**Ações:** conservar a entrega e seu inventário; registrar hash do RIS, data informada, consulta exata, URL e filtros, quantidade observada, páginas declaradas e lacunas. Criar um manifesto único da nova execução com os diretórios dos corpora de entrada e de saída. Propor adendo v1.4 do protocolo, sem alterar a v1.3.

Arquivar uma cópia byte a byte em `dados/brutos/portal-capes/portal-capes__nacional-filtrado__20261116__RIS.ris`, conferindo igualdade de hash e preservando `dados/CAPES-concatenado.ris`. O empacotador vigente não inclui automaticamente um RIS colocado diretamente em `dados/`; a cópia arquivada ou o caminho explícito do manifesto precisa constar do novo pacote.

**Saídas:** manifesto da rodada CAPES; inventário de entrada; protocolo/adendo que distingue data de coleta, corte de publicação e escopo da consulta. Usar como ponto de partida `dados/analises/capes_20261116_avaliacao/Auditoria.json`.

**Conclusão:** 675 ocorrências identificáveis e rastreáveis ao mesmo bruto; a entrega original continua utilizável e reproduzível. Falta de exportações por página fica documentada, sem inventar paginação.

## Etapa 2 — Normalizar e conciliar em lote

**Ações:** reutilizar `_parse_ris` e os normalizadores, preservar valores originais e criar chaves comparativas. Usar IDs estáveis por rodada/posição/hash; manter ID W como identificador bibliográfico, não como indicação de que a recuperação veio do OpenAlex. Não dividir cegamente AU por vírgulas nem contar uma cadeia concatenada como uma única pessoa.

Conciliar, nesta ordem, identidade confirmada anterior/aliases, ID, DOI, título e metadados auxiliares. Incluir aliases DOI/PID já sustentados nas revisões anteriores, que não estão necessariamente no campo principal de proveniência. Registrar cada recuperação CAPES como proveniência adicional, mesmo quando a obra já tem fonte Portal em outra rodada; contar a obra uma vez.

Aplicar a regra proposta aos 25 prefixos/subtítulos: mesmo ID e DOI, mesmo ano e tokens de autoria, título prefixo exato com pelo menos cinco palavras. Preservar títulos completos de cada origem e conferir uma amostra determinística. Não usar igualdade de título isolada para fundir os 17 grupos internos, especialmente “Editorial”.

**Saídas:** registros normalizados, ponte registro→obra, aliases, decisões de identidade com regra/evidência, grupos internos e fila residual. Os 675 registros não se tornam 675 novas unidades. Em contagem bruta de proveniências, 13.748 + 675 = 14.423 ocorrências antes de qualquer ajuste excepcional documentado; deduplicação lógica não apaga ocorrências de origem.

**Conclusão:** todo registro tem ligação sustentada ou pendência justificada; IDs e DOIs conflitantes não unem componentes por transitividade automática.

## Etapa 3 — Resolver apenas as identidades com efeito material

**Prioridades concretas:**

- `CAPES20261116:0029`, “Quero ser professora”: esclarecer se dois componentes já incluídos são a mesma obra por DOI alternativo. Pode reduzir o total nacional; não apenas acrescentar registros.
- `0048/0094`, “Práticas de leitura”: reaproveitar a conferência de PID do fechamento do Marco 2, acrescentar aliases e esclarecer ano 2019 versus publicação arquivada em 2013. Não reiniciar a revisão já sustentada.
- `0134`, Cury: validar a remoção do DOI anexado ao título para comparação e o prefixo DOI repetido. Há candidato local já identificado; preservar o erro de origem na proveniência.
- As outras diferenças de DOI e títulos não resolvidas pela regra objetiva: confrontar autoria, veículo, volume/número/páginas e localizações arquivadas somente quando puderem fundir/separar obras ou mudar tipo/ano.

**Saídas:** log das fusões, manutenções como obras distintas, reparos de chave e pendências. As evidências iniciais estão em [Variantes e prioridades](dados/analises/capes_20261116_avaliacao/Variantes%20e%20prioridades%20bibliograficas.csv).

**Conclusão:** nenhum identificador novo altera uma identidade anterior sem justificativa; casos que dependam de texto ou fonte indisponível ficam separados dos totais confirmados conforme a regra vigente. Não exigir validação externa geral para terminar os demais casos.

## Etapa 4 — Elegibilidade e atualização incremental dos corpora

**Nacional:** reaproveitar inclusões e exclusões sustentadas quando a identidade está estável. Nos 129 componentes pendentes e dez com identidade pendente alcançados pelo diagnóstico, reabrir apenas o critério que recebeu evidência nova ou cuja inconsistência foi demonstrada. Recuperação no Portal, por si, não resolve tema ou natureza acadêmica. Nos candidatos sem vínculo sustentado, aplicar tema/tipo/período com evidência arquivada, começando pelo título e depois pelos resumos já disponíveis.

O lote tem 359 títulos que satisfazem a regra temática preliminar existente e 316 que não bastam por título; isso não significa 359 inclusões ou 316 exclusões. Ausência de resumo no RIS não exclui, e título genérico não autoriza atribuir o PIBID como objeto. O registro `0674`, de 2026 e sobre IA/desinformação, requer tema e data completa. Só propor consulta pontual adicional se uma lacuna material persistir depois do exame local, com fonte, custo e resultado esperado definidos.

**Goiás:** cruzar o delta com a ponte do Marco 3. Para as 12 inclusões já alcançadas, acrescentar proveniência sem refazer eixos quando não houver mudança de evidência. Rever as 11 pendências e exclusões somente se a nova evidência alterar seu fundamento; exclusão temporal regional não é exclusão nacional. Novas obras entram na revisão apenas com tema, natureza, período e contexto ou afiliação goiana sustentados. Extrair os três eixos somente de novas inclusões ou obras cuja evidência mudou, preservando as 291 extrações anteriores e as quatro inclusões por defesa.

**Saídas:** corpora nacional/regional revisados, proveniência completa, delta de composição e fila residual atualizada, em `dados/analises/integracao_capes_20261116/`. Publicar saldo em unidades separadas: registros novos, obras novas, promoções de pendentes, fusões entre inclusões, exclusões justificadas, alterações de ano/tipo, eixos novos e pendências.

**Conclusão:** justificar cada mudança de composição. O novo N não será “7.780 + 675”: depende de inclusões novas/promovidas, fusões entre obras incluídas e eventuais exclusões sustentadas. Reclassificação de registro ligado à mesma obra não aumenta N.

## Etapa 5 — Recalcular cobertura, indicadores e respostas afetadas

**Cobertura:** preservar a matriz histórica do Marco 1. Criar medição própria dos 675 registros, com as quatro categorias e denominadores explícitos. Os 647 IDs encontrados são sobreposição nominal, não 647 identidades validadas. Distinguir “não recuperado na consulta OpenAlex arquivada” de “inexistente no OpenAlex”. Acrescentar matriz por fonte, período e tipo e sobreposição das obras elegíveis por fonte, com a nova rodada CAPES identificável. Não somar duas recuperações da mesma obra como duas obras CAPES.

**Indicadores:** reutilizar os geradores do Marco 4, aceitando o manifesto de caminhos da execução. Atualizar séries, tipos, autoria, instituições, geografia e cobertura apenas conforme metadados sustentados. Guardar anos conflitantes; não substituir afiliação pela marca de produção nacional do Portal. Não reintroduzir instituições nos créditos de pessoas ao processar AU. Preservar a origem algorítmica das temáticas OpenAlex e a origem dos eixos canônicos; a falta de KW/AB no RIS não cria classificação temática nova.

**Comparação Goiás–Brasil:** recalcular numeradores e denominadores no mesmo corpus e período. Os valores **196/7.780 (2,52%)** e **67/3.459 (1,94%)** são a linha de base anterior, não resultados da integração. Só mantê-los na nova entrega se a reconciliação demonstrar que não mudaram; caso contrário, exibir antes/depois e motivo. Continuar chamando-os de frações observadas de afiliação goiana identificada. A participação total permanece não estimável enquanto a recuperação/afiliação incompletas não permitirem outra conclusão. Contexto continua separado de afiliação.

**Síntese:** atualizar as seis subquestões na mesma ordem de `Vaneria.txt`, somente onde composição, evidência ou indicador mudou; referenciar o delta. Preservar as limitações e conferir o estado das 871 pendências regionais e da dúvida artigo/capítulo, sem presumir que este lote as resolveu.

**Conclusão:** tabelas de cobertura e indicadores reconciliadas ao novo corpus; estados consolidado no corpus observado, parcial e não estimável explícitos.

## Etapa 6 — Regenerar a entrega como nova versão e conferir

Gerar em `dados/entregas/marco5_capes_20261116/`, mantendo `dados/entregas/marco5/` intacto. Reaproveitar os scripts da entrega, acrescentando somente parametrização de caminhos por manifesto, com os padrões vigentes preservados; não duplicar o conjunto de scripts ou refazer arquitetura. A parametrização é necessária porque os geradores atuais apontam a diretórios fixos dos marcos anteriores.

| Produto anterior | Atualização necessária |
|---|---|
| Planilha simplificada e gráficos nativos | Nova união de obras por IDs persistentes; pertencimento a cada corpus; fórmulas e séries ligadas às novas tabelas; notas de limites |
| Base técnica separada | RIS/manifesto, registros da nova rodada, proveniência, aliases, decisões, delta e pendências; fontes anteriores preservadas |
| Matriz de cobertura/sobreposição | Versão histórica mantida e nova rodada separada; sobreposição elegível recalculada |
| Relatório metodológico | Consulta/filtros reais, datas, normalização e conciliações efetivamente executadas; contribuição e limites da CAPES |
| Síntese das seis subquestões | Indicadores e evidências atualizados, com identificação dos resultados alterados |
| Pacote reproduzível | Novo bruto, protocolo/adendo, manifestos de execução, consultas, scripts, logs, inventário/hashes e instruções; versão anterior preservada |

Executar os testes relevantes já existentes e novos casos indispensáveis: entidades HTML, DOI alternativo/repetido, título genérico, subtítulo, múltiplas rodadas por obra, ano 2026 sem dia, reparo de alias e não regressão das decisões históricas. Reconciliar registros, pares, componentes, obras, créditos e eixos em suas unidades; testar unicidade, totais, pesos e compatibilidade dos dois denominadores. Recalcular no Excel, verificar tabelas/filtros/ZIP/erros de fórmula, editabilidade e referências dos gráficos; revisar visualmente cada gráfico e sua nota.

Conferir a reconstrução dos indicadores e produtos a partir de uma extração nova do pacote, sem rede, comparando tabelas e valores recalculados. Só gerar o pacote final após congelar os corpora e revisar gráficos, para evitar reempacotamentos sem alteração científica. Se possível, usar um conjunto leve de trabalho para os testes e empacotar o bruto integral uma vez ao final.

**Conclusão da integração:** todos os 675 registros têm destino rastreável; nenhuma inclusão ou fusão é silenciosa; o saldo e as proveniências reconciliam; a nova entrega é reconstruível; nenhuma alegação de completude excede o escopo documentado. Pendência científica justificada não impede entregar as partes concluídas.

## Controle de esforço e limites

Primeiro executar correspondências e variantes objetivas; depois rever identidades que alterem N ou séries; em seguida processar somente o delta de elegibilidade e eixos; gerar planilhas/gráficos uma única vez após o congelamento. Não reler individualmente todas as 675 obras, não reprocessar semanticamente 12.431 OpenAlex e não exigir nova coleta para lacunas que os arquivos existentes resolvem.

A inclusão desta rodada é recomendada para aderência à fonte prevista no documento canônico. A declaração de **completude** deve continuar qualificada: o arquivo é um conjunto CAPES filtrado, com paginação declarada e metadados limitados. O atendimento integral à estratégia de todas as fontes previstas não é demonstrado apenas pela integração deste RIS.
