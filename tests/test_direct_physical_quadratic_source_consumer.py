import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pytest
from flint import arb

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('quadratic_consumer_test',ROOT/'scripts/certify_n12_gate7_direct_physical_quadratic_sources.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)


def source():
    return dict(inputs={},raw_inputs={},axes_SHA256='axes',causal_maps_SHA256='maps')


def test_frozen_direction_families_keep_nonunit_axes_and_fixed_initial_endpoint(monkeypatch):
    frame=np.zeros((99,74));frame[:74]=np.eye(74)*2
    monkeypatch.setattr(p.local.residual.center,'cert',SimpleNamespace(TRIAL_DESCRIPTOR_SCALE=1,_frame=lambda *args:frame))
    inputs=dict(tangents=np.zeros((371,98,73)))
    axes=np.zeros((371,74));axes[:,0]=3
    u0,u1,v0,v1=p.direction_families(13,inputs,axes,'LT','01')
    assert u0[0,0]==6 and all(v.is_zero() for v in u1.entries())
    assert v1[0,0]==2 and all(v.is_zero() for v in v0.entries())
    directions=p.direction_families(0,inputs,axes,'TT','00')
    assert all(v.is_zero() for m in directions for v in m.entries())
    with pytest.raises(ValueError):p.direction_families(13,inputs,axes,'TL','01')


@pytest.fixture
def block(tmp_path,monkeypatch):
    inputs=source();calls=[]
    def build(index,family,pair,*args):
        calls.append((index,family,pair))
        data=np.array([[arb(i,.125)] for i in range(74)],dtype=object)
        mid,rad=p.local.df.values.hs.rational_balls(data)
        return dict(Q_mid_q=mid,Q_rad_q=rad),p.metadata(index,family,pair,inputs)
    monkeypatch.setattr(p,'build_block',build)
    return tmp_path,inputs,calls


def write(block,recompute=False):
    directory,inputs,_=block
    p.write_block(directory,13,'LL','01',inputs,None,None,None,recompute)


def test_real_rational_block_repeats_with_identical_bytes_and_resumes(block):
    directory,_,calls=block
    write(block);before={f.name:f.read_bytes() for f in directory.iterdir()}
    write(block);assert len(calls)==1
    write(block,True);assert len(calls)==2
    assert before=={f.name:f.read_bytes() for f in directory.iterdir()}


def test_metadata_change_and_independent_numeric_mismatch_preserve_evidence(block,monkeypatch):
    directory,inputs,_=block;write(block)
    path=directory/'LL_01.json';original=path.read_bytes()
    record=json.loads(original);record['midpoint_second_incidence_included']=False
    p.hessian.write_json(path,record)
    with pytest.raises(RuntimeError,match='binding changed'):write(block)
    path.write_bytes(original);old_data=(directory/'LL_01.npz').read_bytes()
    def different(*args):
        data=np.full((74,1),arb(999),dtype=object)
        mid,rad=p.local.df.values.hs.rational_balls(data)
        return dict(Q_mid_q=mid,Q_rad_q=rad),p.metadata(13,'LL','01',inputs)
    monkeypatch.setattr(p,'build_block',different)
    for _ in range(2):
        with pytest.raises(ArithmeticError,match='candidates preserved'):write(block,True)
    assert (directory/'LL_01.npz').read_bytes()==old_data
    assert len(list(directory.glob('*.candidate_*.npz')))==2
    assert len(list(directory.glob('*.candidate_*.json')))==2


def test_incomplete_hessian_receipt_is_rejected_before_tensor_load(tmp_path,monkeypatch):
    manifest={'files':{}};p.hessian.write_json(tmp_path/'manifest.json',manifest)
    p.hessian.write_json(tmp_path/'reproduction.json',dict(byte_identical=True))
    monkeypatch.setattr(p.hessian,'point_directory',lambda *a:tmp_path)
    monkeypatch.setattr(p.hessian.df,'point_inputs',lambda *a:({},))
    monkeypatch.setattr(p.hessian,'complete_manifest',lambda *a:manifest)
    with pytest.raises(RuntimeError,match='independently reproduced'):
        p.verify_hessian('midpoint',13,{'value_point_binding':{}})


def test_absent_prior_block_cannot_be_reproduced(block):
    with pytest.raises(RuntimeError,match='previous source'):write(block,True)


@pytest.mark.parametrize('different_value_campaign',[False,True])
def test_hessian_derivative_point_or_value_campaign_mismatch_fails(monkeypatch,different_value_campaign):
    expected=dict(files={},value_point_binding=dict(value_binding={'id':'original'}))
    monkeypatch.setattr(p.hessian,'binding',lambda:expected)
    monkeypatch.setattr(p,'verify_hessian',lambda *a:(None,{},dict(point='Hessian point')))
    binding=dict(value_binding={'id':'changed' if different_value_campaign else 'original'})
    monkeypatch.setattr(p.local,'load_inputs',lambda *a:dict(binding=binding))
    monkeypatch.setattr(p.local.df,'point_inputs',lambda *a:(dict(point='different DF point'),))
    match='value campaigns differ' if different_value_campaign else 'physical points differ'
    with pytest.raises(RuntimeError,match=match):p.load_inputs(13)
