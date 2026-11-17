# Marco 4 — indicadores e respostas canônicas

**Estado: executado até o limite dos dados arquivados.** Foram produzidas as tabelas de indicadores e a [síntese das seis subquestões](Sintese%20das%20seis%20subquestoes.md), na ordem de `Vaneria.txt`, com evidências vinculadas. O panorama nacional permanece operacional e parcial; não houve alteração de corpus, decisão histórica ou coleta. Não foi iniciado o Marco 5.

## Dados e decisões reaproveitados

Foram preservados o corpus nacional de 7.780 obras em `dados/analises/marco2_fechamento/Corpus nacional.csv`, seu registro de decisões e proveniência; as 97 obras regionais e sua proveniência do Marco 3; as 291 extrações de eixos; e a fila residual regional. Aplicaram-se os critérios do protocolo v1.3, o plano de realinhamento e os objetivos canônicos de `Vaneria.txt`.

As 125 páginas OpenAlex de 15/11/2026 foram lidas localmente para extrair os campos necessários aos indicadores: `authorships.author`, `authorships.institutions`, `country_code`, `primary_topic` e `keywords`. Isso complementa metadados; não reexecuta coleta nem triagem de elegibilidade. Foram retidos os metadados de 7.796 registros OpenAlex ligados aos corpora, incluindo múltiplos registros de quatro componentes nacionais. Os 136 hashes dos 11 insumos e 125 páginas estão em [Auditoria.json](Auditoria.json).

## Produtos, denominadores e regras

O [estado dos indicadores](Estado%20dos%20indicadores.csv) separa consolidado no corpus observado, parcial e não estimável. A tabela [Obras dos indicadores](Obras%20dos%20indicadores.csv) tem 7.877 linhas escopo/obra: 7.780 nacionais e 97 regionais. Como os corpora se sobrepõem, 7.877 não é um total de obras distintas de um universo combinado.

| Indicador | Arquivos | Denominador e contagem |
|---|---|---|
| Evolução | [nacional](Evolucao%20nacional.csv), [regional](Evolucao%20goiano.csv) | N=7.780 / 97; ano unívoco, divergente e não informado separados; defesa em estrato próprio |
| Tipos documentais | [nacional](Tipos%20documentais%20nacional.csv), [regional](Tipos%20documentais%20goiano.csv) | Uma categoria harmonizada por obra; totais reconciliam aos corpora |
| Autorias | [nacional](Autorias%20nacional.csv), [regional](Autorias%20goiano.csv), [créditos](Creditos%20de%20autoria.csv) | Uma ocorrência por pessoa identificada/obra; integral=1 e fracionária=1/n autores observados |
| Coautoria | [nacional](Coautoria%20nacional.csv), [regional](Coautoria%20goiano.csv) | Pelo menos duas pessoas observadas; autoria faltante não é autoria individual |
| Instituições | [nacional](Instituicoes%20nacional.csv), [regional](Instituicoes%20goiano.csv), [créditos](Creditos%20institucionais.csv) | Uma ocorrência por instituição única/obra; integral=1 e fracionária=1/k instituições mapeadas |
| Geografia | [nacional](Geografia%20pais%20nacional.csv), [regional](Geografia%20pais%20goiano.csv), [créditos](Creditos%20geograficos.csv) | País da instituição, uma ocorrência país/obra; múltiplos países podem coexistir; fração=1/c países conhecidos |
| Temáticas | [nacional](Tematicas%20OpenAlex%20nacional.csv), [regional](Tematicas%20OpenAlex%20goiano.csv), [por obra](Topicos%20por%20obra.csv) | Um `primary_topic` por obra com campo; classificação algorítmica OpenAlex |
| Palavras-chave | [nacional](Palavras%20chave%20OpenAlex%20nacional.csv), [regional](Palavras%20chave%20OpenAlex%20goiano.csv) | Palavras-chave algorítmicas do OpenAlex; multirrótulo, não aditivas |
| Participação observada | [nacional](Participacao%20e%20contexto%20Goias.csv), [período comum](Participacao%20periodo%20comum.csv) | 196/7.780=2,52% (2007–corte); 67/3.459=1,94% (2020–corte); não participação total |
| Contexto goiano | [contextos](Contexto%20Goias%20separado.csv), [correspondência](Correspondencia%20Goias%20Brasil.csv) | Contagem no conjunto regional; não confundir com afiliação nem extrapolar ao corpus nacional inteiro |
| Três eixos | [indicadores](Indicadores%20dos%20eixos.csv), [evidências](Evidencias%20dos%20eixos.csv) | 97 obras por eixo; 291 pares obra/eixo; eixos se sobrepõem |

