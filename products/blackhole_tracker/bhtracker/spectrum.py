"""Read-only, hash-verified evidence-spectrum snapshot; no fitting or inference."""
from functools import lru_cache
from copy import deepcopy
import base64
import gzip
import hashlib
from html.parser import HTMLParser
from io import BytesIO
import json
from pathlib import Path
import re

SOURCE_MANIFEST_SHA256 = '4e25789156f4bea1dadb422577103efb4886beda391da6fc13596621ebf85743'
SNAPSHOT_VERSION = 'v11'
DATA_REVISION = 'v10'
SOURCE_MANIFEST_BYTES = 2050
SCIENTIFIC_SCOPE = 'Frozen read-only investigation/model records; labels are not validated gravitational imprints, black-hole identities or discoveries.'
NAMES = ('index.html', 'spectrum_data_v1.json', 'spectrum_rows_v1.csv',
         'duration_evidence_spectrum_v1.png', 'duration_evidence_spectrum_v1.svg',
         'catalog_source_score_spectrum_v1.png', 'catalog_source_score_spectrum_v1.svg',
         'INPUT_BINDING_v1.json', 'READ_ME_FIRST.txt', 'OUTPUT_MANIFEST_v1.json')
WEB = Path(__file__).resolve().parent / 'web'
MIME = {'.html': 'text/html; charset=utf-8', '.json': 'application/json; charset=utf-8',
        '.csv': 'text/csv; charset=utf-8', '.txt': 'text/plain; charset=utf-8',
        '.png': 'image/png', '.svg': 'image/svg+xml'}


def _read_limited(path, limit):
    with Path(path).open('rb') as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValueError('spectrum file exceeds its declared size limit')
    return raw


def _unpack(stored, size):
    if type(size) is not int or not 0 <= size <= 64_000_000:
        raise ValueError('unsupported spectrum asset size')
    with gzip.GzipFile(fileobj=BytesIO(stored), mode='rb') as stream:
        raw = stream.read(size + 1)
    if len(raw) != size:
        raise ValueError('spectrum decoded asset size mismatch')
    return raw


@lru_cache(maxsize=1)
def _package_manifest():
    # The canonical source manifest, rather than editable package metadata,
    # owns every original asset identity. Its exact digest is source-pinned.
    raw = _unpack(_read_limited(WEB / 'spectrum__OUTPUT_MANIFEST_v1.json.gz', 4096), SOURCE_MANIFEST_BYTES)
    if hashlib.sha256(raw).hexdigest() != SOURCE_MANIFEST_SHA256:
        raise ValueError('spectrum source manifest SHA-256 mismatch')
    source = json.loads(raw)
    value = json.loads(_read_limited(WEB / 'spectrum_package_manifest.json', 32_000))
    if (not isinstance(value, dict) or value.get('schema') != 'bhtracker.spectrum_snapshot_package.v1'
            or value.get('source_manifest_sha256') != SOURCE_MANIFEST_SHA256
            or value.get('snapshot_version') != SNAPSHOT_VERSION
            or value.get('data_revision') != DATA_REVISION
            or value.get('formal_repository') != 'https://github.com/ncarberry64/Berger-Hopf-Standard-Model'
            or value.get('scientific_scope') != SCIENTIFIC_SCOPE
            or not isinstance(value.get('content_security_policy'), str)
            or not value['content_security_policy']
            or not isinstance(value.get('assets'), dict)):
        raise ValueError('unsupported spectrum package/source manifest')
    if set(value.get('assets', {})) != set(NAMES) or set(source.get('files', {})) != set(NAMES) - {'OUTPUT_MANIFEST_v1.json'}:
        raise ValueError('spectrum package differs from explicit asset allowlist')
    if value.get('model_records') != source['model_records'] or value.get('new_model_calls') != 0:
        raise ValueError('spectrum count or read-only scope mismatch')
    for name in NAMES:
        item = value['assets'][name]
        compressed = not name.endswith('.png')
        expected = source['files'].get(name, {'sha256': SOURCE_MANIFEST_SHA256, 'bytes': len(raw)})
        if (not isinstance(item, dict)
                or item.get('stored_name') != 'spectrum__' + name + ('.gz' if compressed else '')
                or item.get('gzip') is not compressed
                or item.get('sha256') != expected['sha256'] or item.get('bytes') != expected['bytes']
                or type(item.get('stored_bytes')) is not int or not 0 < item['stored_bytes'] <= 64_000_000
                or not isinstance(item.get('stored_sha256'), str)
                or re.fullmatch('[0-9a-f]{64}', item['stored_sha256']) is None):
            raise ValueError('spectrum asset metadata mismatch: ' + name)
    return value


