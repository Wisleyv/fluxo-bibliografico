# Rodada de fechamento do Marco 2

**Estado:** subconjunto operacional incluído consolidado; **o universo do Marco 2 ainda não pode ser declarado integralmente fechado**. A definição nacional foi resolvida pelo usuário. Persistem casos sem evidência suficiente para tema, tipo, publicação ou identidade; não foram convertidos em exclusões para produzir um fechamento artificial.

## Arquivos da rodada

- [Corpus nacional: incluídas](Corpus%20nacional.csv).
- [Proveniência completa](Proveniencia.csv).
- [Cobertura atualizada por fonte](Cobertura%20atualizada.csv).
- [Registro de todas as decisões](Registro%20de%20decisoes.csv).
- [Fila residual](Pendencias%20residuais.csv) e [elegíveis com identidade pendente](Elegiveis%20com%20identidade%20pendente.csv).
- [Revisão das cinco prioridades de identidade](Revisao%20de%20identidades%20prioritarias.csv) e [estado das relações anteriores](Estado%20de%20todas%20as%20relacoes.csv).
- [Tipos com efeito imediato na inclusão](Tipos%20com%20efeito%20imediato.csv).
- [Amostra de regras](Amostra%20de%20conferencia%20de%20regras.csv), [conferência da amostra](Conferencia%20da%20amostra%20de%20regras.csv) e [auditoria](Auditoria.json).
- [Candidatos por defesa para o Marco 3](Candidatos%20por%20defesa%20para%20Marco%203.csv) e [candidatos OpenAlex sinalizados](Candidatos%20OpenAlex%20sinalizados%20para%20Marco%203.csv).

A versão anterior continua integralmente em `dados/analises/marco2/`. Esta rodada não alterou o corpus provisório, a base técnica ou as decisões históricas. Os identificadores anteriores estão preservados nas colunas `ids_anteriores` do registro e `obra_id_anterior` da proveniência.

## Escopo registrado

A instrução do usuário definiu produção brasileira como conjunto nacional de obras elegíveis sobre PIBID recuperadas pelas fontes previstas; ausência de geografia não impede inclusão. A interpretação foi registrada no protocolo v1.3, na raiz, e referenciada no protocolo histórico. Não foi encontrada incompatibilidade explícita com `Vaneria.txt`: a busca nacional é temática e a classificação geográfica é posterior.

Conservaram-se todos os idiomas, o período **01/01/2007–08/11/2026** e a coleta **15/11/2026**. O ano de defesa alternativo continua exclusivamente regional. Não se preencheu publicação com defesa, depósito ou data de coleta. Não se aplicou filtro de país ou afiliação.

## Decisões de identidade prioritárias

As cinco pendências do núcleo de 138 foram examinadas com os materiais locais:

1. **Autoformação docente/Samara Abreu:** tese UECE 2021 (siduece 98506) e publicação RBPAB 2022, volume 7(20), páginas 241–246, com DOI próprio, permanecem publicações distintas relacionadas. O resumo da tese reproduzido no artigo não prova identidade da publicação. Duas relações foram resolvidas como distintas, sem fundir tese e texto do periódico.
2. **Igor Galho Teixeira/UNIPAMPA:** controles BDTD e Catálogo têm título, autoria, instituição, grau e defesa 2024 concordantes; resumos português/espanhol descrevem o mesmo objeto e três encontros de duas horas. Identidade confirmada entre os controles.
3. **Cheila Raiane Menezes Oliveira/UFS:** título, autoria, dissertação e defesa 2024 concordam; resumos inglês/português descrevem a mesma investigação de pensamento computacional no PIBID. Identidade confirmada entre os controles.
4. **Juliana Leal Salmasio/UFMS:** título, autoria, tese, defesa 2024 e TeDiMEM concordam; resumos traduzidos descrevem oito estudantes e 32 reuniões. Identidade confirmada entre os controles.
5. **Práticas de leitura no ensino médio:** o PID SciELO S2176-66812013000300007 está nas localizações arquivadas do OpenAlex. Título, ano e três autoras concordam; nomes institucionais foram indevidamente agregados à autoria da API. Correspondência confirmada com o artigo OpenAlex.

As quatro confirmações provocam **quatro fusões adicionais de componentes**, de 13.226 para 13.222. O conjunto anterior de 138 não perde unidade: cada uma das quatro fusões liga uma unidade do núcleo a outra que ainda estava fora dele. Os vínculos OpenAlex já sustentados e os 40 pares históricos continuam preservados. Novas decisões não reescrevem as classificações antigas.

## Regras objetivas e pertinência

A amostra anterior havia identificado obras pertinentes sem a sigla no título, formatos acadêmicos mal rotulados e resumos traduzidos. A rodada ampliou a avaliação para todos os componentes, aproveitando cada título/resumo de origem, sem leitura individual integral dos 12.431 registros OpenAlex.

