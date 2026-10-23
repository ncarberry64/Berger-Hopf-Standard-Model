"""Package the author-checked v11 viewer on frozen v10 data; never run an analysis or edit its bytes.

Compressed-stream identity requires the same Python/zlib implementation. The
installed snapshot stores frozen gzip bytes; decoded originals are portable.
"""
import argparse
import base64
import gzip
import hashlib
from html.parser import HTMLParser
from io import BytesIO
import json
from pathlib import Path
import re

SOURCE_MANIFEST_SHA256 = '4e25789156f4bea1dadb422577103efb4886beda391da6fc13596621ebf85743'
NAMES = ('index.html', 'spectrum_data_v1.json', 'spectrum_rows_v1.csv',
         'duration_evidence_spectrum_v1.png', 'duration_evidence_spectrum_v1.svg',
         'catalog_source_score_spectrum_v1.png', 'catalog_source_score_spectrum_v1.svg',
         'INPUT_BINDING_v1.json', 'READ_ME_FIRST.txt', 'OUTPUT_MANIFEST_v1.json')


def deterministic_gzip(raw):
    stream = BytesIO()
    # GzipFile fixes the OS byte across Python versions, unlike older
    # gzip.compress(mtime=0) implementations that delegate their header to zlib.
    with gzip.GzipFile(filename='', mode='wb', fileobj=stream, compresslevel=9, mtime=0) as out:
        out.write(raw)
    return stream.getvalue()


def package(source, destination):
    source, destination = Path(source), Path(destination)
    raw_manifest = (source / 'OUTPUT_MANIFEST_v1.json').read_bytes()
    if hashlib.sha256(raw_manifest).hexdigest() != SOURCE_MANIFEST_SHA256:
        raise ValueError('source must be the exact author-checked v11 snapshot')
    manifest = json.loads(raw_manifest)
    if set(manifest['files']) != set(NAMES) - {'OUTPUT_MANIFEST_v1.json'}:
        raise ValueError('source manifest differs from the explicit snapshot inventory')
    blobs = {}
    entries = {}
    for name in NAMES:
        raw = (source / name).read_bytes()
        record = manifest['files'].get(name, {'sha256': SOURCE_MANIFEST_SHA256, 'bytes': len(raw_manifest)})
        if len(raw) != record['bytes'] or hashlib.sha256(raw).hexdigest() != record['sha256']:
            raise ValueError('source snapshot size/hash mismatch: ' + name)
        compressed = not name.endswith('.png')
        stored_name = 'spectrum__' + name + ('.gz' if compressed else '')
        stored = deterministic_gzip(raw) if compressed else raw
        blobs[stored_name] = stored
        entries[name] = dict(stored_name=stored_name, gzip=compressed,
                             sha256=record['sha256'], bytes=len(raw),
                             stored_sha256=hashlib.sha256(stored).hexdigest(), stored_bytes=len(stored))
    text = (source / 'index.html').read_bytes().decode('utf8')
    scripts = re.findall(r'<script\b[^>]*>(.*?)</script>', text, re.S)
    styles = re.findall(r'<style\b[^>]*>(.*?)</style>', text, re.S)
    if len(scripts) != 2 or len(styles) != 1:
        raise ValueError('reviewed v11 inline script/stylesheet count differs')
    class Attributes(HTMLParser):
        def __init__(self):
            super().__init__(); self.values = []
        def handle_starttag(self, tag, attributes):
            self.values.extend(value for key, value in attributes if key == 'style')
    attributes = Attributes(); attributes.feed(text)
    token = lambda s: "'sha256-" + base64.b64encode(hashlib.sha256(s.encode('utf8')).digest()).decode('ascii') + "'"
    # Hashes authorize only these exact frozen blocks. The viewer has no
    # client network/model calls and uses DOM listeners rather than handlers.
    csp = "default-src 'none'; script-src " + ' '.join(map(token, scripts)) + "; style-src 'unsafe-hashes' " + ' '.join(map(token, styles + sorted(set(attributes.values)))) + "; img-src 'self' data:; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
    package_manifest = dict(schema='bhtracker.spectrum_snapshot_package.v1', snapshot_version='v11', data_revision='v10',
        source_manifest_sha256=SOURCE_MANIFEST_SHA256, model_records=manifest['model_records'],
        new_model_calls=0, formal_repository='https://github.com/ncarberry64/Berger-Hopf-Standard-Model',
        scientific_scope='Frozen read-only investigation/model records; labels are not validated gravitational imprints, black-hole identities or discoveries.',
        content_security_policy=csp, assets=entries)
    blobs['spectrum_package_manifest.json'] = (json.dumps(package_manifest, indent=2, sort_keys=True) + '\n').encode('utf8')
    destination.mkdir(parents=True, exist_ok=True)
    # Validate everything before writing; never overwrite prior snapshot bytes.
    for name, raw in blobs.items():
        path = destination / name
        if path.exists() and path.read_bytes() != raw:
            raise ValueError('refusing to replace an existing different snapshot: ' + name)
    for name, raw in blobs.items():
        path = destination / name
        if not path.exists():
            with path.open('xb') as stream:
                stream.write(raw)
    return package_manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    value = package(args.source, args.output)
    print(json.dumps({'snapshot_version': value['snapshot_version'], 'source_files': len(value['assets']),
                      'model_records': value['model_records'], 'new_model_calls': 0}))
