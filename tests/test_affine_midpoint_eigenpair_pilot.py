"""Check complete signed product-domain routing and midpoint provenance."""
from contextlib import nullcontext
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import numpy as np
import pytest
from flint import arb

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_affine_midpoint_eigenpair_pilot as pilot


def test_all_249_signed_columns_reach_the_complete_action_contraction(monkeypatch):
    calls=[]
    def action(state,legs,maps):
        left,middle,right=legs
        assert maps=='bound parent maps' and right.shape==(98,1,249)
        calls.append(left.shape[1])
        return left[37]*middle[37]*right[37]
    cert=SimpleNamespace(_contracted_action=action)
    monkeypatch.setattr(pilot.p.values,'cert',cert)
    monkeypatch.setattr(pilot.p.df.sparse,'use_optimized_mixed',lambda cert:nullcontext())
    monkeypatch.setattr(pilot.affine.factored,'use_ball_factored_integrand',lambda cert,state:nullcontext())
    left=np.full((98,62),arb(0));left[37]=[arb(i-31) for i in range(62)]
    middle=np.full(98,arb(0));middle[37]=arb(2)
    directions=np.full((98,249),arb(0));directions[37]=[arb(i+1) for i in range(249)]
    result=pilot.contract_rows(np.full(98,arb(0)),left,middle,directions,'bound parent maps',None,'test')
    assert result.shape==(62,249) and sum(calls)==62
    assert result[0,-1]==-31*2*249 and result[-1,-1]==30*2*249


def test_center_only_midpoint_cannot_substitute_for_actual_domain(tmp_path,monkeypatch):
    monkeypatch.setattr(pilot.midpoint,'WORK',tmp_path)
    monkeypatch.setattr(pilot.midpoint,'load_inputs',lambda index:dict(binding={}))
    directory=tmp_path/'interval_013';directory.mkdir()
    data=directory/'domain.npz';data.write_bytes(b'unread invalid array fixture')
    record=dict(binding={},algorithm=pilot.midpoint.ALGORITHM,interval=13,
        actual_HS_midpoint_image_enclosed=False,uniform_endpoint_fields_independently_paired=True,
        data_SHA256=pilot.p.values.sha(data))
    path=directory/'record.json';path.write_bytes(pilot.p.geometry.encoded(record))
    (directory/'reproduction.json').write_text(json.dumps(dict(record_SHA256=pilot.p.values.sha(path),
        byte_identical=True,independent_recomputation=True)))
    with pytest.raises(RuntimeError,match='paired actual'):pilot.load_inputs(13)
