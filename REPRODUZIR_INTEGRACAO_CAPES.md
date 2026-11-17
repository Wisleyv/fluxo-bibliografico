# Reconstrução da entrega após integração CAPES

Esta é a instrução da versão incremental. `REPRODUZIR_MARCO5.md` documenta a versão anterior, que permanece preservada. Não executar coletores nem usar os comandos antigos sem manifesto para reconstruir a versão CAPES.

Pré-requisitos utilizados: Python 3.10.11, openpyxl 3.1.5 (`requirements-marco5.txt`), Windows e Microsoft Excel por COM. Os executáveis não são distribuídos. O fluxo openpyxl/Excel foi autorizado pelo usuário como alternativa ao runtime indisponível da skill. Não há dependência de rede, Pillow ou PyMuPDF para reconstruir a entrega.

Extrair o pacote em uma pasta nova preservando os caminhos. A raiz deve conter `scripts/`, `dados/`, `Vaneria.txt` e este documento. O inventário está em `dados/entregas/marco5_capes_20261116/Inventario.csv`: cada membro tem caminho, tamanho e SHA-256. O próprio inventário não contém seu próprio hash. O checksum do ZIP é disponibilizado externamente em `Verificacao do pacote.json`; a conferência dos membros pelo inventário independe desse arquivo externo.

## Executar na raiz extraída

```powershell
python -m scripts.recalcular_cobertura_capes_20261116 --recalcular --atualizar
python -m scripts.entregar_marco5 preparar --manifesto "dados/analises/integracao_capes_20261116/elegibilidade/Manifesto de execucao.json"
powershell -NoProfile -File scripts/conferir_excel_marco5.ps1 -Manifesto "dados/analises/integracao_capes_20261116/elegibilidade/Manifesto de execucao.json"
python -m scripts.entregar_marco5 verificar --manifesto "dados/analises/integracao_capes_20261116/elegibilidade/Manifesto de execucao.json"
```

O manifesto seleciona os corpora nacional/regional da etapa de elegibilidade, os indicadores incrementais e a saída `dados/entregas/marco5_capes_20261116/`. Os valores padrão históricos dos scripts foram mantidos; por isso o manifesto é obrigatório nos comandos de entrega desta versão. Os produtos podem ser sobrescritos na reconstrução, na cópia extraída; os insumos e decisões anteriores não são editados.

Testes relevantes:

```powershell
python -m unittest discover -s tests -p "test_*marco*.py"
python -m unittest discover -s tests -p test_indicadores_capes_20261116.py
python -m unittest discover -s tests -p test_delta_capes_20261116.py
python -m unittest discover -s tests -p test_entrega_capes_20261116.py
```

Para repetir o teste de extração e reconstrução, quando o ZIP estiver presente no diretório da entrega:

```powershell
python -m scripts.testar_reconstrucao_marco5 --manifesto "dados/analises/integracao_capes_20261116/elegibilidade/Manifesto de execucao.json"
```

Esse teste confere hashes, reexecuta os cálculos, gera/recalcula os dois XLSX e compara as tabelas e os valores de todas as abas. Metadados de arquivo, logs e inventários de execução podem diferir; não se promete identidade binária dos XLSX ou dos ZIPs. Os documentos Markdown são redações versionadas; a síntese tem geração incremental a partir da redação anterior. A revisão visual das exportações é conferência interna separada e não é substituída pela existência do PNG/PDF.

## O que está congelado

Os corpora de entrada ficam em `dados/analises/integracao_capes_20261116/elegibilidade/`: 7.779 nacionais, 97 goianas, 291 extrações, 14.423 registros de proveniência e dez ocorrências CAPES em componentes provisórios. As regras são as da v1.3 e do adendo v1.4. Coleta CAPES: 16/11/2026; OpenAlex: 15/11/2026; corte de publicação: 08/11/2026.

As frações atuais são 196/7.779 (2,52%), em 2007–08/11/2026, e 67/3.459 (1,94%), em 2020–08/11/2026. São afiliações goianas identificadas no mesmo corpus/período de cada cálculo; participação total não estimável. Contexto é separado de afiliação. A linha de base anterior 196/7.780 não deve substituir o denominador atualizado.

As 675 recuperações CAPES não são 675 novas obras: 647 IDs coincidem nominalmente com o snapshot, 665 ocorrências têm vínculos conciliados e 509 obras elegíveis foram recuperadas no novo lote. A união das rodadas CAPES alcança 571 obras elegíveis. A medição por registros separa 664 confirmados com o snapshot, três revisões, sete não recuperados e um temporalmente não verificável, com denominador verificável 671. Consultas/datas/filtros distintos impedem alegação de completude ou independência dos índices.

Persistem 871 pendências regionais anteriores, quatro inclusões por defesa, a dúvida artigo/capítulo e afiliações incompletas. As dez ocorrências provisórias adicionais não são obras confirmadas e não se somam automaticamente às pendências regionais. Reexecutar scripts reproduz decisões arquivadas; não constitui nova leitura ou validação científica independente.

O pacote inclui o RIS novo e sua cópia arquivada, protocolos, consultas nos manifestos/envelopes, brutos e geração normalizada vigente, corpora, decisões, scripts, testes, logs, tabelas e produtos finais. Executáveis, staging e normalizações antigas redundantes não são necessários à reconstrução desde os corpora congelados e não são distribuídos. A entrega anterior permanece no workspace original; seu ZIP não é duplicado dentro do novo pacote.
