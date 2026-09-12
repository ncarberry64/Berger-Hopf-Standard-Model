"""Repeat and failure discipline; synthetic fixtures are not physical evidence."""
import json
from pathlib import Path
import sys
import numpy as np
import pytest
from flint import arb,ctx

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_affine_eigenpair_pilot as pilot


@pytest.fixture
def setup(tmp_path,monkeypatch):
    previous=ctx.prec;ctx.prec=512
    source=dict(binding={},index=13,tube=dict(radius_longitudinal=arb(1)/1024,radius_transverse=arb(1)/2048))
    monkeypatch.setattr(pilot,'WORK',tmp_path)
    monkeypatch.setattr(pilot,'load_inputs',lambda index:source)
    monkeypatch.setattr(sys,'argv',['pilot','--endpoint','13'])
    yield tmp_path/'endpoint_013'
    ctx.prec=previous


def test_repeat_reexecutes_evaluation_and_rejects_changed_numeric_result(setup,monkeypatch):
    calls=[]
    def evaluate(source,progress):
        calls.append(True)
        return dict(eigenpair_box=np.array([arb(1)],dtype=object)),dict(validation_passed=True)
    monkeypatch.setattr(pilot,'evaluate',evaluate)
    pilot.main()
    first=(setup/'record.json').read_bytes()
    monkeypatch.setattr(sys,'argv',['pilot','--endpoint','13','--recompute'])
    pilot.main()
    assert len(calls)==2
    assert (setup/'record.json').read_bytes()==first
    assert json.loads((setup/'reproduction.json').read_bytes())['independent_recomputation']
    monkeypatch.setattr(pilot,'evaluate',lambda *args:(dict(eigenpair_box=np.array([arb(2)],dtype=object)),dict(validation_passed=True)))
    with pytest.raises(ArithmeticError,match='differs'):pilot.main()
    assert (setup/'record.json').read_bytes()==first
    assert not (setup/'reproduction.json').exists()
    assert list(setup.glob('eigenpair.candidate_*.npz'))


def test_failed_trial_preserves_bounds_without_publishing_certificate(setup,monkeypatch):
    monkeypatch.setattr(pilot,'evaluate',lambda *args:(dict(trial_0_radii=np.array([arb(1)],dtype=object)),
        dict(validation_passed=False,trials=[dict(validation_passed=False)])))
    with pytest.raises(ArithmeticError,match='proof failed'):pilot.main()
    assert not (setup/'record.json').exists() and not (setup/'reproduction.json').exists()
    candidate=next(setup.glob('eigenpair.candidate_*.json'))
    assert not json.loads(candidate.read_bytes())['report']['validation_passed']
    with np.load(candidate.with_suffix('.npz'),allow_pickle=False) as arrays:
        assert arrays['trial_0_radii_mid_q'].shape==(1,)


def test_action_failure_is_recorded_and_unverified_point_witness_rejected(setup,monkeypatch):
    def fail(*args):raise ArithmeticError('inertia does not have positive lower bound')
    monkeypatch.setattr(pilot,'evaluate',fail)
    with pytest.raises(ArithmeticError,match='inertia'):pilot.main()
    candidate=next(setup.glob('eigenpair.candidate_*.json'))
    assert 'inertia' in json.loads(candidate.read_bytes())['error']
    with pytest.raises(ArithmeticError,match='point witness'):
        pilot.witness_box(dict(validation_passed=True,selected_zero_based_index_verified=24))
