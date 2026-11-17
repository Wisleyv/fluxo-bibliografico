# Reconstrução da entrega PIBID — Marco 5

Os corpora congelados são insumos de reconstrução, não o resultado de uma nova busca. Não executar coletores. Publicação até 08/11/2026; coleta OpenAlex em 15/11/2026.

Pré-requisitos utilizados: Python 3.10.11, openpyxl 3.1.5, Windows e Microsoft Excel por COM. As dependências Python estão em `requirements-marco5.txt`; o Excel não é distribuído no pacote. O uso de openpyxl/Excel como alternativa à skill foi autorizado explicitamente pelo usuário nesta sessão. Não se requer Pillow, PyMuPDF, serviço externo ou nova coleta.

Extrair o ZIP em um diretório novo, preservando os caminhos. A raiz extraída deve conter este arquivo, `Vaneria.txt`, `scripts` e `dados`. Antes de reconstruir, conferir `dados/entregas/marco5/Inventario.csv`: cada linha informa caminho relativo, tamanho e SHA-256. O próprio inventário não contém seu próprio hash. O hash do ZIP está no arquivo externo `Verificacao do pacote.json`.

## Reconstrução dos produtos finais e dos indicadores

Na raiz extraída:

```powershell
python -m scripts.produzir_indicadores_marco4 --atualizar
python -m scripts.documentar_conferencias_marco4 --atualizar
python -m scripts.verificar_marco4 --atualizar
python -m scripts.entregar_marco5 preparar
powershell -NoProfile -File scripts/conferir_excel_marco5.ps1
python -m scripts.entregar_marco5 verificar
python -m unittest discover -s tests -p "test_*marco*.py"
```

`preparar` substitui somente os produtos finais gerados do Marco 5. Os comandos de indicadores com `--atualizar` substituem somente seus próprios resultados, sem alterar os corpora, os registros arquivados ou decisões anteriores. Não usar o diretório original como ambiente de experimentação: preferir uma cópia extraída.

Os gráficos são objetos nativos vinculados às células da planilha; exportações PNG/PDF são somente provas de conferência. O Excel recalcula, salva os valores das fórmulas e exporta os seis gráficos. A inspeção visual humana/interna das exportações acompanha o registro da entrega; não é substituída pela existência do arquivo de imagem. Documentos Markdown são interpretações versionadas, não redação regenerada automaticamente.

Para reconstruir a revisão regional a partir das decisões arquivadas, opcionalmente executar antes dos indicadores:

```powershell
python -m scripts.executar_marco3 --atualizar
python -m scripts.fechar_marco3 --atualizar
python -m scripts.verificar_marco3 --atualizar
```

As leituras individuais e decisões estão codificadas/registradas nos scripts e tabelas. Reexecutá-las reproduz o resultado documentado; não constitui uma nova validação independente. A reconstrução do Marco 2 a partir dos insumos iniciais não faz parte do teste final: o pacote preserva os corpora e etapas históricas, além dos scripts e da geração normalizada vigente para auditoria. Não se deve sobrescrever a história dos marcos 1–2 para simular novas decisões.

## Alcance dos resultados

196/7.780 (2,52%) é a fração observada de obras com afiliação goiana identificada no corpus nacional de publicação 2007–08/11/2026. 67/3.459 (1,94%) usa somente obras nacionais por publicação em 2020–08/11/2026. São numeradores e denominadores compatíveis em cada recorte, não participação total da produção goiana. Esta permanece não estimável. Contexto goiano é contado separadamente de afiliação.

As 97 inclusões regionais e 291 estados de extração descrevem o corpus observado; permanecem 871 componentes pendentes, quatro inclusões por defesa e dúvida artigo/capítulo que pode acrescentar uma ou duas obras à revisão. Ambos os registros desse par continuam no corpus nacional congelado, cujo total pode diminuir em uma unidade se forem a mesma obra. Afiliações incompletas e anos divergentes continuam explícitos. Ver `dados/analises/marco4/Estado dos indicadores.csv`.

O pacote não inclui cópias intermediárias redundantes de `staging`, gerações normalizadas antigas ou executáveis do ambiente. Inclui os brutos citados, a geração normalizada vigente, corpora, decisões, páginas OpenAlex com consulta, protocolos, scripts, testes, logs e produtos. A reprodução demonstrada é a partir dos corpora congelados, sem rede, com os pré-requisitos acima.
