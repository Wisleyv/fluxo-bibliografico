# Marco 1 — cobertura e sobreposição observadas do OpenAlex

Estado: **concluído operacionalmente, com pendências bibliográficas justificadas**. A matriz cobre todos os registros de controle; não equivale a corpus elegível ou estimativa de completude nacional. Rodada posterior ao aceite do Marco 0 registrado em `Aceite do Marco 0.md` na raiz do projeto. Os arquivos de origem e as decisões históricas foram preservados.

## Entrega e reprodução

- [Matriz por fonte, período e tipo documental](Matriz%20de%20cobertura.csv).
- [Classificação dos 1.317 registros de controle](Registros%20de%20controle%20classificados.csv).
- [Conferência individual dos 52 pares](Revisao%20dos%2052%20pares.csv).
- [Todos os 689 pares auditados](Pares%20auditados.csv).
- [Unidades provisórias e vínculos entre fontes](Unidades%20e%20sobreposicao.csv).
- [Sobreposição confirmada entre fontes complementares](Sobreposicao%20entre%20fontes.csv).
- [Exclusivos observados nas fontes complementares](Exclusivos%20observados%20complementares.csv).
- [Auditoria e hashes das entradas](Auditoria.json).

Execução local: `python -m scripts.medir_cobertura_marco1`, na raiz. O script recusa sobrescrita do diretório de resultados; para uma nova rodada, preservar esta versão e escolher novo destino. A tabela dos 52 conserva todos os campos comparativos anteriores e acrescenta decisão, fundamento, RIS de origem e nome da página OpenAlex. O diretório das páginas é `dados/brutos/openalex/busca-restrita-20261115/`.

## Insumos reaproveitados

Base `dados/analises/triagem_criterio_defesa_20261115.xlsx`, aba Triagem; controles definidos pelo campo Fonte. Consolidado `dados/analises/openalex_busca_restrita_20261115.csv`, com 12.431 IDs únicos; conciliação `openalex_correspondencias_candidatas_20261115.csv` e classificação anterior `openalex_identidades_conferidas_20261115.csv`, ambas na mesma pasta. Os 116 pares estritos anteriores foram conservados. Foram reaproveitados 40 pares confirmados entre registros da base, recuperados pelo procedimento existente `pares_confirmados` de `scripts/conciliar_pares_confirmados_20261115.py`, que reconcilia 80 linhas marcadas na triagem. Usaram-se também o normalizador de DOI e o leitor RIS existentes, sem executar coletores ou integradores de elegibilidade.

Os RIS arquivados do Portal CAPES e SciELO e as páginas JSON OpenAlex forneceram a comparação bibliográfica dos casos prioritários. Reutilizaram-se as autorias, afiliações e evidências já preservadas na base para esclarecer abreviações. Nenhuma página externa foi consultada e nenhuma data ou autoria histórica foi corrigida.

O snapshot foi coletado em 15/11/2026 e filtrado por publicação de 01/01/2007 até 08/11/2026. Não é uma reconstrução do índice de 08/11. A medição é da recuperação nessa consulta arquivada, não da presença potencial de qualquer obra no índice OpenAlex completo.

## Revisão dos 52 pares

| Resultado | Pares |
|---|---:|
| Mesma obra confirmada nesta rodada | 51 |
| Mantido em revisão | 1 |
| Demonstrado como obra diferente | 0 |
| Total examinado | 52 |

Todos os 52 possuem DOI normalizado concordante e tipo artigo nas duas origens; a revisão inicial era causada por divergências nos demais campos. Quarenta e quatro têm título e ano concordantes; oito apresentam títulos diferentes, incluindo uma divergência de ano. As decisões novas não resultam de afrouxamento automático da regra histórica: foram examinadas as variantes mostradas na tabela de revisão, com fundamentos individuais para os casos especiais e fundamento bibliográfico comum para nomes abreviados/expandidos.

Nos 51 confirmados, DOI foi usado com evidência bibliográfica adicional: título equivalente ou traduzido, tipo, ano quando concordante, nomes compatíveis, periódico, volume, fascículo e/ou páginas quando disponíveis. Ausência ou abreviação de um campo não foi considerada concordância plena. As variantes de nomes foram mantidas e não interpretadas como desambiguação de pessoas validada independentemente.

