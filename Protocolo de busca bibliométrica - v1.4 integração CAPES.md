# Protocolo bibliométrico — v1.4: adendo de integração CAPES

Adendo de execução de 16/11/2026, preservando a v1.3 e suas regras aprovadas. Não altera a definição temática de produção brasileira, a unidade de obra acadêmica única, os tipos acadêmicos elegíveis ou o recorte regional. A aplicação deste adendo não constitui nova validação independente.

## Recuperação pela fonte prevista no documento canônico

Foi incorporada a exportação `dados/CAPES-concatenado.ris`, fornecida pelo pesquisador, de busca no Portal de Periódicos CAPES em 16/11/2026. A cópia arquivada é `dados/brutos/portal-capes/portal-capes__nacional-filtrado__20261116__RIS.ris`; os hashes coincidem. A expressão informada foi “PIBID” OR “Programa Institucional de Bolsa de Iniciação à Docência”. A URL preservada no manifesto informa publicação 2007:2026, `source=all`, Artigo/Editorial, `national_production=1`, 30 resultados por página e página 23.

O lote contém 675 registros; a concatenação de 23 páginas é declarada pelo fornecedor, sem evidência individual de paginação no RIS. O Portal CAPES é registrado como fonte da recuperação e não substituído pelo OpenAlex na proveniência. O fato de todos os registros terem identificadores em formato W, e de 647 desses IDs coincidirem com o snapshot OpenAlex, não transforma as duas fontes em coleções equivalentes nem comprova completude ou independência de cobertura.

Os filtros observados na interface são condições dessa recuperação, não critérios retroativos de exclusão do corpus nacional. A seleção temática nacional aprovada não exige afiliação brasileira; `national_production=1` não comprova afiliação, nacionalidade da pessoa ou contexto da pesquisa. A recuperação CAPES também não demonstra, por si, pertinência substantiva ao PIBID.

## Datas e critérios mantidos

Publicação nacional de 01/01/2007 a 08/11/2026; revisão goiana de 2020 ao mesmo corte, com a alternativa de defesa 2020–2026 exclusivamente regional. A coleta OpenAlex ocorreu em 15/11/2026; a CAPES, em 16/11/2026. Uma coleta posterior pode recuperar obra publicada antes do corte, mas não reconstitui a indexação nessa data. Ano 2026 sem dia/mês não demonstra publicação até 08/11; os dados de publicação e defesa não são intercambiáveis.

O RIS não tem resumos, palavras-chave, afiliações ou data completa em campos próprios. Reaproveitam-se os metadados e leituras arquivados quando a identidade está sustentada. Título específico pode sustentar tema pela regra vigente; menção genérica, rótulo editorial ou recuperação na busca não bastam. Ausência de informação não é evidência de ausência do fenômeno ou critério automático de exclusão.

## Identidades, metadados e registros provisórios

Cada ocorrência CAPES conserva sua posição, ID original e metadados literais. Todas as recuperações de uma mesma obra contam como proveniências, não como obras adicionais. A fusão de dois componentes anteriormente incluídos para “Quero ser professora” é sustentada por título, autoria, ano, dois DOIs e o mesmo PID em localizações arquivadas. Os identificadores anteriores permanecem numa ponte.

Na etapa bibliográfica foram vinculadas 665 ocorrências. As dez restantes são representadas como componentes provisórios, separados de obras únicas confirmadas; seus candidatos e motivos permanecem na fila. Isso permite inventariar as 675 ocorrências e 14.423 registros de proveniência sem incluir automaticamente novas obras no corpus.

Conservar divergências de autoria, tipo, ano e DOI por fonte; não substituir créditos de pessoas a partir de AU concatenado. “Práticas de leitura” mantém publicação sustentada em 2013 e registra 2019 como metadado CAPES discordante. O reparo do prefixo DOI repetido no registro Cury é uma chave comparativa explícita, preservando o campo original. Ligação de identidade não valida automaticamente um DOI adicional.

## Separação entre versões e interpretação

Os corpora, decisões e a entrega anterior permanecem preservados. Os resultados incrementais da elegibilidade estão em `dados/analises/integracao_capes_20261116/elegibilidade/`, com manifesto e verificações. Esse diretório é o insumo da próxima etapa de cálculo, não a nova entrega final.

Os indicadores anteriores 196/7.780 (2,52%) e 67/3.459 (1,94%) são linha de base, não valores recalculados da integração. A atualização deve separar sobreposição nominal, vínculos bibliográficos e sobreposição por obras elegíveis; manter numerador e denominador no mesmo corpus/período; distinguir afiliação e contexto goiano; e preservar a participação total como não estimável enquanto faltarem cobertura e metadados suficientes. A metodologia substituta deve expor essa separação e as diferenças de escopo das consultas.
