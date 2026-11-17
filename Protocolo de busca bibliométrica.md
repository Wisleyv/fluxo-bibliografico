# Protocolo de busca bibliométrica — versão 1.1

**Atualização de vigência nacional:** a interpretação de produção brasileira e as regras operacionais da rodada de fechamento estão em [v1.3 — fechamento nacional](./Protocolo%20de%20busca%20bibliom%C3%A9trica%20-%20v1.3%20fechamento%20nacional.md). A versão 1.1 abaixo permanece preservada como referência histórica dos pilotos e do critério regional de defesa.

**Status:** aprovado para orientar os pilotos da Etapa 2.  
**Data de referência desta versão:** 15 de novembro de 2026.

## 1. Objetivo

Recuperar e analisar a produção científica sobre o Programa Institucional de Bolsa de Iniciação à Docência (PIBID) publicada no Brasil no período de 2007 a 2026, com posterior identificação de um subconjunto relacionado a Goiás.

## 2. Período e data de corte

- **Período nacional de referência:** 1º de janeiro de 2007 a 8 de novembro de 2026, inclusive. Registrar os filtros efetivamente aplicados pelas fontes, sem converter data de defesa em data de publicação.
- **Cobertura de 2026:** parcial até a data de corte; resultados não representam necessariamente o ano completo.
- **Data de execução de cada busca:** registrar separadamente no log da coleta. Novas execuções podem recuperar registros adicionados ou atualizados depois da primeira busca.
- **Data do registro em repositório:** não usar como substituta do ano de publicação. Em especial, datas de depósito ou atualização OAI-PMH não equivalem necessariamente à data de publicação.
- **Recorte goiano — critério alternativo:** além de publicação no período, aceitar teses e dissertações com ano de defesa de 2020 a 2026, mantendo o tipo de data identificado. O ano de defesa não comprova ano de publicação. Para defesas de 2026 com apenas o ano disponível, a captura em 08/11 indica que o registro estava na exportação, mas não confirma a data individual completa; aceitar operacionalmente com evidência temporal limitada e informar essa ressalva. Os demais critérios de elegibilidade continuam necessários.

## 3. Fontes

Fontes previstas no protocolo:

1. Portal de Periódicos CAPES;
2. SciELO;
3. Catálogo de Teses e Dissertações da CAPES;
4. Biblioteca Digital Brasileira de Teses e Dissertações (BDTD);
5. Google Scholar, exclusivamente como busca complementar.

As interfaces do Portal de Periódicos CAPES e do Catálogo de Teses e Dissertações da CAPES serão tratadas como fontes distintas. A disponibilidade, a cobertura, a sintaxe, os campos e os formatos exportáveis serão confirmados em piloto antes da coleta definitiva. A inclusão de uma fonte no plano não presume que todo o seu conteúdo seja acessível ou exportável.

## 4. Consulta temática

### Consulta nacional de referência

```text
PIBID OR "Programa Institucional de Bolsa de Iniciação à Docência"
```

Aplicar a expressão nos campos de título, resumo e palavras-chave quando a fonte oferecer esses campos. Se a fonte não aceitar a expressão booleana ou não disponibilizar algum campo, adaptar a consulta aos recursos da interface, executar variantes equivalentes quando necessário e registrar a expressão exata utilizada por fonte.

### Consultas complementares de Goiás

Após a recuperação nacional, executar buscas complementares combinando a consulta temática com os descritores:

```text
(PIBID OR "Programa Institucional de Bolsa de Iniciação à Docência")
AND
("Goiás" OR "goiano" OR "goiana")
```

Executar também buscas complementares com nomes de instituições de ensino superior (IES) e contextos de pesquisa de Goiás quando identificados e validados, combinados com a consulta temática. As consultas regionais servem para localizar registros e não substituem a busca nacional. A classificação final do recorte goiano deverá distinguir estudos realizados no estado daqueles que apenas apresentam autores afiliados a instituições goianas.

### Adaptação por fonte

Não presumir que uma única sintaxe funcione em todas as fontes. Para cada execução, registrar:

- consulta literal submetida;
- campos pesquisados;
- filtros de período e tipo documental disponíveis;
- interface, endpoint ou protocolo utilizado;
- data/hora, formato exportado, total informado e limitações observadas.

Os parâmetros concretos de API, OAI-PMH ou interface web serão fixados após o piloto de viabilidade da Etapa 2 do plano de ação.

## 5. Critérios temáticos de inclusão e exclusão

- **Incluir na triagem:** registros recuperados pela consulta temática, em qualquer idioma e em qualquer tipo de produção acadêmica disponibilizado pelas fontes, com evidência temporal pertinente conforme a seção 2, que tratem do PIBID ou de experiência, política, formação, participantes ou resultados diretamente relacionados ao programa. A passagem por um filtro não substitui a triagem temática nem comprova uma data individual.
- **Tipos documentais:** incluir artigos, teses, dissertações, trabalhos em anais, livros, capítulos e outros tipos acadêmicos disponíveis nas fontes. Registrar o tipo informado pela fonte; não excluir automaticamente um formato por não constar nesta lista de exemplos.
- **Idiomas:** aceitar todos os idiomas disponíveis nas fontes. Preservar o idioma original informado, quando disponível.
- **Excluir após triagem:** registros comprovadamente fora do período pelos critérios aplicáveis; duplicatas (mantendo o vínculo com as fontes de origem); registros sem relação substantiva com o PIBID, em que a sigla ou expressão apareça apenas incidentalmente ou com outro significado; e materiais que não sejam produção acadêmica conforme classificados pela fonte.
- **Casos ambíguos:** manter como pendentes para revisão humana e registrar a justificativa da decisão.

## 6. Decisões metodológicas confirmadas

- **Tipos documentais:** todos os tipos de produção acadêmica disponíveis nas fontes, incluindo artigos científicos, teses, dissertações, trabalhos em anais, livros, capítulos e outros formatos acadêmicos.
- **Idiomas:** todos os idiomas disponíveis nas fontes.
- **Pendência operacional para a Etapa 2:** os campos pesquisáveis, filtros, sintaxes literais, cobertura e exportações serão confirmados por piloto para cada fonte. Não reduzir o escopo por limitações de uma interface sem registrar a limitação e avaliar alternativas.

## 7. Controle de versões

| Versão | Data | Status | Alterações |
|---|---|---|---|
| 0.1 | 08/11/2026 | Rascunho | Registra período/data de corte, fontes, consulta temática de referência, campos pretendidos e estratégia nacional seguida do recorte de Goiás; escopo documental e idiomas pendentes. |
| 1.0 | 08/11/2026 | Aprovado para os pilotos | Confirma inclusão de todos os tipos de produção acadêmica disponíveis e de todos os idiomas; explicita critérios de triagem e consulta complementar para Goiás. |
| 1.1 | 15/11/2026 | Critério temporal alternativo aprovado | Aceita ano de defesa de 2020–2026 para teses e dissertações no recorte goiano, sem equipará-lo à publicação; ressalva a evidência limitada de 2026 quando só o ano foi preservado. |
