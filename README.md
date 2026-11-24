# Fluxo bibliográfico

Dados, protocolos e rotinas para coleta, conciliação e análise de registros bibliográficos. A aplicação documentada neste projeto é a produção científica sobre o PIBID no Brasil e em Goiás. A adaptação a outros temas requer revisão de fontes, consultas e critérios; os scripts atuais não são uma ferramenta genérica pronta.

**Versão 0.1.0.** Repositório: https://github.com/Wisleyv/fluxo-bibliografico . DOI não atribuído. Condições de distribuição documentadas em `documentacao/Procedencia e distribuicao.md`.

## Começar

- [Relatório metodológico integrado CAPES](dados/entregas/marco5_capes_20261116/Relatorio%20metodologico.md).
- [Respostas às seis subquestões](dados/entregas/marco5_capes_20261116/Sintese%20das%20seis%20subquestoes.md).
- [Planilha final e gráficos editáveis](dados/entregas/marco5_capes_20261116/Planilha%20final%20PIBID.xlsx).
- [Matriz de cobertura e sobreposição](dados/entregas/marco5_capes_20261116/Matriz%20de%20cobertura%20e%20sobreposicao.xlsx).
- [Dados atuais e decisões](dados/analises/integracao_capes_20261116/elegibilidade/).
- [Dicionário](DICIONARIO_DOS_DADOS.md).

## Uso do Fluxo Bibliográfico como base empírica

A versão 0.1.0 registra a infraestrutura empírica utilizada na investigação sobre a produção científica relativa ao PIBID no Brasil e em Goiás. O repositório documenta a passagem entre as questões do [documento canônico](Vaneria.txt), a recuperação dos registros, a constituição dos corpora, a produção dos indicadores e a organização das evidências qualitativas. Essa cadeia permite relacionar cada afirmação ao seu escopo, às decisões que a sustentam e às limitações conhecidas.

### Estrutura da composição empírica

O desenho reúne dois movimentos complementares, preservados como unidades analíticas distintas:

- **estudo bibliométrico nacional:** 7.779 obras acadêmicas únicas, com publicação entre 2007 e o corte de 08/11/2026, voltadas à caracterização temporal, documental, autoral, institucional e temática da produção recuperada;
- **revisão de escopo regional:** 97 obras relacionadas a Goiás entre 2020 e o corte de 08/11/2026, examinadas nos eixos de aprendizagem da docência e identidade profissional, trajetórias profissionais e relações entre instituições de ensino superior, escolas e comunidades.

O corpus nacional sustenta o panorama bibliométrico; o corpus regional e suas 291 extrações sustentam a revisão de escopo. Registro de fonte e obra acadêmica não são unidades equivalentes. Afiliação institucional em Goiás, contexto de realização da pesquisa em Goiás e objeto relacionado ao estado também permanecem dimensões separadas.

### Relação entre os produtos e a apresentação acadêmica

| Componente | Produtos de referência | Função empírica |
|---|---|---|
| Delineamento e método | [Documento canônico](Vaneria.txt), [relatório metodológico](dados/entregas/marco5_capes_20261116/Relatorio%20metodologico.md) e protocolos v1.3/v1.4 | Documentam questões, fontes, períodos, critérios, unidade de análise, conciliação, elegibilidade e datas de corte e coleta. |
| Resultados | [Síntese das seis subquestões](dados/entregas/marco5_capes_20261116/Sintese%20das%20seis%20subquestoes.md), [planilha final e gráficos](dados/entregas/marco5_capes_20261116/Planilha%20final%20PIBID.xlsx) e tabelas de indicadores | Reúnem valores, denominadores, períodos, unidades, notas interpretativas e visualizações. |
| Discussão | [Evidências dos eixos](dados/analises/integracao_capes_20261116/indicadores/Evidencias%20dos%20eixos.csv) e tabelas temáticas relacionadas | Ligam as frequências às sínteses, fontes e localizações das evidências por obra e eixo. |
| Considerações e limites | Relatório metodológico, síntese e arquivos de pendências e cobertura | Delimitam o que está sustentado, o que permanece parcial ou não estimável e quais questões emergem das lacunas. |
| Rastreabilidade | [Mapa de evidências](dados/analises/integracao_capes_20261116/indicadores/Mapa%20de%20evidencias%20das%20seis%20subquestoes.csv) e [dicionário dos dados](DICIONARIO_DOS_DADOS.md) | Relacionam subquestões, indicadores, corpus, decisões, proveniência e extrações por meio de chaves documentadas. |

### Encadeamento das evidências

A síntese das seis subquestões constitui a entrada temática dos resultados. Cada resposta remete às tabelas que registram numerador, denominador, período, unidade e estado da informação. O mapa de evidências explicita essas relações. Quando a análise exige retorno à unidade documental, o identificador `obra_id` conecta indicadores, corpus, decisões, proveniência e extrações.

Na revisão de escopo, cada uma das 97 obras possui um registro para cada eixo analítico. Os estados “Presente”, “Não informado” e “Não verificável” mantêm separados o achado positivo, a informação não localizada e a evidência insuficiente. Síntese, fonte e localização permitem conferir a base de uma interpretação e recuperar situações específicas para articulação com a literatura do campo.

Os diretórios dos marcos anteriores conservam estados históricos para auditoria. Eles não constituem lotes adicionais e não devem ser somados ao corpus corrente. Da mesma forma, uma atualização das buscas produziria uma nova versão do estudo, pois fontes remotas, cobertura e resultados se modificam ao longo do tempo.

### Alcance interpretativo

Os resultados descrevem os conjuntos observados e avaliados. A leitura conjunta dos produtos preserva distinções essenciais:

