"""Frozen viewer transport/export checks; no native or synthetic fit is run."""
import base64
import gzip
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from unittest.mock import Mock, patch
from urllib.error import HTTPError

import pytest

from bhtracker import spectrum
from test_local_app import service, request


def test_snapshot_summary_pins_source_identity_without_promoting_labels():
    summary = spectrum.summary()
    assert summary['snapshot_version'] == 'v11'
    assert summary['data_revision'] == 'v10'
    assert summary['data_utf8_sha256'] == '0e8a86e4bfa72804c3881c9bbc808014a1e6656b4c6bef90641f6d9e35cf99d8'
    assert summary['model_records'] == 1808 and summary['new_model_calls'] == 0
    assert summary['source_manifest_sha256'] == '4e25789156f4bea1dadb422577103efb4886beda391da6fc13596621ebf85743'
    assert summary['surface_geometry_interpretation']['fit_alone_validates_gravitational_origin'] is False
    assert summary['surface_geometry_interpretation']['fit_alone_identifies_black_hole'] is False
    assert len(summary['assets']) == 10
    source = json.loads(spectrum.read_asset('OUTPUT_MANIFEST_v1.json'))
    assert set(source['files']) == set(spectrum.NAMES) - {'OUTPUT_MANIFEST_v1.json'}
    # Original cohort bytes remain independent of the expanded model spectrum.
    from bhtracker.candidate_atlas import load_inventory
    inventory, _ = load_inventory()
    assert len(inventory['events']) == 155 and len(inventory['benchmarks']) == 1


def test_snapshot_html_and_all_downloads_are_exact_source_bytes(service):
    manifest = spectrum.package_manifest()
    for name in spectrum.NAMES:
        status, raw, headers = request(service, '/spectrum/' + name)
        expected = manifest['assets'][name]
        assert status == 200 and len(raw) == expected['bytes']
        assert hashlib.sha256(raw).hexdigest() == expected['sha256']
        assert headers['Content-Type'] == spectrum.MIME[Path(name).suffix]
        assert headers['X-Content-Type-Options'] == 'nosniff'
    _, canonical, _ = request(service, '/spectrum/')
    _, redirected, _ = request(service, '/spectrum')
    assert canonical == redirected == spectrum.read_asset('index.html')


def test_csp_authorizes_only_frozen_scripts_styles_and_legend_attributes(service):
    _, raw, headers = request(service, '/spectrum/')
    text = raw.decode('utf8')
    policy = headers['Content-Security-Policy']
    assert "'unsafe-inline'" not in policy and "'unsafe-eval'" not in policy
    assert "connect-src 'none'" in policy and "frame-ancestors 'none'" in policy
    token = lambda s: "'sha256-" + base64.b64encode(hashlib.sha256(s.encode('utf8')).digest()).decode('ascii') + "'"
    scripts = re.findall(r'<script\b[^>]*>(.*?)</script>', text, re.S)
    styles = re.findall(r'<style\b[^>]*>(.*?)</style>', text, re.S)
    class Tags(HTMLParser):
        def __init__(self): super().__init__(); self.styles = []
        def handle_starttag(self, tag, attrs): self.styles.extend(v for k, v in attrs if k == 'style')
    tags = Tags(); tags.feed(text)
    assert len(scripts) == 2 and len(styles) == 1 and len(tags.styles) == 4
    directives = dict(part.strip().split(' ', 1) for part in policy.split(';'))
    assert set(directives['script-src'].split()) == {token(s) for s in scripts}
    assert set(directives['style-src'].split()) == {"'unsafe-hashes'", *(token(s) for s in styles + tags.styles)}
    runtime = '\n'.join(scripts[1:])
    assert all(value not in runtime for value in ('fetch(', 'XMLHttpRequest', 'WebSocket', 'sendBeacon', 'eval(', 'new Function'))
    assert 'Potential black hole' in text


@pytest.mark.parametrize('name', ['../pyproject.toml', '%2e%2e/pyproject.toml', 'index.html.gz', 'missing.json', 'spectrum_package_manifest.json'])
def test_http_snapshot_allowlist_rejects_other_paths(service, name):
    with pytest.raises(HTTPError) as caught:
        request(service, '/spectrum/' + name)
    assert caught.value.code == 404
    caught.value.close()


def test_context_copy_cannot_mutate_cached_paths_and_unknown_assets_reject():
    copy = spectrum.package_manifest()
    copy['assets']['READ_ME_FIRST.txt']['stored_name'] = '../../secret'
    assert spectrum.read_asset('READ_ME_FIRST.txt').startswith(b'BHSM')
    with pytest.raises(ValueError): spectrum.read_asset('../pyproject.toml')
    with pytest.raises(ValueError): spectrum._unpack(gzip.compress(b'x' * 100), 10)


