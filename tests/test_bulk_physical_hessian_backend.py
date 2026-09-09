from contextlib import contextmanager
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import derive_n12_gate7_bulk_physical_hessian_errors as backend


def test_bulk_binding_retains_factored_sources_and_uses_new_fingerprint(monkeypatch):
    def original(index):
        return {'state': 'unchanged'}, dict(algorithm='factored', interval=index,
            arrays={'state': 'same'}, sources={'existing_source': 'same'}), 'old'
    monkeypatch.setattr(backend.factored, 'load_inputs', original)
    values, binding, fingerprint = backend.load_inputs(13)
    assert values == {'state': 'unchanged'}
    assert binding['arrays'] == {'state': 'same'}
    assert binding['sources']['existing_source'] == 'same'
    assert 'src/bhsm/interface/bulk_arb_matrices.py' in binding['sources']
    assert binding['algorithm'] == backend.ALGORITHM
    assert fingerprint != 'old' and fingerprint == backend.load_inputs(13)[2]


def test_base_jets_are_prepared_before_conversion_adapter(monkeypatch):
    events = []
    monkeypatch.setattr(backend, 'install_backend', lambda: None)
    monkeypatch.setattr(backend.campaign, 'prepare_worker', lambda *a: events.append('base'))
    @contextmanager
    def adapter(module):
        events.append('install')
        try:
            yield
        finally:
            events.append('restore')
    monkeypatch.setattr(backend.bulk, 'use_bulk_matrices', adapter)
    monkeypatch.setattr(backend.factored, 'worker', lambda *a: events.append('compute') or 'result')
    assert backend.worker(13, 0, 'binding') == 'result'
    assert events == ['base', 'install', 'compute', 'restore']