- contagens de coautoria e instituições podem se sobrepor e não formam, necessariamente, categorias exclusivas;
- classificações temáticas do OpenAlex são metadados algorítmicos auxiliares, não categorias declaradas pelos estudos;
- as frações de afiliação goiana representam afiliações identificadas no corpus operacional, não a participação total do estado;
- a razão `97/7.779` não mede participação regional, pois os corpora têm critérios próprios e apenas parte das obras regionais corresponde ao conjunto nacional;
- “Não informado” e “Não verificável” não demonstram ausência do fenômeno;
- presença de evidência em um eixo não equivale a comprovação de eficácia ou causalidade;
- 2026 é um ano incompleto, e pendências de elegibilidade, identidade e cobertura acompanham as conclusões.

A consistência operacional foi examinada por testes, reconciliações de contagens e reconstrução de produtos. Essas verificações sustentam rastreabilidade e reprodutibilidade computacional, mas não substituem validação científica independente, leitura crítica ou responsabilidade autoral.

### Expansão e reaproveitamento metodológico

A expansão da pesquisa específica requer uma nova versão identificada, com preservação dos cortes anteriores, das exportações brutas, dos protocolos e dos registros de decisão. Entre as possibilidades estão atualização das buscas, avaliação das pendências, complementação de metadados, ampliação da leitura de textos completos, validação independente e produção de indicadores atualmente limitados pela cobertura disponível.

Em outras pesquisas bibliométricas, a arquitetura pode ser reutilizada como modelo: protocolo, preservação dos dados brutos, normalização, conciliação de identidades, elegibilidade rastreável, corpus versionado, extração, indicadores e testes. A pergunta, as fontes, os descritores, os períodos, os critérios e as categorias analíticas pertencem a cada novo objeto e exigem adaptação e validação próprias. Os resultados desta aplicação não são transferíveis para outros temas.

## Método e execução

As perguntas e os eixos derivam de `Vaneria.txt`. A unidade nacional é a obra acadêmica única elegível; ocorrências em fontes sobrepostas não são somadas como novas obras. Contexto goiano e afiliação goiana são dimensões distintas. Os critérios e as conciliações estão nos protocolos v1.3/v1.4 e no relatório integrado.

Corte de publicação nacional: 08/11/2026; coleta OpenAlex: 15/11/2026; exportação CAPES: 16/11/2026. Scripts operam sobre dados e decisões arquivados. Não executar coletores para reconstruir produtos.

O [roteiro CAPES](REPRODUZIR_INTEGRACAO_CAPES.md) contém comandos, parâmetros e testes. Ambiente histórico: Python 3.10.11, openpyxl 3.1.5, Windows e Excel por COM para recálculo e exportação nativa. As dependências estão em `requirements-marco5.txt`. Execute em cópia de trabalho e use o manifesto indicado no roteiro. Resultados e padrões antigos continuam históricos; o manifesto seleciona a versão integrada.

A seleção foi ampliada com os insumos arquivados, mas a reconstrução completa desta cópia ainda não foi testada. ZIPs agregados e algumas planilhas intermediárias foram omitidos. O teste de extração do ZIP exige obter ou reconstruir esse pacote. Inventários históricos copiados descrevem suas versões originais, não esta seleção. O LEIA-ME anterior pode conter links para pacotes omitidos; para a navegação atual use este README.

## Resultados e limites

São 7.779 obras nacionais e 97 goianas, com 291 extrações por obra e eixo. A união da planilha é 7.798 obras. As frações observadas de afiliação goiana identificada são 196/7.779 (2,52%), em 2007–08/11/2026, e 67/3.459 (1,94%), em 2020–08/11/2026. Participação total: não estimável. Não confundir afiliação com contexto.

Persistem 871 pendências regionais, quatro inclusões pelo ano de defesa, dúvida de identidade artigo–capítulo e afiliações incompletas. As verificações históricas são internas; não comprovam completude ou validação científica independente.

## Contribuições e uso de IA

Wisley Vilela desenvolveu o fluxo computacional, com apoio de agentes Codex no VS Code. Vanéria Paula Sousa Martins forneceu as diretrizes básicas da pesquisa. Consulte a [declaração de contribuições](documentacao/Contribuicoes.md). As seis interpretações foram apreciadas pelo interlocutor, conforme o [registro de aceites](documentacao/Aceites%20das%20interpretacoes.md). Esse aceite não equivale à revisão individual de todas as obras.

## Como citar

VILELA, Wisley. *Fluxo bibliográfico: coleta, conciliação e análise de registros bibliográficos*. Versão 0.1.0. https://github.com/Wisleyv/fluxo-bibliografico .

[Arquivo BibTeX para baixar](citacao.bib) — abra e salve o arquivo, ou use a opção de download do GitHub quando o repositório estiver publicado. Metadados também disponíveis em [CITATION.cff](CITATION.cff). A referência identifica a versão 0.1.0; não há DOI atribuído. A citação do software não substitui a citação dos conjuntos de dados e das fontes.

## Licenças e divulgação

Licenças autorizadas: MIT para scripts próprios; CC BY 4.0 para documentação e componentes próprios da base. Isso não amplia direitos sobre conteúdo de terceiros. Os textos e o escopo por componente estão em [LICENSE.md](LICENSE.md); os metadados, em [METADADOS.json](METADADOS.json). Condições de terceiros permanecem pendentes. Emails incorporados aos dados de fontes públicas serão preservados conforme decisão do responsável. Caminhos locais, conteúdo binário não integralmente examinado e condições de redistribuição ainda exigem fechamento antes da publicação externa.

## Dados grandes no próprio GitHub

Planejados como anexos de release. Consulte [recuperação dos dados](RECUPERAR_DADOS.md) e o manifesto `dados_release.json`. Versão e anexos: https://github.com/Wisleyv/fluxo-bibliografico/releases/tag/v0.1.0 .
