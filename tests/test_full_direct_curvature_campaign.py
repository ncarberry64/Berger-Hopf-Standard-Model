"""Campaign process/coverage tests; virtual inventories are not physical data."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('full_curvature_campaign_test',ROOT/'scripts/run_n12_gate7_full_direct_curvature_campaign.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)


@pytest.mark.parametrize('levels,expected',[( [0,1,2],[False,True]),([1,2],[True]),([2],[])])
def test_resume_and_repeat_only_required_stages(levels,expected):
    answers=iter(levels);calls=[]
    p.ensure_pair(lambda:(next(answers),None),calls.append)
    assert calls==expected


@pytest.mark.parametrize('levels',[[0,0],[0,2],[1,1],[3]])
def test_incomplete_or_unexpected_production_cannot_advance(levels):
    answers=iter(levels)
    with pytest.raises(RuntimeError):p.ensure_pair(lambda:(next(answers),None),lambda repeat:None)


def test_all_741_points_and_370_local_intervals_are_dependency_ordered(monkeypatch):
    seen=set();events=[]
    def point(runner,stage,index,expected):
        assert (stage,index) not in seen;seen.add((stage,index));events.append((stage,index))
    def interval(runner,index,base):
        assert {('endpoint',index),('midpoint',index),('endpoint',index+1)}<=seen
        events.append(('local',index))
    monkeypatch.setattr(p,'ensure_hessian',point);monkeypatch.setattr(p,'ensure_local',interval)
    monkeypatch.setattr(p,'state',lambda **record:None)
    p.produce_all(SimpleNamespace(sources={}),None,None)
    assert seen=={(stage,i) for stage,n in (('endpoint',371),('midpoint',370)) for i in range(n)}
    assert [i for kind,i in events if kind=='local']==list(range(370))
    assert events[:4]==[('endpoint',0),('midpoint',0),('endpoint',1),('local',0)]


def test_inventory_requires_every_paired_point_and_interval(monkeypatch):
    def point(stage,index,expected):return 2,{f'{stage}_{index}':'virtual-hash'}
    monkeypatch.setattr(p,'hessian_status',point)
    monkeypatch.setattr(p,'local_status',lambda index,base:(2,{f'local_{index}':'virtual-hash'}))
    record=p.inventory({},None,{})
    assert record['paired_Hessian_points']==741 and record['paired_local_source_intervals']==370
    assert len(record['files'])==1111
    monkeypatch.setattr(p,'hessian_status',lambda stage,index,expected:(1,{}) if (stage,index)==('endpoint',370) else point(stage,index,expected))
    with pytest.raises(RuntimeError,match='741'):p.inventory({},None,{})


def test_process_guard_and_real_owner_lock(tmp_path,monkeypatch):
    identity=p.process_identity(os.getpid());assert identity is not None
    with pytest.raises(RuntimeError,match='still live'):
        p.guard_previous_child(dict(numerical_pid=os.getpid(),numerical_identity=identity))
    monkeypatch.setattr(p,'process_identity',lambda pid:'different-birth')
    p.guard_previous_child(dict(numerical_pid=123,numerical_identity='old-birth'))
    with p.exclusive_owner(tmp_path/'owner.lock'):
        with pytest.raises(OSError):
            with p.exclusive_owner(tmp_path/'owner.lock'):raise AssertionError('second owner accepted')
    # A stale file remains; the OS lock was released.
    with p.exclusive_owner(tmp_path/'owner.lock'):pass


def test_exited_real_child_is_not_treated_as_live():
    child=subprocess.Popen([sys.executable,'-c','pass'],creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    assert child.wait(timeout=20)==0
    assert p.process_identity(child.pid) is None


def test_observation_expiry_keeps_same_child_until_actual_exit(tmp_path,monkeypatch):
    events=[];launches=[]
    class Child:
        pid=12345
        def __init__(self):self.calls=0
        def wait(self,timeout):
            assert timeout==60;self.calls+=1
            if self.calls==1:raise subprocess.TimeoutExpired('fixture',timeout)
            return 0
    def launch(*args,**kwargs):
        child=Child();launches.append(child);return child
    ticks=iter((0,100))
    monkeypatch.setattr(p,'WORK',tmp_path);monkeypatch.setattr(p.subprocess,'Popen',launch)
    monkeypatch.setattr(p,'process_identity',lambda pid:'fixture-birth')
    monkeypatch.setattr(p.time,'monotonic',lambda:next(ticks))
    monkeypatch.setattr(p.shutil,'disk_usage',lambda root:SimpleNamespace(free=10**15))
    monkeypatch.setattr(p,'state',lambda **record:events.append(record))
    runner=p.Runner({},1);runner.run(Path('fixture.py'),[],'FIXTURE',1)
    assert len(launches)==1 and launches[0].calls==2 and runner.child is None
    assert any(r['phase']=='OBSERVATION_WINDOW_EXCEEDED_CHILD_STILL_ATTACHED' and r['terminal'] is False for r in events)
    assert events[-1]['phase']=='CHILD_COMPLETE' and len(list(tmp_path.glob('*.log')))==1


def test_space_reserve_prevents_launch_without_deleting_data(tmp_path,monkeypatch):
    monkeypatch.setattr(p.shutil,'disk_usage',lambda root:SimpleNamespace(free=0))
    monkeypatch.setattr(p.subprocess,'Popen',lambda *a,**kw:pytest.fail('must not launch'))
    with pytest.raises(RuntimeError,match='reserve'):p.Runner({},1).run(Path('fixture.py'),[],'FIXTURE',1)


def test_full_df_gate_rejects_partial_coverage_without_installing_backend(tmp_path,monkeypatch):
    directory=tmp_path/'full';directory.mkdir();backend=p.df_aggregation.backend
    monkeypatch.setattr(p,'ROOT',tmp_path);monkeypatch.setattr(backend,'WORK',directory)
    monkeypatch.setattr(backend,'__file__',str(tmp_path/'backend.py'))
    monkeypatch.setattr(p.df_aggregation,'__file__',str(tmp_path/'aggregate.py'))
    monkeypatch.setattr(p.h.df,'file_key',lambda path:path.relative_to(tmp_path).as_posix())
    monkeypatch.setattr(p.h.df.values,'sha',lambda path:'FIXTURE')
    verified=[];monkeypatch.setattr(p.h.df.values,'verify_binding',lambda record:verified.append(record))
    original=dict(algorithm='ORIGINAL',files={},value_binding={})
    expected=dict(original,algorithm=backend.ALGORITHM,files={'backend.py':'FIXTURE'},campaign_workspace='full')
    files={f'full/{stage}_{i:03d}.{ext}':'FIXTURE' for stage,n in (('endpoint',371),('midpoint',370))
           for i in range(n) for ext in ('npz','json')}
    proofs={f'full/batches/{batch[0]:03d}_{batch[-1]:03d}/{name}':'FIXTURE'
            for batch in p.df_aggregation.BATCHES for name in ('manifest.json','reproduction.json')}
    manifest=dict(binding=expected,all_741_DF_covered=True,endpoints=list(range(371)),midpoints=list(range(370)),files=files)
    receipt=dict(points=741,byte_identical=True,independent_recomputation=True,manifest_SHA256='FIXTURE',
        independently_reproduced_batch_files=proofs,aggregation_source_SHA256='FIXTURE')
    (directory/'manifest.json').write_text(json.dumps(manifest));(directory/'reproduction.json').write_text(json.dumps(receipt))
    before=p.h.df.WORK,p.h.df.binding
    p.verify_full_df(dict(value_point_binding=original))
    assert (p.h.df.WORK,p.h.df.binding)==before
    assert any(len(v['files'])==1482 for v in verified)
    manifest['midpoints'].pop();(directory/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(RuntimeError,match='741-point DF'):p.verify_full_df(dict(value_point_binding=original))


def test_independent_inventory_materialization_preserves_mismatch(tmp_path,monkeypatch):
    monkeypatch.setattr(p,'WORK',tmp_path)
    snapshots=iter(({'fixture':1},{'fixture':1},{'fixture':1},{'fixture':2}))
    monkeypatch.setattr(p,'inventory',lambda *args:next(snapshots))
    runner=SimpleNamespace(sources={},verify=lambda:None)
    p.materialize_inventory({},None,runner)
    first=(tmp_path/'manifest.json').read_bytes()
    receipt=json.loads((tmp_path/'reproduction.json').read_text())
    assert receipt['independent_inventory_verification'] is True
    assert 'independent_recomputation' not in receipt
    with pytest.raises(ArithmeticError,match='both preserved'):p.materialize_inventory({},None,runner)
    assert (tmp_path/'manifest.json').read_bytes()==first
    assert len(list(tmp_path.glob('manifest.repeat_*.json')))==1
    assert len(list(tmp_path.glob('reproduction.before_attempt_*.json')))==1
    assert not (tmp_path/'reproduction.json').exists()
