"""Apply reset-admissible local action basis and its canonical evolution."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_reset_constrained_canonical_variation import (
    canonical_variation_embedding,signed_reset_constrained_trial,canonical_variation_evolution)
from bhsm.interface.muon_holomorphic_two_arm_reset import holomorphic_moving_trace
from bhsm.interface.muon_complex_normal_trace_motion import proper_normal_trace_motion
from bhsm.interface.aether_full_reset_action_jacobian import _attachment_jacobian_at_order,_trace_jacobian_at_order,_symmetric_power
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def clean(x):
    if isinstance(x,dict):return{k:clean(v)for k,v in x.items()}
    if isinstance(x,(list,tuple)):return[clean(v)for v in x]
    if isinstance(x,(complex,np.complexfloating)):return[float(x.real),float(x.imag)]
    if isinstance(x,np.ndarray):return clean(x.tolist())
    if isinstance(x,np.generic):return x.item()
    return x


def materialize(normal_folder,reset_folder,output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve every canonical source/trial application')
    refs={}
    def receipt(folder):
        p=ROOT/folder/'result.json';b=p.read_bytes();refs[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest();return json.loads(b)
    def archive(folder,md,name):
        p=ROOT/folder/name;b=p.read_bytes()
        if sha256(b).hexdigest()!=md['archives'][name]['sha256']:raise ValueError('same actual canonical source archive changed')
        refs[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    nm,rm=receipt(normal_folder),receipt(reset_folder);refs.update(nm['input_hashes']);refs.update(rm['input_hashes'])
    inputs=archive(normal_folder,nm,'same_action_inputs.npz');clock=archive(normal_folder,nm,'clock_and_joint_tangent.npz')
    reset=archive(reset_folder,rm,'application.npz')
    last=rm['history'][-1]['iteration'];checkpoint=archive(reset_folder,rm,f'iteration_{last:04d}.npz')
    if not np.array_equal(checkpoint['raw_pair'],reset['raw_pair']):raise ValueError('actual final Ward quotient checkpoint required')
    quotient=checkpoint['independent_original_rows']
    if quotient.shape!=(224,):raise ValueError('original full224 named Ward quotient required')
    if not np.array_equal(inputs['raw_pair'],reset['raw_pair'])or not np.array_equal(inputs['reference_pair'],reset['reference_pair']):
        raise ValueError('same actual raw/reference reset candidate required')
    H=inputs['Hessian504'];G=inputs['gradient504'];Ht=clock['Hessian_coordinate_time_first'];Ha=inputs['area_Hessian504'];Ga=inputs['area_gradient504']
    x=np.r_[np.arange(106),252+np.arange(106)];v=x+106;y=np.r_[np.arange(212,252),np.arange(464,504)]
    phase=np.r_[v,y];F=inputs['named_temporal_frames'];J=reset['original226_Jacobian']
    groups={name:(record if isinstance(record,dict)else dict(indices=record))for name,record in rm['groups'].items()}
    def ids(names):return np.array([j for name in names for j in groups[name]['indices']],int)
    trace_ids=ids(('gauge_trace','Higgs_trace','moving_geometric_trace','normal_position_trace'))
    ly_ids=ids(('incoming_constraints','child_constraints'));natural_ids=np.array([i for i in range(226)if i not in set(np.r_[trace_ids,ly_ids])])
    if (len(trace_ids),len(ly_ids),len(natural_ids))!=(73,80,73):raise ValueError('exact original reset row role counts required')
    N=np.zeros(504,complex);N[x[:106]]=inputs['parent_proper_and_attachment_trace'][-1]
    static=np.zeros((8,504),complex);static[:,x]=inputs['named_static_radial_frames'][:,:212];static[:,y]=inputs['named_static_radial_frames'][:,212:]
    # The four child Ar conditions are already implied by the literal
    # gauge trace and parent Ar conditions; their full images are audited.
    C=static[:4];B=J[trace_ids]
    rawrate=(inputs['master_lift']@clock['canonical_full_master_coordinate_rate']).reshape(2,268)
    normal_motion=proper_normal_trace_motion(inputs['raw_pair'][0],inputs['one_lift'],rawrate[0]);Nt=np.zeros(504,complex)
    Nt[x[:106]]=normal_motion['trace_coordinate_time_first'][-1]
    weight_path=next(Path(p)for p in refs if p.endswith('true_phase_projection_inputs.npz'))
    if sha256((ROOT/weight_path).read_bytes()).hexdigest()!=refs[weight_path.as_posix()]:raise ValueError('same original weights changed')
    with np.load(ROOT/weight_path,allow_pickle=False)as z:w=z['state_weights'];norm=z['normalization_coordinates']
    T0=np.vstack((_trace_jacobian_at_order(12),_attachment_jacobian_at_order(12,norm)[1]))
    normalizer=_symmetric_power(T0@np.diag(1/w[:37]**2)@T0.T,-.5);Jt=np.zeros_like(J)
    trace_t=np.zeros((4,536),complex)
    for arm in range(2):
        tr=holomorphic_moving_trace(inputs['raw_pair'][arm]);block=np.einsum('aij,j->ai',tr['second'],rawrate[arm,:100])
        trace_t[:,arm*268:arm*268+100]=(-1 if arm==0 else 1)*block
    Jt[groups['moving_geometric_trace']['indices']]=normalizer@trace_t@inputs['master_lift']
    out.mkdir(parents=True);archives={};summaries={}
    def save(name,arrays):
        p=out/name;_compressed_npz(p,arrays)
        if p.stat().st_size>10*1024**2:raise ValueError('split full canonical action/source outputs')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    for name,Gs,Gst,source,amplitude in(
        ('normal_basis',np.zeros(504,complex),np.zeros(504,complex),np.zeros(226,complex),1),
        ('area_source',Ga,Ha@clock['canonical_full_master_coordinate_rate'],reset['area_parameter_source'],0)):
        print(json.dumps(dict(stage='reset_admissible_canonical_basis',case=name)),flush=True)
        a=canonical_variation_embedding(H,x,v,y,F,source_gradient=Gs,hessian_time_first=Ht,source_gradient_time_first=Gst)
        t=signed_reset_constrained_trial(H,a,B,N,C,normal_amplitude=amplitude);e=canonical_variation_evolution(H,a,t)
        delta=t['original_master_direction'];response=J@delta+source
        phase_error=np.r_[H[v]@delta+Gs[v]-t['canonical_coordinates'][212:],H[y]@delta+Gs[y]]
        # This is the exact duplicate audit, not another80 KKT borders.
        actual_ly=H[y]@delta+Gs[y]
        source_scale=np.r_[1/w[74:98],np.ones(16)];scale=np.r_[source_scale,source_scale]
        ly_alias_difference=response[ly_ids]-scale*actual_ly
        trace_time_response=Jt[trace_ids]@delta+J[trace_ids]@e['original_master_direction_time_first']
        summaries[name]=dict(normal_amplitude=t['normal_amplitude'],original_KKT_rows_max=float(np.max(abs(t['original_rows']))),
            original_kinematic_trace_rows_max=float(np.max(abs(response[trace_ids]))),
            original_Ly_rows_max=float(np.max(abs(actual_ly))),original_scaled_Ly_alias_difference_max=float(np.max(abs(ly_alias_difference))),
            original_canonical_compatibility_max=float(np.max(abs(t['original_canonical_compatibility']))),
            all8_named_static_frames_max=float(np.max(abs(static@delta))),
            natural_force_rows_max=float(np.max(abs(response[natural_ids]))),
            natural_group_responses={key:response[record['indices']]for key,record in groups.items()if set(record['indices'])<=set(natural_ids)},
            normal_KKT_reaction=t['natural_normal_KKT_reaction'],signed_action_quadratic=t['signed_action_quadratic'],
            signed_action_source_pairing=t['signed_action_source_pairing'],
            canonical_trial_norm=float(np.linalg.norm(t['canonical_coordinates'])),original_master_trial_norm=float(np.linalg.norm(delta)),
            KKT_balanced_condition=t['balanced_condition'],phase_balanced_condition=a['balanced_condition'],
            original_canonical_embedding_rows_max=float(np.max(abs(a['original_embedding_rows']))),
            original_phase_source_rows_max=float(np.max(abs(a['original_source_rows']))),
            momentum_variational_rate_identity_max=float(np.max(abs(e['original_momentum_rate_identity']))),
            algebraic_variational_time_first_max=float(np.max(abs(e['original_algebraic_time_first']))),
            kinematic_trace_time_first_max=float(np.max(abs(trace_time_response))),
            proper_normal_amplitude_time_first=Nt@delta+N@e['original_master_direction_time_first'],
            canonical_compatibility_time_first_max=float(np.max(abs(e['original_compatibility_time_first']))),
            natural_rows_are_response_not_constrained_zero=True,
            initial_delta_p_selected_only_by_conditional_local_action_KKT=True,
            physical_external_state_or_boundary_load_selected=False)
        save(name+'_phase_elimination.npz',{k:a[k]for k in('original_phase_saddle','canonical_rhs_map','source_rhs','canonical_phase_solution_map',
            'canonical_phase_source_solution','original_embedding_rows','original_source_rows','original_embedding_time_rows','original_source_time_rows')})
        save(name+'_canonical_embedding.npz',{k:a[k]for k in('embedding','source_embedding','embedding_time_first','source_embedding_time_first',
            'compatibility_map','compatibility_source','compatibility_time_first','compatibility_source_time_first')})
        save(name+'_signed_action_KKT.npz',{k:t[k]for k in('original_KKT','original_rhs','solution','original_rows','signed_canonical_action_Hessian',
            'canonical_source_force','constraint_rows','constraint_rhs','constraint_residual')})
        save(name+'_original_trial_and_force.npz',dict(original_master_direction=delta,canonical_trial=t['canonical_coordinates'],
            original226_response=response,natural_force_rows=response[natural_ids],natural_force_indices=natural_ids,
            kinematic_trace_indices=trace_ids,Ly_indices=ly_ids,original_phase_equation_error=phase_error,
            full8_static_frame_response=static@delta,full224_Ward_quotient_indices=quotient,
            named_Ward_response=reset['Ward_rows']@response,scaled_Ly_alias_difference=ly_alias_difference,
            source_original226=source,source_gradient504=Gs,source_gradient_time_first504=Gst))
        save(name+'_canonical_variational_evolution.npz',dict(**{k:val for k,val in e.items()if isinstance(val,np.ndarray)},
            original_kinematic_trace_time_first=trace_time_response,original_trace_Jacobian_time_first=Jt[trace_ids],
            proper_normal_row=N,proper_normal_row_time_first=Nt,
            direct_kinematic_trace_source=np.zeros(73,complex),direct_kinematic_trace_source_time_first=np.zeros(73,complex)))
        print(json.dumps(clean(dict(stage='canonical_basis_complete',case=name,**summaries[name]))),flush=True)
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for p in(Path(__file__),'tests/test_muon_reset_constrained_canonical_variation.py'):
        p=Path(p);p=p if p.is_absolute()else ROOT/p;refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise ValueError('same variational source changed')
    result=dict(classification='EVALUATED_RESET_ADMISSIBLE_CONDITIONAL_CANONICAL_ACTION_SOURCE_BASIS_AND_EVOLUTION',
        archives=archives,input_hashes=refs,action_parameters=rm['action_parameters'],applications=summaries,
        original_base226_residual=float(np.max(abs(reset['original226_rows']))),original_reset_guard_passed=False,
        original80_Gauss_rows_enter_once_through_phase_elimination=True,
        original73_position_trace_rows_bordered=True,original73_natural_rows_retained_as_force_readout=True,
        named4_phase_frames_retained=True,named_static_parent4_independent_child4_audited_through_trace=True,
        analytic_transpose_signed_action_not_Euclidean_minimum_norm=True,
        source_and_embedding_clock_motion_count=1,
        held_gamma_direct_trace_source_zero=True,moving_event_source_not_replaced_by_zero=True,
        conditional_local_Lagrangian_KKT_not_chronological_Jacobi_boundary_response=True,
        subsequent_actual_canonical_variational_vector_evaluated=True,
        physical_normal_mode_or_resistance_or_event_cutoff_selected=False,
        no_pointwise_v_equals_iomega_x_imposed=True,
        gamma_source_held_parameter_partial_not_physical_gamma_assignment=True,
        error_scope='binary same-action canonical/conditional signed-KKT solves and existing finite Hdot; all original rows and natural reactions exported, without action/eigensystem/continuum/domain enclosure')
    p=out/'result.json';p.write_text(json.dumps(clean(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='reset_constrained_canonical_source_application_complete',result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--normal-folder',type=Path,default=Path('artifacts/muon_complex_paired_normal_action_20261012/run_1'))
    p.add_argument('--reset-folder',type=Path,default=Path('artifacts/muon_coupled_complex_two_arm_reset_20261012/continued_run_1'))
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();materialize(a.normal_folder,a.reset_folder,a.output)
