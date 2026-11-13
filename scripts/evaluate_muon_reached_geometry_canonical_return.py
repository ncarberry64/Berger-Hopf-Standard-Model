"""Execute all67 natural directions and sourced geometry on the reached complex path.

The recorded original complex canonical cells are consumed, not a frozen A,
old field-only tail, or a reset-trace reaction imposed continuously.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from evaluate_muon_per_arm_canonical_source import clean
from bhsm.interface.muon_reached_geometry_canonical_return import (
    sourced_original_canonical_batch,structural_geometry_port_lift,complete_natural_boundary_work)
from bhsm.interface.muon_stored_fiber_canonical_tangent import stored_endpoint_constitutive_tangent
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_complex_paired_normal_action import complex_proper_normal_trace
from bhsm.interface.muon_complex_normal_trace_motion import proper_normal_trace_motion
from bhsm.interface.muon_holomorphic_child_action import holomorphic_inherited_child_action
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def run(collar,complex_history,tangent,output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve every reached geometry return')
    pins={};archives={}
    def read(folder,name):
        p=ROOT/folder/name;b=p.read_bytes();pins[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p)as z:return{k:z[k].copy()for k in z.files}
    cm=read(collar,'result.json');xm=read(complex_history,'result.json');tm=read(tangent,'result.json')
    if not xm['all_steps_and_endpoints_passed']:
        raise ValueError('actual reached complex original358 and true146 endpoint required')
    if xm['action_parameters']!=cm['action_parameters']:raise ValueError('same original action parameters required')
    bf=Path(cm['trial']);candidate=read(bf,'candidate.npz');old=read(bf,'action_and_shooting_rows.npz')
    initial=read(tangent,'initial_literal_Ward_fiber.npz')
    actual=read(complex_history,'actual_complex_endpoint_comparison.npz')
    phase,_=retained_input('outgoing',pins);rep=phase['representation'];P=phase['coordinates']['lift']
    F=canonical_central_frame(candidate['raw_pair'][1],rep)['named_frame_covectors']
    # The original67 image remains independent of the source-driven port3.
    # The source has zero Cauchy response; this is not a base IVP selector.
    ret_hi=np.zeros((212,3),complex);ret_lo=ret_hi.copy();records=[]
    fiber_hi=initial['canonical_direction_high'];fiber_lo=initial['canonical_direction_low']
    out.mkdir(parents=True)
    def save(name,a):
        p=out/name;_compressed_npz(p,{k:v for k,v in a.items()if isinstance(v,np.ndarray)})
        if p.stat().st_size>=10*1024**2:raise ValueError('split compact reached return')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    for k in range(xm['steps']):
        stage=read(complex_history,f'step_{k:04d}_stage.npz')
        raw=stage['stage_raw'];tr=complex_proper_normal_trace(raw,P)
        # L_drive=a(t).B(t).delta x with d tau=l(t)dt; coefficients
        # are the declared actual-path computational source, not R_s of
        # a physical moving reset. The three traces are not bulk constraints.
        g=np.zeros((252,3),complex);g[:106]=tr['induced_lapse']*tr['trace'].T
        rh,rlo=ret_hi.copy(),ret_lo.copy()
        a=sourced_original_canonical_batch(stage['stage_Hessian'],stage['coordinate_step'].item(),F,rh,rlo,g,tr['trace'])
        ret_hi,ret_lo=a['canonical_final_high'],a['canonical_final_low']
        save(f'cell_{k:04d}_zero_Cauchy_geometry_source.npz',dict(a,
            stage_raw=raw,proper_geometry_trace=tr['trace'],induced_lapse=np.array(tr['induced_lapse']),
            coordinate_time=stage['coordinate_time'],coordinate_step=stage['coordinate_step']))
        rec=dict(cell=k,proper_source_norm=float(np.linalg.norm(g)),
            original358_upper=a['original_rows_upper'],original_Gauss_upper=a['original_Gauss_upper'],
            framed360_upper=a['framed_rows_upper'],frame_reaction_upper=a['frame_reaction_upper'],
            literal_transpose_pairing_upper=a['literal_pairing_upper'],
            retarded_position_norm=float(np.linalg.norm(ret_hi[:106]+ret_lo[:106])),
            retarded_momentum_norm=float(np.linalg.norm(ret_hi[106:]+ret_lo[106:])),
            base_original358_max=float(np.max(abs(stage['original358_rows']))))
        q=sourced_original_canonical_batch(stage['stage_Hessian'],stage['coordinate_step'].item(),F,
            fiber_hi,fiber_lo,np.zeros((252,67),complex),tr['trace'])
        fiber_hi,fiber_lo=q['canonical_final_high'],q['canonical_final_low']
        save(f'cell_{k:04d}_all67_original_canonical_rows.npz',q)
        rec.update(all67_original358_upper=q['original_rows_upper'],all67_Gauss_upper=q['original_Gauss_upper'],
            all67_frame_reaction_upper=q['frame_reaction_upper'])
        records.append(rec);print(json.dumps(rec,sort_keys=True),flush=True)
    end=read(complex_history,f"step_{xm['steps']-1:04d}_endpoint.npz");time=end['coordinate_time'].item()
    # Reexecute only the actual final action point needed for true v/y.
    action=holomorphic_inherited_child_action(end['endpoint_raw'],time,candidate['raw_pair'],candidate['reference_pair'],rep,**cm['action_parameters'])
    fresh_rows=np.r_[action['gradient'][106:212]-end['endpoint_Pi'],action['gradient'][212:]]
    final_trace=complex_proper_normal_trace(end['endpoint_raw'],P);B=final_trace['trace']
    lift=structural_geometry_port_lift(B);N=lift['lift']
    canon_hi=np.c_[fiber_hi,ret_hi];canon_lo=np.c_[fiber_lo,ret_lo]
    endpoint=stored_endpoint_constitutive_tangent(action['hessian'],F,canon_hi,canon_lo)
    delta=endpoint['direction_high']+endpoint['direction_low'];c=canon_hi+canon_lo
    image=B@c[:106];traction=N.T@c[106:]
    # These coordinate target tractions do not replace the full106 flux.
    energy_first=end['endpoint_master'][106:212]@c[106:]-action['gradient'][:106]@c[:106]-action['gradient'][212:]@delta[212:]
    work=complete_natural_boundary_work(initial['canonical_direction_high'],initial['canonical_direction_low'],
        fiber_hi,fiber_lo,candidate['own_child_Pi'],end['endpoint_Pi'],coordinate_interval=time)
    hi=actual['actual_raw_time']
    motion=proper_normal_trace_motion(end['endpoint_raw'],P,hi)
    primary=image;secondary=B@delta[106:212]+motion['trace_coordinate_time_first']@delta[:106]
    s=np.linalg.svd(c[:106,:67],compute_uv=False)
    save('actual_endpoint_geometry_and_all67_natural_return.npz',dict(
        canonical_direction_high=canon_hi,canonical_direction_low=canon_lo,
        full_phase_direction_high=endpoint['direction_high'],full_phase_direction_low=endpoint['direction_low'],
        full_original146_rows=endpoint['original_rows'],original_frame_reaction_rows=endpoint['reaction_rows'],
        endpoint_raw=end['endpoint_raw'],endpoint_master=end['endpoint_master'],endpoint_Pi=end['endpoint_Pi'],
        action_gradient=action['gradient'],action_Hessian=action['hessian'],fresh_original146_rows=fresh_rows,
        actual_birth226_rows=old['all_original226_birth_rows'],
        final_proper_geometry_trace=B,final_proper_geometry_trace_time_first=motion['trace_coordinate_time_first'],
        structural_geometry_lift=N,structural_geometry_columns=lift['columns'],
        full106_terminal_direction_cotangent=c[106:],geometry_position_image=primary,
        geometry_time_first_image=secondary,geometry_target_traction=traction,
        child_base_energy_first=energy_first,
        terminal_fiber_singular_values=s,**work))
    save('actual_base_boundary_and_source_scope.npz',dict(raw_pair=candidate['raw_pair'],reference_pair=candidate['reference_pair'],
        initial_own_child_Pi=candidate['own_child_Pi'],terminal_own_child_Pi=end['endpoint_Pi'],
        original_full106_terminal_natural_residual=end['endpoint_Pi'],
        initial_fiber_high=initial['canonical_direction_high'],initial_fiber_low=initial['canonical_direction_low'],
        source_final_high=ret_hi,source_final_low=ret_lo))
    bm=read(bf,'result.json')
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path and Path(path).is_relative_to(ROOT):
            p=Path(path);pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for p in (Path(__file__),ROOT/'tests/test_muon_reached_geometry_canonical_return.py'):
        pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('reached action inputs changed')
    full=work['complete_boundary_work_high']+work['complete_boundary_work_low'];scaled=work['clock_scaled_boundary_work_high']+work['clock_scaled_boundary_work_low']
    result=dict(classification='EXECUTED_REACHED_CHANGING_CANONICAL_GEOMETRY_SOURCE_AND_ALL67_NATURAL_CALLBACK',
        input_hashes=pins,archives=archives,history=records,action_parameters=cm['action_parameters'],
        original_birth226_max=bm['all_original226_max'],birth_guard_passed=False,
        actual_final_coordinate_time=clean(time),fresh_final_original146_max=float(np.max(abs(fresh_rows))),
        final_direction_original146_upper=endpoint['original_rows_upper'],final_direction_frame_reaction_upper=endpoint['reaction_rows_upper'],
        all67_complete_boundary_work_max=float(np.max(abs(full))),
        all67_clock_scaled_complete_boundary_work_max=float(np.max(abs(scaled))),
        full106_base_terminal_natural_covector_norm=float(np.linalg.norm(end['endpoint_Pi'])),
        source_driven_final_geometry_matrix=clean(image[:,67:]),
        source_driven_geometry_target_traction=clean(traction[:,67:]),
        all67_geometry_image_norm=float(np.linalg.norm(image[:,:67])),
        all67_terminal_position_rank=int(np.sum(s>max(c[:106,:67].shape)*np.finfo(float).eps*s[0])),
        all67_terminal_position_condition=float(s[0]/s[-1]),structural_port_minor_condition=lift['minor_condition'],
        child_source_driven_energy_first=clean(energy_first[67:]),
        source_domain='declared computational three moving geometry covectors l(t)B(t)^T, zero Cauchy response; no persistent reset glue or assumed exterior graph',
        inherited_parent_and_reference_fixed_as_actual_child_callback=True,
        true_full67_birth_and_natural_rows_retained=True,
        outgoing_geometry_environment_DtN_or_physical_formation_admitted=False,
        physical_a_mu=None,physical_g_mu=None,
        required_action_continuation='Continue the same full constrained child Jacobi/source action and actual material/exterior support to the action-selected event/tail; impose its full outer canonical/Noether relation, then the original all226 reset/natural/energy and common gamma(c) formation equations. Zero response Cauchy data here do not select that tail or the base.',
        actual_complex_history_consumed_not_C1_interpolation=True,
        C1_vs_actual_body_current_comparison=xm['actual_endpoint_comparison']['body_current_differences'],
        error_scope='Executed changing original complex358 cells and true146 action face; stored-coefficient Acb arithmetic only. The finite midpoint/normal-collar source, original action evaluation, common coupled base, physical support, and exterior errors are not enclosed.')
    p=out/'result.json';p.write_text(json.dumps(clean(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='actual_geometry_callback_complete',result_sha256=sha256(p.read_bytes()).hexdigest(),
        all67_workmax=result['all67_complete_boundary_work_max'],scaled_workmax=result['all67_clock_scaled_complete_boundary_work_max'],
        fresh_original146=result['fresh_final_original146_max'],final_direction_rows=endpoint['original_rows_upper']),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--collar',type=Path,default=Path('artifacts/muon_sigma_normal_collar_transport_20261012/trial_0000_run_2'))
    p.add_argument('--complex-history',type=Path,default=Path('artifacts/muon_reached_complex_normal_history_20261012/trial_0000_run_1'))
    p.add_argument('--tangent',type=Path,default=Path('artifacts/muon_stored_fiber_canonical_tangent_20261012/run_1'))
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.collar,a.complex_history,a.tangent,a.output)
