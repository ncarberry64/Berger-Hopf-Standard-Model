"""Domain routing and repeat discipline; fixtures are not BHSM evidence."""
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
import sys
import json
import numpy as np
import pytest
from flint import arb,ctx

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_affine_action_hessian_pilot as p


@pytest.fixture
def source():
    previous=ctx.prec
    ctx.prec=512
    frame=np.zeros((99,2));frame[37,0]=1;frame[38,1]=1
    tube=p.affine.endpoint_tube(np.zeros(99),frame,[1,1],10,.001,np.ones(98))
    yield dict(tube=tube,binding={},index=13,reference=np.eye(61)[24])
    ctx.prec=previous


def test_evaluator_uses_transverse_base_and_full_signed_action_leg(source,monkeypatch):
    calls=[]
    a=np.zeros(98,dtype=int);a[37]=1;a[38]=-1
    def jets(state):
        assert all(float(v.rad()) < .002 for v in state)
        d=state[37]-state[38]
        h=np.array([[arb(int(i==j)*(i+1))+d*int(a[i]*a[j]) for j in range(98)] for i in range(98)],dtype=object)
        return SimpleNamespace(hessian_arb=h,dense_maps=['bound parent maps'])
    def contracted(state,legs,maps):
        assert float(state[37].rad()) > 9
        assert maps==['bound parent maps']
        left,right,u=legs
        assert u[37,0,0]==1 and u[38,0,0]==1
        # D3 of (x37-x38)^3/6, contracting signed legs before hulls.
        result=(left[37]-left[38])*(right[37]-right[38])*(u[37]-u[38])
        calls.append(left.shape[1])
        return result
    cert=SimpleNamespace(STATE=98,QDIM=37,REDUCED=61,_arb_action_jets=jets,_contracted_action=contracted)
    monkeypatch.setattr(p.pilot.values,'cert',cert)
    monkeypatch.setattr(p.pilot.df.sparse,'use_optimized_mixed',lambda cert:nullcontext())
    monkeypatch.setattr(p.factored,'use_ball_factored_integrand',lambda cert,state:nullcontext())
    def fail(*args,**kwargs):
        error=ArithmeticError('synthetic inclusion failure')
        error.eigenpair_inclusion=dict(validation_passed=False)
        raise error
    monkeypatch.setattr(p.pilot.proposal,'propose',fail)
    arrays,report=p.evaluate(source)
    assert sum(calls)==61 and len(calls)==16
    assert all(v.is_zero() for v in arrays['signed_longitudinal_third'].flat)
    assert all(a.contains(b) for a,b in zip(arrays['affine_tube_hessian'].flat,arrays['transverse_base_hessian'].flat))
    assert not report['validation_passed']
    assert report['eigenpair_inclusion']==dict(validation_passed=False)


def test_complete_failed_matrix_repeats_but_cannot_become_rate_certificate(source,tmp_path,monkeypatch):
    monkeypatch.setattr(p,'WORK',tmp_path)
    monkeypatch.setattr(p,'load_inputs',lambda index:source)
    monkeypatch.setattr(p.pilot,'verify_sources',lambda binding:None)
    calls=[]
    def evaluate(source,progress):
        calls.append(True)
        arrays={key:np.full((61,61),arb(1,'.01')) for key in
                ('transverse_base_hessian','signed_longitudinal_third','affine_tube_hessian')}
        arrays.update({key:value for key,value in source['tube'].items() if isinstance(value,np.ndarray)})
        return arrays,dict(validation_passed=False,error='fixture')
    monkeypatch.setattr(p,'evaluate',evaluate)
    monkeypatch.setattr(sys,'argv',['pilot','--endpoint','13'])
    p.main()
    record_path=tmp_path/'endpoint_013/record.json'
    first=record_path.read_bytes()
    monkeypatch.setattr(sys,'argv',['pilot','--endpoint','13','--recompute'])
    p.main()
    assert len(calls)==2 and record_path.read_bytes()==first
    record=json.loads(first)
    assert not record['report']['validation_passed']
    assert not record['uniform_physical_rate_enclosed']
    assert not record['full_coordinate_box_certified']
    receipt=json.loads((record_path.parent/'reproduction.json').read_bytes())
    assert receipt['byte_identical'] and receipt['independent_recomputation']


def test_failed_action_evaluation_retains_attempted_domain(source,tmp_path,monkeypatch):
    monkeypatch.setattr(p,'WORK',tmp_path)
    monkeypatch.setattr(p,'load_inputs',lambda index:source)
    def fail(*args):raise ArithmeticError('third derivative unresolved')
    monkeypatch.setattr(p,'evaluate',fail)
    monkeypatch.setattr(sys,'argv',['pilot','--endpoint','13'])
    with pytest.raises(ArithmeticError,match='unresolved'):p.main()
    directory=tmp_path/'endpoint_013'
    assert not (directory/'record.json').exists()
    attempt=next(directory.glob('attempt_*.json'))
    assert 'unresolved' in json.loads(attempt.read_bytes())['error']
    with np.load(attempt.with_suffix('.npz')) as arrays:
        assert arrays['raw_segment_hull_mid_q'].shape==(99,)
