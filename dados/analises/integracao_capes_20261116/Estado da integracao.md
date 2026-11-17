# Estado vigente da integração incremental

## Etapa 6 — entrega incremental concluída operacionalmente

A entrega paralela está em [marco5_capes_20261116](../../entregas/marco5_capes_20261116/), com planilha editável, base técnica, matriz, relatório metodológico substituto, síntese e pacote reproduzível. A versão anterior permanece preservada. Consulte o relatório, as conferências internas, a revisão visual dos seis gráficos e o teste de reconstrução na nova entrega. O fechamento operacional não elimina as limitações científicas: afiliações incompletas, participação total não estimável, 871 pendências regionais, quatro inclusões por defesa, dúvida artigo/capítulo e dez ocorrências CAPES provisórias.

## Histórico — etapa 5

O recálculo da cobertura e dos indicadores e a atualização da síntese das seis subquestões foram concluídos. Os produtos estão em `indicadores/`: [relatório](indicadores/Relatorio%20dos%20indicadores%20e%20sobreposicao%20CAPES.md), [síntese](indicadores/Sintese%20das%20seis%20subquestoes.md) e [manifesto de saída](indicadores/Manifesto%20de%20saida.json).

As frações observadas são 196/7.779 (2,52%) para 2007–08/11/2026 e 67/3.459 (1,94%) para o período comum 2020–08/11/2026; participação total não estimável. A recuperação Portal CAPES alcança 571 obras elegíveis na união de rodadas, das quais 509 foram recuperadas no novo lote. A matriz diferencia 647 IDs coincidentes, 665 vínculos bibliográficos e 664 correspondências confirmadas com o snapshot entre 671 registros verificáveis.

Os 97 incluídos regionais e os estados das 291 extrações permanecem iguais. A próxima etapa é regerar a entrega paralela e seu relatório metodológico, sem substituir os arquivos históricos.

## Histórico — etapa 4

O delta de elegibilidade e metadados foi concluído até o limite da evidência local. Os insumos vigentes para o próximo cálculo estão em `elegibilidade/`, conforme o [relatório do delta](elegibilidade/Relatorio%20do%20delta%20de%20elegibilidade.md) e o [manifesto](elegibilidade/Manifesto%20de%20execucao.json).

Foram preservadas 7.779 inclusões nacionais e 97 regionais. Não houve promoção, inclusão ou exclusão nacional nova nesta etapa. Todas as 675 ocorrências CAPES estão inventariadas: 665 vinculadas a identidades conciliadas e dez em componentes provisórios, que não contam como obras confirmadas. A proveniência nacional totaliza 14.423 registros; a regional, 2.118, com 291 extrações e 871 pendências regionais anteriores preservadas. O recálculo dos indicadores e a nova entrega continuam sendo a próxima etapa.

## Histórico — fase bibliográfica

A fase bibliográfica dos 49 registros foi executada; os produtos atuais desta fase estão em `conciliacao/`. Os arquivos na pasta superior preservam a primeira fase (626 vínculos e 49 pendências), não os totais mais recentes.

Resultado atual: **665 registros CAPES vinculados e dez residuais**, totalizando as 675 ocorrências. A proveniência vinculada tem **14.413 registros**, e não 14.423: dez ocorrências CAPES ainda não têm destino de obra confirmado e permanecem na fila, sem desaparecer do inventário.

Foram resolvidos 39 dos 49 casos. As decisões, justificativas e referências por registro estão em [Revisao dos 49 registros.csv](conciliacao/Revisao%20dos%2049%20registros.csv). As dez pendências são três divergências de autoria (0161, 0249, 0651) e sete sem identidade sustentada (0421, 0623, 0635, 0644, 0672, 0674, 0675). Não foram tratadas como exclusões ou como obras novas elegíveis.

## Efeito material

“Quero ser professora” foi conciliada como uma obra: os dois DOIs aparecem nas localizações do mesmo registro OpenAlex, junto ao PID SciELO S2176-66812016000100031. Título, três autoras, ano 2016 e dados bibliográficos concordam. A ponte conserva o identificador anterior e aponta a `M2-a279c6aac5c92b01`. A fusão reduz o corpus nacional operacional incremental de 7.780 para **7.779 obras**, sem eliminar registros de origem. Não houve inclusão temática nova nesta fase.

“Práticas de leitura” conserva 2013 como publicação sustentada pela conferência anterior e pelo material arquivado. O ano 2019 do novo RIS permanece na proveniência, explicitamente discordante, sem criar outra obra nem substituir silenciosamente a série. A recuperação com DOI SciELO alternativo foi vinculada à identidade anteriormente sustentada. O registro Cury foi vinculado após conferir o DOI correto anexado ao título, mantendo o campo original com prefixo repetido.

As diferenças de DOI vinculadas pela identidade da obra continuam como divergências de metadado: a ligação não declara automaticamente válido um novo DOI. Listas concatenadas de autoria não substituíram os créditos de pessoas ou suas afiliações.

## Conferência e próximos passos

A execução confirma 49 decisões, 39 vínculos adicionais, dez residuais, 665 registros CAPES vinculados, unicidade de 14.413 identificadores de proveniência, reconciliação de registros por componente, 7.779 inclusões e preservação por hash dos quatro insumos da primeira fase. A fusão possui verificações executáveis de título, autoria, ano, ambos os DOIs, PID e volume/página. Ver [Verificacoes.json](conciliacao/Verificacoes.json).

Esta fase não atualizou indicadores, revisão goiana ou entrega Excel. A próxima etapa é avaliar somente o delta de elegibilidade e metadados, remapear a ponte regional quando aplicável e regerar indicadores e produtos com os caminhos desta versão. As frações 196/7.780 e 67/3.459 são resultados da versão anterior: não devem ser copiadas como indicadores recalculados da integração. A fusão é de uma obra publicada antes de 2020; seu efeito direto é nacional, não uma nova inclusão goiana.

A nota metodológica da pasta superior deve ser lida com este adendo. O relatório substituto deverá registrar separadamente a sobreposição nominal de 647 IDs entre 675 recuperações, os 665 vínculos bibliográficos atuais e a sobreposição de obras elegíveis, que ainda requer recálculo. Esses números têm unidades e denominadores diferentes. Permanecem as ressalvas sobre consulta CAPES filtrada, paginação declarada, datas de coleta, afiliações incompletas, pendências regionais e revisão interna sem validação independente.
