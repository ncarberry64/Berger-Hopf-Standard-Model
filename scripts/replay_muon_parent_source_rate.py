"""Focused additive repair; old contact/body and production kernels reused."""
from pathlib import Path
from fractions import Fraction
import argparse
import hashlib
import json
import sys
import numpy as np


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def array_sha(a):
    header=json.dumps(dict(shape=a.shape,dtype=a.dtype.str),sort_keys=True).encode()
    return hashlib.sha256(header+b'\n'+np.ascontiguousarray(a).tobytes()).hexdigest()
def save(p,x):p.write_bytes((json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())


def norm_upper(a):
    """Conservative IEEE binary64 positive-sum bound for stored arrays.

    No operator/discretization error is inferred. A 3N operation bound
    encloses real/imag products and any sum association without underflow.
    """
    from flint import arb,ctx,fmpq
    if not np.isfinite(a).all():raise ValueError('nonfinite stored coefficient')
    nz=np.concatenate((abs(a.real[a.real!=0]),abs(a.imag[a.imag!=0])))
    if len(nz) and (np.min(nz)<2.**-400 or np.max(nz)>2.**400):
        raise ValueError('norm bound needs explicit under/overflow handling')
    total=float(np.sum(a.real*a.real+a.imag*a.imag,dtype=np.float64))
    k=3*a.size+3;u=Fraction(1,2**53); gamma=k*u/(1-k*u)
    bound=Fraction(total)/(1-gamma)
    with ctx.workprec(192):
        result=arb(fmpq(bound.numerator,bound.denominator)).sqrt()
        return result.upper()


def run(root,output):
    if output.exists():raise FileExistsError('fresh output directory required')
    sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_parent_source_contact import retained_source_cut_rate,repair_source_time_rate
    from flint import arb,ctx,fmpq
    old_path=root/'artifacts/muon_parent_source_contact_20261003/replay_reference/parent_metric_dirac_actions.npz'
    geometry=root/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz'
    if sha(geometry)!='34ab3500a98197aa3db35f5f3d2e6e7234145e7bd819477e81efcbda3bebd95c':
        raise ValueError('historical geometry cache changed')
    rate=retained_source_cut_rate(root)
    with np.load(old_path) as p:old={k:p[k] for k in p.files}
    with np.load(geometry) as g:
        H_used=float(g['boundary_H'][0])
        cells=old['gauss_cells'];points=old['gauss_rho'];rho=g['rho']
        x=(points-rho[cells])/np.diff(rho)[cells]
        dt=float(g['proper_times'][1]-g['proper_times'][0])
        slope=(g['base_radius'][1]-g['base_radius'][0])/dt
        rt=slope[cells]*(1-x)+slope[cells+1]*x
        r=g['base_radius'][0,cells]*(1-x)+g['base_radius'][0,cells+1]*x
        H_inferred=-2*(old['source_kernel_time_log_derivative']+rt/r)
    if np.max(abs(H_inferred-H_used))>1e-14:raise ValueError('H_used not supported by saved source derivative')
    new,delta=repair_source_time_rate(old,H_used=H_used,cut_rate=rate)
    output.mkdir(parents=True)
    np.savez_compressed(output/'parent_source_rate_corrected.npz',**new)
    np.savez_compressed(output/'source_rate_old_new_delta.npz',**delta)
    changed={f'D5_on_same_source_image_b_coefficient_n{n}' for n in (1,3)}|{'source_kernel_time_log_derivative'}
    unchanged={k:array_sha(v) for k,v in old.items() if k not in changed}
    if any(array_sha(new[k])!=h for k,h in unchanged.items()):raise ValueError('unaffected input changed')
    # Exact decimal endpoints of the inherited rate certificate, measured
    # from the actual binary64 H used in the repaired midpoint coefficient.
    h_mid=Fraction(float(rate['value']))
    h_error=max(abs(Fraction(str(e))-h_mid) for e in rate['interval'])
    uncertainty={}
    with ctx.workprec(192):
        h=arb(fmpq(h_error.numerator,h_error.denominator))/2
        for n in (1,3):
            tau=old[f'D5_on_same_source_image_b_tau_coefficient_n{n}']
            old_b=old[f'D5_on_same_source_image_b_coefficient_n{n}']
            nt=norm_upper(tau);nb=norm_upper(old_b)
            inherited=(h*nt).upper()
            repair_roundoff=(4*arb(2)**-53*(nb+abs(float(rate['value'])-H_used)/2*nt)).upper()
            uncertainty[str(n)]=dict(H_only_Frobenius_bound=str(inherited),
                H_only_bound_upper_float=float(np.nextafter(float(inherited),np.inf)),
                additive_repair_roundoff_bound=str(repair_roundoff),
                scope='stored finite source coefficient arrays at fixed remaining inputs; no body/interpolation/operator-tail bound')
    checks=dict(H_used=H_used,H_from_saved_kernel_max_residual=float(np.max(abs(H_inferred-H_used))),
        H_new=float(rate['value']),kernel_log_derivative_shift=-(float(rate['value'])-H_used)/2,
        unchanged_array_count=len(unchanged),unchanged_arrays_byte_preserved=True)
    for n in (1,3):
        checks[f'n{n}']=dict(old_norm=float(np.linalg.norm(delta[f'C_b_old_n{n}'])),
            new_norm=float(np.linalg.norm(delta[f'C_b_new_n{n}'])),
            delta_norm=float(np.linalg.norm(delta[f'C_b_delta_n{n}'])))
    save(output/'cut_rate_record.json',rate)
    save(output/'unchanged_array_hashes.json',unchanged)
    save(output/'affected_array_hashes.json',{k:array_sha(a) for k,a in delta.items()})
    save(output/'result.json',dict(checkpoint='BHSM_MUON_PARENT_SOURCE_TIME_RATE_REPAIR_20261003',
        start_HEAD='c6c4be76609f0f005f2b827a13a16d01f37a5c83',
        formula='C_b,new=C_b,old-(H_new-H_used)/2 C_b_tau,old',checks=checks,
        source_rate=rate,inherited_H_uncertainty=uncertainty,
        interpolation_body_error='unresolved and unchanged; not identified with inherited H interval or affine-logR slope',
        contact_certificate='unchanged; nodal interpolation-model scope only',
        execution=dict(old_body_recomputed=False,old_contact_recomputed=False,
            earlier_source_normalization_or_covariance_replay=False,exterior_response_applications=0,
            full_shifted_source_solves=0,native_heat_evaluations=0,physical_transfer_directions=0),
        physical_a_mu=None,physical_g_mu=None))
    inputs=[old_path,geometry,root/rate['result_path'],root/'src/bhsm/interface/muon_parent_source_contact.py',Path(__file__)]
    save(output/'input_hashes.json',[dict(path=str(p),sha256=sha(p)) for p in inputs])
    save(output/'receipt.json',dict(files=[dict(path=p.name,sha256=sha(p)) for p in sorted(output.iterdir())]))
    print(json.dumps(dict(output=str(output),checks=checks,H_uncertainty=uncertainty)))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.repository.resolve(),a.output.resolve())
