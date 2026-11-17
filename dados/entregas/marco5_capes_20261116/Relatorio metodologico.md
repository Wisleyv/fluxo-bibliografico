# Relatório metodológico — entrega incremental CAPES, 16/11/2026

Esta versão substitui, para a leitura dos resultados integrados, o relatório da entrega anterior, que permanece preservado em `../marco5/`. O corpus nacional operacional tem **7.779 obras**, a revisão goiana **97 obras** e a união da planilha **7.798 obras únicas**: 7.779 + 97 − 78 correspondências. Os resultados estão consolidados dentro dos conjuntos observados, mas são parciais em relação ao universo da produção; a participação total de Goiás é não estimável.

## Fundamentos, escopo e datas

Aplicaram-se [Vaneria.txt](../../../Vaneria.txt), o protocolo vigente v1.3 e o [adendo v1.4 de integração CAPES](../../../Protocolo%20de%20busca%20bibliom%C3%A9trica%20-%20v1.4%20integra%C3%A7%C3%A3o%20CAPES.md), sem reabrir as decisões aprovadas. Produção brasileira designa o conjunto nacional de obras acadêmicas elegíveis sobre o PIBID recuperadas nas fontes previstas; metadados geográficos ausentes não constituem motivo autônomo de exclusão. Goiás é um recorte, com contexto e afiliação registrados separadamente. A unidade analítica é a obra acadêmica única, não o registro de fonte, o DOI isolado ou o par candidato.

O panorama usa publicação de 01/01/2007 a **08/11/2026**; a revisão regional, 2020–2026, conserva quatro inclusões pelo critério alternativo de defesa aprovado. A coleta OpenAlex é de **15/11/2026** e a CAPES de **16/11/2026**. Essas datas descrevem recuperação; não mudam o corte de publicação nem reconstituem retrospectivamente os índices em 08/11. O ano de 2026 é incompleto. A coleta CAPES tardia foi incorporada de modo incremental, mantendo as consultas e os resultados históricos identificáveis.

## Recuperação CAPES e alinhamento à proposta

Incorporou-se a exportação fornecida pelo pesquisador da busca por “PIBID” OR “Programa Institucional de Bolsa de Iniciação à Docência” no Portal de Periódicos CAPES. A consulta informada usou 2007–2026, Artigo/Editorial, `national_production=1` e 30 resultados por página. A concatenação de 23 páginas é declarada; o RIS não identifica cada página, portanto não comprova a completude da paginação. A URL integral, os campos e os hashes estão na [auditoria da recuperação](../../analises/capes_20261116_avaliacao/Auditoria.json). O [RIS recebido](../../CAPES-concatenado.ris) e sua cópia bruta arquivada foram preservados; SHA-256: `c038becb3017fb6c0ff4293aed6e4469bc1824dcd7f14b7034b0775537e98124`.

São 675 registros: 673 artigos e dois editoriais segundo o exportador. Esses tipos de origem não dispensam a avaliação acadêmica e temática. O filtro de produção nacional da interface caracteriza a recuperação, não foi convertido em requisito geral de afiliação brasileira. O RIS não oferece resumos, palavras-chave, afiliações ou datas completas em campos próprios. Não se inferiu afiliação brasileira ou goiana desse filtro. Autorias concatenadas não foram separadas automaticamente em pessoas.

A recuperação foi atribuída ao Portal, enquanto o OpenAlex continuou como fonte operacional e de enriquecimento arquivado. Assim, atende-se à incorporação formal do Portal prevista no documento canônico, sem alegar que sua cobertura integral ou todas as buscas canônicas tenham sido completadas. Não houve nova coleta nesta etapa de entrega, tampouco execução adicional do Google Acadêmico. A mudança de fontes, os filtros e as datas diferentes limitam a comparabilidade; não é possível tratar os índices como amostras independentes ou medir sua completude nacional com estes dados.

## Conciliação, elegibilidade e proveniência

Reutilizaram-se os corpora congelados, as decisões de identidade, os controles históricos, a triagem regional e as extrações dos marcos anteriores, seguidos pelas etapas bibliográfica, de elegibilidade e de indicadores da integração. Identidades sustentadas foram reunidas por obra com todas as proveniências. Nos 49 casos bibliográficos antes em aberto, 39 foram vinculados e dez permaneceram residuais. A [revisão por registro](../../analises/integracao_capes_20261116/conciliacao/Revisao%20dos%2049%20registros.csv) conserva justificativas e referências.

A fusão de duas inclusões de “Quero ser professora” reduziu o corpus de 7.780 para 7.779. Concordaram título, três autoras, publicação em 2016, dados bibliográficos e PID SciELO `S2176-66812016000100031`; ambos os DOIs aparecem nas localizações OpenAlex arquivadas. O identificador anterior foi mantido como ponte para `M2-a279c6aac5c92b01`. Não se eliminaram registros de origem e não houve inclusão nacional nova confirmada. O total de artigos passou de 5.968 para 5.967 e o de 2016 de 575 para 574. A fusão precede 2020 e não altera o denominador comum de 3.459.

