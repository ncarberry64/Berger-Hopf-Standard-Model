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
