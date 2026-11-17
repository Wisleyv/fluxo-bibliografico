# Avaliação dos dez registros prioritários do Portal CAPES

**Data:** 15 de novembro de 2026  
**Base produzida:** [triagem dos registros prioritários](./triagem_portal_prioritario_20261115.xlsx).

## Procedimento e decisões

Foram reexaminados os dez registros que já tinham período e vínculo goiano indicados, usando apenas materiais previamente preservados. Não houve consulta externa ou busca individual adicional. Os oito registros com pertinência temática substantiva foram incluídos **operacionalmente**, com qualidade documental reduzida; os outros dois permaneceram sem decisão por incerteza temática, distinta da ausência do resumo na planilha.

Nos oito incluídos, conferiram-se identidade, DOI, autoria e ano entre a planilha, o RIS e a conferência anterior do Portal; também foram conferidos título, DOI, tipo, data de publicação e afiliação goiana nos metadados OpenAlex arquivados. As datas de publicação são de 2020 a 2023. A relação substantiva foi avaliada nos resumos já consultados, sem leitura integral e sem validação independente.

| Código | Evidência temática resumida |
|---|---|
| `05cbfe1e` | Propostas de atividades de língua portuguesa vinculadas ao PIBID. A aplicação é idealmente planejada, não comprovada. |
| `27027026` | Sequência didática elaborada por bolsistas PIBID e aplicada em escola local. |
| `2fee827b` | Mediação de supervisora na aprendizagem da docência de bolsistas PIBID. |
| `3f830636` | Oficina remota organizada por bolsistas PIBID em evento do IF Goiano. |
| `4a213f79` | Uma das três experiências formativas examinadas envolve o PIBID Matemática Goiânia/UFG. |
| `678fd86d` | Formação matemática de bolsistas de subprojeto PIBID da UEG. |
| `7d7f7dda` | Feira de ciências organizada por subprojetos PIBID de Química e Biologia da UFG Regional Catalão. |
| `8819ba66` | Registros de bolsistas de Pedagogia do PIBID/UEG em Inhumas. |

O artigo `4a213f79` aborda experiências distintas; não se atribuem todas ao PIBID ou a Goiás. O resumo de `3f830636` não permite inferir a localização dos participantes remotos. Em `27027026`, resultados sobre estudantes da escola não são automaticamente tratados como aprendizagem docente. A afiliação goiana e o contexto de pesquisa continuam sendo dimensões distintas; afiliação não estabelece, por si só, a localização da pesquisa.

Os registros `8100e3f1` e `b954db99` continuam pendentes: o primeiro informa coleta de dados por licenciandos PIBID em estudo sobre educação musical; o segundo prevê bolsistas PIBID como participantes de pesquisa em andamento sobre sustentabilidade. Os resumos disponíveis não esclarecem suficientemente se o programa é analisado de forma substantiva. Isso não constitui pendência criada apenas por resumo não preservado e não motivou consulta adicional.

## Qualidade documental e duplicidade

Os oito incluídos foram recuperados na busca regional de **assunto** de 08/11/2026, mas a interface não discriminou o campo correspondente e os RIS não preservaram resumo nem palavras-chave. A busca original, portanto, não prova em qual campo os termos ocorreram. As páginas do Portal e os resumos OpenAlex consultados posteriormente apresentam pertinência temática, mas **não comprovam o conteúdo exibido em 08/11/2026**. A inclusão usa essa evidência posterior como decisão operacional revisável, com essa limitação histórica explícita; não há percentual de confiabilidade calibrado.

A comparação de títulos e DOI no conjunto preservado identificou um candidato para `4a213f79`: `dd5b9244` é tese de outra autoria, sem DOI, ao passo que o primeiro é artigo. O título semelhante não confirma duplicidade; não foram fundidos. Nenhum outro candidato foi identificado para os oito pela regra utilizada, o que não comprova ausência de duplicatas. Todos permanecem com duplicidade **não verificada**.

## Extração dos eixos

Foram preenchidos 15 estados ainda vazios nos cinco registros cujos resumos já permitiam análise; os nove estados preexistentes dos outros três foram preservados. A extração é rastreável no [CSV de evidências](./extracao_portal_prioritario_20261115.csv) e na aba **Eixos de análise**. `Não informado` indica ausência da informação no resumo consultado, não ausência no artigo; `Não verificável` indica evidência insuficiente para caracterizar o eixo.

Nos **19 registros incluídos**, os 57 estados de eixo estão preenchidos: 23 `Presente`, 23 `Não informado` e 11 `Não verificável`. São pares registro/eixo, não 57 estudos distintos; os eixos podem se sobrepor. Essas contagens refletem apenas as evidências consultadas e o conjunto parcial de linhas incluídas, sem deduplicação integral.

## Situação da revisão goiana

| Elegibilidade | Linhas |
|---|---:|
| Incluir | 19 |
| Excluir | 199 |
| Pendente | 247 |
| Não iniciada | 852 |
| **Total** | **1.317** |

Restam **1.099 linhas sem decisão**. As 199 exclusões, inalteradas nesta etapa, são específicas da revisão goiana; não equivalem a exclusões do panorama nacional. Os totais são de linhas, não de obras únicas. A aba **Priorização lote** é um retrato anterior à presente consolidação; as decisões atuais estão em **Triagem** e **Portal prioritário**.

## Verificação e alcance

O [integrador](../../scripts/consolidar_portal_prioritario_20261115.py) impede sobrescrita e verifica os estados anteriores, a identidade, as evidências e os trechos extraídos. Os três [testes](../../tests/test_consolidar_portal_prioritario_20261115.py) passaram, incluindo preservação fora do escopo, validações, tabelas, filtros, fórmulas, integridade ZIP e recusa de conflitos. O arquivo persistido foi aberto por biblioteca; não houve teste interativo no Excel.

Os resultados ainda não representam uma revisão exaustiva: permanecem registros não decididos, duplicidade não inteiramente resolvida e cobertura nacional incompleta. A conferência por código não mede acurácia. Na preparação dos produtos, essas limitações e a diferença entre evidência histórica e complementar devem permanecer visíveis.
