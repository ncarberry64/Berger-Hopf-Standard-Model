"""One bounded full123/material25 alternative on the internal past control."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from evaluate_muon_fixed_parent_finite_shooting import clean
from bhsm.interface.muon_holomorphic_two_arm_action import holomorphic_two_arm_action
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_material_rate_canonical_reduction import fixed_position_material_rate_chart,eliminate_material_rate_quadratic_fields
from bhsm.interface.muon_coupled_phase_trace_projection import _solve
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def run(output,max_iterations,max_backtracks):
    out=ROOT/output;pins={};archives={}
    if out.exists():raise FileExistsError('preserve every bounded positive family attempt')
    def read(p,md=None):
        p=ROOT/p;blob=p.read_bytes();h=sha256(blob).hexdigest();pins[p.relative_to(ROOT).as_posix()]=h
        if p.suffix=='.json':return json.loads(blob)
        if md is not None and h!=md['archives'][p.name]['sha256']:raise ValueError('same actual positivegamma checkpoint required')
        with np.load(p)as z:return{k:z[k].copy()for k in z.files}
    sf=Path('artifacts/muon_gamma_incoming_cauchy_20261012/run_2');md=read(sf/'result.json')
    seed=read(sf/'unchanged_incoming_initial_application.npz',md)
    past=read(Path('artifacts/muon_changing_canonical_source_20261012/run_3/incoming_0001_actual_endpoint.npz'))
    phase,_=retained_input('incoming',pins);rep=phase['representation'];P=phase['coordinates']['lift']
    eta=seed['master'].copy();Pi=seed['canonical_momentum_target'].copy();fixed=eta[:106].copy()
    if not np.array_equal(fixed,seed['unchanged_input_x'])or not np.array_equal(Pi,seed['unchanged_input_Pi']):
        raise ValueError('same INTERNAL fixedpast x/Pi control required')
    frame=canonical_central_frame(P@eta,rep);reference=past['endpoint_master'][106:].copy()
    params=md['action_parameters'];chart=fixed_position_material_rate_chart((P@eta)[:100])
    T=chart['velocity_algebraic_lift'];Ti=chart['velocity_algebraic_inverse'];material=Ti@eta[106:]
    g=chart['nonlinear_geometry_indices'];out.mkdir(parents=True)
    def action(e):
        raw=P@e;pair=np.stack((raw,raw))
        return holomorphic_two_arm_action(pair,pair,rep,**params)['parent']
    def apply(w):
        f=material.copy();f[g]=w
        return eliminate_material_rate_quadratic_fields(np.r_[fixed,T@f],Pi,action,frame,chart,frame_reference=reference)
    def save(name,data):
        p=out/name;_compressed_npz(p,{k:v for k,v in data.items()if isinstance(v,np.ndarray)})
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    w=material[g].copy();print(json.dumps(dict(stage='positive_parent_full123_elimination')),flush=True)
    a=apply(w);scale=1/np.maximum(np.max(abs(a['reduced_geometry_Jacobian']),axis=1),1.)
    history=[];status='BOUNDED_MATERIAL25_ITERATION_LIMIT'
    for iteration in range(max_iterations+1):
        r=a['original_coordinate_constitutive_rows'];R=a['reduced_geometry_rows'];J=a['reduced_geometry_Jacobian']
        merit=float(np.linalg.norm(scale*R));original=a['original_action'];e=a['original_coefficients']
        energy=e[106:212]@original['gradient'][106:212]-original['value']
        rec=dict(iteration=iteration,original146_max=float(np.max(abs(r))),
            original_momentum_max=float(np.max(abs(r[:106]))),original_Gauss_max=float(np.max(abs(r[106:]))),
            material25_merit=merit,field121_max=float(np.max(abs(a['original_field_rows']))),
            frame_reaction_max=float(np.max(abs(a['field_frame_reactions']))),
            own_parent_energy=clean(energy),own_parent_action_value=clean(original['value']),
            field_hessian_identity=a['field_hessian_quadratic_identity_relative_max'],
            field_affine_identity=a['field_gradient_affine_identity_relative_max'])
        history.append(rec)
        save(f'iteration_{iteration:04d}.npz',dict(original_master=e,raw=P@e,original146_rows=r,
            material25_rows=R,material25_Schur=J,field_frame_reactions=a['field_frame_reactions'],
            all121_original_rows=a['original_field_rows'],all_framed_field_rows=a['framed_field_rows'],
            own_parent_energy=np.array(energy),own_parent_action_value=np.array(original['value'])))
        print(json.dumps(clean(dict(stage='positive_parent_material25_Newton',**rec)),sort_keys=True),flush=True)
        if np.max(abs(r))<=2e-10 and np.max(abs(a['framed_field_rows'][-2:]))<=2e-10:
            status='ALL_ORIGINAL146_INTERNAL_CONTROL_TOLERANCE';break
        if iteration==max_iterations:break
        dw=_solve(J,-R)[0];rec['material25_step_norm']=float(np.linalg.norm(dw));rec['trials']=[];accepted=False
        for k in range(max_backtracks):
            damping=2.**(-k);wt=w+damping*dw
            try:
                at=apply(wt);new=float(np.linalg.norm(scale*at['reduced_geometry_rows']));good=np.isfinite(new)and new<merit
            except(ValueError,FloatingPointError,OverflowError,np.linalg.LinAlgError,ArithmeticError)as err:
                new=None;good=False;error=str(err)
            rec['trials'].append(dict(damping=damping,merit=new,accepted=bool(good),
                **({}if new is not None else dict(error=error))))
            if good:w,a=wt,at;accepted=True;break
        if not accepted:status='MATERIAL25_CONTROL_LINE_SEARCH_STALL';break
    e=a['original_coefficients'];own=a['original_action'];r=a['original_coordinate_constitutive_rows']
    # Retain the direct area action at the actual final point, including
    # Hamiltonian distinction; do not confuse L_parent with E_parent.
    raw=P@e;full=holomorphic_two_arm_action(np.stack((raw,raw)),np.stack((raw,raw)),rep,**params)
    E=e[106:212]@own['gradient'][106:212]-own['value']
    gamma=params['surface_gamma'];Ga=full['area_gradient_per_gamma'][:252];La=full['area_value_per_gamma']/2
    area_legendre=e[106:212]@Ga[106:212]-La
    save('application.npz',dict(original_master=e,raw=raw,canonical_momentum_target=Pi,
        unchanged_internal_input_x=fixed,unchanged_internal_input_Pi=Pi,original146_rows=r,
        material25_rows=a['reduced_geometry_rows'],material25_Schur=a['reduced_geometry_Jacobian'],
        full123_saddle=a['field_frame_saddle'],frame_reactions=a['field_frame_reactions'],
        original_frame_reference=reference,action_gradient=own['gradient'],action_Hessian=own['hessian'],
        action_value=np.array(own['value']),own_parent_energy=np.array(E),
        area_action_per_gamma=np.array(La),negative_area_action_contact_per_gamma=np.array(-La),
        held_state_area_Legendre_energy_per_gamma=np.array(area_legendre),
        fixed_target_area_energy_contact_per_gamma=np.array(-La),
        actual_gamma_area_action=np.array(gamma*La),actual_gamma_held_Legendre_energy=np.array(gamma*area_legendre),
        coordinate_time=seed['coordinate_time'],material_chart=T))
    for name,m in sorted(sys.modules.items()):
        p=getattr(m,'__file__',None)
        if name.startswith('bhsm.')and p and Path(p).is_relative_to(ROOT):
            p=Path(p);pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    rec=dict(classification='ONE_BOUNDED_POSITIVE_PARENT_MATERIAL25_INTERNAL_PAST_CONTROL',status=status,
        input_hashes=pins,archives=archives,history=history,action_parameters=params,
        original146_max=float(np.max(abs(r))),own_parent_energy=clean(E),
        own_parent_action_value=clean(own['value']),negative_area_action_contact_per_gamma=clean(-La),
        held_state_area_Legendre_energy_per_gamma=clean(area_legendre),
        original_guard=2e-10,same_internal_x_and_Pi=True,
        qdot_field_cross_kept_in_full123_saddle=True,no_transformed_canonical_x_force=True,
        independent_incoming_environment_or_physical_gamma_member_selected=False,
        no_branch_or_gamma_incompatibility_inferred=True,
        error_scope='Original full ownparent action and exactmaterial polynomial reduction at the unchanged internal past x/Pi control. No physical initial-environment, whole formation/exterior/pole or continuum accuracy conclusion.')
    p=out/'result.json';p.write_text(json.dumps(clean(rec),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='positive_parent_material_control_complete',status=status,original146=rec['original146_max'],
        result_sha256=sha256(p.read_bytes()).hexdigest()),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--max-iterations',type=int,default=6);p.add_argument('--max-backtracks',type=int,default=4)
    z=p.parse_args();run(z.output,z.max_iterations,z.max_backtracks)
