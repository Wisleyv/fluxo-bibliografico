"""Reúne a entrega congelada e seus subsídios sem modificar os originais."""
import csv
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'entrega_final'
REL = Path('dados/entregas/marco5_capes_20261116')
DATA = Path('dados/analises/integracao_capes_20261116/elegibilidade')
NOTE = 'Nota metodológica - uso de agentes de codificação.md'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(2**20), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def main():
    if DEST.exists() and any(DEST.iterdir()):
        raise RuntimeError('entrega_final não está vazia; preservar e conferir antes de outra execução.')
    DEST.mkdir(exist_ok=True)
    archive = ROOT / REL / 'Pacote reproduzivel PIBID.zip'
    expected = json.loads((ROOT / REL / 'Verificacao do pacote.json').read_text(encoding='utf8'))
    assert sha(archive) == expected['sha256_zip']
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            assert (DEST / name).resolve().is_relative_to(DEST.resolve()), name
        z.extractall(DEST)
    original_inventory = read(DEST / REL / 'Inventario.csv')
    for row in original_inventory:
        assert sha(DEST / row['caminho']) == row['sha256'], row['caminho']
    print(f'{len(original_inventory)} membros extraídos e conferidos.', flush=True)
    # Inclui o ZIP selado e os registros externos que não estão dentro dele.
    for p in (ROOT / REL).rglob('*'):
        if p.is_file():
            target = DEST / p.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)
            assert sha(target) == sha(p), str(p)
    shutil.copy2(ROOT / NOTE, DEST / NOTE)
    shutil.copy2(Path(__file__), DEST / 'scripts' / Path(__file__).name)
    (DEST / 'LEIA-ME.md').write_text('''# Entrega final — produção científica sobre o PIBID

Versão integrada CAPES de 16/11/2026. Este diretório é autossuficiente para consultar os resultados e reconstruir os produtos desde os corpora e decisões congelados. Não depende dos caminhos do computador de origem. Abra os arquivos após baixar a pasta inteira; mantenha sua estrutura. O ZIP reproduzível também pode ser extraído sozinho em outro diretório.

## Produtos para leitura e escrita do artigo

- [Planilha: obras únicas e seis gráficos nativos editáveis](dados/entregas/marco5_capes_20261116/Planilha%20final%20PIBID.xlsx).
- [Base técnica separada](dados/entregas/marco5_capes_20261116/Base%20tecnica%20PIBID.zip).
- [Matriz de cobertura e sobreposição](dados/entregas/marco5_capes_20261116/Matriz%20de%20cobertura%20e%20sobreposicao.xlsx).
- [Relatório metodológico atualizado](dados/entregas/marco5_capes_20261116/Relatorio%20metodologico.md).
- [Síntese das seis subquestões, com referências às evidências](dados/entregas/marco5_capes_20261116/Sintese%20das%20seis%20subquestoes.md).
- [Pacote reproduzível completo, cerca de 507 MB](dados/entregas/marco5_capes_20261116/Pacote%20reproduzivel%20PIBID.zip).
- [Nota sobre agentes de codificação e direção humana](Nota%20metodol%C3%B3gica%20-%20uso%20de%20agentes%20de%20codifica%C3%A7%C3%A3o.md).

## Revisão por partes

1. **Fundamentos e decisões:** `Vaneria.txt`, protocolos v1.3/v1.4, planos e aceites na raiz. Documentos históricos mantêm seus estados originais: não são instruções para substituir os resultados atuais.
2. **Dados abertos e rastreabilidade:** [corpora, proveniências, decisões e pendências em CSV](dados/analises/integracao_capes_20261116/elegibilidade/). O [dicionário](DICIONARIO_DOS_DADOS.md) explica unidades e chaves; o [catálogo de campos](CATALOGO_CSV.csv) informa cabeçalhos e contagens. CSV usa vírgula e UTF-8, com ou sem marcador BOM; células vazias não significam ausência do fenômeno.
3. **Cobertura e indicadores:** [tabelas atuais](dados/analises/integracao_capes_20261116/indicadores/) e [matrizes](dados/entregas/marco5_capes_20261116/matriz/). Fontes sobrepostas não são aditivas.
4. **Evidência qualitativa:** `Tres eixos.csv`, materiais locais e decisões regionais; use fonte, localização e estado da evidência. Não presumir leitura integral de todas as obras.
5. **Figuras e conferências:** [prévias PNG/PDF](dados/entregas/marco5_capes_20261116/previews/), `Conferencia visual.csv`, `Conferencias da entrega.csv`, `Testes.txt` e `Teste de reconstrucao.json`, na pasta dos produtos.
6. **Reprodução:** [instruções da versão CAPES](REPRODUZIR_INTEGRACAO_CAPES.md), scripts, testes, requisitos, arquivos brutos e logs. O roteiro antigo `REPRODUZIR_MARCO5.md` é histórico. Execute em cópia de trabalho. Python/openpyxl bastam para leitura e cálculos; Windows/Excel são usados para recálculo e exportação nativos dos gráficos. Executáveis não são incluídos.

## Resultados e limites que devem acompanhar qualquer publicação

São 7.779 obras nacionais, 97 goianas e 7.798 na união deduplicada da planilha; 78 regionais correspondem ao nacional. As frações observadas de afiliação goiana identificada são 196/7.779 (2,52%), publicação 2007–08/11/2026, e 67/3.459 (1,94%), publicação 2020–08/11/2026. A participação total é não estimável. Contexto e afiliação são dimensões separadas.

Permanecem 871 pendências regionais, quatro inclusões por defesa, dúvida artigo/capítulo, dez ocorrências CAPES provisórias e afiliações incompletas. A busca CAPES é filtrada, com 23 páginas declaradas; não demonstra completude. Coletas: OpenAlex 15/11 e CAPES 16/11/2026; corte de publicação 08/11/2026. Resultados consolidados nos conjuntos observados não equivalem ao universo completo. As verificações são internas, sem validação científica independente.

## Integridade e publicação

[VERIFICACAO_DA_REUNIAO.json](VERIFICACAO_DA_REUNIAO.json) registra as verificações desta organização. [MANIFESTO_SHA256.csv](MANIFESTO_SHA256.csv) lista todos os arquivos da pasta, exceto o próprio manifesto e seu arquivo de checksum; o checksum do manifesto está em `MANIFESTO_SHA256.sha256`. Os inventários antigos referem-se a suas versões, não a toda esta pasta. Logs históricos podem conter caminhos absolutos do computador de origem; a reprodução usa caminhos relativos.

Esta organização não altera o ZIP selado nem os resultados científicos. A nota de agentes e os guias desta pasta são suplementos externos ao ZIP. Consulte [PUBLICACAO_E_METADADOS.md](PUBLICACAO_E_METADADOS.md) antes do depósito: licença, autoria, identificadores e permissões de redistribuição ainda precisam ser definidos pelos responsáveis. Nenhum depósito público foi realizado.
''', encoding='utf8')
    (DEST / 'DICIONARIO_DOS_DADOS.md').write_text('''# Dicionário de leitura dos dados

Versão corrente: `dados/analises/integracao_capes_20261116/elegibilidade/`. As pastas dos marcos anteriores preservam estados históricos e não devem ser somadas ao corpus atual.

| Arquivo | Unidade / chave | Uso |
|---|---|---|
| Corpus nacional.csv | Obra incluída / obra_id | 7.779 obras; publicação 2007–08/11/2026 |
| Corpus goiano.csv | Obra regional incluída / obra_id | 97 obras; contexto, afiliação e critério temporal separados |
| Proveniencia.csv | Registro de origem / registro | 14.423 registros ligados por obra_id; inclui componentes pendentes |
| Registro de decisoes.csv | Componente / obra_id | 13.231 componentes, não todos obras confirmadas |
| Decisoes regionais.csv | Unidade de decisão regional / obra_id | Inclusão, exclusão ou pendência fundamentada |
| Proveniencia regional.csv | Ocorrência de origem regional | 2.118 registros; fontes e filas se sobrepõem |
| Tres eixos.csv | Obra × eixo / obra_id + eixo | 291 extrações: síntese, fonte, localização e estado |
| Pendencias regionais.csv | Unidade regional pendente | 871 pendências anteriores; não são inclusões |
| Fila de transferencia regional.csv | Ocorrência CAPES provisória | Dez ocorrências; não dez novas obras |

`obra_id` relaciona corpus, decisões, proveniência e eixos. `ids_anteriores` e campos `obra_id_antes_*` conservam pontes de fusão; não criar obras novas a partir deles. `registro`, `record_id`, `source_record_id` e `source_run_id` identificam ocorrências e rodadas; IDs OpenAlex e códigos de base complementam os relacionamentos. DOI isolado não substitui a decisão de identidade.

`raw_file`, `fonte`, `coletado_em` e os campos terminados em `_original` documentam proveniência; valores discordantes não são necessariamente erros de transcrição. `anos_publicacao` e `anos_defesa` não são intercambiáveis. `decisao`, `justificativa`, `pendencias`, `registro_evidencia` e `trecho_evidencia` sustentam a elegibilidade. `contexto_goias` e `afiliacao_goias` representam vínculos diferentes.

Na tabela dos eixos, `estado` distingue presença, informação não encontrada e evidência insuficiente; não converter as duas últimas em ausência. Campos multivalorados devem ser lidos conforme os scripts, sem presumir uma pessoa por segmento de autoria concatenada. `CATALOGO_CSV.csv` preserva os cabeçalhos exatos; o protocolo, o relatório e os scripts estabelecem a semântica específica dos demais campos.

Nos indicadores, numerador, denominador, escopo, unidade e estado devem ser lidos conjuntamente. Créditos integrais de coautoria/instituições podem somar mais que o corpus; combinações exclusivas de fontes, ao contrário, são disjuntas. Os CSVs são dados; não executar conteúdo de células como comandos ou fórmulas.
''', encoding='utf8')
    (DEST / 'PUBLICACAO_E_METADADOS.md').write_text('''# Metadados e condições para depósito público

Título: Produção científica sobre o PIBID no Brasil (2007–2026) e revisão de escopo em Goiás (2020–2026): dados, decisões e materiais de reprodução.

Versão dos resultados: integração CAPES de 16/11/2026. Idioma principal: português. Tipos: dados tabulares CSV, planilhas XLSX, documentos Markdown/TXT/JSON, figuras PNG/PDF, registros RIS, scripts e arquivos brutos. A referência metodológica principal é o relatório integrado; a referência dos procedimentos de reprodução é `REPRODUZIR_INTEGRACAO_CAPES.md`. Escopo, datas e limitações constam do LEIA-ME.

O conjunto está organizado para revisão e preparação de um depósito de dados. Não foi atribuída uma licença geral: os responsáveis devem indicar autoria/ORCID, instituição, contato público, financiamento, licença dos dados e do código, repositório e identificador persistente. Nenhum desses campos foi inferido ou inventado. O identificador do artigo pode ser acrescentado após sua atribuição.

Os brutos preservam conteúdo de serviços e fontes de terceiros. A inclusão para auditoria não transfere direitos nem autoriza redistribuição irrestrita. Antes de publicar o pacote integral, os responsáveis devem conferir condições das fontes e a redistribuição dos materiais arquivados; se algum arquivo não puder ser distribuído, documentar a restrição e manter sua referência/hash e instrução de acesso. Não apresentar o ZIP integral como licenciado de forma uniforme sem essa definição.

Conferências de estrutura, integridade, links e dados não substituem uma revisão editorial de permissões e informações pessoais. Autorias bibliográficas e caminhos históricos aparecem nos registros; não se declara anonimização ou auditoria integral de privacidade. A responsabilidade pelo depósito e pela interpretação científica é humana. O preparo local desta pasta não constitui publicação externa nem comprova, por si só, atendimento a todos os requisitos FAIR.

Sugestão de citação a completar: [AUTORES]. Produção científica sobre o PIBID no Brasil e em Goiás: dados e materiais de reprodução. Versão integrada CAPES, 16 nov. 2026. [REPOSITÓRIO], [ANO DO DEPÓSITO]. [DOI/URL PERSISTENTE].
''', encoding='utf8')
    selected = [DEST / DATA, DEST / 'dados/analises/integracao_capes_20261116/indicadores', DEST / REL / 'matriz']
    catalog = []
    for folder in selected:
        for p in sorted(folder.glob('*.csv')):
            with p.open(encoding='utf-8-sig', newline='') as f:
                reader = csv.reader(f)
                headers = next(reader)
                count = sum(1 for _ in reader)
            catalog.append({'caminho':p.relative_to(DEST).as_posix(), 'linhas_sem_cabecalho':count, 'campos':json.dumps(headers, ensure_ascii=False)})
    with (DEST / 'CATALOGO_CSV.csv').open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=catalog[0].keys()); w.writeheader(); w.writerows(catalog)
    n = read(DEST / DATA / 'Corpus nacional.csv'); g = read(DEST / DATA / 'Corpus goiano.csv')
    assert len(n) == len({r['obra_id'] for r in n}) == 7779
    assert len(g) == len({r['obra_id'] for r in g}) == 97
    assert len(read(DEST / DATA / 'Tres eixos.csv')) == 291
    links = 0
    for p in [DEST/'LEIA-ME.md', DEST/NOTE, DEST/REL/'Relatorio metodologico.md', DEST/REL/'Sintese das seis subquestoes.md']:
        for target in re.findall(r'\]\(([^)]+)\)', p.read_text(encoding='utf8')):
            if '://' in target: continue
            resolved = (p.parent / unquote(target.split('#')[0])).resolve()
            if resolved.name in ('VERIFICACAO_DA_REUNIAO.json','MANIFESTO_SHA256.csv'): continue
            assert resolved.is_relative_to(DEST.resolve()) and resolved.exists(), str(resolved)
            links += 1
    result = {'estado':'OK', 'membros_do_pacote_conferidos':len(original_inventory), 'sha256_zip_original':expected['sha256_zip'], 'originais_preservados':True, 'csv_catalogados':len(catalog), 'links_locais_primarios_conferidos':links, 'corpus_nacional':len(n), 'corpus_goiano':len(g), 'extracoes':291, 'alcance':'Reunião e conferência de integridade; sem nova coleta, análise científica ou publicação externa. Testes científicos e de reconstrução são os da entrega preservada.', 'publicacao':'Pendentes metadados autorais, licença e conferência de redistribuição pelos responsáveis.'}
    (DEST/'VERIFICACAO_DA_REUNIAO.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
    files = sorted(p for p in DEST.rglob('*') if p.is_file())
    rows = [{'caminho':p.relative_to(DEST).as_posix(), 'bytes':p.stat().st_size, 'sha256':sha(p)} for p in files]
    manifest = DEST/'MANIFESTO_SHA256.csv'
    with manifest.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    (DEST/'MANIFESTO_SHA256.sha256').write_text(sha(manifest)+'  MANIFESTO_SHA256.csv\n', encoding='utf8')
    print(json.dumps({**result, 'arquivos_manifestados':len(rows)}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
