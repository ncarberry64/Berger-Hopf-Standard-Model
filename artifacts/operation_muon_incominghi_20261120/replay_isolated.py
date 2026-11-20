"""Replay the reviewed seven-calculation package under -I -S, one worker.

This preserves the shipped directory, checks its manifest before copying,
and runs only the declared replay scripts in a fresh destination. NumPy
and SciPy are loaded from an explicitly supplied inspected package root.
No startup .pth files, PYTHONPATH, network or child interpreters are used.
"""
import sys
from pathlib import Path
assert sys.flags.isolated and sys.flags.no_site and sys.flags.no_user_site
import argparse, ast, contextlib, hashlib, io, json, os, runpy, shutil, time

parser=argparse.ArgumentParser()
parser.add_argument('--source',required=True)
parser.add_argument('--destination',required=True)
parser.add_argument('--site-packages',required=True)
args=parser.parse_args()
source=Path(args.source).resolve();destination=Path(args.destination).resolve()
runtime=Path(sys.base_prefix).resolve();site=Path(args.site_packages).resolve()
assert site.is_relative_to(runtime) and site.name=='site-packages'
assert all(Path(p).resolve().is_relative_to(runtime) for p in sys.path)
assert not destination.exists(), 'Preserve existing replay output; choose a fresh destination.'
assert source!=destination and not source.is_relative_to(destination)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest={}
for line in (source/'SHA256SUMS').read_text(encoding='utf-8').splitlines():
    h,name=line.split('  ',1);path=(source/name).resolve()
    assert path.is_relative_to(source) and digest(path)==h,name
    manifest[name]=h
assert len(manifest)==57
shutil.copytree(source,destination)
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
sys.dont_write_bytecode=True
sys.path.insert(0,str(site));sys.path.insert(0,str(destination))
# NumPy testing asks platform.machine(); on Python 3.14/Windows the standard
# helper may invoke cmd.exe for an OS version. Populate the same metadata
# from in-process Python APIs, retaining the no-subprocess audit below.
if sys.platform=='win32':
    import platform, sysconfig
    win=sys.getwindowsversion();arch=sysconfig.get_platform()
    machines={'win-amd64':'AMD64','win-arm64':'ARM64','win32':'x86'}
    assert arch in machines,arch
    platform._uname_cache=platform.uname_result('Windows','',str(win.major)+'.'+str(win.minor),
        str(win.major)+'.'+str(win.minor)+'.'+str(win.build),machines[arch])

# The actual seven-entry launch is deliberately separate from the producer's
# subprocess-based verify_package.py, which does not propagate -I -S.
def audit(event,details):
    if event in ('subprocess.Popen','os.system','socket.connect','socket.getaddrinfo'):
        raise RuntimeError('Replay must remain local and single-process: '+event)
sys.addaudithook(audit)
import numpy as np
import scipy
binary_inventory=[]
for path in sorted(destination.rglob('*.npz')):
    with np.load(path,allow_pickle=False) as data:
        columns=[]
        for key in data.files:
            a=data[key];assert not a.dtype.hasobject and a.nbytes<100_000_000
            columns.append(dict(key=key,shape=list(a.shape),dtype=str(a.dtype),bytes=a.nbytes))
        binary_inventory.append(dict(file=path.relative_to(destination).as_posix(),arrays=columns))
scripts=['formed_n0_wall_spin_transfer','formed_n0_equal_local_field_test',
 'formed_n0_minimal_exterior_adjoint','formed_companion_readout_test',
 'formed_higgs_invariant_companion','neutral_higgs_surface_current_identity',
 'frozen_native_central_halfline']
receipts=[];timings=[]
for name in scripts:
    path=destination/'native_patch_first_jet'/(name+'.py')
    output=io.StringIO();start=time.perf_counter()
    with contextlib.redirect_stdout(output):runpy.run_path(str(path),run_name='__main__')
    elapsed=time.perf_counter()-start
    (destination/(name+'.stdout.txt')).write_bytes(output.getvalue().encode('utf-8'))
    receipts.append(dict(script=path.relative_to(destination).as_posix(),source_sha256=manifest[path.relative_to(destination).as_posix()],passed=True))
    timings.append(dict(script=name,seconds=elapsed))
    print('PASS '+name,flush=True)
sub=destination/'native_patch_first_jet'
def read(name):return json.loads((sub/(name+'.json')).read_text(encoding='utf-8'))
x=read('formed_n0_wall_spin_transfer')['records']
np.testing.assert_allclose([x['central']['held_trace_spin_transfer'],x['H_aligned']['held_trace_spin_transfer']],
 [1.2603788642488865,1.0013228590975443],atol=2e-10,rtol=0)
x=read('formed_n0_equal_local_field_test')
assert x['field_null_difference_norm']<1e-12
np.testing.assert_allclose(x['field_null_difference_gap_coordinate'],.2617557137380767,atol=2e-10,rtol=0)
x=read('formed_n0_minimal_exterior_adjoint')['cases']['curvature_and_scalar_zero_rhs_and_temporal_zero_reaction']
assert x['dual_residual_norm']>.17 and x['null_constraint_norm']<1e-10
x=read('formed_higgs_invariant_companion')
assert abs(x['local_pure_central_gauge_residual'])<1e-12
assert x['covariant']['six_force']['relative_residual']<1e-10
assert 1e-8<x['covariant']['full16']['relative_residual']<1e-6
module_count=0
for module in tuple(sys.modules.values()):
    name=getattr(module,'__file__',None)
    if name:
        p=Path(name).resolve()
        assert p.is_relative_to(runtime) or p.is_relative_to(destination) or p==Path(__file__).resolve(),str(p)
        module_count+=1
outputs={}
for p in sorted(sub.iterdir()):
    if p.suffix in ('.json','.npz'):outputs[p.relative_to(destination).as_posix()]=digest(p)
report=dict(classification='FINITE_CONDITIONAL_OFFLINE_REPLAY',shipping_manifest_entries=len(manifest),
 runtime=dict(python=sys.version.split()[0],numpy=np.__version__,scipy=scipy.__version__,isolated=True,no_site=True,
  thread_limit=1,import_origins_bounded=True,checked_module_files=module_count),
 producer_versions=dict(python='3.12',numpy='2.3.5',scipy='1.17.0'),
 scripts=receipts,scientific_checks_passed=True,output_hashes=outputs,binary_inventory=binary_inventory,
 physical_moment=None,physical_guard='2e-10',native_exterior_supplied=False,physical_uncertainty=None)
raw=(json.dumps(report,sort_keys=True,indent=2)+'\n').encode('utf-8')
(destination/'LOCAL_REPLAY_RECEIPT.json').write_bytes(raw)
(destination/'LOCAL_TIMINGS.json').write_bytes((json.dumps(timings,indent=2)+'\n').encode('utf-8'))
print(json.dumps(dict(receipt_sha256=hashlib.sha256(raw).hexdigest(),replays=len(receipts),seconds=sum(x['seconds'] for x in timings),versions=report['runtime'])))