def package_manifest():
    """A reporting copy; callers cannot mutate cached paths or identities."""
    return deepcopy(_package_manifest())


def read_asset(name):
    """Return original frozen bytes; reject traversal, edits and corrupt gzip."""
    if type(name) is not str or name not in NAMES:
        raise ValueError('unknown spectrum asset')
    item = _package_manifest()['assets'][name]
    stored = _read_limited(WEB / item['stored_name'], item['stored_bytes'])
    if len(stored) != item['stored_bytes'] or hashlib.sha256(stored).hexdigest() != item['stored_sha256']:
        raise ValueError('spectrum stored asset SHA-256 mismatch: ' + name)
    raw = _unpack(stored, item['bytes']) if item['gzip'] else stored
    if len(raw) != item['bytes'] or hashlib.sha256(raw).hexdigest() != item['sha256']:
        raise ValueError('spectrum original asset SHA-256 mismatch: ' + name)
    return raw


@lru_cache(maxsize=1)
def html_content_security_policy():
    """Derive the policy from the verified original inline bytes, not a request."""
    text = read_asset('index.html').decode('utf8')
    scripts = re.findall(r'<script\b[^>]*>(.*?)</script>', text, re.S)
    styles = re.findall(r'<style\b[^>]*>(.*?)</style>', text, re.S)
    if len(scripts) != 2 or len(styles) != 1:
        raise ValueError('unexpected frozen spectrum script/style count')
    class Attributes(HTMLParser):
        def __init__(self):
            super().__init__(); self.values = []
        def handle_starttag(self, tag, attributes):
            self.values.extend(value for key, value in attributes if key == 'style')
    attributes = Attributes(); attributes.feed(text)
    token = lambda s: "'sha256-" + base64.b64encode(hashlib.sha256(s.encode('utf8')).digest()).decode('ascii') + "'"
    csp = "default-src 'none'; script-src " + ' '.join(map(token, scripts)) + "; style-src 'unsafe-hashes' " + ' '.join(map(token, styles + sorted(set(attributes.values)))) + "; img-src 'self' data:; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
    if csp != _package_manifest()['content_security_policy']:
        raise ValueError('spectrum inline security policy differs from verified source bytes')
    return csp


def summary():
    from .interpretation import surface_geometry_interpretation
    value = package_manifest()
    return {'snapshot_version': value['snapshot_version'], 'data_revision': DATA_REVISION,
            'data_utf8_sha256':value['assets']['spectrum_data_v1.json']['sha256'], 'source_manifest_sha256': SOURCE_MANIFEST_SHA256,
            'model_records': value['model_records'], 'new_model_calls': 0,
            'scope': value['scientific_scope'], 'formal_repository': value['formal_repository'],
            'surface_geometry_interpretation': surface_geometry_interpretation(),
            'assets': {name: {'sha256': item['sha256'], 'bytes': item['bytes']} for name, item in value['assets'].items()}}


def export_snapshot(directory):
    """Export all ten exact frozen files to a fresh directory; no refit/relabel."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    for name in NAMES:
        with (directory / name).open('xb') as stream:
            stream.write(read_asset(name))
    return verify_snapshot(directory)


def verify_snapshot(directory):
    """Verify a full exported snapshot's byte identity, not scientific validity."""
    directory = Path(directory)
    value = package_manifest()
    for name in NAMES:
        item = value['assets'][name]
        raw = _read_limited(directory / name, item['bytes'])
        if len(raw) != item['bytes'] or hashlib.sha256(raw).hexdigest() != item['sha256']:
            raise ValueError('spectrum export SHA-256 mismatch: ' + name)
    return {'verified': True, 'source_manifest_sha256': SOURCE_MANIFEST_SHA256,
            'files': len(NAMES), 'model_records': value['model_records'], 'new_model_calls': 0,
            'scope': 'Exact frozen snapshot bytes only; no fit replay, new classification or scientific validation.'}
