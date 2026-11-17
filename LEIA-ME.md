# Entrega final — produção científica sobre o PIBID

Versão integrada CAPES de 16/11/2026. Este diretório é autossuficiente para consultar os resultados e reconstruir os produtos desde os corpora e decisões congelados. Não depende dos caminhos do computador de origem. Abra os arquivos após baixar a pasta inteira; mantenha sua estrutura. O ZIP reproduzível também pode ser extraído sozinho em outro diretório.

## Produtos para leitura e escrita do artigo

- [Planilha: obras únicas e seis gráficos nativos editáveis](dados/entregas/marco5_capes_20261116/Planilha%20final%20PIBID.xlsx).
- [Base técnica separada](dados/entregas/marco5_capes_20261116/Base%20tecnica%20PIBID.zip).
- [Matriz de cobertura e sobreposição](dados/entregas/marco5_capes_20261116/Matriz%20de%20cobertura%20e%20sobreposicao.xlsx).
- [Relatório metodológico atualizado](dados/entregas/marco5_capes_20261116/Relatorio%20metodologico.md).
- [Síntese das seis subquestões, com referências às evidências](dados/entregas/marco5_capes_20261116/Sintese%20das%20seis%20subquestoes.md).
- [Pacote reproduzível completo, cerca de 507 MB](dados/entregas/marco5_capes_20261116/Pacote%20reproduzivel%20PIBID.zip).
- [Nota sobre agentes de codificação e direção humana](Nota%20metodol%C3%B3gica%20-%20uso%20de%20agentes%20de%20codifica%C3%A7%C3%A3o.md).

## Revisão por partes

1. **Fundamentos e decisões:** `Vaneria.txt`, protocolos v1.3/v1.4, planos e aceites na raiz. Documentos históricos mantêm seus estados originais: não são instruções para substituir os resultados atuais.
2. **Dados abertos e rastreabilidade:** [corpora, proveniências, decisões e pendências em CSV](dados/analises/integracao_capes_20261116/elegibilidade/). O [dicionário](DICIONARIO_DOS_DADOS.md) explica unidades e chaves; o [catálogo de campos](CATALOGO_CSV.csv) informa cabeçalhos e contagens. CSV usa vírgula e UTF-8, com ou sem marcador BOM; células vazias não significam ausência do fenômeno.
3. **Cobertura e indicadores:** [tabelas atuais](dados/analises/integracao_capes_20261116/indicadores/) e [matrizes](dados/entregas/marco5_capes_20261116/matriz/). Fontes sobrepostas não são aditivas.
4. **Evidência qualitativa:** `Tres eixos.csv`, materiais locais e decisões regionais; use fonte, localização e estado da evidência. Não presumir leitura integral de todas as obras.
5. **Figuras e conferências:** [prévias PNG/PDF](dados/entregas/marco5_capes_20261116/previews/), `Conferencia visual.csv`, `Conferencias da entrega.csv`, `Testes.txt` e `Teste de reconstrucao.json`, na pasta dos produtos.
6. **Reprodução:** [instruções da versão CAPES](REPRODUZIR_INTEGRACAO_CAPES.md), scripts, testes, requisitos, arquivos brutos e logs. O roteiro antigo `REPRODUZIR_MARCO5.md` é histórico. Execute em cópia de trabalho. Python/openpyxl bastam para leitura e cálculos; Windows/Excel são usados para recálculo e exportação nativos dos gráficos. Executáveis não são incluídos.

## Resultados e limites que devem acompanhar qualquer publicação

São 7.779 obras nacionais, 97 goianas e 7.798 na união deduplicada da planilha; 78 regionais correspondem ao nacional. As frações observadas de afiliação goiana identificada são 196/7.779 (2,52%), publicação 2007–08/11/2026, e 67/3.459 (1,94%), publicação 2020–08/11/2026. A participação total é não estimável. Contexto e afiliação são dimensões separadas.

Permanecem 871 pendências regionais, quatro inclusões por defesa, dúvida artigo/capítulo, dez ocorrências CAPES provisórias e afiliações incompletas. A busca CAPES é filtrada, com 23 páginas declaradas; não demonstra completude. Coletas: OpenAlex 15/11 e CAPES 16/11/2026; corte de publicação 08/11/2026. Resultados consolidados nos conjuntos observados não equivalem ao universo completo. As verificações são internas, sem validação científica independente.

## Integridade e publicação

[VERIFICACAO_DA_REUNIAO.json](VERIFICACAO_DA_REUNIAO.json) registra as verificações desta organização. [MANIFESTO_SHA256.csv](MANIFESTO_SHA256.csv) lista todos os arquivos da pasta, exceto o próprio manifesto e seu arquivo de checksum; o checksum do manifesto está em `MANIFESTO_SHA256.sha256`. Os inventários antigos referem-se a suas versões, não a toda esta pasta. Logs históricos podem conter caminhos absolutos do computador de origem; a reprodução usa caminhos relativos.

Esta organização não altera o ZIP selado nem os resultados científicos. A nota de agentes e os guias desta pasta são suplementos externos ao ZIP. Consulte [PUBLICACAO_E_METADADOS.md](PUBLICACAO_E_METADADOS.md) antes do depósito: licença, autoria, identificadores e permissões de redistribuição ainda precisam ser definidos pelos responsáveis. Nenhum depósito público foi realizado.
