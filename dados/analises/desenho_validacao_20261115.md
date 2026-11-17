# Desenho da amostra para validação independente

**Data:** 15 de novembro de 2026  
**Situação:** desenho definido antes do sorteio. A validação só estará concluída após o preenchimento independente e a comparação com as classificações congeladas.

## Universo e finalidade

Sortear 60 das 1.317 linhas da planilha de trabalho, sem eliminar possíveis duplicatas. A unidade de sorteio é o **registro**, não o estudo único. A amostra serve para auditar informações de período e classificações efetivamente produzidas; não transforma sinais textuais em decisões nem permite generalizar desempenho sem considerar os diferentes métodos de análise e as probabilidades de seleção.

## Estratificação e sorteio

1. Fixar por fonte as cotas: **BDTD 24**, **Portal CAPES 14**, **Catálogo CAPES 11** e **SciELO 11**. A alocação sobrerrepresenta fontes menores em relação à sua proporção na base, para permitir sua observação.
2. Em cada fonte, subdividir pelos seguintes fatores:
   - situação temporal: publicação em 2020–2025, publicação anterior/fora, publicação em 2026 com data completa não estabelecida, só defesa de 2020–2026, só defesa fora desse intervalo, ou ano ausente; para os 36 do piloto, usar o avanço ou pendência da triagem piloto;
   - presença ou ausência de sinal literal `Goiás`, `goiano`, `goiana`, `goianos` ou `goianas` nos metadados textuais disponíveis da planilha;
   - disponibilidade ou ausência de resumo na planilha ou no OpenAlex já arquivado para o piloto.
3. Garantir uma vaga em cada estrato não vazio. Distribuir as vagas restantes de cada fonte, uma por vez, ao estrato com maior razão `população do estrato / (vagas já atribuídas + 1)`, sem ultrapassar sua população; desempatar pela ordem lexical dos identificadores de estrato.
4. Ordenar os registros pelo código em cada estrato e sortear sem reposição, percorrendo os estratos em ordem lexical, com gerador pseudoaleatório Python `random.Random(20261115)`. Embaralhar a ordem de apresentação usando `random.Random(20261116)`.
5. Registrar separadamente tamanho da população `N`, vagas `n` e probabilidade de seleção `n/N` de cada registro sorteado. Preservar a amostra e a versão analisada no momento do sorteio.

Esses estratos garantem representação de situações temporais, sinais geográficos e disponibilidade de resumo, além dos estados do piloto. Se não existirem decisões automáticas de exclusão, a amostra não poderá validar uma categoria de exclusão inexistente. Ano de defesa é usado apenas para estratificação e **não** é assumido como ano de publicação. O sinal geográfico é apenas textual: pode faltar quando há relação com Goiás e pode ocorrer em contexto de outro estado.

## Preenchimento independente

Disponibilizar à pesquisadora uma planilha sem as decisões, classificações, sinais, estratos ou justificativas automáticas. Ela terá os metadados e resumos já disponíveis, identificadores e campos vazios para registrar avaliação, fonte, limites e data. O resumo OpenAlex do piloto, quando existente, será reconstruído a partir dos dados já arquivados; nenhuma nova coleta será feita. Não consultar as avaliações automáticas antes de registrar a avaliação de referência.

Analisar separadamente relação substantiva com PIBID, contexto, afiliação, período, tipo acadêmico e eixos, respeitando a opção aprovada de contexto **ou** afiliação em Goiás. Ausência de resumo ou de ano de publicação pode impedir decisão; registrar a pendência em vez de inferir uma resposta.

Após o preenchimento, comparar apenas decisões efetivamente tomadas pelo procedimento automático ou pelo piloto com avaliações de referência comparáveis. Para estimativas globais, considerar o desenho estratificado e os pesos `N/n`; reportar denominadores, casos não avaliáveis e intervalos de incerteza. Não avaliar desempenho dos eixos ou da deduplicação como se todos os 1.317 registros tivessem sido classificados nessas tarefas. A amostra de 60 não assegura precisão por estrato nem a validação das faixas >75% ou >85%.