Três caminhos sustentam a inclusão temática:

- leitura anterior registrada, incluindo as decisões e a amostra do Marco 2;
- título que explicita o programa como objeto formativo ou investigativo, com relação de formação, aprendizagem, experiência, contribuição, análise, prática ou equivalente;
- frase de resumo que relaciona a pesquisa, ação ou participantes investigados ao PIBID e à educação/formação, com enquadramento do próprio estudo ou da atividade realizada.

Cada decisão nova guarda a regra, o registro e o trecho selecionado. As regras abrangem português, inglês e espanhol. A sigla isolada, objetivo genérico do programa, agradecimento ou nome de evento não bastam. Resumo ausente não é exclusão. Títulos ou resumos sem evidência suficiente ficam pendentes. São **decisões operacionais por regras**, não alegação de leitura humana de milhares de documentos ou validação independente.

Quanto aos formatos, mantiveram-se os tipos acadêmicos compatíveis já usados. Resumos em anais, preprints e outros formatos acadêmicos são aceitos quando autoria, veículo/DOI e conteúdo dão suporte. Um DOI sozinho não prova natureza acadêmica: para `other` exige-se também gênero de pesquisa/relato explícito no resumo e fonte identificada. Para editoriais genéricos, conteúdo de trabalhos descritos dentro de uma apresentação não foi automaticamente atribuído ao editorial como pesquisa própria. O rótulo original continua disponível na proveniência.

## Composição: de 138 para 7.780 incluídas operacionais

| Medida | Quantidade | Unidade |
|---|---:|---|
| Entradas preservadas | 13.748 | registros: 12.431 OpenAlex + 1.317 controles |
| Componentes anteriores | 13.226 | unidades antes desta rodada |
| Fusões novas | 4 | reduções adicionais de componentes |
| Componentes após revisão | **13.222** | unidades de identidade sustentada |
| Incluídas no corpus operacional | **7.780** | unidades sem pendência registrada de elegibilidade/identidade |
| Elegíveis com identidade ainda pendente | **285** | unidades fora da contagem incluída |
| Demais pendentes | **5.157** | unidades sem suporte completo em algum critério |
| Exclusões finais novas | **0** | obras excluídas definitivamente nesta rodada |

Reconciliação: **7.780 + 285 + 5.157 = 13.222**; todas as 13.748 entradas ligam exatamente a um componente na proveniência. As 138 unidades anteriores foram preservadas e entram nas 7.780; há **7.642 inclusões operacionais adicionais**. Não se somam relações de pares ou linhas de fonte ao número de obras.

Das incluídas, 138 reaproveitam leituras anteriores, 5.200 têm título com objeto explícito e 2.442 têm suporte da relação investigativa no resumo. As 285 unidades com identidade pendente ficam em arquivo próprio: não são contadas como únicas confirmadas. Isso produz uma contagem conservadora em relação às candidaturas por título conhecidas; não demonstra ausência absoluta de duplicatas além das relações examinadas.

Há 7.777 componentes incluídos com OpenAlex e **três incluídos exclusivamente complementares**. O antigo quarto complementar, `ebceb9d5`, agora tem correspondência OpenAlex confirmada e passa a compartilhar proveniência, sem ser contado duas vezes. Os outros três são Plataforma Inglês Paraná, Um esboço crítico sobre parceria e Quero ser professora. Os códigos e arquivos de todas as fontes permanecem na proveniência.

Os totais por fonte se sobrepõem: uma obra pode aparecer em várias. A matriz de cobertura explicita registros, unidades e estados por fonte; sua soma por registros é 13.748, enquanto a soma de unidades por fonte não é o total nacional.

## Datas divergentes

Os quatro componentes com anos discordantes mantêm ambos os anos, inclusive **2014/2015** no caso original. Nenhum conjunto de anos atravessa o corte de 08/11/2026 ou a fronteira 2020. As divergências não foram usadas para excluir obras do período; também não se escolheu um ano canônico artificial para gráficos.

Dois desses componentes estão incluídos, um tem identidade pendente e outro ainda não tem suporte temático suficiente pelas regras. O caso original 2014/2015 está no conjunto elegível com identidade pendente, não bloqueado pelo ano. A decisão sobre ano preferencial continua necessária somente antes da série anual, com preservação da fonte.

## Conferências e limites

