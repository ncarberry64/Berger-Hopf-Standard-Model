"""Physical value artifact discipline; fixtures do not certify the action."""
import json
from pathlib import Path
import sys
import numpy as np
import pytest
from flint import arb,ctx

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_affine_physical_value_pilot as pilot


@pytest.fixture
def setup(tmp_path,monkeypatch):
    previous=ctx.prec;ctx.prec=512
    source=dict(binding={},index=13,tube=dict(radius_longitudinal=arb(1)/1024,radius_transverse=arb(1)/2048))
    monkeypatch.setattr(pilot,'WORK',tmp_path)
    monkeypatch.setattr(pilot,'load_inputs',lambda index:source)
    monkeypatch.setattr(sys,'argv',['pilot','--endpoint','13'])
    yield tmp_path/'endpoint_013'
    ctx.prec=previous


def test_repeat_reexecutes_action_path_and_preserves_mismatch(setup,monkeypatch):
    calls=[]
    def evaluate(source):
        calls.append(True)
        return dict(rate_candidate=np.full(99,arb(1))),dict(validation_passed=True)
    monkeypatch.setattr(pilot,'evaluate',evaluate)
    pilot.main();first=(setup/'record.json').read_bytes()
    monkeypatch.setattr(sys,'argv',['pilot','--endpoint','13','--recompute'])
    pilot.main()
    assert len(calls)==2 and (setup/'record.json').read_bytes()==first
    assert json.loads((setup/'reproduction.json').read_bytes())['independent_recomputation']
    monkeypatch.setattr(pilot,'evaluate',lambda source:(dict(rate_candidate=np.full(99,arb(2))),dict(validation_passed=True)))
    with pytest.raises(ArithmeticError,match='differs'):pilot.main()
    assert (setup/'record.json').read_bytes()==first and not (setup/'reproduction.json').exists()
    assert list(setup.glob('value.candidate_*.npz'))


def test_nonfinite_field_failure_is_preserved_without_certificate(setup,monkeypatch):
    monkeypatch.setattr(pilot,'evaluate',lambda source:(dict(rate_candidate=np.full(99,arb('nan'))),
        dict(validation_passed=False,positive_physical_G_norm=False)))
    with pytest.raises(ArithmeticError,match='failed'):pilot.main()
    assert not (setup/'record.json').exists() and not (setup/'reproduction.json').exists()
    report=json.loads(next(setup.glob('value.candidate_*.json')).read_bytes())['report']
    assert report['rate_candidate_contains_nonfinite'] and not report['positive_physical_G_norm']


def test_unpaired_eigenpair_is_rejected_before_response_evaluation(tmp_path,monkeypatch):
    directory=tmp_path/'endpoint_013';directory.mkdir()
    monkeypatch.setattr(pilot.eq,'WORK',tmp_path)
    monkeypatch.setattr(pilot.eq,'load_inputs',lambda index:dict(binding={}))
    data=directory/'eigenpair.npz';data.write_bytes(b'unread invalid array fixture')
    record=dict(binding={},endpoint=13,algorithm=pilot.eq.ALGORITHM,data_SHA256=pilot.p.values.sha(data),
        report=dict(validation_passed=True,selected_zero_based_index_verified=24,uniform_action_eigenpair_enclosed=True))
    path=directory/'record.json';path.write_bytes(pilot.p.geometry.encoded(record))
    (directory/'reproduction.json').write_text(json.dumps(dict(record_SHA256=pilot.p.values.sha(path),
        byte_identical=True,independent_recomputation=False)))
    with pytest.raises(RuntimeError,match='paired unchanged'):pilot.load_inputs(13)
