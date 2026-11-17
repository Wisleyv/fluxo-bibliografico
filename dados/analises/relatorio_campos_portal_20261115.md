# Conferência dos campos de oito candidatos do Portal CAPES

**Data:** 15 de novembro de 2026  
**Produto:** [base técnica atualizada](./triagem_portal_campos_20261115.xlsx).

## Procedimento

Foram examinados os oito candidatos que avançavam para avaliação e tinham menção ao PIBID no resumo complementar OpenAlex, mas não no título registrado no RIS. Para cada um, foram confrontados identificador, título, autoria, ano e DOI do RIS e da base com os dados anotados da página de detalhes atual do Portal CAPES. As páginas foram acessadas publicamente pelo navegador em 15/11/2026, sem executar nova busca sistemática nem acrescentar registros ao corpus.

Todos os oito RIS foram localizados, cada um uma vez; nenhum continha campo de resumo ou palavras-chave. As páginas atuais do Portal apresentam a sigla ou o nome do programa no campo **Sobre** dos oito registros. A evidência individual, os endereços e os limites estão na aba **Campos Portal CAPES** e no [registro das conferências](./conferencia_portal_campos_20261115.csv). Foram adicionados os links do Portal às oito linhas da base, sem reproduzir os resumos ou alterar decisões.

| Código | ID no Portal | Síntese da evidência no resumo atual |
|---|---|---|
| `7d7f7dda` | [W3037839654](https://www.periodicos.capes.gov.br/index.php/acervo/buscador.html?task=detalhes&source=digital&id=W3037839654) | Feira organizada por subprojetos PIBID de Química e Biologia da UFG Regional Catalão. |
| `8819ba66` | [W4377861554](https://www.periodicos.capes.gov.br/index.php/acervo/buscador.html?task=detalhes&source=digital&id=W4377861554) | Análise de registros de bolsistas de subprojeto de Pedagogia PIBID da UEG em Inhumas. |
| `678fd86d` | [W4376609888](https://www.periodicos.capes.gov.br/index.php/acervo/buscador.html?task=detalhes&source=digital&id=W4376609888) | Pesquisa sobre formação matemática de bolsistas de subprojeto PIBID da UEG. |
| `27027026` | [W4319783222](https://www.periodicos.capes.gov.br/index.php/acervo/buscador.html?task=detalhes&source=digital&id=W4319783222) | Sequência didática elaborada por bolsistas PIBID de universidade do sudeste goiano e aplicada em escola local. |
| `2fee827b` | [W4280604961](https://www.periodicos.capes.gov.br/index.php/acervo/buscador.html?task=detalhes&source=digital&id=W4280604961) | Mediação de supervisora na aprendizagem da docência de bolsistas PIBID. |
| `3f830636` | [W4385945204](https://www.periodicos.capes.gov.br/index.php/acervo/buscador.html?task=detalhes&source=digital&id=W4385945204) | Oficina remota organizada por bolsistas PIBID para evento do IF Goiano campus Urutaí. |
| `4a213f79` | [W3156162850](https://www.periodicos.capes.gov.br/index.php/acervo/buscador.html?task=detalhes&source=digital&id=W3156162850) | Uma de três experiências formativas envolve o PIBID Matemática Goiânia/UFG. |
| `05cbfe1e` | [W4376603037](https://www.periodicos.capes.gov.br/index.php/acervo/buscador.html?task=detalhes&source=digital&id=W4376603037) | Propostas de atividades de língua portuguesa vinculadas ao PIBID. |

Em `4a213f79`, o contexto é misto: as três experiências não devem ser atribuídas integralmente ao PIBID ou a Goiás. Em `05cbfe1e`, o resumo descreve a aplicação como idealmente planejada; não se presume aplicação efetiva ou efeito observado. A editora de um periódico não comprova afiliação da autoria, e atividade remota não identifica necessariamente o local dos participantes.

## Alcance e limitações

Os registros são os mesmos identificados nos RIS de 08/11/2026, mas a consulta das páginas de detalhes é **posterior ao corte**. Como o RIS não preservou os resumos, a página atual não demonstra que o texto era idêntico ou visível em 08/11/2026. A observação atual apoia a pertinência dos registros; a comparação histórica permanece limitada e não se deve apresentá-la como conferência retrospectiva dos resumos da coleta.

Os identificadores do Portal são os mesmos da consulta OpenAlex previamente arquivada; portanto, as apresentações não constituem validações independentes. As oito linhas continuam em **Avançar para avaliação**, com elegibilidade final e duplicidade pendentes. Não foram geradas extrações adicionais de eixos nem atribuídos percentuais de confiança.

Também foram consultadas as páginas dos periódicos de cinco registros; as três páginas da revista REVELLI retornaram acesso negado e o bloqueio não foi contornado. A leitura dos resumos no Portal não implica acesso ao texto integral nem sua avaliação.

## Verificação

O [integrador](../../scripts/conferir_campos_portal_20261115.py) compara as conferências registradas com o RIS e a base, recusa divergências e não sobrescreve a entrada. Passaram dois testes focados de identidade, estados e preservação; foram comparadas as demais células, as abas históricas, as validações e as fórmulas, além da integridade ZIP e da tabela de auditoria. As evidências das páginas foram registradas por leitura e não são uma captura histórica do Portal. Não houve teste interativo no Excel.

As contagens gerais e os eixos permanecem inalterados: 1.317 linhas, 19 que avançam, 197 excluídas preliminarmente e 1.101 pendentes na triagem; nenhuma decisão final de elegibilidade. A cobertura nacional segue incompleta e permanece necessária a análise das demais pendências, dos 40 resumos ingleses CAPES ainda não contemplados nas etapas bilíngues, a conciliação restante e a elaboração dos produtos finais.