Exemplos de decisões relevantes:

- `8558b71c` e `25b844fb`: títulos CAPES sem subtítulo, com DOI e demais campos compatíveis.
- `320aed50`, `e2fdf173` e `89d30495`: títulos em português/inglês equivalentes; comparação com autores e dados do periódico arquivados.
- `64b40852` e `2511e505`: palavras repetidas ao final do título de origem, sem evidência de outra obra.
- `91146316`: autoria truncada no OpenAlex; DOI, título, ano, fascículo 53 e páginas 149–167 coincidem. A autoria permanece com sua limitação.
- `8819ba66`: as afiliações já arquivadas na base registram as formas expandidas de nomes; DOI, título, ano e coautor sustentam identidade.
- `5c2ab78c`: título traduzido, DOI e autoria compatível sustentam identidade; **2015 na SciELO versus 2014 no OpenAlex** continua divergência temporal. A matriz estratifica pelo ano do controle, sem substituir o ano por aquele do OpenAlex. A divergência pode afetar a série anual no Marco 2, embora ambos pertençam a 2007–2019.
- `4348c88f` / `W2605649933`: DOI atípico `10.5216/10.5216`, nomes repetidos na origem e localização OpenAlex em repositório LA Referencia/UFG. Título e ano concordam, mas a base não tem link de origem que permita comprovar a correspondência com a localização do repositório. O par permanece candidato; não se conclui obra distinta nem se atribui valor discriminante suficiente ao DOI.

Resultado dos 689 pares: **167 confirmados = 116 reaproveitados + 51 novos; 522 pendentes = 521 por título + 1 dos prioritários**. As 522 relações pendentes atingem menos linhas de controle porque um registro pode ter vários candidatos. Confirmação bibliográfica não decide pertinência ao PIBID ou elegibilidade regional/nacional.

Os 167 pares confirmados ligam os controles a **166 IDs OpenAlex distintos**: uma obra tem registros confirmados tanto no Portal CAPES quanto na SciELO. A matriz de linhas preserva ambos; o panorama consolidado deverá contar a obra uma vez.

## Categorias, numeradores e denominadores

A unidade da matriz de cobertura é **linha do controle de origem**, rastreável por Código. O par é identificado por (`openalex_id`, `codigo_base`). Uma linha com pelo menos uma identidade confirmada entra em `mesma obra confirmada`; candidatos adicionais permanecem visíveis na coluna própria. Sem confirmação, havendo candidato, entra em `candidato em revisão`. Sem candidato e com título e autoria ou DOI suficientes à regra de comparação, entra em `não recuperado no OpenAlex`. Metadados insuficientes gerariam `não verificável`; nenhum dos 1.317 controles caiu nessa condição.

O agrupamento entre controles usa exclusivamente os 40 pares históricos e os pares OpenAlex confirmados. Título igual não cria fusão. A categoria considera evidência do componente confirmado; não se propagam decisões de elegibilidade. Uma correspondência no controle nacional e outra no regional continuam duas linhas na cobertura de origem, ainda que representem a mesma obra.

Definições das taxas no CSV:

- `numerador_confirmado` = linhas com identidade confirmada (C).
- `denominador_verificavel` = C + linhas sem candidato local (A).
- `cobertura_verificavel_pct` = 100 × C / (C + A); revisão (R) e não verificáveis (NV) ficam fora. Denominador zero produz célula vazia.
- `confirmado_sobre_total_pct` = 100 × C / (C + A + R + NV), percentual descritivo de confirmação já obtida em todo o controle.

A primeira taxa é **condicionada aos casos decididos pelas regras locais** e pode ser elevada pela exclusão dos casos difíceis. A segunda mostra o avanço de confirmação sobre a totalidade das linhas. Nenhuma é acurácia, sensibilidade validada ou completude da produção brasileira. Em particular, 0 confirmações na BDTD não significa 0 cobertura real: 474 linhas ainda têm candidatos.

