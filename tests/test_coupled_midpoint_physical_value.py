"""Actual midpoint field routing must retain its descriptor and all directions."""
from contextlib import nullcontext
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import numpy as np
import pytest
from flint import arb

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_coupled_midpoint_physical_value as pilot


def test_signed_response_keeps_all_four_terms_and_all_249_columns():
    calls=[]
    def action(state,legs,maps):
        calls.append(len(legs))
        result=legs[0][37]*legs[-1][37]
        if len(legs)==3:result*=legs[1][37]
        return result
    directions=np.full((98,249),arb(0));directions[37]=[arb(i+1) for i in range(249)]
    left=np.full((98,62),arb(0));left[37]=[arb(i-31) for i in range(62)]
    fixed=np.full(98,arb(0));fixed[37]=arb(3)
    legs=dict(gradient_left=10*left,configuration_left=left,hessian_left=left,
        configuration=fixed,configuration_derivative=2*directions,hard=fixed/3)
    result=pilot.signed_response_derivatives(SimpleNamespace(_contracted_action=action),
        np.full(98,arb(0)),legs,directions,None)
    # 10 - 3 - 2 - 1 = 4, with signs retained on each affine direction.
    assert result.shape==(62,249) and calls==[2,3,2,3]*16
    assert result[0,-1]==-31*249*4 and result[-1,-1]==30*249*4


def test_point_descriptor_comes_from_exact_midpoint_anchor(monkeypatch):
    captured=[]
    def rate(state,descriptor,*args):
        captured.append(descriptor)
        raise ArithmeticError('intentional stop after observing point input')
    cert=SimpleNamespace(_rate_enclosure=rate,_verified_solve=object(),_eigenline=object())
    monkeypatch.setattr(pilot.p.values,'cert',cert)
    monkeypatch.setattr(pilot.p.values,'operands',lambda:(None,None,[-999]*14,None,None))
    monkeypatch.setattr(pilot.p,'verify_sources',lambda binding:None)
    monkeypatch.setattr(pilot.p.df.sparse,'use_optimized_mixed',lambda cert:nullcontext())
    monkeypatch.setattr(pilot.eq.engine.affine.factored,'use_ball_factored_integrand',lambda *a:nullcontext())
    monkeypatch.setattr(pilot.p.hs,'verified_eigenline',lambda *a,**kw:nullcontext())
    shapes=dict(eigenbox=(62,),center=(98,),rm=(62,62),eigen_center=(62,),
        directions=(98,249),radii=(62,),variation=(62,),full=(98,))
    paired={key:np.full(shape,arb(0)) for key,shape in shapes.items()}
    anchor=np.full(99,arb(0));anchor[98]=arb(1)+arb(2)**-100
    _,report=pilot.evaluate(dict(index=13,paired=paired,raw_center=anchor,raw_domain=anchor,binding={}))
    assert captured[0] is anchor[98]
    assert not report['validation_passed'] and not report['uniform_actual_HS_midpoint_field_enclosed']


def test_endpoint_eigenpair_cannot_replace_paired_midpoint(tmp_path,monkeypatch):
    monkeypatch.setattr(pilot.eq,'WORK',tmp_path)
    monkeypatch.setattr(pilot.eq,'load_inputs',lambda index:dict(binding={}))
    directory=tmp_path/'interval_013';directory.mkdir()
    record=dict(binding={},interval=13,algorithm=pilot.eq.ALGORITHM,report=dict(
        validation_passed=True,selected_zero_based_index_verified=24,
        uniform_action_eigenpair_enclosed=True,uniform_actual_HS_midpoint_eigenpair_enclosed=False))
    (directory/'record.json').write_text(json.dumps(record))
    (directory/'reproduction.json').write_text('{}')
    with pytest.raises(RuntimeError,match='paired unchanged'):pilot.load_inputs(13)
