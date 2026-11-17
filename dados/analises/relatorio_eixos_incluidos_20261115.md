# Extração dos eixos dos registros incluídos

**Data:** 15 de novembro de 2026  
**Base produzida:** [triagem com eixos preenchidos](./triagem_eixos_incluidos_20261115.xlsx).

## Procedimento

Foram preenchidos os **21 estados de eixo ainda vazios** para sete dos 11 registros incluídos na revisão goiana. Utilizaram-se os títulos e resumos OpenAlex já arquivados em 15/11/2026, sem novas consultas ou busca de resumos ausentes. As 12 extrações anteriormente preenchidas dos outros quatro registros foram preservadas.

Cada nova extração contém síntese, localização, fonte e limites na aba **Eixos de análise**. As decisões individuais também estão no [arquivo de extração](./extracao_eixos_incluidos_20261115.csv). A classificação `Presente` indica conteúdo pertinente ao eixo no material examinado, **não necessariamente um resultado empírico ou efeito comprovado**. `Não informado` refere-se ao resumo consultado, não ao artigo inteiro; `Não verificável` indica evidência insuficiente para caracterizar o aspecto.

Por exemplo, em `813fdfa6` as contribuições à formação são apresentadas como expectativa, não como resultado observado. Em `91522d0b`, a história do subprojeto não foi tratada como trajetória profissional. Em `00683d4e`, os resultados atribuídos aos estudantes não foram convertidos em aprendizagem docente. Relações entre universidade e educação básica não foram tomadas como comprovação de participação comunitária ou espaços híbridos.

## Situação dos 11 registros incluídos

| Eixo | Presente | Não informado | Não verificável | Total de linhas |
|---|---:|---:|---:|---:|
| Aprendizagem da docência e identidade profissional | 9 | 0 | 2 | 11 |
| Trajetórias profissionais | 1 | 10 | 0 | 11 |
| Relações IES, escolas e comunidades; saberes e espaços híbridos | 6 | 2 | 3 | 11 |
| **Total registro/eixo** | **16** | **12** | **5** | **33** |

As categorias de eixos podem se sobrepor; a tabela não deve ser interpretada como 33 estudos. As contagens são preliminares e restritas às **11 linhas atualmente incluídas**, não representam o conjunto completo da revisão. Os demais registros continuam por analisar, e a busca de duplicatas não é exaustiva. Os resumos OpenAlex usados nas novas extrações foram arquivados após o corte e não comprovam o conteúdo exibido no momento da coleta; não substituem o texto integral.

As decisões de elegibilidade não foram alteradas: permanecem 11 inclusões, 110 exclusões temporais do recorte goiano, 343 pendentes e 853 não iniciadas. A elegibilidade nacional não foi decidida por essas exclusões. Dez dos 11 incluídos têm qualidade documental reduzida no campo de resumo da planilha; isso não implica ausência de resumo complementar. Não foram calculados percentuais de confiança: a análise é não independente.

## Verificação

O [integrador](../../scripts/extrair_eixos_incluidos_20261115.py) confere os códigos, estados anteriores, DOI e resumo arquivado, bloqueia divergências e não sobrescreve a base de entrada. Os três [testes](../../tests/test_extrair_eixos_incluidos_20261115.py) passaram e verificaram a seleção e os limites das extrações, a preservação das demais células e abas, validações, tabela e filtro, fórmulas, ZIP e recusa de conflitos. O arquivo persistido foi aberto por biblioteca, e seus totais e integridade ZIP foram conferidos. Não houve teste interativo no Excel.

**Próxima prioridade:** preparar uma apresentação provisória dos resultados disponíveis e dos respectivos denominadores, preservando a incompletude da triagem; em seguida, prosseguir para os produtos finais conforme a suficiência dos dados e dos recursos.
