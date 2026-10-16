"""A new coupled tail cell on the ORIGINAL ea02 four-response primal branch.

This reuses the existing full368 nonlinear canonical solver and the already
reviewed independent same-material-equations chart4. It does not replay any
prefix, select outgoing terminal data, or correct the original birth state.
The native effective load and external spatial-domain return remain open.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace

os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
ROOT=Path(__file__).resolve().parents[1]
FAMILY='artifacts/muon_baton_zoo_maximal_current_realization_20261013'
RADIAL='artifacts/muon_baton_zoo_radial_convergence_20261014'


def assert_original_response_primal_chain(root,read,cut,F):
    """Require exact saved field epochs/pointers, not merely equal clocks."""
    import numpy as np
    folder=FAMILY+'/actual_response_cut_compatible368_refinement_flow_run_1/'
    initial=read(folder+'actual_precise_compatible_cut_constitutive_rows.npz')
    previous=initial['master368'];records=[]
    for i in range(8):
        middle_rel=folder+f'cell_{i:04d}_retry_00_precise_original526_midpoint.npz'
        end_rel=folder+f'cell_{i:04d}_retry_00_precise_original210_endpoint.npz'
        middle,end=read(middle_rel),read(end_rel)
        run=('actual_new_only_compatible316_matrixfree_retarded_cell'+str(i)+('_warm_run_2' if i==7 else '_run_1'))
        response_rel=FAMILY+'/'+run+'/actual_new_only_compatible316_response_and_full252_source_return.npz'
        q,meta=read(response_rel),read(FAMILY+'/'+run+'/result.json')
        if not meta.get('admitted_finite_cell',False)or meta['original526_rows_upper']>2e-10:raise ValueError('Every accepted response cell original guard is required')
        if Path(q['actual_midpoint_packet'].item()).resolve()!=(root/middle_rel).resolve():raise ValueError('Response coefficients belong to a different primal-cell branch')
        if not np.array_equal(q['actual_midpoint_master368'],middle['midpoint_master368']):raise ValueError('Exact complete368 primal epoch mismatch; equal clock does not authorize splicing')
        if not np.array_equal(q['completed_frames'],F)or not np.array_equal(q['original252_to_augmented368'],cut['original252_to_augmented368']):raise ValueError('Original field/frame incidence changed')
        if q['coordinate_time'].item()!=middle['coordinate_time'].item():raise ValueError('Actual source/operator midpoint clock changed')
        # The old producers form endpoint tags in different B64 addition
        # orders. Exact full field/pointer/hash identities above own the
        # node; do not interpret one-ulp tag differences as a physical step.
        node_tag_delta=q['authoritative_node_time'].item()-end['coordinate_time'].item()
        if abs(node_tag_delta)>1e-18:raise ValueError('Accepted response endpoint tag is inconsistent with its exact primal-cell identity')
        consumed={str(Path(k).resolve()):v for k,v in meta['inputs'].items()}
        if consumed.get(str((root/middle_rel).resolve()))!=sha256((root/middle_rel).read_bytes()).hexdigest():raise ValueError('Exact primal midpoint byte hash was not consumed by the response')
        position_defect=float(np.max(abs(middle['midpoint_master368'][:158]-(previous[:158]+end['master368'][:158])/2)))
        if position_defect>2e-10:raise ValueError('Primal positions do not form the retained accepted canonical chain')
        records.append(dict(cell=i,primal_midpoint=middle_rel,primal_endpoint=end_rel,response=response_rel,position_midpoint_identity_absolute=position_defect,endpoint_tag_delta=[node_tag_delta.real,node_tag_delta.imag],tag_delta_used_as_physical_time_step=False,all_original526_upper=meta['original526_rows_upper']))
        previous=end['master368']
    if not np.array_equal(cut['master368'],previous):raise ValueError('Requested new tail cut differs from original target final accepted field')
    for key in('Pi158_high','Pi158_low'):
        if not np.array_equal(cut[key],end[key]):raise ValueError('Requested initial Pi is not the original response primal endpoint')
    return dict(identity='EXACT_COMPLETE_PRIMAL_FIELD_EPOCH_AND_CONSUMED_BYTE_CHAIN',records=records,final_primal_master368_bit_identical=True,final_Pi158_high_low_bit_identical=True,equal_clock_alone_used=False,principal_branch_spliced=False)


def execute(repository,output,step=1.0e-7):
    root,out=Path(repository).resolve(),Path(output).resolve()
    if out.exists():raise FileExistsError('Preserve every previous tail attempt')
    out.mkdir(parents=True)
    sys.path[:0]=[str(root/'src'),str(root/'scripts'),str(root/'audits')]
    import numpy as np
    from flint import ctx,acb_mat
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper,_mid
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _rows,_cat,_split
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from evaluate_muon_continued_current_factor import retained_input
    ctx.prec=256;pins={};archives={};calls=0
    def read(relative):
        p=root/relative;b=p.read_bytes();pins[relative]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def module(name,relative):
        p=root/relative;b=p.read_bytes();pins[relative]=sha256(b).hexdigest()
        target=out/(name+'_consumed_source.py');target.write_bytes(b)
        spec=importlib.util.spec_from_file_location(name,p)
        value=importlib.util.module_from_spec(spec);sys.modules[name]=value;spec.loader.exec_module(value)
        return value
    def save(name,values):
        arrays={}
        for k,v in values.items():
            if isinstance(v,acb_mat):arrays[k+'_high'],arrays[k+'_low']=_split(v)
            else:arrays[k]=v
        p=out/name;_compressed_npz(p,arrays)
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    solver=module('same_action_existing_full_precision_tail_solver',FAMILY+'/actual_compatible368_full_precision_cut_control_run_1/initial_producer.py')
    binary=module('same_action_existing_augmented_scalar',FAMILY+'/actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/bhsm_baton_zoo_augmented_source_domain_derivative_imported_runtime.py')
    precise=module('same_action_repaired_native_scalar',FAMILY+'/actual_new620_fresh_native_MP_new_exact_R7_clock_control_run_1/new620_fresh_actual_native_MP_scalar_imported_runtime.py')
    chart=module('same_action_independent_material_chart4',FAMILY+'/actual_new620_fresh_native_MP_new_exact_R7_clock_control_run_1/new620_fresh_same_material_equations_chart4_imported_runtime.py')
    cut=read(FAMILY+'/actual_response_cut_compatible368_refinement_flow_run_1/last_actual_compatible_primal_with_unclosed_future.npz')
    maps_in=read(RADIAL+'/compatible_explicit_maps_all_epochs_run_1/birth_degree_02_compatible_connected_radial_action.npz')
    frames=read(RADIAL+'/compatible_explicit_maps_all_epochs_run_1/birth_degree_02_compatible_literal_central_frames.npz')
    lifts=read(RADIAL+'/literal_MP_point_wall_tables_run_1/degree_02_literal_MP_original_and_extra_point_wall_tables.npz')
    born=read('artifacts/muon_birth_full_proper_port_saddle_20261013/run_1/birth_fixed_germ_and_source_compatibility.npz')
    params=read('artifacts/muon_coupled_birth_full_application_20261012/run_1/result.json')['action_parameters']
    phase,_=retained_input('outgoing',pins);rep=dict(phase['representation']);P=phase['coordinates']['lift']
    oldrad='artifacts/muon_baton_zoo_radial_completion_20261013/action_gauge_degree2_run_1/'
    oldmaps=binary.augmented_maps(read(oldrad+'birth_current288_connected_action_and_rate_operands.npz'),read(oldrad+'enlarged_birth_radial_action.npz'))
    original=np.asarray(maps_in['child_original252_to_augmented'],int)
    extra=252+np.r_[maps_in['previous_radial_to_augmented'][np.asarray(oldmaps['extra_coordinates_to_full'],int)-252],maps_in['derivative_compatible_position_indices'],maps_in['derivative_compatible_rate_indices']]
    maps=dict(old504_to_full=maps_in['old504_to_full'],extra_coordinates_to_full=extra,full_dimension=620,child_original252_to_augmented=original)
    for name in('original_gauge_basis','original_gauge_radial_basis','original_wall_trace_map'):
        for part in('high','low'):maps[name+'_'+part]=lifts[name+'_'+part]
    for name,source in(('extra_point_lift','compatible_extra_point_lift'),('extra_wall_lift','compatible_extra_wall_lift')):
        for part in('high','low'):maps[name+'_'+part]=lifts[source+'_'+part]
    maps['extra_point_lift']=maps['extra_point_lift_high']+maps['extra_point_lift_low']
    for key,rkey in(('original_gauge_basis','gauge_basis'),('original_gauge_radial_basis','gauge_radial_basis'),('original_wall_trace_map','wall_trace_map')):
        v=maps[key+'_high']+maps[key+'_low']
        if rkey!='wall_trace_map':v=v.reshape(len(rep['rho']),80,1,5,4)
        if np.any(v.imag!=0):raise ValueError('Same real numerical preconditioner tables required')
        rep[rkey]=v.real
    F=frames.get('frames_completed',frames.get('frames'))
    if not np.array_equal(cut['original252_to_augmented368'],original)or not np.array_equal(cut['completed_frames'],F):raise ValueError('Same complete canonical domain required')
    e=_matrix(cut['master368'])
    Pi=_matrix(cut['Pi158_high'])+_matrix(cut['Pi158_low'])
    time=_matrix([[cut['coordinate_time'].item()]])[0,0]
    if 'coordinate_time_low' in cut:time+=_matrix([[cut['coordinate_time_low'].item()]])[0,0]
    history_guard=assert_original_response_primal_chain(root,read,cut,F)
    if abs(complex(time)-complex(8.4152529296875e-5,-2.292213182443259e-8))>1e-18:raise ValueError('Original target response branch frontier required')
    reference=_matrix(cut['frame_reference']);initial=acb_mat(e);initialPi=acb_mat(Pi)
    def phase_action(*args,**kwargs):
        kwargs['material_chart_precision']='independent_mp_same_material_equations'
        kwargs['material_chart_owner']=chart.anchored_material_chart4
        kwargs['precision_bits']=256
        return precise.phase_action_contractions(*args,**kwargs)
    context=(rep,P,maps,born['raw_pair'],born['reference_pair'],params,SimpleNamespace(phase_action_contractions=phase_action),binary,'independent_mp_same_material_equations')
    def evaluate(value,clock):
        nonlocal calls
        calls+=1
        print(json.dumps(dict(stage='new_tail_actual_same_action_gradient',call=calls,time=[complex(clock).real,complex(clock).imag])),flush=True)
        return solver._action(value,clock,context)
    warm=solver._warm(e,Pi,lambda x:evaluate(x,time),F,reference,guard=2e-10,max_iterations=12,
        checkpoint=lambda r:print(json.dumps(dict(stage='new_tail_fixed_Cauchy_constitutive_admission',**r)),flush=True))
    save('initial_fixed_Cauchy_constitutive_rows.npz',dict(master368=warm['master'],Pi158=Pi,original210=warm['original_rows'],frame_reactions=warm['frame_reactions'],initial_x_change=_rows(warm['master'],0,158)-_rows(initial,0,158)))
    if warm['status']!='ALL_MP_ORIGINAL_CONSTITUTIVE_ROWS_PASS':
        status='INITIAL_SAME_CAUCHY_CONSTITUTIVE_ADMISSION_UNRESOLVED';attempts=[]
    else:
        e=warm['master'];attempts=[];status='NEW_CLASSICAL_TAIL_CELL_UNRESOLVED'
        for retry in range(3):
            h=float(step)*2**(-retry);hb=_matrix([[h]])[0,0];tm=time+hb/2;te=time+hb
            mid=solver._cell(_rows(e,0,158),Pi,e,h,lambda v:evaluate(v,tm),F,reference,guard=2e-10,max_iterations=12,
                checkpoint=lambda r:print(json.dumps(dict(stage='new_tail_original526',retry=retry,step=h,**r)),flush=True))
            save(f'retry_{retry:02d}_new_tail_original526.npz',dict(midpoint_master368=mid['master_midpoint'],final_x158=mid['final_x'],final_Pi158=mid['final_Pi'],original526=mid['original_rows'],framed_rows=mid['framed_rows'],frame_reactions=mid['frame_reactions'],coordinate_time=np.asarray(complex(tm)),coordinate_time_low=np.asarray(complex(tm-_matrix([[complex(tm)]])[0,0])),step=np.asarray(h)))
            record=dict(retry=retry,step=h,status=mid['status'],original526_upper=_upper(mid['original_rows']),records=mid['records']);attempts.append(record)
            if mid['status']!='ALL_MP_ORIGINAL_CANONICAL_ROWS_PASS':continue
            guess=_cat(mid['final_x'],_rows(mid['master_midpoint'],158,368))
            end=solver._warm(guess,mid['final_Pi'],lambda v:evaluate(v,te),F,reference,guard=2e-10,max_iterations=12,
                checkpoint=lambda r:print(json.dumps(dict(stage='new_tail_original210_endpoint',**r)),flush=True))
            save(f'retry_{retry:02d}_new_tail_original210_endpoint.npz',dict(master368=end['master'],Pi158=mid['final_Pi'],original210=end['original_rows'],coordinate_time=np.asarray(complex(te)),coordinate_time_low=np.asarray(complex(te-_matrix([[complex(te)]])[0,0])),original252_to_augmented368=original,completed_frames=F,frame_reference=cut['frame_reference']))
            record.update(endpoint_status=end['status'],original210_upper=_upper(end['original_rows']))
            if end['status']=='ALL_MP_ORIGINAL_CONSTITUTIVE_ROWS_PASS':status='GENUINELY_NEW_CLASSICAL_COUPLED_TAIL_CELL_ADMITTED';break
    pins[Path(__file__).resolve().relative_to(root).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    for name,m in list(sys.modules.items()):
        p=getattr(m,'__file__',None)
        if p and name.startswith('bhsm.')and Path(p).is_relative_to(root):pins[Path(p).relative_to(root).as_posix()]=sha256(Path(p).read_bytes()).hexdigest()
    report=dict(classification='ORIGINAL_EA02_RESPONSE_BRANCH_NEW_FULL368_CLASSICAL_COUPLED_TAIL_CELL',status=status,initial_time=[complex(time).real,complex(time).imag],
        input_sha256=dict(sorted(pins.items())),archives=archives,action_parameters=params,original_target_history_guard=history_guard,material_owner='independent same original96-point material equations, chart4',
        initial_constitutive_status=warm['status'],initial_original210_upper=_upper(warm['original_rows']),initial_x_fixed_upper=_upper(_rows(warm['master'],0,158)-_rows(initial,0,158)),initial_Pi_fixed_upper=_upper(Pi-initialPi),
        attempts=attempts,scalar_action_calls=calls,prefix_replayed=False,original_birth_matching_state_changed=False,original_coupled_corrections=0,
        existing_four_response_prefix_preserved=True,new_four_response_columns_evaluated=False,new_physical_outgoing_graph=None,new_physical_C0_Cj=None,
        source_domain_physical_derivative_pass=False,native_effective_action_application_evaluated=False,physical_exterior_spatial_domain_evaluated=False,
        original_Maxwell_after_or_all226_after_pass=False,physical_muon_magnetic_moment=None,
        next_required_actual_application='Evaluate source-clock and full direct CHILD620 Hessian applications at the NEW accepted midpoint, then transport existing seven split/four combined responses through a contiguous same-primal history; no new terminal Y=0 or gap interpolation is permitted.')
    (out/'result.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(status=status,scalar_action_calls=calls,result_sha256=sha256((out/'result.json').read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',default=str(ROOT));p.add_argument('--output',required=True);p.add_argument('--step',type=float,default=1e-7)
    a=p.parse_args();execute(a.repository,a.output,a.step)
