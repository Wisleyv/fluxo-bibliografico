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
