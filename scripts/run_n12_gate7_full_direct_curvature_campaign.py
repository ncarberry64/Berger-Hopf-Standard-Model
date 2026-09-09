"""Complete paired physical Hessians, local sources and causal composition."""
import argparse
from contextlib import contextmanager
import ctypes
from ctypes import wintypes
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_direct_causal_quadratic as composition
import certify_n12_gate7_full_direct_df_reproduction as df_aggregation

q=composition.producer;h=q.hessian
WORK=ROOT/'artifacts/flagship_integration/.full_direct_curvature_campaign_work'
STATE=WORK/'active_state.json'
THEORY=ROOT/'theory/n12_gate7_full_direct_curvature_campaign.md'
ALGORITHM='FULL_DIRECT_PHYSICAL_CURVATURE_CAMPAIGN_PAIRED_POINTS_AND_LOCAL_SOURCES_V1'


def process_identity(pid):
    """Return a live process identity; unavailable/denied inspection raises."""
    if type(pid) is not int or pid<=0:raise ValueError('positive process ID required')
    if os.name=='nt':
        api=ctypes.WinDLL('kernel32',use_last_error=True)
        api.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];api.OpenProcess.restype=wintypes.HANDLE
        api.CloseHandle.argtypes=[wintypes.HANDLE]
        api.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD]
        api.GetProcessTimes.argtypes=[wintypes.HANDLE]+[ctypes.POINTER(wintypes.FILETIME)]*4
        handle=api.OpenProcess(0x100000|0x1000,False,pid)
        if not handle:
            error=ctypes.get_last_error()
            if error==87:return None
            raise ctypes.WinError(error)
        try:
            result=api.WaitForSingleObject(handle,0)
            if result==0:return None
            if result!=258:raise ctypes.WinError(ctypes.get_last_error())
            times=[wintypes.FILETIME() for _ in range(4)]
            if not api.GetProcessTimes(handle,*(ctypes.byref(t) for t in times)):
                raise ctypes.WinError(ctypes.get_last_error())
            return str((times[0].dwHighDateTime<<32)|times[0].dwLowDateTime)
        finally:api.CloseHandle(handle)
    # POSIX signal zero checks existence; it must never be used on Windows.
    try:os.kill(pid,0)
    except ProcessLookupError:return None
    return f'live-posix-pid:{pid}'


@contextmanager
def exclusive_owner(path):
    """OS lock survives stale lock-file contents, but not process exit."""
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a+b') as stream:
        if stream.tell()==0:stream.write(b'0');stream.flush()
        stream.seek(0)
        if os.name=='nt':
            import msvcrt
            msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        try:yield
        finally:
            stream.seek(0)
            if os.name=='nt':msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)
            else:fcntl.flock(stream.fileno(),fcntl.LOCK_UN)


def guard_previous_child(record):
    pid=record.get('numerical_pid')
    if pid is None:return
    actual=process_identity(pid)
    if actual is not None and (record.get('numerical_identity') is None or actual==record['numerical_identity']):
        raise RuntimeError('previous numerical child is still live; overlapping campaign refused')


def state(**record):
    h.write_json(STATE,dict(record,FULL_BHSM_COMPLETE=False));print(json.dumps(record),flush=True)


def verify_seed():
    path=composition.result_path([13]);payload=json.loads(path.read_text())
    receipt=json.loads(path.with_suffix('.reproduction.json').read_text())
    if (payload.get('algorithm')!=composition.ALGORITHM or payload.get('validation_passed') is not True
            or payload.get('coverage')!=dict(active_intervals=[13],interval_count=1,total_intervals=370,complete=False)
            or receipt.get('byte_identical') is not True or receipt.get('independent_recomputation') is not True
            or receipt.get('result_SHA256')!=h.df.values.sha(path)):
        raise RuntimeError('paired interval-13 causal integration seed required')
    h.df.values.verify_binding(dict(files=payload['raw_input_SHA256']))
    q.local.residual.foundation.coordinate._verified_inputs(dict(inputs=payload['inputs']))