“Práticas de leitura” mantém publicação sustentada em 2013, com o valor CAPES 2019 preservado como discordância de origem. O DOI de Cury com prefixo repetido foi tratado por chave normalizada de comparação, preservando o campo original. Dois casos nacionais continuam sem ano unívoco (2011/2012 e 2022/2025): contam no corpus, mas ficam separados da curva anual, que soma 7.777 obras. As comparações e as filas estão no [relatório do delta](../../analises/integracao_capes_20261116/elegibilidade/Relatorio%20do%20delta%20de%20elegibilidade.md).

Os 675 registros novos reconciliam como 665 vinculados mais dez provisórios. A proveniência nacional contém **14.423 registros**; o registro de decisões, **13.231 componentes**, incluindo 7.779 inclusões, 286 elegíveis com identidade pendente e 5.166 pendentes. Componentes pendentes não são obras confirmadas. Das dez ocorrências CAPES provisórias, uma é elegível com identidade pendente e nove permanecem pendentes: três divergências de autoria (0161, 0249, 0651) e sete identidades não sustentadas (0421, 0623, 0635, 0644, 0672, 0674, 0675). Nenhuma foi promovida automaticamente ao corpus. A fila regional adicional distingue quatro ocorrências anteriores a 2020 e seis pendentes; não são dez obras novas e não se somam automaticamente às 871 pendências regionais.

## Sobreposição CAPES–OpenAlex: unidades e denominadores

| Medida | Resultado observado | Interpretação |
|---|---:|---|
| Coincidência nominal de IDs | 647/675 (95,85%) | Não equivale a identidade bibliográfica validada |
| Vínculos bibliográficos com o acervo | 665/675 | 664 com snapshot OpenAlex e um com controle sem registro nessa consulta |
| Confirmados com snapshot sobre denominador verificável | 664/671 (98,96%) | Revisões e caso temporal não verificável fora do denominador |
| Confirmados sobre todas as recuperações | 664/675 (98,37%) | Mantém todos os estados no denominador |
| Obras elegíveis recuperadas pelo novo lote | 509 | Obras já incluídas; não são novas inclusões |
| Obras elegíveis com Portal na união de rodadas | 571 | 83 anteriores + 509 atuais − 21 comuns |

As quatro categorias por registro são: 664 confirmados, três em revisão, sete não recuperados no snapshot e um temporalmente não verificável. Assim, 675 − 3 − 1 = 671 registros verificáveis. “Não recuperado” se refere à consulta arquivada, não à ausência no índice inteiro. Os casos em revisão não foram contados como correspondências confirmadas. Todas as categorias permanecem na matriz por período e tipo documental.

No corpus elegível nacional de 7.779 obras, a interseção OpenAlex–Portal tem 571 obras; 7.206 têm OpenAlex sem Portal; nenhuma tem Portal sem OpenAlex; duas vêm de outras fontes sem essas duas. São conjuntos disjuntos cuja soma é 7.779. As 488 novas atribuições ao Portal (509 − 21) acrescentam proveniência, sem acrescentar obras elegíveis. Exclusividade relativa às duas fontes não significa exclusividade diante de BDTD, SciELO ou Catálogo. As interseções de fontes não podem ser somadas como obras únicas.

Na proveniência integrada, o Portal tem 778 registros (103 históricos + 675 novos), abrangendo também pendências. Esse número não deve ser confundido com 571 obras elegíveis. As medições históricas dos 1.317 controles foram preservadas em abas próprias e não receberam rótulo de cobertura corrente. Consulte a [matriz final](Matriz%20de%20cobertura%20e%20sobreposicao.xlsx), seus [CSV](matriz/) e o [relatório dos indicadores e da sobreposição](../../analises/integracao_capes_20261116/indicadores/Relatorio%20dos%20indicadores%20e%20sobreposicao%20CAPES.md).

## Indicadores, pesos e participação goiana

A [planilha](Planilha%20final%20PIBID.xlsx) reúne uma linha por obra da união, indicadores, 291 extrações e seis gráficos nativos ligados a células editáveis. As regras detalhadas e as respostas, na ordem canônica, estão na [síntese das seis subquestões](Sintese%20das%20seis%20subquestoes.md). Contagem integral de autoria atribui uma ocorrência a cada pessoa identificada por obra; a fracionária distribui uma unidade entre as pessoas observadas. Instituições e países são contados uma vez por obra por entidade distinta, mesmo com vários autores; a fração distribui uma unidade entre as entidades observadas. Coautoria e múltiplas afiliações tornam as contagens integrais não aditivas. Créditos não identificados não foram inventados.

Há autoria informada em 7.752 obras: 6.198 com coautoria observada, 1.554 com uma autoria e 27 sem autoria. A afiliação é conhecida em 3.024 obras, parcial em 1.485 e desconhecida em 3.270; “conhecida” refere-se às autorias observadas, sem garantir completude externa. Instituições/países mapeados alcançam 4.228 obras. A revisão regional tem 51/34/12 nesses estados de afiliação. Tópicos e palavras-chave OpenAlex são classificações algorítmicas, disponíveis em 7.777 obras nacionais, não categorias atribuídas pelos autores nem os três eixos qualitativos. Distribuição integral por UF/região, grupos de pesquisa e redes consolidadas não foram estimados sem suporte suficiente. Rankings e distribuição são parciais à cobertura desses campos.

