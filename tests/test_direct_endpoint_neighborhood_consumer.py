import json
import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import derive_n12_gate7_direct_endpoint_neighborhoods as producer


@pytest.fixture
def setup(monkeypatch, tmp_path):
    calls = []
    def payload():
        calls.append(True)
        return {'weighted_box_mid_q': np.array(['1'])}, dict(
            algorithm=producer.ALGORITHM, uniform_endpoint_rates_enclosed=False, FULL_BHSM_COMPLETE=False)
    monkeypatch.setattr(producer, 'WORK', tmp_path)
    monkeypatch.setattr(producer, 'build_payload', payload)
    monkeypatch.setattr(sys, 'argv', ['producer'])
    return tmp_path, calls


def test_repeat_actually_rebuilds_and_attests_same_bytes(setup, monkeypatch):
    path, calls = setup
    producer.main()
    before = (path/'endpoints.npz').read_bytes(), (path/'endpoints.json').read_bytes()
    monkeypatch.setattr(sys, 'argv', ['producer', '--recompute'])
    producer.main()
    assert len(calls) == 2
    assert before == ((path/'endpoints.npz').read_bytes(), (path/'endpoints.json').read_bytes())
    receipt = json.loads((path/'reproduction.json').read_text())
    assert receipt['byte_identical'] and receipt['independent_recomputation']
    assert receipt['record_SHA256'] == producer.df.values.sha(path/'endpoints.json')
    assert not receipt['uniform_endpoint_rates_enclosed']


def test_changed_repeat_preserves_candidate_and_archives_previous_receipt(setup, monkeypatch):
    path, _ = setup
    producer.main()
    monkeypatch.setattr(sys, 'argv', ['producer', '--recompute'])
    producer.main()
    monkeypatch.setattr(producer, 'build_payload', lambda: ({'weighted_box_mid_q': np.array(['2'])}, {}))
    with pytest.raises(ArithmeticError, match='differs'):
        producer.main()
    assert not (path/'reproduction.json').exists()
    assert len(list(path.glob('reproduction.before_attempt_*.json'))) == 1
    assert len(list(path.glob('endpoints.candidate_*.npz'))) == 1
    assert len(list(path.glob('endpoints.candidate_*.json'))) == 1


def test_corrupted_first_evidence_prevents_repeat(setup, monkeypatch):
    path, calls = setup
    producer.main()
    (path/'endpoints.npz').write_bytes(b'changed')
    monkeypatch.setattr(sys, 'argv', ['producer', '--recompute'])
    with pytest.raises(RuntimeError, match='changed'):
        producer.main()
    assert len(calls) == 1


def test_no_accidental_overwrite_or_repeat_without_evidence(setup, monkeypatch):
    _, calls = setup
    monkeypatch.setattr(sys, 'argv', ['producer', '--recompute'])
    with pytest.raises(RuntimeError, match='previous'):
        producer.main()
    assert calls == []
    monkeypatch.setattr(sys, 'argv', ['producer'])
    producer.main()
    with pytest.raises(RuntimeError, match='explicit independent repeat'):
        producer.main()
