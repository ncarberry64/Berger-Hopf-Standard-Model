"""Execute literal joint action/rate second contacts of temporal reset traces."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_endpoint_second_domain_germ import endpoint_trace_first_germ,endpoint_second_from_first_germs
from bhsm.interface.muon_holomorphic_two_arm_action import holomorphic_two_arm_action
from bhsm.interface.muon_holomorphic_joint_reference_clock import joint_reference_explicit_clock
from bhsm.interface.muon_complex_paired_normal_action import full_joint_canonical_tangent
from bhsm.interface.aether_full_reset_action_jacobian import _attachment_jacobian_at_order,_trace_jacobian_at_order,_symmetric_power
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(output,normalized_step):
    source=ROOT/'artifacts/muon_complex_paired_normal_action_20261012/run_1';out=ROOT/output
    if out.exists():raise FileExistsError('preserve every literal second-domain application')
    b=(source/'result.json').read_bytes();md=json.loads(b);refs=dict(md['input_hashes'])
    refs[(source/'result.json').relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
    def load(name):
        p=source/name;b=p.read_bytes();h=sha256(b).hexdigest()
        if h!=md['archives'][name]['sha256']:raise ValueError('same joint germ input changed '+name)
        refs[p.relative_to(ROOT).as_posix()]=h
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    base=load('same_action_inputs.npz');clock=load('clock_and_joint_tangent.npz')
    wp=next(Path(p)for p in refs if p.endswith('true_phase_projection_inputs.npz'))
    if sha256((ROOT/wp).read_bytes()).hexdigest()!=refs[wp.as_posix()]:raise ValueError('original geometry normalizer changed')
    with np.load(ROOT/wp,allow_pickle=False)as z:weights=z['state_weights'];normalization=z['normalization_coordinates']
    phase,_=retained_input('outgoing',refs);rep=phase['representation'];params=md['action_parameters']
    raw,reference=base['raw_pair'],base['reference_pair'];R=base['master_lift'];P=base['one_lift'];eta=R.T@raw.reshape(-1)
    rate=clock['canonical_full_master_coordinate_rate'];ref_rate=clock['reference_raw_coordinate_rate']
    mw=abs(R.T)@np.tile(np.r_[weights,np.ones(170)],2);magnitude=float(np.max(abs(mw*rate)))
    unit=rate/magnitude;ref_unit=ref_rate/magnitude;F=base['named_temporal_frames']
    B=_attachment_jacobian_at_order(12,normalization);T0=np.vstack((_trace_jacobian_at_order(12),B[1]))
    norm=_symmetric_power(T0@np.diag(1/weights[:37]**2)@T0.T,-.5)
    initial=endpoint_trace_first_germ(raw,(R@rate).reshape(2,268),R,P,norm)
    out.mkdir(parents=True);archives={};diagnostics={};results={}
    def maximum(a):return float(np.max(abs(a)))
    def save(name,arrays):
        p=out/name;_compressed_npz(p,arrays)
        if p.stat().st_size>10*1024**2:raise ValueError('split literal full action provenance')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    for label,h in(('primary',normalized_step),('half_step',normalized_step/2)):
        branches={}
        for side,sign in(('plus',1),('minus',-1)):
            print(json.dumps(dict(stage='literal_second_endpoint_domain_branch',step=label,side=side)),flush=True)
            rr=(R@(eta+sign*h*unit)).reshape(2,268);ref=reference+sign*h*ref_unit
            action=holomorphic_two_arm_action(rr,ref,rep,**params)
            explicit=joint_reference_explicit_clock(rr,ref,rep,action,nu_squared_action=params['nu_squared_action'])
            tangent=full_joint_canonical_tangent(action['gradient'],action['hessian'],R.T@rr.reshape(-1),F,
                gradient_clock_first=explicit['gradient_clock_first'])
            r=tangent['full_master_coordinate_rate'];first=endpoint_trace_first_germ(rr,(R@r).reshape(2,268),R,P,norm)
            branches[side]=dict(first=first,rate=r,Hessian=action['hessian'],clock=explicit['gradient_clock_first'])
            key=label+'_'+side
            diagnostics[key]=dict(original_canonical_rows_max=maximum(tangent['original_rows']),
                unframed_canonical_rows_max=maximum(tangent['unframed_original_rows']),
                phase_rate_norm=float(np.linalg.norm(r)),frame_reactions_abs_max=maximum(tangent['frame_reactions']),
                exact_reference_only_gradient_clock_norm=float(np.linalg.norm(explicit['gradient_clock_first'])))
            save(key+'_literal_action_rate.npz',dict(raw_pair=rr,reference_pair=ref,
                full_master_gradient=action['gradient'],full_master_Hessian=action['hessian'],
                explicit_reference_clock_gradient=explicit['gradient_clock_first'],
                original_canonical_saddle=tangent['original_saddle'],original_canonical_rhs=tangent['original_rhs'],
                canonical_solution=tangent['solution'],original_canonical_rows=tangent['original_rows'],
                original_unframed_canonical_rows=tangent['unframed_original_rows'],
                full_master_coordinate_rate=r,**first))
            print(json.dumps(dict(stage='literal_domain_branch_complete',step=label,side=side,**diagnostics[key]),sort_keys=True),flush=True)
        result=endpoint_second_from_first_germs(branches['plus']['first'],branches['minus']['first'],
            branches['plus']['rate'],branches['minus']['rate'],normalized_step=h,rate_magnitude=magnitude)
        result['Hessian_total_time_first']=magnitude*(branches['plus']['Hessian']-branches['minus']['Hessian'])/(2*h)
        result['explicit_reference_clock_gradient_total_time_first']=magnitude*(branches['plus']['clock']-branches['minus']['clock'])/(2*h)
        results[label]=result
    primary=results['primary'];control=results['half_step'];arrays=dict(raw_pair=raw,reference_pair=reference,
        original_master_lift=R,original_one_lift=P,base_full_master_coordinate_rate=rate,
        reference_affine_raw_rate=ref_rate,raw_coordinate_rate=(R@rate).reshape(2,268),**initial)
    for label,result in results.items():
        arrays.update({label+'_'+k:v for k,v in result.items()if isinstance(v,np.ndarray)})
    arrays['primary_raw_coordinate_rate_time_first']=(R@primary['original_master_coordinate_rate_time_first']).reshape(2,268)
    arrays['half_step_raw_coordinate_rate_time_first']=(R@control['original_master_coordinate_rate_time_first']).reshape(2,268)
    save('endpoint_second_domain_contacts.npz',arrays)
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for p in(Path(__file__),'tests/test_muon_endpoint_second_domain_germ.py'):
        p=Path(p);p=p if p.is_absolute()else ROOT/p;refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same action second-domain source changed')
    comparisons={}
    for k in('moving_geometric_trace_time_second','proper_normal_rows_time_second','induced_lapse_time_second',
              'original_master_coordinate_rate_time_first','explicit_reference_clock_gradient_total_time_first'):
        comparisons[k]=dict(primary_norm=float(np.linalg.norm(primary[k])),half_step_norm=float(np.linalg.norm(control[k])),
            difference_norm=float(np.linalg.norm(primary[k]-control[k])),
            relative_difference=float(np.linalg.norm(primary[k]-control[k])/max(np.linalg.norm(control[k]),np.finfo(float).tiny)),
            primary_max=maximum(primary[k]))
    data=dict(classification='EVALUATED_LITERAL_JOINT_ENDPOINT_TIME_SECOND_CONTACTS_AND_CANONICAL_RATE_JERK',
        archives=archives,input_hashes=refs,action_parameters=params,normalized_step=normalized_step,
        rate_magnitude=magnitude,coordinate_time_step=normalized_step/magnitude,
        branch_diagnostics=diagnostics,step_comparisons=comparisons,
        original_Hdot_reproduction_max=maximum(primary['Hessian_total_time_first']-clock['Hessian_coordinate_time_first']),
        original_Hdot_half_step_reproduction_max=maximum(control['Hessian_total_time_first']-clock['Hessian_coordinate_time_first_control']),
        endpoint_trace_role='original C73 is birth/reset matching, not established continuous material bulk glue',
        derivative_role='total action-vector-field derivative at the same complex joint snapshot, including reference-only affine clock; physical versus event-family motion is not identified by this computation',
        normal_control='if consumed as a computational endpoint normal basis: a=1,a_first=a_second=0; area_source has a=0, without physical mode assignment',
        per_arm_momenta='own parentPi must be distinguished from graph parentPi before separate chronological propagation; joint rate here retains graph Pi',
        actual_parent_partial_reference_clock_added_twice=False,
        original292_phase_equations_and4_named_frames_retained=True,
        both_normal_coframe_jerks_and_source_clock_contacts_retained=True,
        persistent_bulk_trace_reaction_or_physical_formation_selected=False,
        error_scope='binary original action and framed canonical rate solves, centered two-step total derivatives; measured step difference is diagnostic, not an enclosure or a physical trajectory error bound')
    p=out/'result.json';p.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='endpoint_second_domain_germ_complete',result_sha256=sha256(p.read_bytes()).hexdigest(),
        comparisons=comparisons,Hdot_reproduction=data['original_Hdot_reproduction_max']),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--normalized-step',type=float,default=2e-5);a=p.parse_args();materialize(a.output,a.normalized_step)
