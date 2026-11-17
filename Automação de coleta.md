Para automatizar a coleta, é preciso lidar com o fato de que cada base possui uma arquitetura diferente. Algumas oferecem interfaces abertas para robôs (APIs), enquanto outras bloqueiam raspagem de dados ativamente e exigem simulação de navegação humana.

Aqui estão as ferramentas e bibliotecas recomendadas para o seu ambiente de desenvolvimento, seguidas do passo a passo de implementação.

### Ferramentas e Bibliotecas Disponíveis

- **SciELO:** Possui uma API REST pública e oficial (ArticleMeta API). A coleta é feita de forma limpa via requisições HTTP padrão.
    
      
    
- **BDTD (Teses e Dissertações):** Opera sob o protocolo internacional OAI-PMH (Open Archives Initiative Protocol for Metadata Harvesting). A ferramenta ideal é a biblioteca Python `Sickle`, construída especificamente para extrair metadados XML de repositórios acadêmicos.
    
      
    
- **Portal de Periódicos CAPES:** Não possui uma API pública estruturada e depende de renderização dinâmica (e frequentemente de autenticação institucional via CAFe). A abordagem mais eficaz é o **Playwright**, um framework de automação de navegador que interage com a página como um usuário real, preenche formulários e intercepta os downloads dos arquivos `.ris`.
    
      
    
- **Google Scholar:** Tem políticas rigorosas contra bots e bloqueia requisições rapidamente com CAPTCHAs. A biblioteca Python `scholarly` consegue contornar bloqueios leves, mas para um volume de 20 anos de publicações, geralmente é necessário integrá-la a proxies ou utilizar uma API de terceiros especializada (como a SerpApi).
    
      
    

### Passo a Passo da Implementação Técnica

**1. Preparação do Ambiente de Raspagem** Abra o VS Code, inicie seu terminal no WSL (Ubuntu) e ative seu ambiente virtual Python (`venv`). Instale o pacote de ferramentas necessárias para cobrir todas as bases:

  

Bash

```
pip install requests pandas sickle playwright scholarly
playwright install chromium
```

**2. Coleta na BDTD via OAI-PMH** Crie um script em Python utilizando a biblioteca `Sickle`. Você fará uma requisição direta ao endpoint da BDTD, passando os descritores do PIBID e o recorte de data.

  

- **Ação:** Configure a requisição para puxar os metadados no formato `oai_dc`.
    
      
    
- **Vantagem:** O protocolo OAI-PMH permite paginação nativa, iterando por todos os resultados de 2007 a 2026 sem sofrer bloqueio de IP. Os dados retornam estruturados em dicionários Python, facilitando a extração de Título, Resumo, Autor e Instituição para um arquivo CSV.
    
      
    

**3. Coleta na SciELO via ArticleMeta API** Construa um módulo no script utilizando a biblioteca `requests`.

  

- **Ação:** Faça requisições GET para o endpoint de busca da SciELO (`[http://articlemeta.scielo.org/api/v1/article/](http://articlemeta.scielo.org/api/v1/article/)`).
    
      
    
- **Filtros:** A API permite passar parâmetros de busca diretamente na URL. Você extrairá o JSON de resposta, navegando nas chaves do dicionário para isolar os metadados bibliográficos e salvá-los no mesmo padrão tabular usado para a BDTD.
    
      
    

**4. Coleta no Google Scholar via Scholarly** Implemente um laço de repetição utilizando a biblioteca `scholarly` para buscar a string exata do seu projeto: `PIBID OR "Programa Institucional de Bolsa de Iniciação à Docência" Goiás`.

  

- **Ação:** Use `scholarly.search_pubs()`. Como a ferramenta emula as requisições, insira comandos de `time.sleep()` entre 5 e 15 segundos (com tempos aleatórios) a cada iteração para evitar que o IP seja banido pela Google. Salve os resultados incrementalmente.
    
      
    

**5. Automação do Portal CAPES via Playwright** Como a CAPES exige interação com a interface, você instanciará um navegador _headless_ (invisível) com o Playwright.

  

- **Ação:** O script deverá navegar até a URL de busca avançada do Portal de Periódicos, localizar os seletores CSS da barra de pesquisa, preencher com os termos do PIBID, selecionar o filtro de anos (2007-2026) e clicar em buscar.
    
      
    
- **Extração:** Em vez de raspar o texto da tela, configure o Playwright para clicar na opção de "Exportar Resultados" e fazer o download automático do arquivo `.ris` ou `.bib` gerado pelo próprio portal.
    
      
    

**6. Consolidação e Exportação (Pandas)** Ao final da execução dos módulos acima, você terá dados brutos de diferentes fontes.

  

- **Ação:** Utilize a biblioteca `pandas` para ler os dados da SciELO, BDTD e Scholar, padronizar o nome das colunas (Ex: `AU` para autores, `TI` para título, etc.) e compilar tudo em um único arquivo `PIBID_consolidado.csv`. Importe este arquivo (junto com o `.ris` baixado da CAPES) para o Zotero para a desduplicação final.
    
      
    

Você prefere começar estruturando os scripts de coleta das bases com APIs abertas (SciELO e BDTD) ou prefere focar primeiro no desafio da automação de navegador para o Portal CAPES?