As frações de obras com **afiliação goiana identificada** são **196/7.779 (2,52%)**, em publicação 2007–08/11/2026, e **67/3.459 (1,94%)**, no período comum de publicação 2020–08/11/2026. Numerador e denominador de cada fração pertencem ao mesmo corpus nacional, com os mesmos tipos e regras. Não são estimativas da participação total: esta permanece **não estimável**, por afiliações incompletas e cobertura/pendências não resolvidas. O valor histórico 196/7.780 aparece somente como linha de base anterior.

A revisão goiana tem 80 obras com afiliação goiana, separadas de 56 com contexto local/institucional documentado, duas com objeto goiano e local escolar não confirmado, 32 com contexto desconhecido, seis nacionais/múltiplas e uma com contexto externo (Pará, vínculo UFCAT). Não se usa 97/7.779 como participação nacional. Das 97 regionais, 78 correspondem ao corpus nacional e 19 ficam fora de sua elegibilidade, incluindo as quatro por defesa.

## Revisão de escopo e alcance dos eixos

Preservaram-se 97 inclusões, 871 pendências regionais anteriores, 2.118 registros de proveniência regional e 291 extrações (97 × três eixos), sem nova leitura ou reclassificação qualitativa nesta etapa. Das 97, 93 entram por publicação e quatro por defesa. A dúvida de identidade entre artigo e capítulo e as versões pendentes podem alterar a contagem após validação; não foram resolvidas por conveniência estatística.

| Eixo | Presente | Não informado | Não verificável |
|---|---:|---:|---:|
| Aprendizagem da docência / identidade profissional | 66 | 24 | 7 |
| Trajetórias profissionais | 6 | 87 | 4 |
| Relações IES–escolas–comunidades | 51 | 34 | 12 |

Cada extração conserva obra, síntese, fonte, localização e estado da evidência. Informação não encontrada não demonstra ausência do fenômeno; evidência insuficiente não sustenta conclusão negativa. As 871 pendências podem alterar distribuição e síntese e impedem apresentar os 97 como universo regional completo. As quatro defesas não foram misturadas com ano de publicação nos gráficos nem usadas indevidamente nas proporções nacionais. A interpretação deve acompanhar essas ressalvas em qualquer reutilização dos indicadores.

## Entrega e conferência interna

Foram reaproveitados os dados científicos e as verificações dos marcos anteriores e da integração; foram gerados novamente, em diretório paralelo, a planilha, a matriz, a base técnica e os gráficos, e atualizadas a síntese transportada, a documentação metodológica e as instruções de reconstrução. A entrega original não foi sobrescrita. A [base técnica separada](Base%20tecnica%20PIBID.zip) contém corpora, decisões, proveniências e tabelas; o [pacote reproduzível](Pacote%20reproduzivel%20PIBID.zip) acrescenta consultas, protocolos, brutos, scripts, testes, logs e inventário. O roteiro de reconstrução é [REPRODUZIR_INTEGRACAO_CAPES.md](../../../REPRODUZIR_INTEGRACAO_CAPES.md).

Foram aprovadas 25 verificações gerais dos indicadores e 13 específicas da integração, além de 54 testes relevantes (31 dos marcos, dez de indicadores CAPES, sete do delta e seis da entrega). As [19 conferências da entrega](Conferencias%20da%20entrega.csv) verificam unicidade, 11 fórmulas de conferência recalculadas no Excel, denominadores, séries, tipos, eixos, integridade ZIP/XML, tabelas/filtros, ausência de erros Excel, referências de seis gráficos nativos e reconciliação da proveniência CAPES. A [conferência visual](Conferencia%20visual.csv) registra a inspeção dos seis PNGs exportados: títulos e notas legíveis, eixos, legendas, valores e ressalvas compatíveis com as tabelas. Os gráficos continuam como objetos editáveis no XLSX; PNG/PDF são prévias auxiliares.

O [teste de reconstrução](Teste%20de%20reconstrucao.json) documenta a extração em diretório novo, hashes dos membros, execução local sem rede, identidade das tabelas CSV e dos valores de todas as abas dos dois XLSX após recálculo nativo. Metadados binários e logs podem variar. O inventário e a [verificação externa do pacote](Verificacao%20do%20pacote.json) explicitam o ZIP testado e a relação com o ZIP final. A reprodução parte de corpora e decisões congelados, não reproduz uma coleta remota histórica nem constitui validação científica independente. Windows e Excel local são requisitos para o recálculo/renderização nativos; seus executáveis não são distribuídos.

As correções materiais desta entrega foram a propagação do denominador nacional 7.779 e da fusão para tabelas, fórmulas, séries e documentação, a separação explícita dos três níveis de sobreposição e a inclusão das novas proveniências sem inflar o corpus. As limitações científicas residuais permanecem identificadas; sua confirmação externa não foi realizada. O encerramento operacional da entrega não converte resultados parciais ou não estimáveis em consolidados.
