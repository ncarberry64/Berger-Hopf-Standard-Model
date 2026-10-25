"""A native-observation replay preserves its likelihood and unavailable quantities."""
from io import BytesIO
import hashlib
import json
import zipfile

import numpy as np
import pytest

from bhtracker import fit
from bhtracker.examples import make_example
from bhtracker.photometry import fit_photometry
from bhtracker.report import export_analysis_bundle, replay_analysis
from test_unresolved_observations import synthetic_dataset


def rewrite_bundle(path, files):
    with zipfile.ZipFile(path, 'w') as archive:
        for name, blob in files.items():
            archive.writestr(name, blob)


def test_native_export_replay_and_protocol_integrity(tmp_path):
    data = synthetic_dataset(noise=True)
    result = fit_photometry(data, starts=4)
    bundle = export_analysis_bundle(result)
    source = tmp_path / 'native photometry.zip'
    source.write_bytes(bundle)
    with zipfile.ZipFile(BytesIO(bundle)) as archive:
        files = {name: archive.read(name) for name in archive.namelist()}
    saved = json.loads(files['dataset.json'])
    assert saved == data.to_dict()
    assert json.loads(files['result.json'])['mass_status'] == 'MASS_UNRESOLVED'
    assert len(files['native_observations.csv'].splitlines()) == len(data.rows) + 1
    assert b'one' in files['report.html'] and b'BHSM' in files['report.html']
    assert all(value is None for value in result['unresolved_quantities'].values())
    check = replay_analysis(source, tmp_path / 'replayed')
    assert check['passed'] and check['same_native_row_identities_and_order']
    assert check['same_unresolved_quantities'] and check['same_interpretation']
    new = json.loads((tmp_path / 'replayed/result.json').read_text(encoding='utf8'))
    np.testing.assert_allclose(new['predictions_magnitude'], result['predictions_magnitude'], atol=1e-10)
    files['dataset.json'] += b' '
    rewrite_bundle(source, files)
    with pytest.raises(ValueError, match='hash mismatch'):
        replay_analysis(source, tmp_path / 'tampered')
    files['dataset.json'] = json.dumps(saved, indent=2).encode() + b'\n'
    manifest = json.loads(files['manifest.json'])
    manifest['files']['dataset.json'] = hashlib.sha256(files['dataset.json']).hexdigest()
    manifest['protocol_sha256'] = '0' * 64
    files['manifest.json'] = json.dumps(manifest).encode()
    rewrite_bundle(source, files)
    with pytest.raises(ValueError, match='likelihood protocol differs'):
        replay_analysis(source, tmp_path / 'wrong protocol')


def test_resolved_legacy_replay_refits_raw_and_certifies_worldtube(tmp_path):
    raw, _ = make_example('nearby_motion')
    result = fit(raw, starts=1)
    source = tmp_path / 'legacy.zip'
    with zipfile.ZipFile(BytesIO(export_analysis_bundle(result))) as archive:
        files = {name: archive.read(name) for name in archive.namelist()}
    old = json.loads(files['result.json'])
    old['model'].pop('parameter_basis')
    # A legacy internal vector is deliberately unusable in the current basis.
    old['_internal']['mean'] = ['legacy coordinates must never be evaluated']
    files['result.json'] = json.dumps(old).encode()
    manifest = json.loads(files['manifest.json'])
    manifest['files']['result.json'] = hashlib.sha256(files['result.json']).hexdigest()
    files['manifest.json'] = json.dumps(manifest).encode()
    rewrite_bundle(source, files)
    check = replay_analysis(source, tmp_path / 'migrated')
    assert check['passed'] and check['same_physical_worldtube']
    assert check['parameter_basis_handling']['migration']
    old['model']['r0_pc'] *= 2
    files['result.json'] = json.dumps(old).encode()
    manifest['files']['result.json'] = hashlib.sha256(files['result.json']).hexdigest()
    files['manifest.json'] = json.dumps(manifest).encode()
    rewrite_bundle(source, files)
    with pytest.raises(ValueError, match='replay differs'):
        replay_analysis(source, tmp_path / 'changed domain')
    failure = json.loads((tmp_path / 'changed domain/replay_check.json').read_text())
    assert not failure['same_physical_worldtube']
    assert 'historical default worldtube differs' in failure['model_migration_required']