Os percentuais nas tabelas de frequência usam o corpus inteiro do escopo como denominador, com a disponibilidade do campo explicitada. As contagens integrais de pessoas, instituições, países e palavras-chave não somam N, pois uma obra pode ter várias categorias. As frações somam uma unidade por obra **com o campo mapeado**: 7.753 obras nacionais com autoria, 4.228 com instituição/país; 97 e 83 respectivamente no regional. Não se redistribuiu crédito das obras sem campo.

Identidades de pessoa: ORCID, quando arquivado; OpenAlex Author ID quando não há ORCID; nome normalizado como fallback, sem fusão aproximada de nomes. Foram propagados ORCIDs unívocos em 5.977 identificadores OpenAlex, sem conflitos de ORCID observados nessa referência cruzada. Isso evita separar artificialmente o mesmo identificador quando o ORCID falta numa publicação; não constitui validação externa da pessoa. Veja [referência cruzada](Referencia%20cruzada%20de%20autoria.csv). Instituições usam OpenAlex Institution ID, com nome como fallback; não se fundiram automaticamente instituições após desmembramentos, campi ou mudanças históricas.

Para componentes com múltiplos OpenAlex, escolheu-se um único registro: maior número de autorias pessoais, depois maior número de autorias com instituição, depois ID como desempate determinístico. Assim, não se somam listas de autores de registros duplicados. Os quatro componentes foram conferidos: autoria nominal, tipo e tópico concordam; afiliações diferem em completude. Todos os anos discordantes permanecem visíveis. A fonte escolhida é registrada por obra, e as demais proveniências permanecem nos marcos anteriores.

Tipos: rótulos equivalentes `Artigo/article` foram harmonizados; `Tese/dissertation` e `Dissertação/dissertation` usam o grau explícito; `dissertation` sozinho permanece “tese/dissertação sem grau discriminado”. Não foram inventados graus ou promovidos rótulos insuficientes fora do corpus elegível.

## Cobertura e comparabilidade

| Campo | Nacional | Regional |
|---|---:|---:|
| Autoria informada | 7.753/7.780 | 97/97 |
| Todas as pessoas observadas com identificador | 7.207/7.780 | 81/97 |
| Afiliação conhecida | 3.024 (38,87%) | 51 (52,58%) |
| Afiliação parcial | 1.485 (19,09%) | 34 (35,05%) |
| Afiliação desconhecida | 3.271 (42,04%) | 12 (12,37%) |
| Instituição e país mapeados | 4.228/7.780 | 83/97 |
| Tópico principal OpenAlex | 7.777/7.780 | 93/97 |

“Conhecida”: todas as autorias pessoais observadas têm instituição mapeada e não há rótulo institucional sinalizado em autoria. “Parcial”: alguma instituição/afiliação textual ou evidência regional explícita está disponível, mas não todas as autorias estão mapeadas ou há alerta. “Desconhecida”: não há evidência de afiliação nos campos utilizados. Essas categorias descrevem cobertura no arquivo, não completude comprovada do mundo real. A cobertura institucional da tabela de rankings usa apenas instituições mapeadas em `authorships`; evidência histórica goiana não foi convertida em identificador institucional fictício. Evidência: [cobertura](Cobertura%20de%20campos.csv).

