# Avaliação da nova exportação do Portal CAPES

Data da avaliação e coleta informada pelo usuário: **16/11/2026**. Insumo: [CAPES-concatenado.ris](../../CAPES-concatenado.ris). Esta rodada é diagnóstico e planejamento: **nenhum corpus, decisão histórica ou produto do Marco 5 foi atualizado**.

## Parecer

Recomenda-se integrar a exportação como nova rodada de recuperação do **Portal de Periódicos CAPES**, fonte expressamente prevista em [Vaneria.txt](../../../Vaneria.txt). A contribuição principal demonstrada é ampliar a proveniência e a medição de cobertura da fonte originalmente prevista, além de permitir revisar identidades e possíveis lacunas. A contribuição em **novas obras elegíveis ainda não está determinada**. Não se devem somar 675 ao total nacional ou substituir por esse RIS as fontes já utilizadas.

O arquivo não demonstra completude do Portal nem da produção nacional. A URL informada contém a expressão temática, intervalo 2007:2026, `source=all`, `num=30`, `page=23`, **Artigo/Editorial** e **`national_production=1`**. Portanto, a recuperação entregue é filtrada por tipos e pelo atributo de produção nacional da interface. Esses filtros não foram especificados como restrições gerais na busca temática de `Vaneria.txt` e não equivalem à definição nacional aprovada, que não exige metadado geográfico. O lote é admissível como fonte complementar/documentada; não deve impor seus filtros retroativamente ao corpus inteiro.

A tentativa de abrir a URL via ferramenta web não teve sucesso; não foi verificado o conteúdo remoto. As 23 páginas são informação fornecida pelo usuário. O RIS não contém página de origem, total anunciado pelo buscador ou manifesto das exportações individuais. **675 é aritmeticamente compatível com 22 páginas de 30 e uma de 15**, mas isso não prova paginação completa, estabilidade dos resultados ou ausência de omissão entre páginas.

## Conferência do arquivo

| Observação | Valor | Unidade / limite |
|---|---:|---|
| Registros RIS | 675 | 675 marcadores TY e 675 ER; sem erro do parser |
| Tipos | 673 artigos; 2 editoriais | Rótulos originais preservados |
| IDs distintos | 675 | Todos em formato W do OpenAlex; nenhuma repetição de ID |
| DOI preenchido | 633 | 93,78% dos registros; 633 valores distintos após normalização conservadora |
| Títulos normalizados distintos | 658 | 17 grupos repetidos; não determina número de obras únicas |
| Duplicatas de conteúdo idêntico | 0 | IDs distintos não impedem duplicação bibliográfica |
| Ano, título, autoria e veículo preenchidos | 675 cada | Autoria está concatenada num campo AU por registro |
| Resumo, palavras-chave, afiliação, data completa e URL individual | 0 campos específicos | Não confundir ausência na exportação com ausência no estudo ou no Portal |
| Ano 2026 | 35 registros | O RIS informa somente o ano |
| Anos observados | 2010–2026 | Ausência em 2007–2009 não prova ausência de produção |

Os autores concatenados incluem casos com instituições agregadas indevidamente, como o registro `CAPES20261116:0094`. Dividir automaticamente todas as vírgulas pode transformar instituições em pessoas ou fragmentar nomes. A execução deve reaproveitar identidades de autoria e afiliações já conferidas; o RIS bruto permanece preservado.

O SHA-256 do arquivo e dos insumos vigentes utilizados está em [Auditoria.json](Auditoria.json). A [distribuição anual](Distribuicao%20anual.csv) conta registros de recuperação, não obras elegíveis ou evolução nacional revisada.

## Sobreposição com o acervo vigente

Há **647/675 IDs no snapshot OpenAlex arquivado (95,85%)**. Dos 28 IDs restantes, cinco encontram componentes por DOI; 15 encontram candidatos somente por título; oito não têm correspondência nos índices estritos utilizados. Todos terem ID em formato W não demonstra que CAPES e OpenAlex sejam coleções equivalentes, nem que os resultados sejam duas coberturas bibliográficas independentes. “Não encontrado no snapshot” não significa “ausente de todo o OpenAlex”.

Após normalizar caixa, pontuação, acentos e entidades HTML, o diagnóstico é:

| Encaminhamento preliminar | Registros |
|---|---:|
| Identificador concordante com acervo, sem divergência nos campos comparados | 601 |
| Identificador concordante, com divergência bibliográfica | 51 |
| Somente título: identidade não sustentada | 15 |
| Sem correspondência pelos índices estritos | 8 |
| Total | 675 |

Essas categorias são de **diagnóstico**, não decisões finais de identidade ou inclusão. O primeiro grupo também requer os controles de consistência previstos no plano. Os campos e as referências por registro estão em [Registros e correspondências](Registros%20e%20correspondencias.csv).

As 51 divergências compreendem 45 diferenças de título, cinco diferenças de DOI e uma de ano. **25 das 45 diferenças de título** são prefixos/subtítulos com mesmo ID, DOI, ano e multiconjunto de tokens de autoria: podem ser tratadas objetivamente em lote, com amostra de conferência, em vez de nova leitura individual de todos os casos. Os 20 casos restantes de título e as seis divergências de DOI/ano merecem prioridade conforme seu efeito em identidade ou indicadores.

Os candidatos apontam para **651 componentes distintos** do acervo: 512 atualmente incluídos, 129 pendentes e dez elegíveis com identidade pendente. Esses números agregam correspondências fortes e fracas; não confirmam 651 identidades. Em unidade de registros, são 521 registros associados a incluídos, 136 a pendentes, dez a elegíveis com identidade pendente e oito sem candidato. A diferença decorre de múltiplos registros por componente e de um registro que aponta a dois componentes.