| Fonte | Total | Confirmada C | Revisão R | Sem candidato A | Não verificável | C / (C+A) | C / total |
|---|---:|---:|---:|---:|---:|---:|---:|
| BDTD | 1.060 | 0 | 474 | 586 | 0 | 0/586 = 0% | 0/1.060 = 0% |
| Catálogo CAPES | 78 | 0 | 16 | 62 | 0 | 0/62 = 0% | 0/78 = 0% |
| Portal CAPES | 103 | 101 | 2 | 0 | 0 | 101/101 = 100% | 101/103 = 98,06% |
| SciELO | 76 | 66 | 6 | 4 | 0 | 66/70 = 94,29% | 66/76 = 86,84% |
| **Total de linhas** | **1.317** | **167** | **498** | **652** | **0** | **167/819 = 20,39%** | **167/1.317 = 12,68%** |

## Estratos por fonte, período e tipo

A base temporal é explícita: usa publicação quando preenchida; caso contrário, defesa, sem convertê-la em publicação. Períodos são 2007–2019 e 2020–2026. O CSV também oferece estratificação por **ano exato**, com a mesma separação de bases temporais. Os rótulos de tipo são os do controle; o mapeamento de tipos OpenAlex não foi alterado. Em estratos da BDTD com ambas as datas, prevalece publicação para alocação única, preservando defesa na base original.

| Fonte | Base temporal | Período | Tipo | C | R | A | Total |
|---|---|---|---|---:|---:|---:|---:|
| BDTD | Defesa | 2007–2019 | Dissertação | 0 | 249 | 266 | 515 |
| BDTD | Defesa | 2007–2019 | Tese | 0 | 115 | 90 | 205 |
| BDTD | Defesa | 2020–2026 | Dissertação | 0 | 72 | 165 | 237 |
| BDTD | Defesa | 2020–2026 | Tese | 0 | 38 | 63 | 101 |
| BDTD | Publicação | 2020–2026 | Dissertação | 0 | 0 | 2 | 2 |
| Catálogo CAPES | Defesa | 2020–2026 | Dissertação | 0 | 11 | 52 | 63 |
| Catálogo CAPES | Defesa | 2020–2026 | Tese | 0 | 5 | 9 | 14 |
| Catálogo CAPES | Defesa | 2020–2026 | Produto, processo ou técnica | 0 | 0 | 1 | 1 |
| Portal CAPES | Publicação | 2007–2019 | Artigo | 65 | 1 | 0 | 66 |
| Portal CAPES | Publicação | 2007–2019 | Editorial | 0 | 1 | 0 | 1 |
| Portal CAPES | Publicação | 2020–2026 | Artigo | 36 | 0 | 0 | 36 |
| SciELO | Publicação | 2007–2019 | Artigo | 33 | 6 | 4 | 43 |
| SciELO | Publicação | 2020–2026 | Artigo | 33 | 0 | 0 | 33 |

Para cada estrato o CSV fornece as mesmas quatro categorias e os dois denominadores. Não somar níveis diferentes do CSV: `total`, `fonte`, `fonte+base_temporal+periodo+tipo_documental` e `fonte+base_temporal+ano+tipo_documental` são visões alternativas do mesmo universo de 1.317 linhas.

## Sobreposição e exclusivos observados

O agrupamento por identidades sustentadas resulta em **1.277 unidades provisórias**, reconciliadas com 1.317 linhas. A redução de 40 decorre dos pares históricos. Não é contagem final de obras únicas: há candidaturas por título ainda não conciliadas entre controles e com OpenAlex.

A sobreposição confirmada entre fontes diferentes nos controles é de um grupo Portal CAPES/SciELO (o par histórico `83224e28` / `387c5254`, agora também confirmado com OpenAlex). Os demais 39 pares históricos são sobreposições de linhas dentro da BDTD. Zeros entre outras fontes na tabela de sobreposição significam ausência de identidade **confirmada neste conjunto de regras**, não inexistência de sobreposição. A aba histórica Comparação entre fontes documenta candidatos BDTD/Catálogo e BDTD/SciELO; eles não foram promovidos por título isolado.

A listagem de exclusivos observados contém **652 linhas em 626 grupos provisórios** sem candidato OpenAlex nas tabelas locais:

| Fonte do grupo | Grupos provisórios | Linhas de origem |
|---|---:|---:|
| BDTD | 560 | 586 |
| Catálogo CAPES | 62 | 62 |
| SciELO | 4 | 4 |
| Portal CAPES | 0 | 0 |
| Total | 626 | 652 |

