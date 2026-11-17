"""Confere e restaura anexos baixados de uma release; sem rede."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pasta-downloads', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    entries = json.loads((root/'dados_release.json').read_text(encoding='utf8'))['arquivos']
    for e in entries:
        target = (root/e['caminho']).resolve()
        if not target.is_relative_to(root):
            raise ValueError('Destino fora do projeto')
        source = target if target.exists() else (args.pasta_downloads/e['asset'] if args.pasta_downloads else None)
        if source is None or not source.is_file():
            raise FileNotFoundError('Baixe o anexo: '+e['asset'])
        if source.stat().st_size != e['bytes'] or digest(source) != e['sha256']:
            raise ValueError('Tamanho ou SHA-256 divergente: '+e['asset'])
        if source.resolve() != target:
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.name+'.download')
            with temporary.open('xb') as output, source.open('rb') as inp:
                shutil.copyfileobj(inp, output)
            if digest(temporary) != e['sha256']:
                raise ValueError('Falha na copia; arquivo temporario preservado')
            temporary.rename(target)
        print('OK: '+e['caminho'])

if __name__ == '__main__':
    main()
