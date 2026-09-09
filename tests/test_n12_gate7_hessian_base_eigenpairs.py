from contextlib import contextmanager
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pytest
from flint import arb

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('hessian_base_test', ROOT/'scripts/certify_n12_gate7_hessian_base_eigenpairs.py')
producer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(producer)


@pytest.fixture
def base_campaign(tmp_path, monkeypatch):
    monkeypatch.setattr(producer, 'ROOT', tmp_path)
    monkeypatch.setattr(producer, 'WORK', tmp_path/'proof')
    monkeypatch.setattr(producer, 'proof_sources', lambda: {})
    raw = tmp_path/'raw'
    raw.mkdir()
    binding = dict(sources={}, original_provenance={}, precision_bits=256)
    (raw/'binding.json').write_text(json.dumps(binding))
    for i in range(99):
        for ext in ('npz', 'json'):
            (raw/f'row_{i:03d}.{ext}').write_bytes(b'test row')
    calls = []
    values = dict(state=np.array([1.]), reference=np.array([1.]))
    jets = SimpleNamespace(hessian_arb=np.array([[arb(1)]], dtype=object), hessian_mid=np.array([[1.]]))
    cert = SimpleNamespace(QDIM=0, _arb_action_jets=lambda state: jets,
        _eigenline=lambda *args: (np.array([arb(1)], dtype=object), arb(1), 1., 0.))
    def assemble(directory, fingerprint):
        for i in range(99):
            for ext in ('npz', 'json'):
                if not (directory/f'row_{i:03d}.{ext}').exists():
                    raise RuntimeError('missing Hessian row')
        return None, None, [{} for _ in range(99)]
    campaign = SimpleNamespace(PRECISION=256, CONTEXT='old', graph=SimpleNamespace(cert=cert),
        load_inputs=lambda index: (values, binding, 'fingerprint'), point_directory=lambda index: raw,
        sha=producer.sha, cache=SimpleNamespace(assemble_rows=assemble),
        prepare_worker=lambda *args: calls.append(args))
    monkeypatch.setattr(producer, 'install', lambda backend: campaign)
    @contextmanager
    def verify(cert, checks, *, expected_index):
        assert expected_index == 24
        checks.append(dict(validation_passed=True, selected_zero_based_index_verified=24,
            spectral_index_verification=dict(validation_passed=True)))
        yield
    monkeypatch.setattr(producer.hs, 'verified_eigenline', verify)
    return raw, calls, campaign


def test_requires_complete_rows_before_base_evaluation(base_campaign):
    raw, calls, _ = base_campaign
    (raw/'row_098.npz').unlink()
    with pytest.raises(RuntimeError, match='missing Hessian row'):
        producer.worker('bulk', 13, 'fingerprint', {})
    assert calls == []


def test_recompute_reconstructs_base_and_preserves_equal_scientific_evidence(base_campaign):
    _, calls, campaign = base_campaign
    producer.worker('bulk', 13, 'fingerprint', {})
    assert producer.worker('bulk', 13, 'fingerprint', {})['reused']
    assert len(calls) == 1
    result = producer.worker('bulk', 13, 'fingerprint', {}, recompute=True)
    assert result['independently_reproduced']
    assert len(calls) == 2 and campaign.CONTEXT is None


def test_changed_base_reproduction_preserves_original_and_candidate(base_campaign):
    _, _, campaign = base_campaign
    producer.worker('bulk', 13, 'fingerprint', {})
    path = producer.WORK/'bulk/midpoint_013.npz'
    original = path.read_bytes()
    campaign.graph.cert._eigenline = lambda *args: (np.array([arb(1)], dtype=object), arb(2), 1., 0.)
    with pytest.raises(ArithmeticError, match='reproduction differs'):
        producer.worker('bulk', 13, 'fingerprint', {}, recompute=True)
    assert path.read_bytes() == original
    assert path.with_suffix('.partial.npz').exists()
    assert path.with_suffix('.repeat_mismatch.json').exists()


def test_missing_index_evidence_cannot_be_reused(base_campaign):
    producer.worker('bulk', 13, 'fingerprint', {})
    path = producer.WORK/'bulk/midpoint_013.json'
    record = json.loads(path.read_text())
    del record['eigenpair_verification']['spectral_index_verification']
    path.write_text(json.dumps(record))
    with pytest.raises(RuntimeError, match='cache binding failed'):
        producer.worker('bulk', 13, 'fingerprint', {})


def test_changed_proof_source_blocks_base_evaluation(base_campaign, monkeypatch):
    _, calls, _ = base_campaign
    monkeypatch.setattr(producer, 'proof_sources', lambda: {'primitive': 'new'})
    with pytest.raises(RuntimeError, match='proof source changed'):
        producer.worker('bulk', 13, 'fingerprint', {'primitive': 'old'})
    assert calls == []
