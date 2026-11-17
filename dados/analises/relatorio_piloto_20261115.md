# Relatório preliminar — regras e piloto de 36 referências

**Data:** 15 de novembro de 2026  
**Situação:** teste operacional e análise preliminar não validada; as contagens abaixo não são resultados finais nem medidas de acurácia.

## 1. Objetivo e materiais

Testar as [regras provisórias](./regras_piloto_20261115.md) de triagem e extração no lote de 36 referências do Portal CAPES já identificado no pacote preliminar. Os 36 registros foram selecionados anteriormente por conveniência e não são uma amostra representativa.

O teste utilizou os títulos e demais dados da [cópia de diagnóstico](./triagem_base_diagnostico_20261115.xlsx) e metadados e resumos do OpenAlex, preservados na [resposta da consulta](./openalex_piloto_20261115.json). A análise individual está em [avaliação do piloto](./avaliacao_piloto_20261115.csv); o teste de extração por eixo, em [extração dos eixos](./extracao_eixos_piloto_20261115.csv).

A [primeira planilha do piloto](./triagem_piloto_20261115.xlsx) aplicou provisoriamente o critério de contexto goiano. Após a escolha informada pelo usuário por contexto **ou** afiliação em Goiás, foi gerada a [planilha do piloto com o critério aprovado](./triagem_piloto_20261115_criterio_aprovado.xlsx). Nenhuma delas é a planilha final simplificada: suas colunas técnicas e os alertas ainda são necessários para revisão e rastreabilidade.

## 2. Procedimentos executados

1. Em 15 de novembro, após um teste de acesso a um registro, foi realizada uma consulta pública em lote ao OpenAlex com os 36 identificadores já presentes na planilha. Os 36 retornaram com resumo, tipo, data e metadados de autoria.
2. Os 36 DOIs e anos de publicação retornados coincidiram com os valores da planilha. As datas disponíveis ficaram dentro do recorte até 8 de novembro de 2026. A concordância entre fontes não comprova, por si só, a correção da informação original.
3. Foram examinados títulos e resumos para registrar a relação com PIBID e o contexto goiano, mantendo-os separados da afiliação de autoria. As afiliações retornadas foram registradas como metadados sujeitos a conferência; uma lista incompleta não demonstra ausência de vínculo.
4. Foi comparado o DOI de cada registro piloto com os demais registros da planilha; não se identificou correspondência exata. Isso não esgota a busca de duplicatas: títulos, autorias e variantes ainda precisam de conferência.
5. Foram testadas extrações dos três eixos em três registros, totalizando nove pares estudo/eixo. As sínteses distinguem o que o resumo informa dos limites do material consultado. Os demais 99 pares permanecem sem extração.
6. As avaliações foram aplicadas à cópia; após a escolha do critério, [preparar_piloto_20261115.py](../../scripts/preparar_piloto_20261115.py) foi atualizado para gerar a segunda versão. Nenhuma decisão definitiva de inclusão ou exclusão foi registrada.

Não houve leitura dos textos integrais, revisão independente pela pesquisadora ou validação interativa no Excel. O conteúdo e a disponibilidade das fontes primárias não foram conferidos nesta etapa.

## 3. Resultado preliminar da aplicação

| Dimensão | Situação observada no piloto |
|---|---|
| Relação com PIBID | 33 com relação substantiva e 3 incertos. |
| Contexto | 10 com contexto goiano identificado, 11 incertos e 15 sem evidência goiana identificada no título/resumo consultado. |
| Afiliação | 20 com alguma instituição goiana identificada nos metadados OpenAlex e 16 incertos; ausência de vínculo não foi confirmada. |
| Avanço de triagem, após escolha do critério | 18 avançam para avaliação e 18 permanecem pendentes. A elegibilidade dos 36 continua pendente. |
| Eixos testados | Cinco `Presente` e quatro `Não informado`, distribuídos em três estudos; estados referem-se somente aos resumos consultados. |

As dimensões são distintas e suas contagens não devem ser somadas. `Sem evidência de contexto goiano` não significa exclusão nem comprovação de que o estudo não tenha relação com Goiás. Dos 18 registros encaminhados para avaliação, dez têm afiliação identificada sem contexto goiano confirmado; os 18 não são inclusões finais. Na primeira versão, antes da escolha por contexto ou afiliação, oito avançavam e 28 permaneciam pendentes.

### Exemplos de casos que exigem cuidado

- **9f59b93c:** a pesquisa é descrita em Araguaína, Tocantins; o nome de uma escola contém “Norte Goiano”. Um filtro geográfico apenas por palavras produziria um sinal enganoso.
- **8100e3f1:** o resumo situa a pesquisa em Goiânia, mas o PIBID aparece na coleta; sua relação substantiva com o objeto ainda precisa de confirmação.
- **4a213f79:** o trabalho reúne experiências de três universidades, incluindo um subprojeto de Goiânia. O contexto goiano não representa necessariamente todo o conteúdo do estudo.
- **3f830636:** a oficina foi remota e vinculada a evento de campus goiano; a modalidade deve acompanhar a interpretação do contexto.
- **4e3f5a3d:** o resumo informa cinco egressos atuando na educação básica, mas não deixa suficientemente claro o denominador dessa contagem. Não calcular proporção a partir dele.

## 4. Verificação técnica

Após gravar as cópias, foram verificadas a integridade ZIP, a abertura por biblioteca, as dimensões das abas, as tabelas e as validações de dados. A comparação célula a célula confirmou alterações apenas nas colunas previstas dos 36 registros piloto e nas nove extrações de eixo; a aba de possíveis duplicatas e os demais registros não foram alterados. A regra de avanço da segunda versão foi conferida para os 36 registros. O arquivo original e a cópia de diagnóstico mantiveram o mesmo SHA-256 documentado no diagnóstico inicial.

Essa verificação é estrutural: não valida as classificações nem substitui um teste de abertura no Excel. As regras, os CSVs e a resposta recuperada permitem revisar e reconstruir a planilha sem modificar o original.

## 5. Tempo, custo e próximos passos

A consulta em lote para os 36 metadados durou aproximadamente **1,23 segundo**, além de uma consulta inicial de teste. A resposta em lote informou custo de processamento OpenAlex de **US$ 0,0001**, dentro de um orçamento gratuito compartilhado por IP informado pela própria API; isso não mede créditos do assistente nem garante disponibilidade ou custo futuro. Não se registrou tempo isolado de análise semântica ou revisão humana, portanto não há base para extrapolar o prazo total para 1.317 registros.

Antes da expansão, recomenda-se:

1. Aplicar a escolha por contexto ou afiliação em Goiás, mantendo essas dimensões separadas e identificando contextos mistos.
2. Desenhar uma amostra inicial de 60 registros para validação independente, estratificada por fontes e decisões; medir tempo por tarefa e registrar os critérios de amostragem.
3. Trabalhar apenas com os dados disponíveis, conforme escolha informada pelo usuário, sem atribuir cobertura nacional à base incompleta.
4. Rever os casos incertos e os achados piloto com os materiais já disponíveis; manter pendências que exijam novas fontes. Só então decidir elegibilidade e estender a extração de eixos.
5. Calcular desempenho e incerteza apenas após validação independente. As faixas de confiança pretendidas não podem ser derivadas deste teste de conveniência.
