# Segundo lote de leituras bilíngues do Catálogo CAPES

**Data:** 15 de novembro de 2026  
**Produto:** [base técnica atualizada](./triagem_catalogo_lote2_20261115.xlsx).

## Procedimento

Foram selecionados os dez primeiros registros ainda não avaliados e não lidos nas etapas bilíngues anteriores, na ordem do inventário CAPES. Foram examinados título, resumos em português e inglês e palavras-chave do arquivo anual original de 2024; identificador, título, autoria e resumo em português foram confrontados com a base anterior. As classificações e justificativas individuais constam do [arquivo de avaliações](./avaliacao_catalogo_lote2_20261115.csv) e da aba **CAPES bilíngue lote 2**.

Esta seleção é operacional, não uma amostra representativa. A busca original alcançou todos os campos; a leitura dos metadados visíveis é aplicada como critério preliminar posterior. Não houve consulta externa nesta etapa.

## Resultado do lote

| Relação com o PIBID | Registros | Triagem |
|---|---:|---|
| Tema central | 4 | Pendente |
| Relação substantiva | 1 | Pendente |
| Incerta | 4 | Pendente |
| Menção incidental | 1 | Exclusão preliminar |
| **Total** | **10** | |

O registro `2d401ae4` foi excluído preliminarmente por menção incidental: os resumos tratam de uma sequência de Educação Física e apresentam o PIBID entre exemplos gerais de iniciativas formativas. A decisão é reversível mediante evidência complementar e não afirma ausência do programa no texto integral.

Nos registros `978a3b06`, `dc90d61c` e `b73823c3`, o PIBID figura entre experiências ou vínculos de participantes, mas os resumos não permitem separar adequadamente a contribuição do programa. Em `2f6de541`, experiência e material do PIBID aparecem como ponto de partida autobiográfico, mas seu alcance analítico e os achados permanecem incertos. Esses quatro casos continuam pendentes, sem atribuir seus resultados ao PIBID.

Em `3f9314f2`, participantes apontam PIBID e residência como importantes à formação sobre saúde e ambiente; a síntese não isola a contribuição de cada programa nem demonstra efeito causal. Em `ad83dff8`, o resumo inglês termina antes de parte dos resultados presentes no português. Em `3d19b827`, os achados sobre estudantes da escola e interações não foram extrapolados para aprendizagem docente.

Não foi identificada evidência de contexto goiano no título e nos resumos desses dez registros. Isso não prova ausência de contexto ou afiliação em Goiás; a afiliação permaneceu incerta. Ano de defesa não foi convertido em publicação. Nenhuma duplicata foi decidida.

Para os nove registros sem exclusão preliminar, foram acrescentadas 27 extrações provisórias de eixos: seis `Presente`, nove `Não informado` e 12 `Não verificável`. Não foram criadas extrações para o registro excluído. As sínteses e os limites devem ser interpretados em conjunto com cada estado.

## Situação da base

| Triagem de título e resumo | Linhas |
|---|---:|
| Avançar para avaliação | 19 |
| Excluir preliminarmente por período | 112 |
| Excluir preliminarmente pelo critério de termos | 38 |
| Excluir preliminarmente por menção incidental | 3 |
| Pendente | 1.145 |
| **Total** | **1.317** |

Na elegibilidade final, 338 linhas estão pendentes e 979 não iniciadas; não há decisão final. Permanecem 80 linhas em 40 pares de duplicatas confirmadas e 1.237 linhas com duplicidade não verificada. São contagens de linhas, não de obras únicas. A base contém 714 pares registro/eixo, dos quais 633 têm estado preenchido: 175 `Presente`, 199 `Não informado` e 259 `Não verificável`. Esses dados incluem duplicatas e casos sem elegibilidade definida e não são resultados finais.

Nas três etapas bilíngues foram lidos 38 dos 78 resumos ingleses CAPES, sem sobreposição entre os lotes; **40 permanecem sem leitura nessas etapas**. O inventário original foi preservado como registro histórico; as abas de auditoria registram as leituras posteriores. A busca literal anterior não substitui a análise semântica.

## Verificação e limites

O [script de integração](../../scripts/integrar_catalogo_lote2_20261115.py) impede sobrescrita da base e verifica identidade, resumos, histórico e estados anteriores. Os dados fora do escopo, validações, tabela e filtro dos eixos, fórmulas e integridade ZIP foram verificados. Passaram **nove testes focados**, incluindo os da revisão bilíngue anterior; não houve teste interativo no Excel.

A conferência é documental e computacional **não independente**, não mede acurácia e não fundamenta percentuais de confiança. A coleta nacional permanece incompleta. Ainda faltam a triagem dos demais registros, a leitura dos resumos ingleses restantes, a conciliação de duplicidades e datas, decisões finais e elaboração dos produtos finais.
