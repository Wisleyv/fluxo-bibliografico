# Autoavaliação da amostra de 60 registros

**Data:** 15 de novembro de 2026  
**Produto:** [amostra preenchida](./amostra_60_autoavaliacao_20261115.xlsx). A [amostra cega original](./validacao_independente_60_20261115.xlsx) foi preservada.

## Alcance e limitações

Foram examinados os 60 registros sorteados, sem consultar a planilha de pré-análise antes de registrar as decisões. A mesma assistência computacional participou da pré-análise e da presente revisão: **esta é uma autoavaliação, não uma validação independente**. Não permite estimar acurácia, concordância independente ou índices de confiabilidade de 100%, >85% ou >75%.

A unidade é a linha sorteada, não o estudo único. A amostra tem cotas desproporcionais entre fontes e inclui duplicatas: as contagens abaixo descrevem somente suas 60 linhas e não devem ser extrapoladas ao conjunto de 1.317 registros nem interpretadas como quantidade de estudos únicos. O [desenho](./desenho_validacao_20261115.md) e o manifesto original preservam as probabilidades de seleção.

Foram examinados títulos, resumos substantivos e metadados locais. Fontes externas foram consultadas pontualmente para esclarecer lacunas decisivas, conforme a autorização posterior; não foi realizada nova busca sistemática nem ampliada a cobertura da coleta. As sínteses e os limites aparecem em cada linha e no [registro de decisões](./decisoes_autoavaliacao_60_20261115.csv). A classificação considera o conteúdo consultado, não substitui a leitura integral. `Não informado` nos eixos significa somente que o material analisado não apresentou a informação; `Não verificável` indica material insuficiente.

## Resultado provisório da triagem para Goiás, 2020–2026

| Situação | Registros |
|---|---:|
| Avançar para avaliação | 3 |
| Excluir desse recorte por ano de publicação fora do intervalo | 14 |
| Pendente | 43 |
| **Total** | **60** |

Avançar não é inclusão definitiva: ainda são necessárias a conferência das fontes e a verificação de duplicidade no conjunto. As exclusões são **apenas para o recorte de Goiás 2020–2026**; registros anteriores podem continuar relevantes para o panorama nacional. A falta de menção a Goiás ou ao PIBID em um resumo, isoladamente, não gerou exclusão.

Quanto ao período, 11 linhas têm publicação de 2020–2025 confirmada no material consultado; 14 têm ano de publicação fora de 2020–2026; 32 têm somente ano de defesa; e três permanecem temporalmente incertas. Uma dessas três envolve divergência entre metadados e referência. Para 2026, foi mantida a exigência de confirmação da publicação até 08/11/2026.

Há oito registros com contexto goiano identificado no material examinado e quatro com afiliação de autoria goiana identificada; essas dimensões podem se sobrepor. A ausência ou incompletude dos metadados de afiliação não foi tratada como prova de inexistência de vínculo. Uma instituição associada à tese não foi tomada como afiliação da autoria nem como prova do lugar da pesquisa.

## Conferências adicionais e pendências importantes

Consultas realizadas em **15/11/2026**, usando apenas endereços bibliográficos públicos:

- **06792f41:** o [repositório da UnB](https://repositorio.unb.br/handle/10482/51101) informa publicação em 05/12/2024 e oferece resumo substantivo. O resumo cita o PIBID entre várias experiências formativas, sem separar seus efeitos. O campo local da amostra continha apenas referência bibliográfica e foi marcado como não contendo resumo substantivo; a síntese da consulta externa consta na evidência.
- **c3920958:** o [repositório da UnB](https://repositorio.unb.br/handle/10482/38162) descreve defesa em 17/12/2019 e data de publicação em 25/06/2020, mas sua referência cita 2019; a amostra registra defesa em 2020. A inconsistência foi preservada e a decisão temporal ficou incerta, sem substituir silenciosamente o dado de origem.
- **5dbf2cee:** o [repositório do IF Goiano](https://repositorio.ifgoiano.edu.br/handle/prefix/2162) identifica a pesquisa no campus Morrinhos e informa `dc.date.issued` de 25/08/2021; o [registro completo](https://repositorio.ifgoiano.edu.br/items/a77da873-730c-4640-8845-ebd62f6014f5/full) distingue essa data das datas de disponibilidade. Como não foi estabelecido de modo inequívoco que a data de emissão represente publicação distinta da defesa, o período permanece incerto.
- **fe4d6c4f:** a [Crossref](https://api.crossref.org/works/10.1590%2F1980531411328) informa publicação e publicação online em 2026, sem mês ou dia. A disponibilidade até o corte de 08/11/2026 não foi confirmada.
- **46baf45a:** o arquivo BDTD bruto associa título sobre periódico histórico a resumo sobre autoscopia no PIBID Química. O endereço do repositório da UEM não respondeu; não se atribuiu o resumo à obra. O caso segue pendente.
- **1bfed0a9**, **e03ee3e1** e **7b83d4de:** respectivamente, o repositório Unicamp apresentou validação da requisição; o repositório FURG retornou 403; e a biblioteca UFABC retornou 404. Os bloqueios não foram contornados. Os campos preenchidos apenas com orientação ou referência não foram tratados como resumos substantivos.
- **83224e28** e **387c5254:** título, autoria, ano e DOI coincidem. O resumo SciELO já disponível na amostra foi usado como fonte cruzada para o registro Portal CAPES, com indicação explícita da origem. As duas linhas representam a mesma obra e permanecem no sorteio; não devem ser contadas como dois estudos.
- **7d7f7dda:** a afiliação UFG informada no OpenAlex sustenta o avanço, mas a localização da escola não foi presumida a partir da universidade.

## Procedimento e verificações

O preenchimento foi aplicado pelo [script](../../scripts/preencher_autoavaliacao_20261115.py), a partir de decisões registradas por código, em cópia separada. Cada linha recebeu avaliação dos critérios, três eixos, síntese de evidências, limites, data e indicação de autoavaliação. O ano de publicação de 06792f41 foi acrescentado com base no repositório; as divergências não resolvidas não foram substituídas. O indicador de resumo local foi corrigido para três campos que continham apenas referência ou orientação.

Foram verificados os 60 códigos únicos, preenchimento dos campos, estrutura da tabela e listas de validação, ausência de fórmulas inesperadas e preservação da amostra cega. Os testes automatizados focados de preenchimento e pré-análise passaram. A abertura e edição interativas no Excel não foram testadas.

**Próximo passo recomendado:** a pesquisadora ou outra pessoa independente deve revisar a amostra cega, sem acesso prévio a estas decisões. Em seguida, a comparação deve considerar o desenho estratificado, os pesos e a incerteza; uma amostra de 60 pode não sustentar estimativas precisas por estrato ou as faixas pretendidas.