def test_corrupt_packaged_source_and_stored_asset_fail_closed(tmp_path, monkeypatch):
    original = spectrum.WEB
    names = ['spectrum_package_manifest.json', 'spectrum__OUTPUT_MANIFEST_v1.json.gz', 'spectrum__READ_ME_FIRST.txt.gz']
    for name in names: (tmp_path / name).write_bytes((original / name).read_bytes())
    try:
        monkeypatch.setattr(spectrum, 'WEB', tmp_path)
        spectrum._package_manifest.cache_clear()
        path = tmp_path / 'spectrum__READ_ME_FIRST.txt.gz'
        path.write_bytes(path.read_bytes() + b'edited')
        with pytest.raises(ValueError): spectrum.read_asset('READ_ME_FIRST.txt')
        manifest = tmp_path / 'spectrum__OUTPUT_MANIFEST_v1.json.gz'
        manifest.write_bytes(gzip.compress(b'{}'))
        spectrum._package_manifest.cache_clear()
        with pytest.raises(ValueError): spectrum.package_manifest()
    finally:
        spectrum._package_manifest.cache_clear()


@pytest.mark.parametrize('bad', [[], {'schema': 'bhtracker.spectrum_snapshot_package.v1', 'assets': []}])
def test_malformed_package_metadata_returns_explicit_rejection(tmp_path, monkeypatch, bad):
    (tmp_path / 'spectrum__OUTPUT_MANIFEST_v1.json.gz').write_bytes((spectrum.WEB / 'spectrum__OUTPUT_MANIFEST_v1.json.gz').read_bytes())
    (tmp_path / 'spectrum_package_manifest.json').write_text(json.dumps(bad), encoding='utf8')
    try:
        monkeypatch.setattr(spectrum, 'WEB', tmp_path)
        spectrum._package_manifest.cache_clear()
        with pytest.raises(ValueError): spectrum.package_manifest()
    finally:
        spectrum._package_manifest.cache_clear()


@pytest.mark.parametrize('field,replacement,remove', [
    ('content_security_policy', None, True), ('content_security_policy', [], False),
    ('scientific_scope', None, True), ('scientific_scope', 'These labels establish black holes.', False),
    ('data_revision', None, True), ('data_revision', 'invented-new-data', False)])
def test_reporting_metadata_cannot_disappear_or_promote_scientific_scope(service, tmp_path, monkeypatch, field, replacement, remove):
    original = spectrum.WEB
    value = spectrum.package_manifest()
    if remove: value.pop(field)
    else: value[field] = replacement
    (tmp_path / 'spectrum_package_manifest.json').write_text(json.dumps(value), encoding='utf8')
    (tmp_path / 'spectrum__OUTPUT_MANIFEST_v1.json.gz').write_bytes((original / 'spectrum__OUTPUT_MANIFEST_v1.json.gz').read_bytes())
    try:
        monkeypatch.setattr(spectrum, 'WEB', tmp_path)
        spectrum._package_manifest.cache_clear()
        with pytest.raises(ValueError): spectrum.package_manifest()
        with pytest.raises(HTTPError) as caught: request(service, '/spectrum/')
        assert caught.value.code == 503
        caught.value.close()
    finally:
        spectrum._package_manifest.cache_clear()


def test_export_verify_preserves_all_bytes_and_rejects_tampering(tmp_path):
    destination = tmp_path / 'export'
    check = spectrum.export_snapshot(destination)
    assert check['verified'] and check['files'] == 10 and check['new_model_calls'] == 0
    assert set(p.name for p in destination.iterdir()) == set(spectrum.NAMES)
    assert spectrum.verify_snapshot(destination) == check
    path = destination / 'READ_ME_FIRST.txt'; path.write_bytes(path.read_bytes() + b'edited')
    with pytest.raises(ValueError): spectrum.verify_snapshot(destination)
    with pytest.raises(FileExistsError): spectrum.export_snapshot(destination)


def test_installed_content_provenance_binds_every_compressed_asset_and_figure():
    from bhtracker.provenance import software_provenance
    files = software_provenance()['package_files_sha256']
    for item in spectrum.package_manifest()['assets'].values():
        assert files['web/' + item['stored_name']] == item['stored_sha256']
    assert files['web/spectrum_package_manifest.json'] == hashlib.sha256((spectrum.WEB / 'spectrum_package_manifest.json').read_bytes()).hexdigest()


