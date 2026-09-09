"""Numerical row/cache and campaign boundary tests using explicit fixtures."""
from concurrent.futures import Future
from contextlib import nullcontext
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import numpy as np
import pytest
from flint import arb

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('direct_hessian_campaign_test',
    ROOT/'scripts/derive_n12_gate7_direct_physical_hessians.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)


@pytest.fixture
def row_campaign(tmp_path,monkeypatch):
    monkeypatch.setattr(p,'WORK',tmp_path)
    expected=dict(files={},kernel_files={},algorithm='TEST_ONLY')
    context=dict(state=np.ones(98),descriptor=arb(1),weights=np.ones(98),reference=np.ones(61),dependencies={})
    proof=dict(validation_passed=True,selected_zero_based_index_verified=24,
        spectral_index_verification=dict(validation_passed=True),
        positive_stored_reference_overlap=True,proposal_center_normalized_before_verification=True)
    prepared=SimpleNamespace(use=lambda:nullcontext(),eigenpair_verification=proof)
    monkeypatch.setattr(p,'point_context',lambda *a:context)
    monkeypatch.setattr(p,'prepare',lambda *a:prepared)
    monkeypatch.setattr(p.df.sparse,'use_optimized_mixed',lambda *a:nullcontext())
    monkeypatch.setattr(p.bulk,'use_bulk_matrices',lambda *a:nullcontext())
    monkeypatch.setattr(p.factored,'use_ball_factored_integrand',lambda *a:nullcontext())
    calls=[]
    def evaluate(state,descriptor,weights,reference,axis,directions):
        row=next(i for i,v in enumerate(axis) if v==1)
        assert directions.shape==(99,99-row)
        assert all(isinstance(v,arb) and v.is_exact() for v in directions.flat)
        assert all(directions[i,j]==int(i==j+row) for i,j in np.ndindex(directions.shape))
        calls.append(row)
        return np.array([[arb(i+j+row, .125) for j in range(99-row)] for i in range(99)],dtype=object)
    monkeypatch.setattr(p.graph,'batched_axis_map',evaluate)
    directory=p.point_directory('midpoint',13);directory.mkdir()
    return expected,context,directory,calls


def test_restart_reuses_row_and_independent_repeat_recomputes_identical_bytes(row_campaign):
    expected,_,directory,calls=row_campaign
    p.worker('midpoint',13,97,expected)
    first={path.name:path.read_bytes() for path in directory.iterdir()}
    assert p.worker('midpoint',13,97,expected)['reused']
    assert calls==[97]
    assert p.worker('midpoint',13,97,expected,True)['independently_reproduced']
    assert calls==[97,97]
    assert first=={path.name:path.read_bytes() for path in directory.iterdir()}


def test_changed_repeat_preserves_every_candidate(row_campaign,monkeypatch):
    expected,_,directory,_=row_campaign
    p.worker('midpoint',13,98,expected)
    original=(directory/'row_098.npz').read_bytes()
    monkeypatch.setattr(p.graph,'batched_axis_map',lambda *a:np.full((99,1),arb(999),dtype=object))
    for _ in range(2):
        with pytest.raises(ArithmeticError,match='candidates preserved'):
            p.worker('midpoint',13,98,expected,True)
    assert (directory/'row_098.npz').read_bytes()==original
    assert len(list(directory.glob('row_098.candidate_*.npz')))==2
    assert len(list(directory.glob('row_098.candidate_*.json')))==2


def test_partial_nonfinite_or_missing_repeat_row_fails(row_campaign,monkeypatch):
    expected,_,directory,_=row_campaign
    with pytest.raises(RuntimeError,match='prior evidence'):
        p.worker('midpoint',13,98,expected,True)
    for bad in (np.full((99,2),arb(0),dtype=object),np.full((99,1),arb('nan'),dtype=object)):
        monkeypatch.setattr(p.graph,'batched_axis_map',lambda *a:bad)
        with pytest.raises(ArithmeticError,match='nonfinite'):
            p.worker('midpoint',13,98,expected)
    assert not (directory/'row_098.npz').exists()


@pytest.mark.parametrize('change',['data','dependencies','proof','format'])
def test_changed_evidence_is_rejected_before_reuse(row_campaign,change):
    expected,context,directory,calls=row_campaign
    p.worker('midpoint',13,98,expected)
    record_path=directory/'row_098.json';record=json.loads(record_path.read_text())
    if change=='data':
        with (directory/'row_098.npz').open('ab') as stream:stream.write(b'changed')
    elif change=='dependencies':context['dependencies']={'changed':'source'}
    elif change=='format':record_path.write_bytes(b' '+record_path.read_bytes())
    else:
        record['eigenpair_verification']['positive_stored_reference_overlap']=False
        p.write_json(record_path,record)
    with pytest.raises(RuntimeError,match='binding'):
        p.worker('midpoint',13,98,expected)
    assert calls==[98]


def test_source_change_during_evaluation_cannot_publish_a_row(row_campaign,monkeypatch,tmp_path):
    expected,_,directory,_=row_campaign
    source=tmp_path/'kernel.py';source.write_text('original')
    expected['kernel_files']={str(source):p.df.values.sha(source)}
    def evaluate(*args):
        source.write_text('changed')
        return np.full((99,1),arb(1),dtype=object)
    monkeypatch.setattr(p.graph,'batched_axis_map',evaluate)
    with pytest.raises(RuntimeError,match='input changed'):
        p.worker('midpoint',13,98,expected)
    assert not (directory/'row_098.npz').exists()


def test_prepare_reuses_verified_base_and_requires_paired_value_overlap(monkeypatch):
    calls=[]
    prepared=SimpleNamespace(use=lambda:nullcontext())
    def construct(*args):
        calls.append(True)
        return prepared
    monkeypatch.setattr(p.base,'VerifiedHessianBase',construct)
    monkeypatch.setattr(p.df.sparse,'use_optimized_mixed',lambda *a:nullcontext())
    monkeypatch.setattr(p.graph.cert,'_rate_enclosure',lambda *a:SimpleNamespace(value=[arb(1)]*99))
    context=dict(prepared=None,state=np.ones(98),descriptor=arb(1),weights=np.ones(98),
                 reference=np.ones(61),value=[arb(1)]*99)
    assert p.prepare(context) is prepared and p.prepare(context) is prepared
    assert len(calls)==1
    context['prepared']=None;context['value']=[arb(2)]*99
    with pytest.raises(ArithmeticError,match='paired direct value'):p.prepare(context)
    assert context['prepared'] is None


def test_manifest_requires_every_row_and_exact_inventory(row_campaign,monkeypatch):
    expected,context,directory,_=row_campaign
    seen=[]
    # Virtual numerical rows isolate the complete-inventory boundary here.
    def load(stage,index,row,binding,dependencies):
        assert binding==expected and dependencies==context['dependencies']
        assert (directory/f'row_{row:03d}.npz').exists()
        seen.append(row)
    monkeypatch.setattr(p,'load_row',load)
    monkeypatch.setattr(p.df,'file_key',lambda path:path.name)
    for row in range(99):
        for ext in ('json','npz'):(directory/f'row_{row:03d}.{ext}').write_bytes(b'fixture')
    manifest=p.complete_manifest('midpoint',13,expected,{})
    assert seen==list(range(99)) and len(manifest['files'])==198
    assert manifest['complete_point_ambient_Hessian'] and not manifest['FULL_BHSM_COMPLETE']
    (directory/'row_050.npz').unlink()
    with pytest.raises(AssertionError):p.complete_manifest('midpoint',13,expected,{})


def test_repeat_uses_spawn_and_revokes_current_receipt_until_success(row_campaign,monkeypatch):
    expected,context,directory,_=row_campaign
    manifest=dict(test_only=True)
    p.write_json(directory/'manifest.json',manifest)
    p.write_json(directory/'reproduction.json',dict(previous_success=True))
    monkeypatch.setattr(p,'binding',lambda:expected)
    monkeypatch.setattr(p,'complete_manifest',lambda *a:manifest)
    monkeypatch.setattr(sys,'argv',['campaign','--stage','midpoint','--index','13','--recompute'])
    observed=[]
    class Executor:
        def __init__(self,*,max_workers,mp_context):
            assert max_workers==6 and mp_context.get_start_method()=='spawn'
            assert not (directory/'reproduction.json').exists()
        def submit(self,function,stage,index,row,binding,recompute):
            observed.append((row,recompute))
            future=Future();future.set_result(dict(row=row,independently_reproduced=True))
            return future
        def shutdown(self,**kwargs):pass
    monkeypatch.setattr(p,'ProcessPoolExecutor',Executor)
    p.main()
    assert observed==[(i,True) for i in range(99)]
    assert len(list(directory.glob('reproduction.before_attempt_*.json')))==1
    receipt=json.loads((directory/'reproduction.json').read_text())
    assert receipt['independent_recomputation'] and receipt['rows']==list(range(99))


def test_failed_repeat_preserves_prior_receipt_as_history(row_campaign,monkeypatch):
    expected,_,directory,_=row_campaign
    manifest=dict(test_only=True)
    p.write_json(directory/'manifest.json',manifest)
    p.write_json(directory/'reproduction.json',dict(previous_success=True))
    monkeypatch.setattr(p,'binding',lambda:expected)
    monkeypatch.setattr(p,'complete_manifest',lambda *a:manifest)
    monkeypatch.setattr(sys,'argv',['campaign','--stage','midpoint','--index','13','--recompute'])
    class Executor:
        def __init__(self,**kwargs):pass
        def submit(self,*args):
            future=Future();future.set_exception(ArithmeticError('fixture failure'));return future
        def terminate_workers(self):pass
    monkeypatch.setattr(p,'ProcessPoolExecutor',Executor)
    with pytest.raises(ArithmeticError,match='fixture failure'):p.main()
    assert not (directory/'reproduction.json').exists()
    assert len(list(directory.glob('reproduction.before_attempt_*.json')))==1
    assert json.loads((directory.parent/'active_state.json').read_text())['terminal']


@pytest.mark.parametrize('stage,index',[('midpoint',370),('endpoint',371),('other',0),('midpoint',-1)])
def test_invalid_point_rejected(stage,index):
    with pytest.raises(ValueError):p.validate_point(stage,index)
