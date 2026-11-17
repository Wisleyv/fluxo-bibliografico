# Conferência computacional por regras — amostra de 60 registros

**Data:** 15 de novembro de 2026  
**Produto:** [planilha de conferência](./conferencia_por_regras_60_20261115.xlsx).

## Finalidade e procedimento

Após a escolha de uma segunda verificação computacional, foram aplicadas regras reproduzíveis aos metadados e ao texto disponível nas colunas A–O da [amostra cega](./validacao_independente_60_20261115.xlsx). Em seguida, os sinais obtidos foram comparados com a [autoavaliação](./amostra_60_autoavaliacao_20261115.xlsx) e com a [base integrada](./triagem_integrada_autoavaliacao_20261115.xlsx). Para localizar candidatos a duplicidade, os DOI e títulos foram comparados também com os 1.317 registros da base. Não houve nova consulta externa.

A conferência **não constitui avaliação independente nem simula uma referência independente confiável**: usa regras e materiais relacionados ao mesmo processo de análise. Ela verifica alguns aspectos formais e identifica situações para exame; não mede a verdade das classificações, a validade dos eixos ou a acurácia. Portanto, não fundamenta os índices de 100%, >85% ou >75%.

Foram verificadas as seguintes situações:

1. Diferença entre a situação temporal obtida dos dados cegos e a registrada na autoavaliação, sem substituir ano de defesa por ano de publicação.
2. Sinais literais de PIBID e de Goiás/goiano no título e no campo de resumo. Esses sinais não estabelecem objeto, contexto geográfico ou ausência de relação.
3. Campos de resumo vazios ou iniciados por padrões que podem indicar apenas referência bibliográfica ou orientação. A regra não certifica que outros textos sejam resumos substantivos.
4. Correspondências de DOI normalizado e título normalizado exato no conjunto da base; são candidatas, não deduplicação automática.
5. Coerência lógica entre as respostas declaradas para triagem, período, natureza, relação com PIBID e contexto ou afiliação; a coerência não confirma que as respostas sejam corretas.
6. Diferenças nos seis campos correspondentes entre a autoavaliação e a base integrada. A inconsistência título–resumo de **46baf45a**, já documentada anteriormente, foi explicitamente incluída como alerta conhecido, não como descoberta semântica da regra.

## Resultados dos controles

Foram conferidas **60 linhas**. As regras geraram **27 alertas em 20 linhas**; um mesmo registro pode gerar vários alertas. Alertas não equivalem a erros, e a ausência deles nos demais registros não comprova correção.

| Regra ou situação registrada | Alertas |
|---|---:|
| Período diferente entre dados cegos e autoavaliação | 3 |
| Campo de resumo possivelmente bibliográfico ou de orientação | 3 |
| Título normalizado repetido na base | 16 |
| Diferença entre autoavaliação e base integrada | 1 |
| Contexto goiano declarado sem sinal literal no título ou resumo local | 1 |
| DOI repetido na base | 2 |
| Inconsistência título–resumo anteriormente documentada | 1 |

As 16 linhas com título repetido não representam necessariamente 16 obras ou 16 duplicatas distintas: incluem as duas linhas do par com DOI repetido e um grupo com três registros. Os outros códigos candidatos constam na planilha, para comparação bibliográfica.

As respostas dos três registros marcados para avanço são logicamente compatíveis com os requisitos declarados; as 14 exclusões declaradas têm período fora do recorte; e os 43 restantes estão pendentes. Isso **não confirma** a veracidade dos critérios nem a elegibilidade científica.

## Interpretação dos alertas principais

- **06792f41:** o ano de publicação 2024 foi obtido posteriormente no repositório, por isso não consta na amostra cega original. O campo local de resumo é uma referência, e existe candidato de mesmo título **1235abfa**; a correspondência necessita de conferência como par.
- **c3920958:** a divergência temporal permaneceu incerta na autoavaliação. O candidato de mesmo título **a7f3b245** apresenta ano de defesa 2019, enquanto c3920958 registra 2020; a consulta anterior à UnB indicou defesa em 2019. A relação entre os registros e a divergência devem ser tratadas em conjunto, sem alteração automática.
- **5dbf2cee:** a data de emissão localizada no repositório não foi equiparada automaticamente a publicação; o período ficou incerto. O par **2e073f75** continua candidato a duplicata.
- **796dae04:** a diferença de contexto entre autoavaliação e base integrada já havia sido preservada deliberadamente; o avanço na base também se apoia na afiliação goiana.
- **83224e28/387c5254:** os dois alertas de DOI se referem ao mesmo par, previamente conferido por DOI, título, autoria e ano. O resumo SciELO sustenta o contexto identificado para 83224e28 apesar da ausência de sinal literal em seu título ou resumo local.
- **f116ff8b:** há dois registros de mesmo título e autoria na BDTD, com endereços de repositório diferentes; é necessário verificar se representam a mesma obra ou versões distintas antes de deduplicar.
- **46baf45a:** permanece a incompatibilidade já identificada entre título e resumo. A conferência por regras não resolve nem detecta, por si só, a divergência de conteúdo.

## Etapa seguinte: quatro pares conferidos

Os metadados dos candidatos foram comparados. Quatro pares têm, em cada par, o mesmo endereço de repositório, título, autoria, tipo de produção, ano de defesa e instituição associada: **dca33e23/740184cf**, **3ee25c3e/5f5259e7**, **f1d6e487/361dd6b1** e **5dbf2cee/2e073f75**. Essa combinação sustenta tratá-los como quatro pares de registros da mesma obra, sem depender apenas de título coincidente.

Os oito registros foram marcados como `Duplicata confirmada` em uma [nova cópia da base](./triagem_duplicatas_conferidas_20261115.xlsx); a aba **Duplicatas conferidas** registra identificadores, evidências e estados anteriores. Nenhum registro principal foi escolhido, nenhum registro foi removido e nenhuma elegibilidade foi alterada. O par **83224e28/387c5254** já estava confirmado anteriormente: a base agora identifica dez linhas em cinco pares confirmados, não dez obras distintas. Outras correspondências continuam candidatas.

## Verificação técnica e limites

O [script de conferência](../../scripts/conferir_amostra_por_regras_20261115.py) gera a planilha sem sobrescrever arquivos existentes e preserva as três entradas. O [script dos pares](../../scripts/confirmar_duplicatas_amostra_20261115.py) exige a coincidência dos metadados indicados antes de alterar a cópia. Foram conferidos os 60 códigos únicos, preenchimento dos campos gerados, totais, tabelas, integridade ZIP e ausência de fórmulas inesperadas. A comparação com a versão anterior confirmou que somente os campos de duplicidade e observações das oito linhas foram alterados; as abas históricas foram preservadas. Os 17 testes focados de duplicidade, conferência, integração, preenchimento e pré-análise passaram. A abertura interativa no Excel não foi testada.

**Próxima etapa:** examinar e resolver, quando os dados permitirem, os candidatos de duplicidade e as demais pendências; continuar a análise dos registros não avaliados semanticamente. As decisões devem continuar identificadas como preliminares e sem confiança percentual validada.