def verify_full_df(expected_hessian):
    backend=df_aggregation.backend;directory=backend.WORK
    path=directory/'manifest.json';receipt_path=directory/'reproduction.json'
    manifest=json.loads(path.read_text());receipt=json.loads(receipt_path.read_text())
    original=expected_hessian['value_point_binding']
    expected=dict(original,algorithm=backend.ALGORITHM,files=dict(original['files']),
                  campaign_workspace=directory.relative_to(ROOT).as_posix())
    expected['files'][h.df.file_key(Path(backend.__file__))]=h.df.values.sha(Path(backend.__file__))
    files={h.df.file_key(directory/f'{stage}_{i:03d}.{ext}') for stage,count in (('endpoint',371),('midpoint',370))
           for i in range(count) for ext in ('npz','json')}
    proofs={h.df.file_key(directory/'batches'/f'{indices[0]:03d}_{indices[-1]:03d}'/name)
            for indices in df_aggregation.BATCHES for name in ('manifest.json','reproduction.json')}
    if (manifest.get('binding')!=expected or manifest.get('all_741_DF_covered') is not True
            or manifest.get('endpoints')!=list(range(371)) or manifest.get('midpoints')!=list(range(370))
            or set(manifest.get('files',{}))!=files or receipt.get('points')!=741
            or receipt.get('byte_identical') is not True or receipt.get('independent_recomputation') is not True
            or receipt.get('manifest_SHA256')!=h.df.values.sha(path)
            or set(receipt.get('independently_reproduced_batch_files',{}))!=proofs
            or receipt.get('aggregation_source_SHA256')!=h.df.values.sha(Path(df_aggregation.__file__))):
        raise RuntimeError('complete matching paired 741-point DF campaign required before Hessian expansion')
    h.df.values.verify_binding(dict(files=manifest['files']));h.df.values.verify_binding(expected)
    h.df.values.verify_binding(dict(files=receipt['independently_reproduced_batch_files']))
    sources=dict(expected['files']);h.merge(sources,receipt['independently_reproduced_batch_files'])
    for item in (path,receipt_path,Path(df_aggregation.__file__)):
        sources[h.df.file_key(item)]=h.df.values.sha(item)
    return sources


def hessian_status(stage,index,expected):
    directory=h.point_directory(stage,index);path=directory/'manifest.json';receipt_path=directory/'reproduction.json'
    if not path.exists():
        if receipt_path.exists():raise RuntimeError('Hessian receipt has no complete manifest')
        return 0,None
    dependencies=h.df.point_inputs(stage,index,expected['value_point_binding'])[-1]
    current=h.complete_manifest(stage,index,expected,dependencies)
    if path.read_bytes()!=h.encoded(current):raise RuntimeError('existing Hessian manifest changed')
    files=dict(current['files']);files[h.df.file_key(path)]=h.df.values.sha(path)
    if not receipt_path.exists():return 1,files
    receipt=json.loads(receipt_path.read_text())
    if (receipt.get('byte_identical') is not True or receipt.get('independent_recomputation') is not True
            or receipt.get('fresh_spawned_worker_processes') is not True or receipt.get('rows')!=list(range(99))
            or receipt.get('manifest_SHA256')!=h.df.values.sha(path)):
        raise RuntimeError('Hessian independent reproduction changed or incomplete')
    files[h.df.file_key(receipt_path)]=h.df.values.sha(receipt_path)
    return 2,files


def local_status(index,base):
    directory=q.WORK/f'interval_{index:03d}';path=directory/'manifest.json';receipt_path=directory/'reproduction.json'
    if not path.exists():
        if receipt_path.exists():raise RuntimeError('local receipt has no complete manifest')
        return 0,None
    manifest=json.loads(path.read_text())
    expected={h.df.file_key(directory/f'{family}_{pair}.{ext}') for family in ('LL','LT','TT')
              for pair in ('00','01','10','11') for ext in ('npz','json')}
    if (manifest.get('algorithm')!=q.ALGORITHM or manifest.get('interval')!=index
            or manifest.get('complete_local_source_blocks') is not True or set(manifest.get('files',{}))!=expected
            or path.read_bytes()!=h.encoded(manifest)):
        raise RuntimeError('complete unchanged local source manifest required')
    h.df.values.verify_binding(dict(files=manifest['files']));source=None
    for family in ('LL','LT','TT'):
        for pair in ('00','01','10','11'):
            data=directory/f'{family}_{pair}.npz';record=json.loads(data.with_suffix('.json').read_text())
            current=composition.verify_record(index,family,pair,record,data,base)
            if source is not None and current!=source:raise RuntimeError('local source bindings disagree')
            source=current
    h.df.values.verify_binding(dict(files=source['raw_inputs']))
    q.local.residual.foundation.coordinate._verified_inputs(dict(inputs=source['inputs']))
    files=dict(manifest['files']);files[h.df.file_key(path)]=h.df.values.sha(path)
    if not receipt_path.exists():return 1,files
    receipt=json.loads(receipt_path.read_text());composition.verify_manifest(index,manifest,receipt,path)
    files[h.df.file_key(receipt_path)]=h.df.values.sha(receipt_path)
    return 2,files


