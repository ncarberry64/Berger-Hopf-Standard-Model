import importlib.util
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('direct_residual_consumer_test', ROOT/'scripts/certify_n12_gate7_direct_physical_residual.py')
consumer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(consumer)


@pytest.fixture
def claimed_campaign(tmp_path, monkeypatch):
    monkeypatch.setattr(consumer, 'ROOT', tmp_path)
    work = tmp_path/'values'
    work.mkdir()
    monkeypatch.setattr(consumer.values, 'WORK', work)
    manifest = dict(endpoints=list(range(371)), midpoints=list(range(370)), all_741_values_covered=True, files={})
    receipt = dict(byte_identical=True, independent_recomputation=True, points=741)
    def save():
        path = work/'manifest.json'
        path.write_text(json.dumps(manifest))
        receipt['manifest_SHA256'] = consumer.values.sha(path)
        (work/'reproduction.json').write_text(json.dumps(receipt))
    return manifest, receipt, save


def test_coverage_flag_does_not_replace_actual_complete_point_list(claimed_campaign):
    manifest, _, save = claimed_campaign
    manifest['midpoints'].remove(13)
    save()
    with pytest.raises(RuntimeError, match='all 741'):
        consumer.load_all_values()


def test_cache_reuse_receipt_does_not_count_as_independent_reproduction(claimed_campaign):
    _, receipt, save = claimed_campaign
    receipt['independent_recomputation'] = False
    save()
    with pytest.raises(RuntimeError, match='all 741'):
        consumer.load_all_values()


def test_complete_point_list_does_not_replace_full_file_inventory(claimed_campaign):
    _, _, save = claimed_campaign
    save()
    with pytest.raises(RuntimeError, match='file inventory'):
        consumer.load_all_values()


def test_common_operand_bindings_cannot_be_overwritten():
    existing = {'input': 'A'}
    with pytest.raises(RuntimeError, match='inconsistent residual source'):
        consumer.merge(existing, {'input': 'B'})
    assert existing == {'input': 'A'}


@pytest.fixture
def crlf_source(tmp_path, monkeypatch):
    monkeypatch.setattr(consumer, 'ROOT', tmp_path)
    monkeypatch.setattr(consumer.values, 'ROOT', tmp_path)
    path = tmp_path/'source.py'
    path.write_bytes(b'x = 1\r\n')
    return path


def test_raw_and_normalized_hashes_are_retained_as_distinct_attestations(crlf_source):
    path=crlf_source
    normalized={'source.py':consumer.center._sha(path)}
    raw={}
    supplied={'source.py':consumer.values.sha(path)}
    assert supplied['source.py'] != normalized['source.py']
    consumer.merge_verified_raw_sources(normalized,raw,supplied)
    assert raw==supplied
    assert normalized['source.py']==consumer.center._sha(path)


def test_line_ending_change_does_not_bypass_raw_byte_attestation(crlf_source):
    path=crlf_source
    normalized={'source.py':consumer.center._sha(path)}
    supplied={'source.py':consumer.values.sha(path)}
    path.write_bytes(b'x = 1\n')
    assert normalized['source.py']==consumer.center._sha(path)
    raw={}
    with pytest.raises(RuntimeError,match='input changed'):
        consumer.merge_verified_raw_sources(normalized,raw,supplied)
    assert not raw


def test_semantic_source_change_cannot_replace_legacy_binding(crlf_source):
    path=crlf_source
    normalized={'source.py':consumer.center._sha(path)}
    original=dict(normalized)
    path.write_bytes(b'x = 2\r\n')
    raw={}
    with pytest.raises(RuntimeError,match='inconsistent residual source'):
        consumer.merge_verified_raw_sources(normalized,raw,{'source.py':consumer.values.sha(path)})
    assert normalized==original and not raw


def test_conflicting_raw_attestation_cannot_be_replaced(crlf_source):
    path=crlf_source
    normalized={'source.py':consumer.center._sha(path)}
    raw={'source.py':'PRIOR_DIGEST'}
    with pytest.raises(RuntimeError,match='inconsistent residual source'):
        consumer.merge_verified_raw_sources(normalized,raw,{'source.py':consumer.values.sha(path)})
    assert raw=={'source.py':'PRIOR_DIGEST'}
