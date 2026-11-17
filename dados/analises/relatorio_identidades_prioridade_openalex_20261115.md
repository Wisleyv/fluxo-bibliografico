# Conferência de identidades e prioridade goiana — OpenAlex

**Data:** 15/11/2026. **Situação:** conferência bibliográfica em lote e organização dos registros com sinais geográficos; seleção e revisão de escopo continuam incompletas.

## Identidade bibliográfica

Os 689 pares candidatos da [conciliação inicial](./relatorio_conciliacao_openalex_20261115.md) foram confrontados com os metadados OpenAlex e os campos da [base técnica anterior](./triagem_criterio_defesa_20261115.xlsx). A [planilha CSV de conferência](./openalex_identidades_conferidas_20261115.csv) registra a evidência de cada par:

| Classificação operacional | Pares |
|---|---:|
| Mesma obra: DOI e metadados concordantes | 116 |
| Identificador concordante; metadados requerem revisão | 52 |
| Título somente; identidade não estabelecida | 521 |
| **Total** | **689** |

Para classificar operacionalmente como mesma obra, foram exigidos DOI normalizado igual, título normalizado igual, ano de publicação igual, tipo artigo em ambas as fontes e concordância dos nomes de cada autor após normalização de caixa, acentos e pontuação, inclusive reordenação de palavras dentro do nome. Não foram aceitos dados ausentes como concordância. Foram obtidos 116 identificadores OpenAlex e 116 códigos da base nessa condição: 71 pares com Portal CAPES e 45 com SciELO. Doze correspondem a linhas anteriormente incluídas no recorte goiano; o registro OpenAlex correspondente **não deve ser contado como nova obra** apenas por pertencer a outra fonte.

Essa classificação preserva as duas linhas e sua proveniência; não confirma pertinência temática, elegibilidade ou ausência de outras duplicatas e não é validação independente. A comparação por nomes pode deixar variantes como abreviações entre os 52 casos de revisão: uma divergência dos metadados não comprova obras distintas. Oito pares com identificador concordante apresentam títulos divergentes ou não comparáveis, inclusive traduções ou títulos mais curtos; um deles também difere no ano. Os 521 pares por título apenas continuam candidatos, inclusive possíveis artigos derivados de teses e dissertações.

## Prioridade para Goiás

O [inventário de 333 registros sinalizados](./openalex_prioridade_goias_20261115.csv) reúne título, autoria, resumo disponível, instituições, tipo, data e ligações candidatas com a base, ordenados por data de publicação informada pelo OpenAlex. É uma fila para exame, não uma lista de estudos elegíveis.

| Data de publicação OpenAlex | Registros com sinal |
|---|---:|
| 2020–2025 | 84 |
| 2026 | 16 |
| 2007–2019 | 233 |

Dos 333, 72 têm alguma correspondência candidata na base anterior, incluindo 37 com pelo menos uma correspondência operacionalmente sustentada como mesma obra. Os conjuntos se sobrepõem. A data de publicação do OpenAlex é distinta da defesa; não se excluíram automaticamente os 233 registros anteriores de outras análises nem se inferiu seu ano de defesa. Em 2026, a data OpenAlex dentro do corte não comprova que o registro estava indexado em 08/11.

Os sinais identificam termos Goiás/goiano/goiana em título, resumo, palavras-chave ou nomes institucionais disponíveis. Não demonstram automaticamente contexto ou afiliação, não abrangem todos os possíveis vínculos goianos e não excluem os demais registros. Uma instituição na autoria não estabelece o lugar da pesquisa. Não se criou pendência nem busca individual apenas por resumo não preservado.

## Conferência dos oito registros priorizados por defesa

Foram relidos os resumos já preservados dos três pares confirmados e dos dois registros individuais:

- `ca80f876` / `b577aa7f`: tese com defesa em 2023 analisa o PIBID na UEG. O material apoia pertinência temática e contexto goiano; a afiliação da autoria em Goiás não foi presumida.
- `2e073f75` / `5dbf2cee`: dissertação com defesa em 2021 estuda o PIBID nas licenciaturas do IF Goiano campus Morrinhos. O material apoia pertinência e contexto goiano.
- `d9c78129` / `3c89a0bd`: dissertação com defesa em 2022 examina a execução de projeto PIBID de História em escola de Goiânia. O material apoia pertinência e contexto goiano; os resultados descritos sobre estudantes escolares não demonstram aprendizagem docente.
- `ca6145ae` e `938c2a7b`: dissertações com defesa em 2024 e participantes vinculados ao PIBID em contexto do IFG. Os resumos não esclarecem suficientemente se as intervenções analisadas integram ações do programa; a pertinência substantiva permanece incerta, não por ausência de resumo.

Os três pares têm suporte preliminar para os critérios de tema, contexto e período alternativo, **mas ainda não foram incluídos na base nem contados**: falta escolher tratamento único de cada par e incorporar as extrações consistentes aos produtos. Os dois casos individuais não foram excluídos. Não houve consulta externa ou alteração de ano de publicação.

## Verificação e continuidade

Os [scripts de identidade](../../scripts/conferir_identidades_openalex_20261115.py) e [priorização](../../scripts/priorizar_openalex_goias_20261115.py) recusam sobrescrita; suas auditorias estruturadas estão em [identidades](./openalex_identidades_auditoria_20261115.json) e [prioridade](./openalex_prioridade_goias_auditoria_20261115.json). Foram reabertos os CSVs e verificadas as 689 chaves de pares e os 333 identificadores, os requisitos das 116 correspondências e a integridade da base anterior. Passaram sete testes focados relacionados ao fluxo OpenAlex. As verificações não medem acurácia científica.

A próxima ação é incorporar de forma auditável um registro por par confirmado elegível e tratar, em lotes, os 100 sinalizados com publicação OpenAlex em 2020–2026, preservando casos sem sinal e critérios de defesa. Depois, reconciliar seleção e duplicidade antes de atualizar gráficos e relatório. As 19 inclusões anteriores, as 1.099 linhas sem decisão na base anterior e os produtos preliminares não foram modificados.
