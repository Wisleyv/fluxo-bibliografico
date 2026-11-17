# Leitura de pares confirmados ainda pendentes

**Data:** 15 de novembro de 2026  
**Produto:** [cópia técnica atualizada](./triagem_pares_pendentes_20261115.xlsx).

**Atualização posterior:** a situação dos 16 pares incertos foi reavaliada. Dois possuem resumos pertinentes na fonte primária, não recuperados na exportação local; os outros 14 foram excluídos preliminarmente pelo critério de termos nos metadados disponíveis. As decisões atuais e seus limites estão no [relatório de conferência](./relatorio_conferencia_termos_20261115.md) e na [base posterior](./triagem_conferencia_termos_20261115.xlsx). As contagens abaixo descrevem a etapa anterior.

## Procedimento

Foram lidos 19 conjuntos de título, campo de resumo, palavras-chave e metadados locais, correspondentes a **38 linhas** em 19 pares de duplicatas já confirmadas. Antes de reaproveitar cada síntese, foram conferidos identificador de repositório, título, autoria, tipo, ano de defesa e instituição, além da igualdade dos campos de resumo e palavras-chave. As avaliações estão no [arquivo de decisões](./avaliacao_pares_pendentes_20261115.csv) e na aba **Pares pendentes lidos**.

Em 17 pares havia resumo substantivo. Nos dois pares restantes, o campo continha apenas uma referência bibliográfica, sem resumo substantivo nem palavras-chave. Não foram realizadas consultas externas nesta etapa.

| Relação com PIBID | Pares | Linhas |
|---|---:|---:|
| Tema central do estudo | 3 | 6 |
| Incerto | 16 | 32 |
| **Total** | **19** | **38** |

Entre os três estudos com PIBID como tema central, um relata escolhas profissionais de egressos, outro apresenta objetivo de investigar a formação em Geografia sem descrever resultados no resumo e o terceiro relata aprendizagens docentes, atuação de egressos e vínculo universidade–escola. As sínteses de cada eixo foram registradas sem substituir resultados por objetivos.

Nos outros 16 pares, o PIBID não é mencionado no material examinado e sua relação com o estudo permanece incerta. Isso **não prova que o programa esteja ausente do texto completo** e não constitui exclusão. Por exemplo, trajetórias de egressos não foram atribuídas ao PIBID sem evidência; aprendizagem de estudantes escolares não foi convertida em aprendizagem docente; o Prolind não foi confundido com o PIBID.

Em 17 pares não foi encontrada evidência de contexto goiano no material consultado; nos dois pares sem resumo substantivo o contexto permanece incerto. A ausência de evidência não estabelece ausência no estudo. A instituição associada à tese não foi tomada automaticamente como local da pesquisa nem como afiliação de autoria.

## Situação da base

Foram acrescentadas **114 extrações registro/eixo**: oito `Presente`, quatro `Não informado` no material consultado e 102 `Não verificável`. Incluem duplicatas e são preliminares, não resultados consolidados ou contagens de estudos únicos.

As 38 linhas permanecem com triagem pendente; sua elegibilidade passou de não iniciada para pendente. Nenhuma foi excluída ou selecionada definitivamente. Anos de defesa não foram convertidos em anos de publicação, nenhuma duplicata foi removida e não foi escolhido registro principal. Dois outros registros com um par já revisado não foram incluídos, pois exigem conciliação com a avaliação anterior.

| Situação geral | Linhas |
|---|---:|
| Triagem: avançar para avaliação | 19 |
| Triagem: excluir do recorte goiano por ano de publicação | 110 |
| Triagem: pendente | 1.188 |
| Elegibilidade: pendente | 317 |
| Elegibilidade: não iniciada | 1.000 |

As contagens de triagem e elegibilidade representam dimensões diferentes e não devem ser somadas. A base contém 1.317 linhas, incluindo 80 linhas em 40 pares confirmados; a duplicidade das outras 1.237 linhas permanece não verificada. Há 681 pares registro/eixo, dos quais 600 têm estado preenchido.

## Verificação e limites

O [script de integração](../../scripts/integrar_pares_pendentes_20261115.py) impede reaproveitamento entre pares com identidade ou conteúdo divergente e interrompe a integração se alguma linha já tiver revisão ou estado incompatível. Foram conferidos dados fora do escopo, abas e eixos históricos, validações, tabela e filtro, fórmulas e integridade ZIP. Passaram **14 testes focados**, incluindo os testes da etapa anterior; não houve teste interativo no Excel.

A leitura e a conferência por código não são independentes e não medem acurácia. Não foram atribuídos percentuais de confiança. A coleta nacional continua incompleta. Permanecem a análise dos demais registros, a conciliação de avaliações e duplicatas, a verificação de datas, a seleção final e os produtos finais de resultados e metodologia.
