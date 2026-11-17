# Triagem temática de registros BDTD sem termo literal

**Data:** 15 de novembro de 2026  
**Produto:** [base técnica atualizada](./triagem_bdtd_termos_lote_20261115.xlsx).

## Priorização e procedimento

Na base anterior, 979 linhas tinham elegibilidade não iniciada, das quais 939 eram da BDTD. Para avançar em uma frente numerosa, foram selecionados 20 registros BDTD distintos por título, ainda não analisados, com resumo de pelo menos 500 caracteres e sem sigla ou expressão portuguesa do PIBID nos campos locais. Foram também lidas quatro linhas de títulos e autorias correspondentes: três traziam resumo em outro idioma e uma tinha resumo igual, mas link diferente. Não se presumiu que fossem duplicatas.

Foram lidos título, resumo e assuntos disponíveis das 24 linhas e confrontados título, autoria, link e resumo com as exportações BDTD. A leitura temática, não a contagem de caracteres nem a ausência literal isolada, fundamentou as decisões. A busca BDTD original foi realizada em todos os campos; o critério de termos é aplicado posteriormente aos metadados visíveis disponíveis. O [arquivo de avaliações](./avaliacao_bdtd_termos_lote_20261115.csv) e a aba **BDTD termos lote** registram as decisões individuais.

## Resultado

| Tratamento de triagem | Linhas |
|---|---:|
| Exclusão preliminar pelo critério de termos e leitura temática | 22 |
| Pendente, com vínculo ao PIBID identificado na UFS | 1 |
| Pendente, com possível tradução inglesa do nome do programa | 1 |
| **Total** | **24** |

As 22 exclusões são **preliminares e reversíveis** se surgirem evidências adicionais. Elas não afirmam ausência do programa no texto integral. Na planilha, o motivo é `Outro`, detalhado nas evidências; a elegibilidade final continua pendente. Essas linhas não devem compor contagens temáticas sem reavaliar o critério e a evidência. Em `7d880e9f`, não havia palavras-chave na cópia; foram considerados o título e o resumo disponíveis.

Dois resumos em inglês revelaram uma limitação importante da busca literal:

- **`05895f12`:** a expressão inglesa remete a programa de iniciação à docência. O [resumo em português da UFS](https://ri.ufs.br/jspui/handle/riufs/11943), consultado em 15/11/2026, identifica o Programa Institucional de Bolsa de Iniciação à Docência como contexto das oficinas. A relação passou a substantiva, mas a triagem e a elegibilidade permanecem pendentes. Os resultados descritos dizem respeito a estudantes escolares; não foram extrapolados para aprendizagem docente. A fonte apresenta emissão e referência em 2019, sem estabelecer nesta etapa publicação distinta da defesa.
- **`9d2082d5`:** o resumo inglês menciona programa traduzido como *Institutional Program for Teaching Initiation Scholarships* e identificado como IPTIS, em ações integradas com residência pedagógica. O vínculo com o PIBID permanece incerto; a consulta ao repositório UFS retornou erro 503. Não se atribuiu o resultado a qualquer programa isoladamente.

A conferência pontual da UFS está registrada em [arquivo de fontes](./consulta_ufs_bdtd_20261115.json). A busca por uma formulação inglesa semelhante também sinalizou `52ecb111`, ainda não avaliado; outras traduções ou descrições indiretas podem existir. Assim, **a ausência de sigla ou nome em português não basta, sozinha, para excluir resumos em inglês**.

Não foram criadas extrações de eixos para este lote: as 22 exclusões são preliminares, e os dois casos restantes exigem conciliação antes de sua utilização nos resultados. Não se modificaram datas nem estados de duplicidade. A escolha de registros principais e a resolução dos candidatos continuam pendentes.

## Situação da base

| Triagem de título e resumo | Linhas |
|---|---:|
| Avançar para avaliação | 19 |
| Excluir preliminarmente por período | 112 |
| Excluir preliminarmente pelo critério de termos | 60 |
| Excluir preliminarmente por menção incidental | 3 |
| Pendente | 1.123 |
| **Total** | **1.317** |

Na elegibilidade final, 362 linhas estão pendentes e 955 não iniciadas; não há decisão final. Permanecem 80 linhas em 40 pares de duplicatas confirmadas e 1.237 linhas com duplicidade não verificada. São contagens de linhas, não de obras únicas. Os 40 resumos ingleses CAPES remanescentes de etapas anteriores continuam por ler; a triagem BDTD não altera esse total.

## Verificação e limites

O [script de integração](../../scripts/integrar_bdtd_termos_lote_20261115.py) impede sobrescrita, confere os estados e a identidade com as exportações e bloqueia exclusão dos casos com a formulação inglesa sinalizada. Esse bloqueio é uma salvaguarda limitada, não um detector exaustivo de traduções. Foram verificados dados fora do escopo, validações, tabela e filtro dos eixos, fórmulas e integridade ZIP. Passaram **oito testes focados**, incluindo os do lote anterior; não houve teste interativo no Excel.

A análise e a conferência são **não independentes**: não medem acurácia nem fundamentam percentuais de confiança. A eventual impossibilidade de validar essas margens deverá constar nas limitações do estudo. A coleta nacional permanece incompleta.
