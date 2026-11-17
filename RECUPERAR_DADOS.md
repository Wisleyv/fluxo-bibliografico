# Recuperar os arquivos grandes

Release de referência: https://github.com/Wisleyv/fluxo-bibliografico/releases/tag/v0.1.0 . Links diretos dos anexos em `dados_release.json`.

Os dois CSVs descritos em `dados_release.json` serão anexos de uma release no próprio GitHub. Não serão incluídos no download do código-fonte. Não exigem Git LFS. Depois da publicação, baixe os dois anexos da mesma release correspondente ao código e execute:

```powershell
python scripts/recuperar_dados_release.py --pasta-downloads "C:/caminho/dos/downloads"
```

O programa confere tamanho e SHA-256 antes de restaurar os arquivos nos caminhos usados pelos scripts. Se já estiverem presentes e corretos, apenas os confere. Não substitui arquivos existentes com conteúdo diferente. Os nomes dos anexos e destinos estão no manifesto. O comando usa apenas Python e arquivos locais, sem credenciais ou rede.

Após a recuperação, siga `REPRODUZIR_INTEGRACAO_CAPES.md`. O download dos dados e a reprodução integral após publicação ainda precisam ser testados. A inclusão no manifesto não resolve condições de redistribuição das fontes.