- Preservação das cinco entradas principais verificadas por SHA-256 antes/depois; arquivos do Marco 2 anterior não foram sobrescritos.
- Partição das 13.748 entradas, relação um-registro→uma-unidade, 13.222 IDs únicos, existência dos caminhos dos brutos e reconciliação dos estados persistidos.
- Preservação das 138 unidades anteriores, sem inclusão dependente de afiliação/geografia.
- Reaproveitamento da validação anterior das 125 páginas, cursores e datas; nenhuma nova chamada externa.
- Nova amostra reproduzível de **42 unidades**, semente 20261116, seis por combinação disponível de regra temática/estado, sem selecionar as 138 já lidas. Foram inspecionados título, trecho selecionado e estado: 12 incluídas, 12 elegíveis com identidade pendente e 18 pendentes. As pendências não se tornaram exclusões; os trechos selecionados dos casos positivos são compatíveis com as regras. Essa checagem não estima acurácia nem substitui revisão científica independente.
- **19 testes focados aprovados**, incluindo seis novos de tema: sigla isolada, título com objeto explícito, metadado de evento, objetivo genérico do programa, relação investigativa em resumo e inglês. Os testes anteriores verificam datas, identidade, distinção tese/artigo e denominadores.

Reprodução: `python -m scripts.fechar_marco2` produz os arquivos em novo diretório e recusa destino existente. `--atualizar` regenera somente os produtos desta rodada, preservando as entradas históricas. `python -m scripts.verificar_fechamento_marco2` reabre os resultados e confere a partição e os hashes. A auditoria conserva os totais da rodada e as entradas utilizadas.

## Pendências específicas e fechamento

A definição nacional **não é mais uma pendência**. Ainda existem **5.442 unidades fora do corpus incluído** (285 + 5.157). Os motivos se sobrepõem:

| Motivo | Unidades afetadas |
|---|---:|
| Pertinência insuficientemente sustentada | 4.632 |
| Relação de identidade pode alterar contagem | 696 |
| Natureza acadêmica/tipo sem suporte suficiente | 157 |
| Publicação no corte não comprovada | 786 |

Não somar essa tabela como se fossem unidades distintas. As 696 unidades com relações de identidade incluem tanto elegíveis quanto casos com outros critérios pendentes. As decisões individuais estão na fila residual e o estado das relações está em arquivo separado.

Para os tipos, **39 unidades** já têm tema e publicação sustentados e poderiam mudar a composição assim que sua natureza/contagem fosse resolvida. A tabela Tipos com efeito imediato lista exatamente quais:

- **12 datasets/depositórios:** distinguir dados de pesquisa autônomos de espelhos/suplementos de artigos. Parte dos registros Figshare reproduz título e resumo de artigo. Decisão específica: dados de pesquisa autônomos devem contar como obra acadêmica separada? Mesmo se a resposta for sim, espelhos ainda exigem conciliação; o efeito máximo imediato desse grupo é 12 unidades antes dessa deduplicação.
- **15 registros de paratexto/anais completos:** decidir se o volume integral misto de evento que inclui PIBID conta como obra temática autônoma ou se só entram contribuições individualizadas sobre o programa. Um nome de evento não torna cada contribuição pertinente. Efeito máximo imediato: 15 unidades; título/abstract podem descrever o volume ou um trabalho agregado incorretamente.
- **Sete editoriais e cinco registros “other”:** falta evidência discriminante de gênero/conteúdo ou metadado atribui ao recipiente o resumo de outra contribuição. Não se pede aprovação em bloco: a providência é classificação bibliográfica com os materiais disponíveis, mantendo pendente se eles não bastarem.

Os demais tipos sem suporte também têm tema/data pendentes; aprovar um tipo não os inclui automaticamente. Não é necessária nova decisão para excluir registros por falta de geografia: essa exclusão não existe. Tampouco há base para excluir definitivamente os 4.632 casos de tema insuficiente apenas para reduzir a fila.

**Conclusão de estado:** o subconjunto operacional incluído está fechado nesta versão, com regras e proveniência; o Marco 2 completo permanece aberto pelas pendências acima. Não apresentar 7.780 como total exaustivo da produção brasileira nem converter os casos fora do corpus em resultados negativos. O próximo trabalho deve selecionar casos que alterem inclusão/identidade, em vez de repetir toda a coleta ou toda a consolidação.

## Transferência para o Marco 3

Foram preservadas **417 linhas de teses/dissertações com defesa 2020–2026**, incluindo a ressalva de data incompleta de 2026. Elas não representam 417 obras goianas elegíveis: a fila conserva contexto e afiliação para o exame regional. A falta de publicação nacional não elimina a via temporal por defesa.

Foram também relacionados aos IDs atuais os **100 registros OpenAlex de 2020–2026 com sinais geográficos** da fila já arquivada. Esses sinais não comprovam contexto/afiliação, não esgotam nomes de IES e não podem excluir os demais registros. As duas filas podem se sobrepor e não devem ser somadas. O exame regional deverá usar o mapeamento de proveniência e as decisões nacionais como evidências, mantendo independentes os critérios regionais. Não houve nova seleção ou extração de eixos de Goiás nesta rodada.