O numerador goiano foi construído **dentro do corpus nacional**, por variantes de IES documentadas no Marco 3 ou afiliação regional já sustentada, sem usar instituição de depósito como afiliação. Por isso é uma contagem conservadora de afiliação identificada, não uma classificação exaustiva de toda instituição possivelmente goiana. Ausência de reconhecimento não significa não Goiás. As 196 obras e as 7.780 usam o mesmo período nacional, tipos e regras. O segundo cálculo usa apenas as 3.459 nacionais cujos anos de publicação estão inteiramente em 2020–2026, incluindo a divergência 2022/2025 no mesmo intervalo. Nenhuma das quatro inclusões regionais por defesa foi inserida artificialmente no denominador ou numerador.

Somente 78/97 obras regionais pertencem ao nacional congelado; 66 delas têm afiliação goiana documentada regionalmente. O restante exige propagação explícita de decisões ou publicação comprovada antes de eventual comparação. A participação total Goiás–Brasil permanece não estimável: a coleta não mede todo o universo e 42,04% das afiliações nacionais são desconhecidas. Os 2,52% e 1,94% não devem ser apresentados sem o qualificativo “fração identificada no corpus operacional”.

O contexto regional foi preservado separadamente: 56 obras com contexto local/institucional documentado, duas com objeto goiano sem local escolar verificado; não são automaticamente 58 pesquisas em escolas de Goiás. Os demais estados estão tabulados. Não se calculou proporção de contexto goiano em todo o nacional, pois sua triagem não foi realizada integralmente.

## Resultados e limites que alteram interpretação

Os três eixos mantêm as 291 decisões do Marco 3:

| Eixo | Presente | Não informado | Não verificável | Denominador |
|---|---:|---:|---:|---:|
| Aprendizagem/identidade | 66 | 24 | 7 | 97 |
| Trajetórias | 6 | 87 | 4 | 97 |
| Relações IES–escolas–comunidades | 51 | 34 | 12 | 97 |

“Presente” abrange objetivo, expectativa, abordagem ou resultado relatado; não é prova uniforme de efeito. “Não informado” não estabelece ausência do fenômeno. “Não verificável” indica insuficiência do material. As menções específicas registradas (14 comunidades, uma saberes escolares/comunitários, duas espaços híbridos) são localização conservadora, não diagnóstico de inexistência nos demais estudos. A síntese distingue intenções de resultados e aprendizagens dos escolares de aprendizagem docente.

A série nacional tem 7.778 obras com ano unívoco e duas divergentes: `M2-b392c929d917bbc5` (2011/2012) e `M2-fa2ee6741136b725` (2022/2025). A divergência altera a distribuição anual, não a contagem do corpus. Há limites inferiores/superiores por ano nas tabelas: cada obra divergente pode ocupar um dos seus anos, não todos. Somar limites superiores contaria essas obras duas vezes. A distribuição regional separa 93 publicações e quatro defesas; não se atribuiu publicação à defesa. O ano 2026 é incompleto em ambos os escopos.

As 871 pendências regionais continuam fora das 97 inclusões. O par artigo/capítulo `M2-6fc274039407a243` / `M2-f5ac63d543e7078a` permanece fora da revisão e pode acrescentar uma ou duas obras. No nacional congelado, ambos estão incluídos; resolver que são a mesma obra reduziria o denominador nacional em uma unidade e exige manter todas as proveniências e recalcular os indicadores. Somente o capítulo tem afiliação goiana identificada nos metadados selecionados; a fusão preservaria essa evidência. Não se resolveu identidade a partir de DOI diferente ou resumo equivalente isoladamente.

Afiliação não é contexto: há uma obra sobre UNIFESSPA/Pará incluída por vínculo UFCAT. Estudos nacionais ou com múltiplos contextos não viraram pesquisas locais. Publicações relacionadas do mesmo projeto não são amostras independentes. As classificações OpenAlex não foram apresentadas como categorias dos autores ou como achados empíricos. Sem campo sistemático de grupos, UF/região e sem qualidade suficiente para uma rede consolidada, esses resultados ficaram não estimáveis, sem inventar grupos por agrupamento algorítmico.

