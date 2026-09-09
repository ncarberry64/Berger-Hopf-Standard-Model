import importlib.util
from contextlib import contextmanager, nullcontext
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pytest
from flint import arb

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('direct_df_test',ROOT/'scripts/derive_n12_gate7_direct_physical_jacobians.py')
producer=importlib.util.module_from_spec(spec);spec.loader.exec_module(producer)


@pytest.fixture
def campaign(tmp_path,monkeypatch):
    monkeypatch.setattr(producer,'WORK',tmp_path)
    expected=dict(files={},algorithm='TEST_ONLY')
    calls=[]
    reference=np.array([arb(1)]*99,dtype=object)
    monkeypatch.setattr(producer,'point_inputs',lambda *args:(np.ones(98),arb(1),np.ones(98),np.ones(61),reference,{}))
    monkeypatch.setattr(producer.sparse,'use_optimized_mixed',lambda cert:nullcontext())
    @contextmanager
    def verify(cert,checks,*,expected_index,normalize_proposal_center):
        assert expected_index==24 and normalize_proposal_center is True
        checks.append(dict(validation_passed=True,selected_zero_based_index_verified=24,
                           spectral_index_verification=dict(validation_passed=True)))
        yield
    monkeypatch.setattr(producer.values.hs,'verified_eigenline',verify)
    def rate(state,descriptor,weights,reference,directions):
        assert directions.shape==(99,99)
        assert all(isinstance(v,arb) and v.is_exact() for v in directions.flat)
        assert all(directions[i,j]==int(i==j) for i,j in np.ndindex(directions.shape))
        calls.append(True)
        return SimpleNamespace(value=np.array([arb(1)]*99),derivative=directions)
    monkeypatch.setattr(producer.values.cert,'_rate_enclosure',rate)
    return expected,calls


def test_independent_DF_reproduction_recomputes_and_matches_all_bytes(campaign,tmp_path):
    expected,calls=campaign
    producer.worker('midpoint',13,expected)
    first={p.name:p.read_bytes() for p in tmp_path.iterdir()}
    assert producer.worker('midpoint',13,expected)['reused']
    assert len(calls)==1
    assert producer.worker('midpoint',13,expected,True)['independently_reproduced']
    assert len(calls)==2
    assert first=={p.name:p.read_bytes() for p in tmp_path.iterdir()}


def test_wrong_value_cannot_enter_DF_cache(campaign,tmp_path,monkeypatch):
    expected,_=campaign
    monkeypatch.setattr(producer.values.cert,'_rate_enclosure',lambda *args:SimpleNamespace(
        value=np.array([arb(2)]*99),derivative=np.array([arb(0)]*99**2).reshape(99,99)))
    with pytest.raises(ArithmeticError,match='overlap'):
        producer.worker('midpoint',13,expected)
    assert not (tmp_path/'midpoint_013.npz').exists()
    assert (tmp_path/'midpoint_013.partial.npz').exists()
    assert (tmp_path/'midpoint_013.candidate_failure.json').exists()


def test_changed_derivative_reproduction_preserves_both_results(campaign,tmp_path,monkeypatch):
    expected,_=campaign
    producer.worker('midpoint',13,expected)
    first=(tmp_path/'midpoint_013.npz').read_bytes()
    monkeypatch.setattr(producer.values.cert,'_rate_enclosure',lambda *args:SimpleNamespace(
        value=np.array([arb(1)]*99),derivative=np.array([arb(2)]*99**2).reshape(99,99)))
    with pytest.raises(ArithmeticError,match='reproduction'):
        producer.worker('midpoint',13,expected,True)
    assert (tmp_path/'midpoint_013.npz').read_bytes()==first
    assert (tmp_path/'midpoint_013.partial.npz').read_bytes()!=first


def test_partial_or_nonfinite_DF_fails(campaign,monkeypatch):
    expected,_=campaign
    for matrix in (np.array([[arb(1)]]),np.array([arb('nan')]*99**2).reshape(99,99)):
        monkeypatch.setattr(producer.values.cert,'_rate_enclosure',lambda *args:SimpleNamespace(
            value=np.array([arb(1)]*99),derivative=matrix))
        with pytest.raises(ArithmeticError,match='finite physical DF'):
            producer.worker('midpoint',13,expected)


def test_corrupt_derivative_cache_is_rejected_before_reuse(campaign,tmp_path):
    expected,calls=campaign
    producer.worker('midpoint',13,expected)
    with (tmp_path/'midpoint_013.npz').open('ab') as stream:stream.write(b'changed')
    with pytest.raises(RuntimeError,match='cache binding'):
        producer.worker('midpoint',13,expected)
    assert len(calls)==1
