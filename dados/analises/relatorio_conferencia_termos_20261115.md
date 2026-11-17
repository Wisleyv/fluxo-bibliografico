# Conferência de termos e resumos incompletos

**Atualização posterior:** a emissão de 2017 do par `a3e7321c` / `69c845eb` coincide com a incorporação ao repositório e não comprova publicação distinta. A exclusão preliminar por período foi revertida e a data passou a incerta; as 28 exclusões temáticas por ausência de termos foram consolidadas para o recorte goiano. Consultar o [relatório da triagem em lote](./relatorio_triagem_lote_consolidacao_20261115.md). As contagens e decisões abaixo registram a etapa histórica.

**Data:** 15 de novembro de 2026  
**Produto:** [base técnica atualizada](./triagem_conferencia_termos_20261115.xlsx).

## Questão e procedimento

Foi reavaliado o lote de 16 pares cujo material local não mencionava o PIBID. O protocolo prevê a consulta `PIBID OR "Programa Institucional de Bolsa de Iniciação à Docência"` e, quando disponíveis na fonte, campos de título, resumo e palavras-chave. Entretanto, os registros de execução mostram que a busca BDTD realmente efetuada foi em **todos os campos**; os 16 pares constam nas exportações nacional e regional. Nenhum dos termos foi encontrado nos campos exportados desses pares. Não foi identificada a razão pela qual a interface os recuperou.

Foram confrontados títulos, autorias, links e resumos nas exportações BDTD com a cópia técnica e verificada a presença da sigla ou da expressão nos campos exportados de título, resumo e assuntos. Foram também consultados os registros públicos da UnB para os dois pares cujo campo de resumo local continha apenas referência bibliográfica. As consultas e seus resultados selecionados estão em [registro de fontes](./conferencia_resumos_unb_20261115.json); a aba **Conferência termos e UnB** conserva as decisões por linha.

## Resultado

| Tratamento preliminar | Pares | Linhas |
|---|---:|---:|
| Exclusão por ausência dos termos nos metadados disponíveis e resumo substantivo sem evidência do PIBID | 14 | 28 |
| PIBID e contexto goiano identificados na UnB; fora do período da revisão | 1 | 2 |
| PIBID e contexto goiano identificados na UnB; período incerto | 1 | 2 |
| **Total** | **16** | **32** |

Para os 14 pares com resumo substantivo, a leitura anterior descreve objetos diversos sem identificar o PIBID; também não há termo nos campos de título, resumo e palavras-chave disponíveis. A exclusão é **operacional e preliminar**, baseada no critério de busca e nos metadados efetivamente examinados. Na planilha, o motivo é `Outro`, detalhado em evidências e limitações; a elegibilidade final continua `Pendente`. A exclusão não afirma que o texto integral não contenha o programa e deve ser revista se outra fonte demonstrar termo ou pertinência. Esses registros não devem entrar nas contagens temáticas nacionais sem reavaliar o critério e a evidência. Tentativas pontuais de acesso a registros de outros repositórios não foram concluídas; não se presume que seus metadados atuais coincidam integralmente com a exportação.

Os dois pares sem resumo substantivo mostram por que não se deve aplicar a regra sumariamente a campos ausentes ou incompletos:

- **a3e7321c / 69c845eb:** o [resumo da UnB](https://repositorio.unb.br/handle/10482/23588) descreve formação com bolsistas do PIBID no Sudoeste Goiano. A fonte indica emissão em 2017 e a referência também apresenta 2017. O par foi excluído preliminarmente da revisão goiana de 2020–2026 por período, mas permanece disponível para o panorama nacional.
- **e92d970d / 6fb14721:** o [resumo da UnB](https://repositorio.unb.br/handle/10482/38351) relata pesquisa documental sobre subprojetos do PIBID de Goiás. A página rotula 29/06/2020 como data de publicação e os metadados a registram em `dc.date.issued`; o dia coincide com a incorporação ao repositório, enquanto a referência traz 2019 e a defesa é de 2019. Como não se estabeleceu se a emissão representa publicação distinta da incorporação, o período permanece **incerto** e o par não foi excluído.

Nos dois casos, a instituição da tese não foi confundida com afiliação de autoria; não se atribuiu afiliação goiana sem evidência. Foram revisados os três eixos de cada linha desses pares a partir dos resumos da UnB, sem substituir objetivos ou proposições teóricas por resultados de aprendizagem. As extrações anteriores dos demais registros permanecem no histórico técnico e não são resultados dos estudos selecionados.

## Situação da base

| Triagem de título e resumo | Linhas |
|---|---:|
| Avançar para avaliação | 19 |
| Excluir preliminarmente por período | 112 |
| Excluir preliminarmente pelo critério de termos | 28 |
| Pendente | 1.158 |
| **Total** | **1.317** |

Todas as exclusões acima são de triagem preliminar, não decisões finais de elegibilidade. Na elegibilidade, 317 linhas estão pendentes e 1.000 não iniciadas. Permanecem 80 linhas em 40 pares de duplicatas confirmadas e 1.237 linhas com duplicidade não verificada. As contagens são de linhas, não de obras únicas. A base contém 681 pares registro/eixo, dos quais 600 têm estado preenchido; incluem duplicatas e casos ainda não elegíveis.

## Limites e verificação

O [script](../../scripts/conferir_termos_e_resumos_20261115.py) confere os pares, as exportações, a ausência de termos e os estados anteriores antes de integrar decisões. Foram verificados células fora do escopo, histórico, eixos anteriores fora dos quatro registros da UnB, validações, tabelas, fórmulas e integridade ZIP. Passaram **11 testes focados**, incluindo testes da integração anterior; não houve teste interativo no Excel.

A conferência é documental e computacional **não independente**; não mede acurácia. Não foram atribuídos percentuais de confiança. A coleta nacional continua incompleta, e a classificação dos demais registros, a deduplicação, as datas e as decisões finais permanecem em andamento.
