"""Consumer boundary tests; synthetic records do not certify physical data."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('full_linear_consumer',
    ROOT/'scripts/certify_n12_gate7_full_direct_causal_linear_defect.py')
consumer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(consumer)


@pytest.fixture
def paired_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(consumer, 'WORK', tmp_path)
    monkeypatch.setattr(consumer.local.df, 'file_key', lambda p: str(p))
    verified = []
    monkeypatch.setattr(consumer.local.df.values, 'verify_binding', lambda record: verified.append(record))
    path = tmp_path/'manifest.json'
    path.write_text('{}')
    manifest = dict(algorithm=consumer.local.ALGORITHM, intervals=list(range(370)),
        all_intervals_assembled=True,
        files={str(tmp_path/f'interval_{i:03d}.{ext}'): 'virtual-digest'
               for i in range(370) for ext in ('json', 'npz')})
    receipt = dict(intervals=list(range(370)), byte_identical=True, independent_recomputation=True,
                   manifest_SHA256=consumer.local.df.values.sha(path))
    return manifest, receipt, path, verified


def test_complete_pair_is_verified_not_merely_counted(paired_manifest):
    manifest, receipt, path, verified = paired_manifest
    consumer.verify_manifest(manifest, receipt, path)
    assert verified == [dict(files=manifest['files'])]


@pytest.mark.parametrize('fault', ['missing_interval', 'missing_file', 'unpaired', 'changed_manifest'])
def test_partial_or_stale_pair_fails(paired_manifest, fault):
    manifest, receipt, path, verified = paired_manifest
    if fault == 'missing_interval':
        manifest['intervals'].pop()
    elif fault == 'missing_file':
        manifest['files'].pop(next(iter(manifest['files'])))
    elif fault == 'unpaired':
        receipt['independent_recomputation'] = False
    else:
        path.write_text('{"changed":true}')
    with pytest.raises(RuntimeError, match='370'):
        consumer.verify_manifest(manifest, receipt, path)
    assert not verified


def test_local_record_requires_identical_frames_sources_and_actual_midpoint(tmp_path):
    path = tmp_path/'point.npz'
    path.write_bytes(b'fixture')
    source = dict(inputs={'frame': 'normalized'}, raw_inputs={'frame': 'raw'},
                  causal_maps_SHA256='maps', axes_SHA256='axes')
    record = dict(algorithm=consumer.local.ALGORITHM,
        scope='FIXED_FRAME_DIRECT_PHYSICAL_HS_LOCAL_NEWTON_DEFECT', interval=13,
        precision_bits=512, initial_endpoint_fixed=False, actual_physical_HS_midpoint_DF_used=True,
        validation_passed=True, inputs=copy.deepcopy(source['inputs']),
        raw_input_SHA256=copy.deepcopy(source['raw_inputs']), causal_maps_SHA256='maps', axes_SHA256='axes',
        input_hash_convention='SHA256_CRLF_TO_LF_FOR_JSON_MD_PY',
        raw_input_hash_convention='SHA256_EXACT_FILE_BYTES', data_SHA256=consumer.local.df.values.sha(path))
    consumer.verify_record(record, 13, source, path)
    for key, value in [('inputs', {'frame': 'other'}), ('raw_input_SHA256', {'frame': 'other'}),
                       ('causal_maps_SHA256', 'other'), ('axes_SHA256', 'other'),
                       ('actual_physical_HS_midpoint_DF_used', False), ('initial_endpoint_fixed', True)]:
        changed = dict(record, **{key: value})
        with pytest.raises(RuntimeError, match='common operands'):
            consumer.verify_record(changed, 13, source, path)
    path.write_bytes(b'changed')
    with pytest.raises(RuntimeError):
        consumer.verify_record(record, 13, source, path)


def test_repeat_recomputes_and_preserves_mismatch(tmp_path, monkeypatch):
    result = tmp_path/'result.json'
    monkeypatch.setattr(consumer, 'RESULT', result)
    calls = []
    payload = dict(response=dict(frozen_inverse_linear_defect_bounds_upper=[[1, 2], [3, 4]]))
    def build(progress):
        calls.append(True)
        return payload
    monkeypatch.setattr(consumer, 'build_payload', build)
    monkeypatch.setattr(consumer.sys, 'argv', ['consumer'])
    consumer.main()
    original = result.read_bytes()
    monkeypatch.setattr(consumer.sys, 'argv', ['consumer', '--recompute'])
    consumer.main()
    assert len(calls) == 2
    receipt = result.with_suffix('.reproduction.json')
    assert json.loads(receipt.read_text())['independent_recomputation']
    payload['changed'] = True
    with pytest.raises(ArithmeticError, match='both results preserved'):
        consumer.main()
    assert len(calls) == 3 and result.read_bytes() == original
    assert json.loads(result.with_suffix('.repeat_candidate.json').read_text())['changed']
