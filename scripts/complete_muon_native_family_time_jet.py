"""Add the canonical mass/time coefficient; reuse all saved source actions."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from flint import arb,ctx

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_bytes((json.dumps(x,indent=2,sort_keys=True)+'\n').encode())
def run(base,out):
    if out.exists():raise FileExistsError('new temporal-coefficient output required')
    path=base/'family_source_actions.npz'
    with np.load(path) as z:
        incidence=np.array(z['weak_incidence']);T=np.array(z['weak_mass_tau'])
    mass=-incidence@T;time=1j*incidence
    cross=mass.conj().T@time
    ctx.prec=192
    r=json.loads((base/'outward_display_fix/result.json').read_text())
    rr=r['form_family_quadrature']['ratios']
    delta=arb(rr['r_mu'])-arb(rr['r_e'])
    # Constant derivative: exact two-node Gauss weights are reused. There
    # is no heat integration or reevaluation of old point/source actions.
    integrated=delta/2+delta/2
    if not (integrated-delta).contains(0):raise ArithmeticError('time coefficient family integral failed')
    arrays=dict(B_H_time_action=time,mass_action_per_kappa_r=mass,
        mass_time_0tau_per_kappa_Delta_r=cross,mass_time_tau0_per_kappa_Delta_r=cross.conj().T,
        endpoint_time_0tau_per_kappa=float(delta)*cross,
        endpoint_time_tau0_per_kappa=float(delta)*cross.conj().T,
        integral_time_0tau_per_kappa=float(integrated)*cross,
        integral_time_tau0_per_kappa=float(integrated)*cross.conj().T)
    result=dict(classification='CANONICAL_FIXED_ANGULAR_MASS_TIME_JET_COMPLETION_NOT_NATIVE_HEAT',
        equation='Delta q=amplitude terms+c^dagger(-i kappa Delta_r T)c_tau+c_tau^dagger(+i kappa Delta_r T)c',
        scope='corrects amplitude-only presentation; canonical instantaneous angular amplitude/time coefficients, not full moving-frame temporal/native action',
        cross_0tau_norm=float(np.linalg.norm(cross)),
        action_identity_residual=float(np.linalg.norm(cross+1j*T)),
        reverse_is_actual_dual=True,endpoint_integral_coefficient=str(integrated-delta),
        source_actions_recomputed=False,old_family_amplitude_arrays_changed=False,
        old_parent_solve_changed=False,native_heat_evaluations=0,
        moving_profile_domain_completion_jets=None,physical_a_mu=None,physical_g_mu=None)
    out.mkdir(parents=True);np.savez_compressed(out/'mass_time_actions.npz',**arrays)
    save(out/'result.json',result)
    save(out/'input_hashes.json',{k:dict(path=str(p),sha256=sha(p)) for k,p in dict(
        source_arrays=path,accepted_amplitude_result=base/'outward_display_fix/result.json',script=Path(__file__).resolve()).items()})
    save(out/'output_hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps(result,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.input.resolve(),a.output.resolve())
