"""Apply paired complex normal trial and reference-clock Jacobi contacts."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_two_arm_action import holomorphic_two_arm_action
from bhsm.interface.muon_complex_coupled_reset_continuation import coupled_reset_application
from bhsm.interface.muon_complex_paired_normal_action import (paired_complex_normal_application,
    full_joint_canonical_tangent,chronological_jacobi_coefficient_contact)
from bhsm.interface.muon_holomorphic_joint_reference_clock import joint_reference_explicit_clock
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def _json(x):
    if isinstance(x,dict):return{k:_json(v)for k,v in x.items()}
    if isinstance(x,(list,tuple)):return[_json(v)for v in x]
    if isinstance(x,(complex,np.complexfloating)):return[float(x.real),float(x.imag)]
    if isinstance(x,np.ndarray):return _json(x.tolist())
    if isinstance(x,np.generic):return x.item()
    return x


def materialize(source_folder,output,difference_step):
    source=ROOT/source_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve earlier same-action normal applications')
    rb=(source/'result.json').read_bytes();md=json.loads(rb);refs=dict(md['input_hashes'])
    refs[(source/'result.json').relative_to(ROOT).as_posix()]=sha256(rb).hexdigest()
    p=source/'application.npz';digest=sha256(p.read_bytes()).hexdigest()
    if digest!=md['archives'][p.name]['sha256']:raise ValueError('actual coupled reset candidate changed')
    refs[p.relative_to(ROOT).as_posix()]=digest
    with np.load(p,allow_pickle=False)as z:saved={k:z[k].copy()for k in z.files}
    input_path=next(Path(p)for p in refs if p.endswith('true_phase_projection_inputs.npz'))
    if sha256((ROOT/input_path).read_bytes()).hexdigest()!=refs[input_path.as_posix()]:raise ValueError('owned normal weights changed')
    with np.load(ROOT/input_path,allow_pickle=False)as z:weights=z['state_weights'].copy();norm=z['normalization_coordinates'].copy()
    phase,_=retained_input('outgoing',refs);rep=phase['representation'];params=md['action_parameters']
    raw,reference=saved['raw_pair'],saved['reference_pair']
    print(json.dumps(dict(stage='same_complex_pair_normal_action',reset_rows_max=float(np.max(abs(saved['original226_rows']))))),flush=True)
    base=coupled_reset_application(raw,reference,rep,weights,norm,action_parameters=params,compute_jacobian=False)
    a=base['action'];normal=paired_complex_normal_application(a['hessian'],a['parent']['hessian'],a['area_Hessian_per_gamma'],raw,rep)
    clock=joint_reference_explicit_clock(raw,reference,rep,a,nu_squared_action=params['nu_squared_action'])
    eta=a['master_lift'].T@raw.reshape(-1)
    tangent=full_joint_canonical_tangent(a['gradient'],a['hessian'],eta,base['named_frame_map'],gradient_clock_first=clock['gradient_clock_first'])
    mw=abs(a['master_lift'].T)@np.tile(np.r_[weights,np.ones(170)],2)
    rate=tangent['full_master_coordinate_rate'];magnitude=float(np.max(abs(mw*rate)));unit=rate/magnitude
    ref_unit=clock['reference_raw_coordinate_rate']/magnitude
    print(json.dumps(dict(stage='joint_normal_canonical_tangent',tangent_norm=float(np.linalg.norm(rate)),
        original_rows_max=float(np.max(abs(tangent['original_rows']))),reference_clock_norm=float(np.linalg.norm(clock['gradient_clock_first'])))),flush=True)
    def time_hessian(h):
        plus=holomorphic_two_arm_action((a['master_lift']@(eta+h*unit)).reshape(2,268),reference+h*ref_unit,rep,**params)['hessian']
        minus=holomorphic_two_arm_action((a['master_lift']@(eta-h*unit)).reshape(2,268),reference-h*ref_unit,rep,**params)['hessian']
        return magnitude*(plus-minus)/(2*h)
    Ht=time_hessian(difference_step);control=time_hessian(difference_step/2)
    order=normal['ordering'];contact=chronological_jacobi_coefficient_contact(Ht[np.ix_(order,order)],212)
    contact_control=chronological_jacobi_coefficient_contact(control[np.ix_(order,order)],212)
    freq=normal['frequency'];kin=normal['kinetic'];gamma=normal['area_frequency_parameter'];l=normal['child_trace']['induced_lapse']
    sectors=normal['frequency_sector_pairings']['sector_taylor'];phase_ids=np.arange(212,504)
    left,right=kin['left'][:292],kin['right'][:292]
    kinetic_sectors={name:l*(left@H[np.ix_(phase_ids,phase_ids)]@right)for name,H in
        dict(parent=normal['parent_sector_Hessian'],inherited_child=normal['ordered_hessian']-normal['parent_sector_Hessian']).items()}
    # Project the actual reached changing-coefficient contact, preserving
    # the independently solved left at each frequency order.
    u=freq['right_taylor'][:292];v=freq['left_taylor'][:292]
    reached_contact=np.array([sum(v[:,i]@contact[j]@u[:,k-i-j]for i in range(k+1)for j in range(k-i+1))for k in range(3)])
    reached_contact_control=np.array([sum(v[:,i]@contact_control[j]@u[:,k-i-j]for i in range(k+1)for j in range(k-i+1))for k in range(3)])
    out.mkdir(parents=True);archives={}
    def save(name,arrays):
        p=out/name;_compressed_npz(p,arrays)
        if p.stat().st_size>10*1024**2:raise RuntimeError('split complete normal action outputs')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    def arrays(obj):return{k:v for k,v in obj.items()if isinstance(v,np.ndarray)}
    save('same_action_inputs.npz',dict(raw_pair=raw,reference_pair=reference,gradient504=a['gradient'],Hessian504=a['hessian'],
        parent_gradient252=a['parent']['gradient'],parent_Hessian252=a['parent']['hessian'],
        area_gradient504=a['area_gradient_per_gamma'],area_Hessian504=a['area_Hessian_per_gamma'],
        original226_reset_rows=base['residual'],one_lift=a['one_lift'],master_lift=a['master_lift'],
        ordered_indices=order,parent_proper_and_attachment_trace=normal['parent_trace']['trace'],
        child_proper_and_attachment_trace=normal['child_trace']['trace'],physical_gluing=normal['physical_gluing'],
        named_static_radial_frames=normal['named_static_radial_frames'],named_temporal_frames=normal['named_temporal_frames']))
    save('frequency_application.npz',arrays(freq));save('frequency_area_response.npz',arrays(gamma));save('true_Lyy_kinetic_application.npz',arrays(kin))
    save('clock_and_joint_tangent.npz',dict(**arrays(clock),**{'canonical_'+k:v for k,v in arrays(tangent).items()},
        Hessian_coordinate_time_first=Ht,Hessian_coordinate_time_first_control=control,
        Jacobi_coefficient_contact=contact,Jacobi_coefficient_contact_control=contact_control,
        projected_Jacobi_contact_taylor=reached_contact,projected_Jacobi_contact_control_taylor=reached_contact_control,
        parent_frequency_sector=sectors['parent'],inherited_child_frequency_sector=sectors['inherited_child'],
        parent_kinetic_sector=np.array(kinetic_sectors['parent']),inherited_child_kinetic_sector=np.array(kinetic_sectors['inherited_child'])))
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for p in (Path(__file__),'tests/test_muon_complex_paired_normal_action.py','tests/test_muon_holomorphic_joint_reference_clock.py'):
        p=Path(p);p=p if p.is_absolute()else ROOT/p;refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('normal action producer changed during application')
    R=freq['proper_restoring'];I=kin['proper_inertia'];If=freq['proper_frequency_inertia'];childR=-sectors['inherited_child'][0]/l;childI=kinetic_sectors['inherited_child']
    data=dict(classification='EVALUATED_COMPLEX_CURRENT_PAIR_NORMAL_ACTION_AREA_AND_CHRONOLOGICAL_JACOBI_CONTACT',input_hashes=refs,
        archives=archives,action_parameters=params,original226_reset_rows_max=float(np.max(abs(base['residual']))),
        original_reset_guard_passed=False,parent_proper_normal=normal['parent_trace'],child_proper_normal=normal['child_trace'],
        frozen_frequency_restoring=R,frozen_frequency_inertia=If,true_Lyy_kinetic_inertia=I,
        frozen_frequency_area_parameter_restoring=gamma['proper_restoring_parameter'],
        frozen_frequency_area_parameter_inertia=gamma['proper_frequency_inertia_parameter'],
        true_Lyy_kinetic_area_parameter_inertia=kin['proper_inertia_gamma_parameter'],
        signed_frequency_sectors=sectors,signed_kinetic_sectors=kinetic_sectors,
        child_plus_trial_restoring=childR,child_plus_trial_kinetic_inertia=childI,
        diagnostic_complex_child_I_over_R=childI/childR,diagnostic_complex_common_I_over_R=I/R,
        frequency_original_rows_max=float(np.max(abs(freq['right_original_rows']))),
        frequency_transpose_rows_max=float(np.max(abs(freq['left_original_rows']))),
        frequency_sector_identity_max=float(np.max(abs(normal['frequency_sector_pairings']['total_minus_reduced_response']))),
        gamma_frequency_original_rows_max=float(np.max(abs(gamma['parameter_original_rows']))),
        kinetic_original_rows_max=float(np.max(abs(kin['right_original_rows']))),
        kinetic_transpose_rows_max=float(np.max(abs(kin['left_original_rows']))),
        frequency_balanced_condition=freq['balanced_condition'],kinetic_balanced_condition=kin['balanced_condition'],
        exact_reference_only_value_clock_first=clock['value_clock_first'],
        exact_reference_only_gradient_clock_norm=float(np.linalg.norm(clock['gradient_clock_first'])),
        joint_canonical_tangent_norm=float(np.linalg.norm(rate)),joint_canonical_framed_rows_max=float(np.max(abs(tangent['original_rows']))),
        joint_canonical_unframed_rows_max=float(np.max(abs(tangent['unframed_original_rows']))),
        joint_canonical_frame_reactions=tangent['frame_reactions'],
        projected_chronological_Jacobi_contact_taylor=reached_contact,
        projected_Jacobi_contact_step_difference=reached_contact-reached_contact_control,
        Hessian_time_first_step_relative_difference=float(np.linalg.norm(Ht-control)/max(np.linalg.norm(control),np.finfo(float).tiny)),
        area_law='gamma=alpha_FSC*c^(-m/2); gamma_c=-m*gamma/(2c); gamma_cc=(m/2)*(m/2+1)*gamma/c^2',
        formation_relation='c*r(gamma(c),same corrected base,selected section/domain)-i(gamma(c),same base,section/domain)=0',
        held_state_local_linear_gamma_formation_load='(c*R0-I0)+gamma(c)*(c*R_gamma-I_gamma)+O(gamma(c)^2); inverse response is not affine in gamma',
        membrane_dimension_M8=7,alpha_FSC_or_gamma_or_c_assigned=False,
        trace_clock_held_in_gamma_response=True,proper_normal_gluing_before_elimination=True,
        full80_multiplier_rows_and212_dynamic_rows_retained=True,
        joint_momentum_not_ownparent_momentum=True,actual_parent_partial_clock_not_added_twice=True,
        implicit_chart_branch_used=True,physical_selected_normal_or_first_hit_or_formation_cutoff=False,
        dynamical_consumer='Lx-d_t Lv with -dotLvx, -dotLvv, -dotLvy and moving proper-normal/gluing/lapse jets; actual joint canonical tangent plus reference-only clock executed here; selected event/domain and corrected base still must be applied',
        error_scope='binary same-action polynomial/phase solves and exact analytic first reference-clock derivative; finite directional Hessian time jet and two-step projected comparison only, with no producer/evaluation/physical-domain enclosure')
    # Trace arrays live in the compact input archive, keeping the receipt legible.
    for name in ('parent_proper_normal','child_proper_normal'):data[name]={k:v for k,v in data[name].items()if not isinstance(v,np.ndarray)}
    p=out/'result.json';p.write_text(json.dumps(_json(data),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='same_complex_pair_normal_action_complete',proper_R=_json(R),proper_I=_json(I),
        child_R=_json(childR),child_I=_json(childI),projected_Jacobi_contact=_json(reached_contact),
        result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-folder',type=Path,
        default=Path('artifacts/muon_coupled_complex_two_arm_reset_20261012/continued_run_1'))
    p.add_argument('--output',type=Path,required=True);p.add_argument('--difference-step',type=float,default=2e-5)
    a=p.parse_args();materialize(a.source_folder,a.output,a.difference_step)
