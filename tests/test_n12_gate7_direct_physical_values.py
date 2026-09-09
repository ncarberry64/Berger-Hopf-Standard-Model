import importlib.util
from pathlib import Path
from types import SimpleNamespace
import json
import numpy as np
import pytest
from flint import arb

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('direct_values_test', ROOT/'scripts/derive_n12_gate7_direct_physical_values.py')
producer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(producer)


@pytest.fixture
def tiny_campaign(tmp_path, monkeypatch):
    monkeypatch.setattr(producer, 'ROOT', tmp_path)
    work = tmp_path/'work'
    work.mkdir()
    monkeypatch.setattr(producer, 'WORK', work)
    expected = dict(files={}, algorithm='TEST_ONLY')
    monkeypatch.setattr(producer, 'binding', lambda: expected)
    x = np.ones((371, 98))
    weights = np.ones(98)
    monkeypatch.setattr(producer, 'operands', lambda: (x, weights, np.ones(371), np.ones(61), np.ones(370)))
    calls = []
    from contextlib import contextmanager
    @contextmanager
    def verified(cert, checks, *, expected_index, normalize_proposal_center):
        assert expected_index == 24
        assert normalize_proposal_center is True
        checks.append(dict(validation_passed=True, selected_zero_based_index_verified=24,
                           spectral_index_verification=dict(validation_passed=True)))
        yield
    monkeypatch.setattr(producer.hs, 'verified_eigenline', verified)
    def rate(state, descriptor, weights, reference, directions):
        calls.append(state)
        return SimpleNamespace(value=np.array([arb(1)]*99, dtype=object))
    monkeypatch.setattr(producer.cert, '_rate_enclosure', rate)
    return expected, work, calls


def test_independent_recompute_evaluates_again_and_requires_identical_records(tiny_campaign):
    expected, work, calls = tiny_campaign
    producer.worker('endpoint', 0, expected)
    before = {p.name: p.read_bytes() for p in work.iterdir()}
    assert producer.worker('endpoint', 0, expected)['reused']
    assert len(calls) == 1
    assert producer.worker('endpoint', 0, expected, recompute=True)['independently_reproduced']
    assert len(calls) == 2
    assert before == {p.name: p.read_bytes() for p in work.iterdir()}


def test_corrupted_cache_is_rejected_before_reuse(tiny_campaign):
    expected, work, calls = tiny_campaign
    producer.worker('endpoint', 0, expected)
    with (work/'endpoint_000.npz').open('ab') as stream:
        stream.write(b'changed')
    with pytest.raises(RuntimeError, match='cache binding'):
        producer.worker('endpoint', 0, expected)
    assert len(calls) == 1


def test_changed_reproduction_preserves_both_candidates(tiny_campaign, monkeypatch):
    expected, work, _ = tiny_campaign
    producer.worker('endpoint', 0, expected)
    before = (work/'endpoint_000.npz').read_bytes()
    monkeypatch.setattr(producer.cert, '_rate_enclosure', lambda *args: SimpleNamespace(value=np.array([arb(2)]*99)))
    with pytest.raises(ArithmeticError, match='reproduction differs'):
        producer.worker('endpoint', 0, expected, recompute=True)
    assert (work/'endpoint_000.npz').read_bytes() == before
    assert (work/'endpoint_000.partial.npz').is_file()
    assert (work/'endpoint_000.repeat_mismatch.json').is_file()


def test_midpoint_requires_both_new_endpoints_and_records_them(tiny_campaign):
    expected, work, calls = tiny_campaign
    producer.worker('endpoint', 0, expected)
    with pytest.raises(FileNotFoundError):
        producer.worker('midpoint', 0, expected)
    producer.worker('endpoint', 1, expected)
    producer.worker('midpoint', 0, expected)
    record = json.loads((work/'midpoint_000.json').read_text())
    assert len(record['dependencies']) == 4
    assert record['midpoint_Taylor_truncation_used'] is False
    assert record['legacy_endpoint_value_cache_used'] is False
    assert record['physical_Y_recertified'] is False
    assert all(isinstance(v, arb) for v in calls[-1])