def test_workspace_navigation_and_spectrum_launcher(service):
    for route in ('/', '/photometry', '/joint', '/atlas'):
        _, raw, _ = request(service, route)
        assert b'href="/spectrum/"' in raw
    from bhtracker.server import serve
    server = Mock(server_port=9999); server.serve_forever.side_effect = KeyboardInterrupt
    with patch('bhtracker.server.make_server', return_value=server), patch('bhtracker.server.webbrowser.open') as browser:
        serve(9999, True, 'spectrum')
    browser.assert_called_once_with('http://127.0.0.1:9999/spectrum/')


def test_cli_summary_and_verification_do_not_invoke_fitting(tmp_path):
    completed = subprocess.run([sys.executable, '-B', '-m', 'bhtracker', 'spectrum', 'summary'],
                               capture_output=True, text=True, check=True)
    assert json.loads(completed.stdout)['model_records'] == 1808
    failed = subprocess.run([sys.executable, '-B', '-m', 'bhtracker', 'spectrum', 'verify', str(tmp_path / 'missing')],
                            capture_output=True, text=True)
    assert failed.returncode == 2 and 'Input/model error' in failed.stderr


def test_v11_view_patch_preserves_all_eight_v10_non_view_members():
    source=json.loads(spectrum.read_asset('OUTPUT_MANIFEST_v1.json'))
    assert source['view_patch']['view_revision']=='v11'
    assert source['view_patch']['data_revision']=='v10'
    assert source['view_patch']['parent_view_manifest_sha256']=='c7d7034a7ef8e4ae65ec3f10a9939539cc8efe823af32ac686a6976c495ebdf2'
    assert source['view_patch']['search_semantics']=='qualified_membership_aliases.v1'
    expected={
      'spectrum_data_v1.json':'0e8a86e4bfa72804c3881c9bbc808014a1e6656b4c6bef90641f6d9e35cf99d8',
      'spectrum_rows_v1.csv':'a57032a950865ec8a7e40a328994e608c6ad357ef1923ccc280ce7ed727c2964',
      'duration_evidence_spectrum_v1.png':'cdd48c63842f122f0f51f32e34f229c7bc81d612f713eaf4065a4436b85b0b6c',
      'duration_evidence_spectrum_v1.svg':'b7b1d7af9de3e3209a26d70200de137df423618fc3de4943380dd6224e6d4e56',
      'catalog_source_score_spectrum_v1.png':'7484aa3ad337dfd1f015bcbd8a05f1d67a32c1aec6a2c9ac136b457a4f17e121',
      'catalog_source_score_spectrum_v1.svg':'b67433d39d9023d055f6933c0ce761cae7c52fcadbb6230e08401c5c29b46688',
      'INPUT_BINDING_v1.json':'9b9a9ee33df0d2c920c026a848acb615ef48879ec939671f6ab9ddb9d6f4db39',
      'READ_ME_FIRST.txt':'b89494fd87245b136810070ff8fa869938be10784ec3750a762006592f8c4312'}
    for name,digest in expected.items():
        assert hashlib.sha256(spectrum.read_asset(name)).hexdigest()==digest
    html=spectrum.read_asset('index.html')
    assert hashlib.sha256(html).hexdigest()=='7859d08ccc806653cd43e544b81041795072f950ab85bf46a5436815b9610997'
    payload=re.search(rb'<script id="spectrum-data" type="application/json">(.*?)</script>',html,re.S).group(1)
    assert hashlib.sha256(payload).hexdigest()=='5cbdeb197a87f511650a25626ad8e09cccc92a3bfd835e4dc8233346f98c7b4f'
    assert b'viewer_identity:trackViewerIdentity' in html


def test_portable_installed_viewer_search_and_view_replay_regression():
    node=shutil.which('node')
    assert node is not None, 'Node is required for the release viewer regression controls'
    fixture=Path(__file__).with_name('spectrum_alias_search_fixture.js')
    completed=subprocess.run([node,str(fixture),str(spectrum.WEB/'spectrum__index.html.gz')],
                             capture_output=True,text=True,timeout=90)
    assert completed.returncode==0,completed.stdout+completed.stderr
    result=json.loads(completed.stdout)
    assert result['passed'] and set(result['known_alias_counts'].values())=={1}
    assert result['context_neighbor_matches']==result['gaia18ajz_historical_matches']==0
    assert result['view_revision']=='v11' and result['data_revision']=='v10'
    assert result['json_csv_replay'] and result['hidden_sequence_count']==2
    assert result['legacy_wrong_subset_refused'] and result['legacy_canonical_compatible']
    assert result['unknown_viewer_refused']
