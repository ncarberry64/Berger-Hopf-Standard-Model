"""Evaluate held-endpoint tension and exact explicit-clock canonical work."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_high_precision_canonical_compatibility import high_precision_original_constitutive_action
from bhsm.interface.muon_holomorphic_child_clock_application import holomorphic_child_explicit_clock_application
from bhsm.interface.muon_complex_endpoint_area_action import original_endpoint_area_coefficient,held_endpoint_hamiltonian_area_coefficients
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(endpoint_folder,output,precision):
    source=ROOT/endpoint_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve every actual area/clock parameter application')
    refs={};rb=(source/'result.json').read_bytes();md=json.loads(rb);refs.update(md['input_hashes'])
    refs[(source/'result.json').relative_to(ROOT).as_posix()]=sha256(rb).hexdigest()
    p=source/'application.npz';b=p.read_bytes();h=sha256(b).hexdigest()
    if h!=md['archives']['application.npz']['sha256']:raise ValueError('same compatible endpoint changed')
    refs[p.relative_to(ROOT).as_posix()]=h
    with np.load(p,allow_pickle=False)as z:data={k:z[k].copy()for k in z.files}
    phase,_=retained_input('outgoing',refs);P=phase['coordinates']['lift'];rep=phase['representation'];n=106
    e=data['coefficients'];Pi=data['canonical_momentum_target'];t=data['coordinate_time'].item();raw=P@e
    params=md['action_parameters']
    if params['surface_gamma']is not None:raise ValueError('this affine consumer requires the retained unassigned-tension base')
    args=(phase['arrays']['initial_pair'],phase['arrays']['reference_pair'],rep)
    a=high_precision_original_constitutive_action(raw,t,*args,decimal_precision=precision,**params)
    r=a['gradient'][n:]-np.r_[Pi,np.zeros(40,complex)]
    if np.max(abs(r))>md['tolerance']:raise ValueError('actual endpoint original canonical compatibility required')
    area=original_endpoint_area_coefficient(raw,P);energy=held_endpoint_hamiltonian_area_coefficients(e,Pi,a,area)
    clock=holomorphic_child_explicit_clock_application(raw,t,*args,**params)
    frame=canonical_central_frame(raw,rep);C=frame['named_frame_covectors'];D=a['hessian'][n:,n:]
    K=np.block([[D,C.T],[C,np.zeros((2,2),complex)]])
    scale=1/np.sqrt(np.maximum(np.max(abs(K),axis=1),np.finfo(float).tiny))
    def solve(rhs):return scale*np.linalg.solve(scale[:,None]*K*scale[None,:],scale*rhs)
    parameter_rhs=-np.r_[area['gradient'][n:],np.zeros(2,complex)];parameter=solve(parameter_rhs)
    tangent_rhs=np.r_[clock['canonical_tangent_rhs'],np.zeros(2,complex)];tangent=solve(tangent_rhs)
    # On the actual coordinate canonical tangent, all remaining action
    # residual contacts are explicit; a small row tolerance is not a work
    # error enclosure when the tangent is large.
    contact=-r@tangent[:-2]
    canonical_energy_rate=-clock['value_clock_first']+contact
    out.mkdir(parents=True);p=out/'application.npz'
    _compressed_npz(p,dict(coefficients=e,raw_fields=raw,canonical_momentum_target=Pi,coordinate_time=np.array(t),
        original_constitutive_rows=r,original_action_gradient=a['gradient'],original_action_Hessian=a['hessian'],
        area_action_value=np.array(area['value']),area_action_gradient=area['gradient'],area_action_Hessian=area['hessian'],
        area_original_Lx=area['position_force'],area_original_Pi=area['Legendre_cotangent'],area_original_Ly=area['algebraic_source'],
        area_fixed_Pi_Hamiltonian_coefficient=np.array(energy['fixed_target_Pi_area_coefficient']),
        area_Legendre_Pi_Hamiltonian_coefficient=np.array(energy['same_state_Legendre_Pi_area_coefficient']),
        base_Hamiltonian=np.array(energy['base']),fixed_x_Pi_area_constitutive_response=parameter[:-2],
        area_named_frame_reactions=parameter[-2:],area_framed_parameter_rows=K@parameter-parameter_rhs,
        area_original_parameter_rows=D@parameter[:-2]+area['gradient'][n:],
        literal_area_gauge_source_pairing=frame['literal_generators'].T@area['gradient'][n:],
        coordinate_canonical_tangent=tangent[:-2],tangent_frame_reactions=tangent[-2:],
        original_tangent_rows=D@tangent[:-2]-clock['canonical_tangent_rhs'],
        explicit_action_clock_first=np.array(clock['value_clock_first']),
        canonical_energy_residual_contact=np.array(contact),canonical_energy_coordinate_rate=np.array(canonical_energy_rate)))
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for f in(Path(__file__),'tests/test_muon_complex_endpoint_area_action.py'):
        f=Path(f);f=f if f.is_absolute()else ROOT/f;refs[f.relative_to(ROOT).as_posix()]=sha256(f.read_bytes()).hexdigest()
    if any(sha256((ROOT/r).read_bytes()).hexdigest()!=h for r,h in refs.items()):raise RuntimeError('same area/clock action source changed')
    cj=lambda z:[float(complex(z).real),float(complex(z).imag)]
    result=dict(classification='EVALUATED_SAME_COMPLEX_ENDPOINT_UNASSIGNED_AREA_AND_CANONICAL_CLOCK_ACTION',input_hashes=refs,
        archives={p.name:dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())},
        base_Hamiltonian=cj(energy['base']),area_action_value_per_gamma=cj(area['value']),
        fixed_target_Pi_Hamiltonian_per_gamma=cj(energy['fixed_target_Pi_area_coefficient']),
        same_state_Legendre_Pi_Hamiltonian_per_gamma=cj(energy['same_state_Legendre_Pi_area_coefficient']),
        area_Pi_coefficient_norm=float(np.linalg.norm(area['Legendre_cotangent'])),area_Ly_coefficient_max=float(np.max(abs(area['algebraic_source']))),
        area_full252_Hessian_norm=float(np.linalg.norm(area['hessian'])),
        fixed_x_Pi_parameter_velocity_algebraic_response_norm=float(np.linalg.norm(parameter[:-2])),
        original_area_parameter_rows_max=float(np.max(abs(D@parameter[:-2]+area['gradient'][n:]))),
        framed_area_parameter_rows_max=float(np.max(abs(K@parameter-parameter_rhs))),
        explicit_action_coordinate_clock_first=cj(clock['value_clock_first']),canonical_energy_coordinate_rate=cj(canonical_energy_rate),
        canonical_energy_residual_contact=cj(contact),coordinate_canonical_tangent_norm=float(np.linalg.norm(tangent[:-2])),
        original_tangent_rows_max=float(np.max(abs(D@tangent[:-2]-clock['canonical_tangent_rhs']))),
        surface_gamma_assigned=False,original_target_Pi_or_state_changed=False,area_present_as_symbolic_coefficient=True,
        fixed_state_stationarity_for_nonzero_gamma_claimed=False,action_parameters=params,
        required_coupled_parameter_consumer='original inherited two-arm birth/attachment parameter response and canonical Pi reset, followed by full endpoint Gy/Legendre solve; the held-state Pi_area alone does not remove Ly_area',
        physical_energy_first_hit_or_Pauli_bound=False,
        error_scope='binary analytic full252 area twojet and same-action precise-tail endpoint application; framed parameter/tangent solves and residual contacts are diagnostics, not parameter branch stationarity or physical error enclosure')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='held_endpoint_area_clock_complete',area_action_value_per_gamma=result['area_action_value_per_gamma'],
        area_Ly_max=result['area_Ly_coefficient_max'],energy=result['base_Hamiltonian'],result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--endpoint-folder',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--precision',type=int,default=60)
    a=p.parse_args();materialize(a.endpoint_folder,a.output,a.precision)
