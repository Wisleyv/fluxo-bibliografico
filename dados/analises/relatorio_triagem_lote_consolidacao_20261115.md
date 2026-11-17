# Triagem em lote e consolidação de decisões

**Data:** 15 de novembro de 2026  
**Base produzida:** [triagem em lote consolidada](./triagem_lote_consolidada_20261115.xlsx).

## Alcance e procedimento

Foram examinadas em lote as **1.196 linhas que ainda não tinham decisão de elegibilidade** na base anterior. A varredura organizou os estados e evidências já registrados; ela **não realizou nova leitura semântica integral de todas as linhas**. Não houve consulta externa nem busca individual para suprir resumos ausentes.

Foram reaproveitadas 87 leituras que já sustentavam exclusão temática preliminar, com confronto dos metadados e resumos originais e dos registros de auditoria existentes. Em 82 linhas, os campos disponíveis não identificam o termo e a leitura temática anterior não identificou relação com o programa. Nas outras cinco, a leitura dos resumos do Catálogo CAPES descreve menção incidental. As exclusões são operacionais e reversíveis se surgirem evidências adicionais; não demonstram ausência do PIBID no texto integral. As buscas em todos os campos e os projetos associados não provam, por si sós, pertinência substantiva nos campos examinados.

Mais duas linhas BDTD foram lidas com seus resumos locais: `6fd8a46d` menciona o PIBID como possibilidade de estudos futuros sobre supervisão, e `6af837ea` o menciona, junto à residência pedagógica, entre experiências que motivaram uma análise de livros didáticos. Ambas receberam exclusão temática no recorte goiano. Existem candidatos de títulos correspondentes no Catálogo CAPES, mas a avaliação dessas duas linhas usou seus próprios resumos e não confirmou duplicidade.

Ao todo, **89 linhas** tiveram a exclusão temática consolidada na coluna de elegibilidade. Essa decisão se refere ao recorte goiano; não substitui uma avaliação específica para o panorama nacional. Os registros continuam preservados.

## Correção de duas datas

As linhas `a3e7321c` e `69c845eb`, duplicata já confirmada, tinham ano de publicação 2017 e exclusão preliminar por período. A [consulta anteriormente registrada](./conferencia_resumos_unb_20261115.json) informa emissão em 26/05/2017, no mesmo dia da incorporação ao repositório, e referência com ano 2017. Essa coincidência **não demonstra publicação distinta da incorporação**. Para aplicar o mesmo critério conservador usado nos demais casos, o ano de publicação foi retirado da coluna correspondente, o período passou a `Incerto` e a exclusão preliminar por período foi revertida. A defesa, a emissão, a referência e a decisão anterior permanecem documentadas. A incerteza é temporal, não uma pendência criada pela falta de resumo.

## Situação da revisão goiana

| Elegibilidade | Linhas |
|---|---:|
| Incluir | 11 |
| Excluir | 199 |
| Pendente | 255 |
| Não iniciada | 852 |
| **Total** | **1.317** |

As 199 exclusões incluem 110 por publicação anterior a 2020 e 89 por critério temático. São **linhas**, não obras únicas; incluem duplicatas. As exclusões temporais dizem respeito apenas à revisão goiana e não ao panorama nacional. A busca de duplicatas não está encerrada.

Na aba **Priorização lote**, as 1.196 linhas inicialmente sem decisão estão organizadas por estados já existentes. Entre as **1.107 ainda sem decisão**:

| Priorização operacional | Linhas |
|---|---:|
| Período e vínculo com Goiás não estabelecidos | 1.019 |
| Período indicado; vínculo com Goiás não estabelecido | 47 |
| Vínculo com Goiás indicado; período não confirmado | 31 |
| Período, vínculo com Goiás e pertinência indicados; conferir evidências | 8 |
| Período e vínculo com Goiás indicados; pertinência não estabelecida | 2 |

Esses grupos são uma **organização dos campos registrados**, não decisões automáticas. A falta de evidência de Goiás não prova ausência de contexto ou afiliação; a instituição associada à tese não foi convertida em afiliação de autoria. Entre as 1.107 linhas, 1.040 têm somente ano de defesa no campo temporal; esse ano não foi usado como publicação. Os oito registros com indicadores favoráveis continuam sujeitos aos limites já documentados da pesquisa original e das evidências preservadas. A qualidade documental reduzida aparece separadamente e não cria, por si, pendência ou necessidade de consulta.

As extrações dos 11 registros já incluídos permanecem inalteradas. A análise é não independente, não mede acurácia e não sustenta percentuais de confiança. A coleta nacional é incompleta e não deve ser apresentada como abrangendo toda a produção brasileira.

## Verificação

O [integrador](../../scripts/triagem_lote_consolidacao_20261115.py) confere as leituras prévias com as exportações BDTD e CAPES, verifica os dois resumos adicionais e os dados da UnB, e impede sobrescrita. Os três [testes](../../tests/test_triagem_lote_consolidacao_20261115.py) passaram; foram conferidos os dados fora do escopo, as abas anteriores, validações, tabela e filtro, fórmulas e integridade ZIP. O arquivo persistido foi aberto por biblioteca e seus totais e ZIP foram verificados; não houve teste interativo no Excel.

**Próxima prioridade:** examinar, com as evidências já preservadas e sem consultas individuais, os dez registros com período e vínculo goiano indicados; em seguida, preparar a planilha simplificada e o relatório metodológico, informando os casos que não puderem ser resolvidos.
