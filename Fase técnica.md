A implementação técnica ideal para o cenário de bases brasileiras (SciELO, BDTD, Portal de Periódicos CAPES) exige uma arquitetura híbrida, combinando scripts de limpeza de dados estruturados com pacotes bibliométricos dedicados. Bases nacionais raramente exportam metadados no padrão rígido (Scopus/WoS) que softwares cientométricos exigem nativamente, tornando o pré-processamento a etapa mais crítica do projeto.

  

### 1. Gestão e Desduplicação do Corpus (Zotero 7)

Para a centralização e triagem dos registros brutos, o **Zotero 7**, operando em conjunto com a extensão **Better BibTeX**, fornece a base para a padronização das chaves de citação e exportação limpa.

  

- **Exportação:** Utilize o Better BibTeX para gerar arquivos `.bib` ou `.csv` consolidados após a leitura de títulos e resumos.
    
      
    
- **Desduplicação:** O cruzamento entre SciELO, BDTD e Google Scholar gerará alta sobreposição. Realize a mesclagem utilizando exclusivamente a ferramenta nativa de desduplicação do Zotero 7; evite recorrer a plugins de limpeza em massa antigos (de 2022 ou anteriores), pois encontram-se abandonados e são incompatíveis com a arquitetura atual do Zotero 7.
    
      
    

### 2. Tratamento e Limpeza de Metadados (Python via WSL)

Antes de carregar os dados no R, os metadados precisarão ser higienizados (por exemplo, aglutinar diferentes grafias para a mesma universidade em Goiás ou separar palavras-chave agrupadas incorretamente). A abordagem mais estável para esse volume de dados é estruturar o tratamento via script.

  

- **Ambiente:** Configure um ambiente virtual (`venv`) utilizando **Python** no **WSL (Ubuntu)** para isolar as dependências e manipular os arquivos de forma ágil.
    
      
    
- **Processamento Tabular:** Utilize a biblioteca `pandas` para ler os dados exportados do Zotero, preencher campos vazios, normalizar os nomes das IES goianas e reestruturar colunas essenciais (Autor, Ano, Instituição, Resumo, Palavras-chave) para um formato `.csv` padronizado.
    
      
    
- **Análise Quantitativa Direta:** O próprio Python (combinado a bibliotecas como `matplotlib` ou `seaborn`) pode ser utilizado nesta etapa para gerar os gráficos de evolução temporal (2007-2026) e a quantificação de publicações por tipo de produção e por instituição, resolvendo grande parte das subquestões descritivas do seu projeto.
    
      
    

### 3. Análise Bibliométrica de Redes (R Studio + Bibliometrix)

Com o arquivo `.csv` devidamente limpo e padronizado pelo Python, o ecossistema R é a escolha mais robusta para a extração de indicadores cientométricos e o mapeamento das conexões.

  

- **Bibliometrix / Biblioshiny:** A interface web `biblioshiny`, instanciada a partir do pacote `bibliometrix` no R, permite gerar mapas de colaboração interinstitucional e redes de coocorrência de temáticas.
    
      
    
- **Mapeamento de Colunas:** Como o `bibliometrix` espera dados estruturados em padrões internacionais, será necessário utilizar a função `convert2df()` ou adaptar o cabeçalho do seu `.csv` para as tags padrão do pacote (ex: `AU` para autores, `DE` para palavras-chave dos autores, `PY` para ano de publicação, `AB` para resumo).
    
      
    

### 4. Visualização Avançada (VOSviewer)

Se o `bibliometrix` apresentar limitações estéticas ou de clusterização para as redes específicas das IES goianas e das temáticas de formação, o **VOSviewer** opera como um excelente complemento independente.

  

- **Aplicação Prática:** Ele lê diretamente arquivos de dados bibliográficos e possui algoritmos otimizados para identificar subgrupos temáticos por meio da mineração de texto nos resumos. É a ferramenta ideal para gerar os grafos que evidenciarão como os eixos de "aprendizagem da docência", "identidade profissional" e "espaços híbridos" estão conectados na literatura do PIBID.
    
      
    

**Fluxo de Trabalho Sugerido:**

  

1. Exportação bruta das bases brasileiras $\rightarrow$ Importação centralizada no Zotero 7.
    
      
    
2. Limpeza nativa de duplicatas no Zotero $\rightarrow$ Exportação via Better BibTeX (`.csv`).
    
      
    
3. Higienização de metadados e correção de grafias institucionais em Python (via `venv`/WSL) usando `pandas` $\rightarrow$ Exportação do DataFrame consolidado.
    
      
    
4. Importação no R Studio (`bibliometrix`) para geração das matrizes de colaboração.
    
      
    
5. Exportação das redes para renderização visual final e análise de clusters no VOSviewer.