## Verificações efetivamente executadas

Passaram **24 verificações internas**, registradas em [Verificacoes internas.csv](Verificacoes%20internas.csv): hashes dos insumos; unicidade escopo/obra; reconciliação temporal e documental; cobertura de afiliação; soma de pesos de pessoas/instituições/países por obra com campo; preservação dos 291 pares e seus estados; correspondência 78/97; numerador compatível 196/7.780; duas divergências explícitas; período comum 67/3.459 sem defesa; localização exata de nove trechos qualitativos; exclusão de rótulos institucionais do ranking de pessoas; mapa das seis respostas; existência dos caminhos dos metadados.

A [conferência adicional](Conferencia%20adicional.csv) tem 40 entradas: oito registros OpenAlex de quatro componentes duplicados, dez verificações qualitativas por obra/extração e 22 ocorrências de autoria institucional em 18 obras. Foram revisitadas as seis obras com trajetória e exemplos de aprendizagem, comunidade e espaços híbridos. Duas localizações automáticas frágeis foram complementadas na evidência da síntese: `M2-241143e71e333621` tinha no eixo A um trecho sobre orçamento, embora o resumo sustentasse aprendizagem; `M2-c45f9d2575dddbd5` tinha no eixo T um trecho sobre objetivo genérico do programa, embora o resumo sustentasse resultado crítico sobre carreira. Os estados permaneceram “Presente”; a interpretação passou a usar os resultados específicos. O corpus e as extrações anteriores não foram sobrescritos.

Foram removidos dos créditos de pessoas os 22 rótulos institucionais identificados, mantendo os dados brutos e as obras. O ORCID unívoco foi propagado entre registros com o mesmo identificador de autor, sem fusões aproximadas. As diferenças de ano foram expostas, sem escolher silenciosamente uma data. Nenhuma dessas correções alterou as 7.780 ou 97 inclusões.

Passaram **28 testes existentes e novos dos marcos**, sendo sete testes novos de indicadores: equivalência de rótulos documentais, grau não discriminado, tipos diferentes preservados, instituição não tratada como pessoa, cobertura parcial/desconhecida e identidade ORCID sem fusão em conflito. A revisão é interna; não mede acurácia nem constitui validação independente. Confirmação externa de versões, identidades ou textos integrais ausentes foi tratada como limitação documental, sem bloquear as contagens verificáveis.

## Reprodução e encaminhamento ao Marco 5

A partir da raiz, sem rede:

```text
python -m scripts.produzir_indicadores_marco4
python -m scripts.documentar_conferencias_marco4
python -m scripts.verificar_marco4
python -m unittest discover -s tests -p "test_*marco*.py"
```

Os scripts recusam sobrescrita; para reconstruir somente os produtos desta rodada, acrescentar `--atualizar`. Os relatórios Markdown são documentos de interpretação; as tabelas e as conferências são geradas pelos scripts. Os corpora e as páginas de origem não são modificados. O [inventário](Inventario%20de%20produtos.csv) lista arquivos e hashes dos produtos para a conferência final.

Para o Marco 5: transportar as tabelas e suas notas para a planilha simplificada e gráficos editáveis; conferir visualmente cada gráfico; conferir fórmulas, filtros, integridade e igualdade de contagens; manter o mesmo qualificativo dos resultados parciais e não estimáveis; incorporar os marcos e a matriz de cobertura ao pacote reproduzível. Qualquer correção autorizada de identidade ou propagação de inclusão regional ao nacional exige regenerar os indicadores, sem alterar silenciosamente denominadores. As quatro defesas, o par artigo/capítulo, as afiliações desconhecidas e as pendências regionais devem acompanhar a entrega. Nenhuma dessas tarefas de empacotamento ou validação externa foi apresentada como concluída nesta rodada.