Entre os 103 controles CAPES antigos, 26 têm correspondência candidata nesta nova exportação; 77 não foram localizados pelos índices utilizados. Preservar todos os controles anteriores: a nova consulta tem filtros e data distintos, e ausência não invalida a recuperação histórica. Há 649 registros novos sem proveniência Portal previamente localizada no componente candidato ou ainda sem componente; isso não significa 649 obras novas. Mesmo as 26 recuperações repetidas devem registrar a nova rodada como proveniência, sem duplicar a obra.

O cruzamento alcança 62 componentes do universo regional já examinado: **12 incluídos, 11 pendentes e 39 excluídos**. Não se incluem 62 na revisão; reaproveitam-se seus estados até que evidência específica justifique mudança. O RIS não fornece afiliação/contexto regional novo em campos próprios.

## Casos que orientam a integração

1. **“Quero ser professora” — `CAPES20261116:0029`.** Mesmo W2345075798, título e autoria do acervo, mas DOI novo `10.1590/s2176-6681/3368314027` e DOI arquivado `10.24109/2176-6681.rbep.97i245.3421`. ID e DOI apontam aos componentes incluídos `M2-a279c6aac5c92b01` e `M2-d0c27c83901c3376`. É forte candidato a conciliação entre inclusões já existentes; uma fusão sustentada reduziria o denominador, em vez de acrescentar obra. Não foi decidida nesta avaliação.
2. **“Práticas de leitura” — registros `0048` e `0094`.** O primeiro informa 2019 para uma obra com publicação arquivada de 2013; o segundo traz outro ID e DOI SciELO. O fechamento do Marco 2 já conferiu a identidade bibliográfica do artigo por PID/localização. Reaproveitar esse parecer, preservar os dois anos de origem e os DOIs como possíveis aliases, sem contar nova obra ou substituir silenciosamente o ano canônico. A divergência 2013/2019 não muda o enquadramento nacional, mas pode alterar a série anual.
3. **Cury — `CAPES20261116:0134`.** Entre os oito sem correspondência estrita, o título contém um DOI anexado, e o campo DO repete o prefixo `10.5752/`. Remover o sufixo DOI apenas da chave de comparação encontra o candidato local `M2-7e1c0fb88fce15de` / W2141262701; o DOI correto está escrito no próprio título e no snapshot. A normalização ampliada recupera candidato, sem corrigir o bruto ou declarar uma obra nova. Restam sete dos oito sem candidato nesse exame adicional.
4. **`CAPES20261116:0674` — “INTELIGÊNCIAS ARTIFICIAIS E DESINFORMAÇÃO”.** É o único registro 2026 sem data completa no material diretamente relacionado pelo ID nesta avaliação. Tema e data de publicação exigem evidência; aparecer na busca não comprova pertinência substantiva ao PIBID nem publicação até 08/11.
5. **“Editorial”.** Há dois registros com esse título genérico, um sem ID no snapshot. Igualdade de título não autoriza fusão, e o tipo editorial não prova relação substantiva com o programa.

Os casos, as variantes objetivas e as referências estão em [Variantes e prioridades](Variantes%20e%20prioridades%20bibliograficas.csv). A tabela [Títulos repetidos](Titulos%20repetidos%20no%20RIS.csv) mantém os 17 grupos como candidatos, sem fusão automática.

## Datas, completude e impacto esperado

Recomenda-se manter **08/11/2026 como corte de publicação** para uma atualização comparável, registrando a nova coleta CAPES em **16/11/2026** e a anterior OpenAlex em **15/11/2026**. Um documento pode ser recuperado após o corte e ser elegível por publicação anterior; isso não demonstra que estivesse indexado em 08/11. A busca CAPES por ano inteiro não garante o dia de publicação.

Há suporte temporal preliminar por data arquivada para 646 registros, por ano 2007–2025 para 28 e insuficiência de data completa para um registro 2026. Esses totais se referem a registros e a relações candidatas; identidade ainda em revisão impede transferir data automaticamente entre obras. As quatro inclusões por defesa continuam exclusivamente regionais.

A integração pode: adicionar proveniência a obras já incluídas; recuperar novas obras; promover pendências por evidência suficiente; identificar duplicatas que reduzam totais; melhorar ou conflitar com anos/tipos; e mudar cobertura de autoria/afiliação. O saldo líquido ainda é desconhecido. Não há base para antecipar novo total nacional, regional ou percentual de participação.

Até executar e conferir a integração, permanecem os resultados da entrega anterior: 7.780 nacionais, 97 regionais, 291 extrações; frações observadas 196/7.780 (2,52%) e 67/3.459 (1,94%); participação total não estimável; 871 pendências regionais e dúvidas de identidade já documentadas. Esses valores não devem ser apresentados como recalculados com o novo RIS.

## Verificação e reprodução deste diagnóstico

Foram reutilizados o parser RIS e os normalizadores existentes, acrescentando apenas tratamento comparativo de entidades HTML e prefixos DOI. Passaram **sete testes existentes do normalizador** e **seis verificações locais**: integridade/fechamento dos registros, partição das categorias, IDs/repetição exata, comparação dos controles, reconciliação dos componentes e preservação dos dez insumos por hash. Ver [verificações](Verificacoes%20locais.csv).

Reprodução: `python -m scripts.avaliar_capes_20261116`. O script recusa diretório já existente; `--atualizar` regenera apenas os produtos deste diagnóstico. Não escreve nos corpora, na base histórica ou na entrega. O [plano proposto](../../../Plano%20de%20a%C3%A7%C3%A3o%20-%20integra%C3%A7%C3%A3o%20CAPES%20e%20atualiza%C3%A7%C3%A3o%20da%20entrega.md) define a integração subsequente.