class Runner:
    def __init__(self,sources,min_free_gib):
        self.sources=sources;self.min_free_bytes=int(min_free_gib*1024**3);self.child=None

    def verify(self):h.df.values.verify_binding(dict(files=self.sources))

    def run(self,script,args,label,observation_seconds):
        self.verify()
        if shutil.disk_usage(ROOT).free<self.min_free_bytes:raise RuntimeError('campaign free-space reserve reached')
        log=WORK/f'{label}_{time.time_ns()}.log';started=time.monotonic();observed=False
        with log.open('x') as stream:
            self.child=subprocess.Popen([sys.executable,str(script),*args],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            identity=process_identity(self.child.pid)
            state(phase=label,terminal=False,numerical_pid=self.child.pid,numerical_identity=identity,log=str(log),sources=self.sources)
            while True:
                try:code=self.child.wait(timeout=60);break
                except subprocess.TimeoutExpired:
                    if not observed and time.monotonic()-started>=observation_seconds:
                        observed=True
                        state(phase='OBSERVATION_WINDOW_EXCEEDED_CHILD_STILL_ATTACHED',stage=label,terminal=False,
                            numerical_pid=self.child.pid,numerical_identity=identity,log=str(log),sources=self.sources)
            if code!=0:raise RuntimeError(f'child failed with exit {code}; evidence retained in {log}')
        self.child=None;self.verify();state(phase='CHILD_COMPLETE',stage=label,terminal=False,sources=self.sources)


def ensure_pair(status,run):
    """Resume first production, repeat an unpaired result, reuse a valid pair."""
    level,_=status()
    if level==0:
        run(False);level,_=status()
        if level!=1:raise RuntimeError('first computation did not produce one complete unpaired result')
    if level==1:
        run(True);level,_=status()
        if level!=2:raise RuntimeError('independent reproduction did not complete')
    if level!=2:raise RuntimeError('invalid campaign completion state')


def ensure_hessian(runner,stage,index,expected):
    def run(repeat):
        args=['--stage',stage,'--index',str(index),'--workers','6','--worker-hour-cap','8']
        if repeat:args.append('--recompute')
        runner.run(Path(h.__file__),args,f'H_{stage}_{index:03d}_{"repeat" if repeat else "first"}',5100)
    ensure_pair(lambda:hessian_status(stage,index,expected),run)


def ensure_local(runner,index,base):
    def run(repeat):
        args=['--interval',str(index),'--full-derivatives']
        if repeat:args.append('--recompute')
        runner.run(Path(q.__file__),args,f'Q_{index:03d}_{"repeat" if repeat else "first"}',7200)
    ensure_pair(lambda:local_status(index,base),run)


def produce_all(runner,expected,base):
    ensure_hessian(runner,'endpoint',0,expected)
    for index in range(370):
        ensure_hessian(runner,'midpoint',index,expected)
        ensure_hessian(runner,'endpoint',index+1,expected)
        ensure_local(runner,index,base)
        state(phase='INTERVAL_PAIRED',paired_intervals=index+1,terminal=False,sources=runner.sources)


def inventory(expected,base,sources):
    files={}
    for stage,count in (('endpoint',371),('midpoint',370)):
        for index in range(count):
            level,point_files=hessian_status(stage,index,expected)
            if level!=2:raise RuntimeError('all 741 paired physical Hessian points required')
            h.merge(files,point_files)
    for index in range(370):
        level,point_files=local_status(index,base)
        if level!=2:raise RuntimeError('all 370 paired local source intervals required')
        h.merge(files,point_files)
    return dict(algorithm=ALGORITHM,endpoints=list(range(371)),midpoints=list(range(370)),intervals=list(range(370)),
        files=files,sources=sources,Hessian_binding=expected,paired_Hessian_points=741,paired_local_source_intervals=370,
        all_finite_history_physical_point_sources_paired=True,neighborhood_remainder_enclosed=False,
        physical_quotient_identified=False,physical_contraction_proved=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)


def materialize_inventory(expected,base,runner):
    path=WORK/'manifest.json';receipt=WORK/'reproduction.json'
    if receipt.exists():receipt.replace(WORK/f'reproduction.before_attempt_{time.time_ns()}.json')
    first=inventory(expected,base,runner.sources);data=h.encoded(first)
    if path.exists() and path.read_bytes()!=data:
        h.write_json(WORK/f'manifest.mismatch_{time.time_ns()}.json',first)
        raise RuntimeError('earlier full curvature inventory differs; preserved')
    h.write_json(path,first);runner.verify()
    second=inventory(expected,base,runner.sources);candidate=WORK/f'manifest.repeat_{time.time_ns()}.json'
    h.write_json(candidate,second)
    if candidate.read_bytes()!=path.read_bytes():raise ArithmeticError('independent full inventory differs; both preserved')
    candidate.unlink();runner.verify()
    h.write_json(receipt,dict(byte_identical=True,independent_inventory_verification=True,
        numerical_results_independently_recomputed_in_point_and_interval_receipts=True,
        manifest_SHA256=h.df.values.sha(path),FULL_BHSM_COMPLETE=False))


def full_composition_status():
    path=composition.result_path(None);receipt_path=path.with_suffix('.reproduction.json')
    if not path.exists():
        if receipt_path.exists():raise RuntimeError('full composition receipt lacks result')
        return 0,None
    payload=json.loads(path.read_text())
    if (payload.get('algorithm')!=composition.ALGORITHM or payload.get('validation_passed') is not True
            or payload.get('scope')!='SELECTED_BRANCH_FIXED_FRAME_FINITE_HISTORY_QUADRATIC_BOUND'
            or payload.get('coverage')!=dict(active_intervals=list(range(370)),interval_count=370,total_intervals=370,complete=True)
            or payload.get('polynomial_convention')!='LL*rL^2+2*LT*rL*rT+TT*rT^2'
            or set(payload.get('families',{}))!=set(('LL','LT','TT'))):
        raise RuntimeError('full physical point causal composition required')
    for family in ('LL','LT','TT'):
        row=payload['families'][family];values=row.get('frozen_inverse_quadratic_coefficients_upper',[])
        if (row.get('active_intervals')!=list(range(370)) or row.get('all_intervals_covered') is not True
                or len(values)!=2 or any(type(v) is not float or not math.isfinite(v) or v<0 for v in values)
                or payload.get('quadratic_coefficients_upper',{}).get(family)!=values):
            raise RuntimeError('all three complete finite causal coefficient families required')
    h.df.values.verify_binding(dict(files=payload['raw_input_SHA256']))
    q.local.residual.foundation.coordinate._verified_inputs(dict(inputs=payload['inputs']))
    if not receipt_path.exists():return 1,None
    receipt=json.loads(receipt_path.read_text())
    if (receipt.get('byte_identical') is not True or receipt.get('independent_recomputation') is not True
            or receipt.get('result_SHA256')!=h.df.values.sha(path)):
        raise RuntimeError('paired full causal composition required')
    return 2,h.df.values.sha(path)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--min-free-gib',type=int,default=16);args=parser.parse_args()
    if args.min_free_gib<1:raise ValueError('positive free-space reserve required')
    WORK.mkdir(parents=True,exist_ok=True);runner=None
    with exclusive_owner(WORK/'owner.lock'):
        if STATE.exists():guard_previous_child(json.loads(STATE.read_text()))
        try:
            verify_seed();expected=h.binding();df_sources=verify_full_df(expected)
            base=q.local.residual.load_foundation()[0]
            paths=(Path(__file__),THEORY,Path(q.__file__),q.THEORY,Path(q.quadratic.__file__),Path(q.second.__file__),
                Path(composition.__file__),composition.THEORY,Path(composition.causal.__file__),
                Path(composition.causal._matrix.__code__.co_filename),Path(composition.causal._squared_norm.__code__.co_filename),
                Path(composition.causal._float_upper.__code__.co_filename),Path(composition.causal.transport_local_errors.__code__.co_filename),
                Path(composition.causal.combine_stored_causal_errors.__code__.co_filename))
            sources=dict(expected['files']);h.merge(sources,df_sources)
            h.merge(sources,{h.df.file_key(path):h.df.values.sha(path) for path in paths})
            runner=Runner(sources,args.min_free_gib);runner.verify()
            produce_all(runner,expected,base)
            materialize_inventory(expected,base,runner)
            def compose(repeat):
                runner.run(Path(composition.__file__),['--recompute'] if repeat else [],
                           'FULL_CAUSAL_Q_REPEAT' if repeat else 'FULL_CAUSAL_Q_FIRST',7200)
            ensure_pair(full_composition_status,compose)
            state(phase='COMPLETE',terminal=True,paired_Hessian_points=741,paired_local_source_intervals=370,
                full_causal_quadratic_SHA256=full_composition_status()[1],sources=sources,
                neighborhood_remainder_enclosed=False,physical_quotient_identified=False,Gate7_closed=False)
        except BaseException as error:
            child=runner.child if runner else None
            state(phase='CHAIN_FAILED',terminal=True,error=repr(error),sources=runner.sources if runner else {},
                numerical_pid=child.pid if child else None,numerical_identity=process_identity(child.pid) if child else None,
                numerical_returncode=child.poll() if child else None,observation_timeout_does_not_prove_child_stopped=True)
            raise


if __name__=='__main__':main()
