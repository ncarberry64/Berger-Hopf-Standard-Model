from pathlib import Path
import os, sys, hashlib, json, subprocess, argparse
import numpy as np
p=Path(__file__).resolve().parent
s=p/'native_patch_first_jet'
a=argparse.ArgumentParser()
a.add_argument('--hashes',action='store_true')
a.add_argument('--rebuild-action',action='store_true')
opt=a.parse_args()
for line in (p/'SHA256SUMS').read_text().splitlines():
    h,f=line.split('  ',1)
    assert hashlib.sha256((p/f).read_bytes()).hexdigest()==h, f
print('All shipping hashes match.')
if opt.hashes: sys.exit(0)
env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'}
def run(f):
    z=subprocess.run([sys.executable,str(f)],cwd=p,env=env,capture_output=True,text=True)
    if z.returncode: raise RuntimeError(str(f)+'\n'+z.stdout+'\n'+z.stderr)
    print('PASS',f.relative_to(p))
if opt.rebuild_action:
    path=p/'native_n0_coupled_static.npz'
    with np.load(path) as z: base={k:z[k] for k in ['K84','M84','B84','KH20','Dirichlet_trial_return20']}
    run(p/'native_n0_coupled_static.py')
    with np.load(path) as z:
        for k,x in base.items():
            np.testing.assert_allclose(z[k],x,atol=1e-7,rtol=1e-8,err_msg=k)
for f in ['formed_n0_wall_spin_transfer','formed_n0_equal_local_field_test','formed_n0_minimal_exterior_adjoint','formed_companion_readout_test','formed_higgs_invariant_companion','neutral_higgs_surface_current_identity','frozen_native_central_halfline']:
    run(s/(f+'.py'))
def j(f): return json.loads((s/(f+'.json')).read_text())
x=j('formed_n0_wall_spin_transfer')['records']
np.testing.assert_allclose([x['central']['held_trace_spin_transfer'],x['H_aligned']['held_trace_spin_transfer']],[1.2603788642488865,1.0013228590975443],atol=2e-10,rtol=0)
x=j('formed_n0_equal_local_field_test')
assert x['field_null_difference_norm']<1e-12
np.testing.assert_allclose(x['field_null_difference_gap_coordinate'],.2617557137380767,atol=2e-10,rtol=0)
x=j('formed_n0_minimal_exterior_adjoint')
assert x['cases']['curvature_and_scalar_zero_rhs_and_temporal_zero_reaction']['dual_residual_norm']>.17
assert x['cases']['curvature_and_scalar_zero_rhs_and_temporal_zero_reaction']['null_constraint_norm']<1e-10
x=j('formed_higgs_invariant_companion')
assert abs(x['local_pure_central_gauge_residual'])<1e-12
assert x['covariant']['six_force']['relative_residual']<1e-10
assert 1e-8<x['covariant']['full16']['relative_residual']<1e-6
print('Pinned scientific replay checks passed; scope remains conditional.')
