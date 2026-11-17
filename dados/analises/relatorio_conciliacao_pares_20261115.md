# Conciliação de duplicatas e conferência de candidatos goianos

**Data:** 15 de novembro de 2026  
**Produto:** [base técnica conciliada](./triagem_pares_conciliados_20261115.xlsx).

## Procedimento

Foram reunidos os 40 pares já confirmados nos registros anteriores de duplicidade e confrontados com as 80 linhas assim classificadas na base. Compararam-se os estados de relação com o PIBID, contexto, afiliação, período, produção acadêmica, triagem e elegibilidade, além dos anos e dos estados dos três eixos. A comparação identifica inconsistências, mas não valida os valores que coincidem nem encerra a busca de outras duplicatas.

Foram encontradas quatro divergências em três pares. Antes de conciliar, conferiu-se que as duas linhas de cada par tinham os mesmos título, autoria, tipo, ano de defesa, instituição, endereço, resumo e palavras-chave. Os valores anteriores, as justificativas e os limites estão na aba **Conciliação pares confirmados**. Não foram removidas linhas nem escolhido registro principal.

## Ajustes realizados

| Par confirmado | Conciliação | Fundamentação e limites |
|---|---|---|
| `2e073f75` / `5dbf2cee` | Relação com PIBID de `2e073f75` passou a **Tema central do estudo**. | O resumo identifica o programa como objeto da pesquisa nas licenciaturas do IF Goiano em Morrinhos. |
| Mesmo par | Período de `2e073f75` passou de **Só ano de defesa disponível** para **Incerto**. | A consulta anterior ao [repositório IF Goiano](https://repositorio.ifgoiano.edu.br/handle/prefix/2162), registrada em `5dbf2cee`, encontrou emissão em 25/08/2021, sem esclarecer se essa data representa publicação distinta da defesa. Não se confirmou o período. |
| `361dd6b1` / `f1d6e487` | Contexto de `361dd6b1` passou a **Sem evidência de contexto goiano**. | O resumo descreve pesquisa em Pedro Canário, Espírito Santo. A mudança não demonstra ausência de afiliação goiana. |
| `5f5259e7` / `3ee25c3e` | Contexto de `5f5259e7` passou a **Sem evidência de contexto goiano**. | O resumo descreve intervenção remota com estudantes do CAp-UERJ. A mudança não demonstra ausência de contexto ou afiliação goiana fora do material consultado. |

As exclusões preliminares pelo critério de termos já registradas para os dois últimos pares não foram alteradas. Todas as decisões finais permanecem pendentes. Não se presumiu que a instituição associada à dissertação corresponda à afiliação da autoria.

## Eixos e candidatos prioritários

Nos 40 pares, dos 120 pares duplicata/eixo possíveis, 105 apresentaram estados preenchidos iguais nas duas linhas, nove tinham estado preenchido em apenas uma linha e seis não o tinham em nenhuma. Não se copiaram extrações entre linhas nem se tratou campo vazio como ausência de achado. A comparação dos estados não confirma a adequação das sínteses nem a elegibilidade.

Para os 19 registros que avançam à avaliação, compararam-se os DOIs normalizados e os títulos com os demais registros da base. A comparação de títulos usou similaridade de pelo menos 0,80 ou inclusão como prefixo, após normalização; é uma busca de candidatos, não prova de ausência de duplicatas. Apenas `4a213f79` apresentou candidato por prefixo, `dd5b9244`: os tipos, as autorias e os anos disponíveis diferem. Não se confirmou duplicidade nem se alterou a situação de nenhum desses registros.

Dos 18 candidatos do Portal CAPES, oito não têm o termo literal do programa no título, mas o apresentam no resumo complementar OpenAlex preservado na [consulta do piloto](./openalex_piloto_20261115.json). Esses resumos complementares não demonstram, por si sós, o conteúdo dos campos visíveis na plataforma originalmente pesquisada. A aplicação do critério de busca a esses oito registros requer conferência da fonte; não se procedeu a exclusão automática.

O candidato de 2026 `22f73924` já tinha data anterior ao corte nos metadados OpenAlex. Em consulta adicional à [Crossref](https://api.crossref.org/works/10.69843%2Frir.v22iunico.77255), o DOI e título coincidiram e o campo de publicação online indicou **01/06/2026**. A página do periódico indicada pela Crossref retornou 404 na consulta de 15/11/2026. A evidência adicional apoia o período, mas não resolve a disponibilidade da fonte primária, a afiliação ou a elegibilidade final; os metadados não constituem validação independente.

## Situação da base e verificações

Há **1.317 linhas**: 19 avançam para avaliação, 197 têm exclusão preliminar e 1.101 permanecem pendentes na triagem. Na elegibilidade final, 423 estão pendentes e 894 não iniciadas; não há decisão final. Permanecem 80 linhas em 40 pares confirmados e 1.237 com duplicidade não verificada. São contagens de linhas, não de obras únicas. Os 714 pares registro/eixo, dos quais 633 têm estado preenchido, permanecem inalterados e incluem duplicatas e registros sem elegibilidade definida.

O [integrador](../../scripts/conciliar_pares_confirmados_20261115.py) impede sobrescrita, reconcilia os pares com as 80 linhas e recusa alteração quando o material ou os estados esperados divergem. Passaram dois testes focados de decisões, preservação, integridade e recusa de conflitos. Foram comparadas as demais células, as abas históricas, as validações e as fórmulas; a estrutura ZIP e a tabela da auditoria foram verificadas. Não houve teste interativo no Excel.

A análise e a conferência são não independentes e não fundamentam percentuais de confiança. A coleta nacional permanece incompleta. Persistem a leitura dos demais registros, a conferência dos campos originais dos candidatos, datas, duplicidades e decisões finais, além da planilha simplificada, dos gráficos e do relatório metodológico final.