Cada grupo lista os códigos originais e um título representante. Esses são exclusivos **em relação à busca OpenAlex arquivada e às regras locais de correspondência**, não prova de inexistência no índice inteiro nem de exclusividade absoluta de uma única fonte complementar. Possíveis duplicatas não resolvidas entre BDTD e Catálogo impedem declarar os 626 grupos como 626 obras definitivamente distintas. Não foram incorporados ao corpus nacional. A lista é a fila rastreável para conciliação/eligibilidade do Marco 2, com essa limitação.

## Conferências executadas

1. Dimensões de entrada: 1.317 códigos únicos, 12.431 IDs OpenAlex e 689 pares com chaves idênticas nas duas tabelas anteriores.
2. Recontagem das classes históricas 116/52/521 e conferência dos 40 pares internos contra as 80 linhas marcadas como duplicata confirmada pelo utilitário existente.
3. Presença de códigos e IDs de todos os pares nas respectivas entradas; localização em RIS por DOI para os 52 prioritários; leitura dos metadados nas páginas locais dos casos especiais.
4. Reconciliação de 116 + 51 = 167 confirmações; 521 + 1 = 522 pares pendentes. A projeção por controle produz 167 + 498 + 652 + 0 = 1.317 linhas.
5. Totais de cada nível de estratificação reconciliados com 1.317; soma de linhas de todos os componentes também igual a 1.317; quatro classes mutuamente exclusivas por registro.
6. Hash SHA-256 das quatro entradas principais antes/depois idêntico; hashes registrados em Auditoria.json. Sem alteração da planilha técnica ou das conciliações históricas.
7. Sete testes focados aprovados: três novos testes de precedência, denominadores e fronteiras temporais; quatro testes existentes de identidade e conciliação. Nenhuma alegação de validação científica independente.

Após a gravação, os CSVs foram reabertos e as contagens, chaves únicas, fórmulas dos denominadores e os quatro níveis da matriz foram reconferidos independentemente da geração. Todos reconciliaram com 1.317. Os caminhos de RIS e páginas dos 52 pares existem; os hashes das entradas continuaram idênticos. Nos exclusivos, 600 grupos têm uma linha e 26 têm duas: 626 grupos e 652 linhas.

## Pendências e efeito no Marco 2

- **Um par prioritário inconclusivo:** `4348c88f`. Pode elevar de 101 para 102 as linhas Portal confirmadas, alterando cobertura por fonte, ano e tipo. Necessita evidência bibliográfica discriminante; nenhuma coleta foi feita para supri-la.
- **521 pares por título:** podem mudar correspondências de 498 linhas ainda em revisão (incluindo o par prioritário). Títulos de tese e artigo podem corresponder a produções distintas. Não se presume que resolver todas positivamente seja válido. A comparação restrita dos controles pode orientar a próxima fila de maior impacto.
- **Divergência temporal `5c2ab78c`:** identidade aceita, ano não conciliado; decidir a regra de data antes da série anual nacional. O estrato amplo de período desta rodada não muda.
- **Exclusivos e sobreposição interna incompletamente deduplicados:** 626 grupos provisórios ainda podem se sobrepor entre fontes; não somá-los ao OpenAlex para obter total nacional sem conciliação.
- **Definição brasileira e tipos ambíguos:** permanecem decisões explicitamente abertas do Marco 0 para consolidação nacional; a consulta OpenAlex não tem filtro de país. Não limitam a matriz descritiva desta rodada.
- **Validação independente:** não realizada; a revisão local não gera percentuais de confiança. É necessário fechar o desenho de validação antes de alegar desempenho.

O Marco 1 satisfaz a entrega de classificação completa dos controles e medição reconciliada, com pares inconclusivos justificados, conforme o critério de saída que admite pendências documentadas. O Marco 2 pode começar pela preparação determinística e pela conciliação dirigida dessas filas. Sua consolidação final e os indicadores devem aguardar tratamento das pendências com efeito material ou uma decisão metodológica explícita sobre sua exclusão do denominador e análise de limites. Nenhum registro em revisão foi convertido em ausência ou exclusão de elegibilidade.
