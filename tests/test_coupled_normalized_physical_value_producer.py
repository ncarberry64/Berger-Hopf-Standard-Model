"""Recompute normalization refinements and preserve their failed attempts."""
import json
from pathlib import Path
import sys
import numpy as np
import pytest
from flint import arb,ctx

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_coupled_normalized_physical_value as pilot


@pytest.fixture
def setup(tmp_path,monkeypatch):
    previous=ctx.prec;ctx.prec=512
    source=dict(binding={},tube=dict(radius_longitudinal=arb(1)/1024,radius_transverse=arb(1)/2048))
    monkeypatch.setattr(pilot,'WORK',tmp_path);monkeypatch.setattr(pilot,'load_inputs',lambda index:source)
    monkeypatch.setattr(sys,'argv',['pilot','--endpoint','13'])
    yield tmp_path/'endpoint_013'
    ctx.prec=previous


def test_refinement_repeat_reexecutes_computation_and_rejects_changed_value(setup,monkeypatch):
    calls=[]
    def evaluate(source):
        calls.append(True)
        arrays={key:np.full(shape,arb(1)) for key,shape in dict(rate_candidate=(99,),old_rate=(99,),
            complete_descriptor_contractions=(2,),raw_domain=(99,)).items()}
        return arrays,dict(validation_passed=True)
    monkeypatch.setattr(pilot,'evaluate',evaluate)
    pilot.main();first=(setup/'record.json').read_bytes()
    monkeypatch.setattr(sys,'argv',['pilot','--endpoint','13','--recompute']);pilot.main()
    assert len(calls)==2 and (setup/'record.json').read_bytes()==first
    assert json.loads((setup/'reproduction.json').read_bytes())['independent_recomputation']
    def changed(source):
        arrays,report=evaluate(source);arrays['rate_candidate'][0]=arb(2);return arrays,report
    monkeypatch.setattr(pilot,'evaluate',changed)
    with pytest.raises(ArithmeticError,match='differs'):pilot.main()
    assert (setup/'record.json').read_bytes()==first and not (setup/'reproduction.json').exists()


def test_unresolved_border_sign_is_retained_without_new_certificate(setup,monkeypatch):
    def fail(source):raise ArithmeticError('verified nonzero border sign required')
    monkeypatch.setattr(pilot,'evaluate',fail)
    with pytest.raises(ArithmeticError,match='border sign'):pilot.main()
    assert not (setup/'record.json').exists()
    candidate=next(setup.glob('value.candidate_*.json'))
    assert 'border sign' in json.loads(candidate.read_bytes())['error']
