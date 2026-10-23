"""Execute signed D3S operands and classical mixed action on actual causal points."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_holomorphic_n1_magnetic_action import original_signed_stage
from bhsm.interface.muon_holomorphic_n1_magnetic_operands import signed_n1_magnetic_point_operands
from bhsm.interface.muon_holomorphic_n1_magnetic_operand_application import (
    homogeneous_original_field_trial,signed_point_mixed_action,signed_two_trace_temporal_block,PLACEMENTS)
from bhsm.interface.muon_intrinsic_scalar_discretization import scalar_s3_discretization
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(source_folder,output):
    source=ROOT/source_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve signed D3S output, including incomplete executions')
    pins={};archives={}
    def read(p,expected=None):
        p=ROOT/p if not p.is_absolute()else p
        if not p.is_relative_to(ROOT):raise ValueError('same calling worktree sources required')
        b=p.read_bytes();h=sha256(b).hexdigest();pins[p.relative_to(ROOT).as_posix()]=h
        if expected is not None and h!=expected:raise ValueError('actual causal/stage source pin differs')
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    md=read(source/'result.json')
    if (md['classification']!='EVALUATED_CHANGING_CANONICAL_SIGNED_N1_PRESCRIBED_MAGNETIC_ACTION_AND_UNSQUARED_EM_CURRENT'
            or not md['causal_initial_x_p_zero']or not md['causal_background_source_first_response_executed']):
        raise ValueError('completed actual causal source/source-first application required')
    for p,h in md['input_hashes'].items():
        if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('actual causal producer input changed')
        pins[p]=h
    get=lambda name:read(source/name,md['archives'][name]['sha256'])
    points=get('actual_zero_Cauchy_magnetic_source_points.npz');prefix=get('actual_zero_Cauchy_magnetic_prefix.npz')
    current=get('actual_zero_Cauchy_magnetic_unit_EM_current.npz')
    q=len(points['sigma']);order=prefix['original_stage_order'];steps=prefix['future_coordinate_steps']
    if (q!=15 or points['total_field'].shape!=(15,336,3)or points['total_coordinate_rate'].shape!=(15,336,3)
            or points['total_field_first'].shape!=(15,2,336,3)or sorted(order.tolist())!=[0,1]
            or not np.allclose(steps,steps[0],rtol=0,atol=0)):
        raise ValueError('complete actual15-point equal-step causal prefix schema required')
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=ROOT)
    pins.update(phase['input_hashes']);rep=phase['representation']
    root_source=ROOT/md['source_folder'];rootmd=read(root_source/'result.json')
    angular=scalar_s3_discretization(3);labels=np.array(angular['real_basis_labels'])
    degrees=labels[:,0].astype(int)
    even=np.flatnonzero(np.isin(degrees,(0,2)));odd=np.flatnonzero(degrees==1)
    E=angular['real_angular_derivative_matrices'];Y=angular['real_basis_values'];haar=angular['haar_weights']
    Ee=E[:,even][:,:,even];Eo=E[:,odd][:,:,odd]
    G=np.einsum('qe,q,qo,qs->eos',Y[:,even],haar,Y[:,odd],Y[:,odd],optimize=True)
    zero=np.flatnonzero(degrees[even]==0)
    if len(zero)!=1 or np.max(abs(Y[:,even[zero[0]]]-1))>2e-14:raise ValueError('owned unit-Haar constant trial required')
    bindings=[];trials=[];stage_inputs=[]
    for j in order:
        name=md['stages'][int(j)]['source_archive'];a=read(root_source/name,rootmd['archives'][name]['sha256'])
        dirs=lambda n:np.stack((a[n+'_high'],a[n+'_low']),axis=-1)
        b=original_signed_stage(a['stage_raw'],dirs('stage_raw_direction'),a['parent_source_stage_raw'],
            dirs('parent_source_stage_raw_direction'),a['reference_stage_pair'],dirs('reference_stage_direction'),rep,
            side='parent'if md['side']=='incoming'else'child',lambda_H=rep['scalar_matching']['lambda_H'],
            nu_squared_action=rootmd['action_parameters']['nu_squared_action'])
        saved=get(f'stage_{j}_actual_magnetic_trace.npz')
        if not np.array_equal(a['stage_raw'],saved['source_raw']):raise ValueError('same stage source/raw differs')
        if not np.array_equal(b['value_permutation'],bindings[0]['value_permutation']if bindings else b['value_permutation']):
            raise ValueError('original field coordinate order differs between cells')
        bindings.append(b);trials.append(homogeneous_original_field_trial(dirs('stage_raw_direction'),b['value_permutation'],labels[even]))
        stage_inputs.append(dict(source_archive=name,original_stage=int(j),coordinate_time=[a['coordinate_time'].item().real,a['coordinate_time'].item().imag]))
    for n,m in sorted(sys.modules.items()):
        p=getattr(m,'__file__',None)
        if n.startswith('bhsm.')and p:
            p=Path(p)
            if p.is_relative_to(ROOT):pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_holomorphic_n1_magnetic_operands.py',
            'tests/test_muon_holomorphic_n1_magnetic_operand_application.py'):
        pins[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    out.mkdir(parents=True)
    def save(name,obj):
        p=out/name;_compressed_npz(p,{k:v for k,v in obj.items()if isinstance(v,np.ndarray)})
        if p.stat().st_size>=10*1024**2:raise ValueError('split D3S output below10MiB')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    save('same_action_maps_and_trials.npz',dict(even_labels=labels[even],odd_labels=labels[odd],even_indices=even,odd_indices=odd,
        even_derivatives=Ee,odd_derivatives=Eo,gaunt_even_odd_source=G,value_permutation=bindings[0]['value_permutation'],
        coordinate_steps=steps,original_stage_order=order,scale=points['scale'],sigma=points['sigma'],cell=points['cell'],
        even_trial_field=np.array([t['field']for t in trials]),even_trial_coordinate_rate=np.array([t['coordinate_rate']for t in trials])))
    # Local cells retain the held initial face, so deleting it cannot hide
    # its forced/boundary source. Global free-trace assembly is separately
    # exported on two traces (even1680, odd672), with no inverse implied.
    cell_blocks=np.zeros((2,2,2,3,840,336),complex)
    force_value=[];force_rate=[];records=[];contractions={}
    temporal_force=np.zeros((3,3,3,840),complex)
    prefixes=('','Maxwell_','intrinsic_','intrinsic_off_shell_DH_')
    totals={pre+n:np.zeros((2,3,3),complex)for pre in prefixes for n in PLACEMENTS+('total',)}
    absolute={key:np.zeros((2,3,3))for key in totals}
    for i in range(q):
        j=int(points['cell'][i]);local=2*points['sigma'][i]-j;p=np.array([1-local,local]);v=np.array([-1/steps[j],1/steps[j]])
        if j not in(0,1)or not(0<=local<=1):raise ValueError('causal point outside actual source cell')
        f,ft=points['total_field'][i],points['total_coordinate_rate'][i]
        a=signed_n1_magnetic_point_operands(bindings[j],f,ft,Ee,Eo,Eo,G)
        t=trials[j];m=signed_point_mixed_action(a,t['field'],t['coordinate_rate'],f,ft);scale=points['scale'][i]
        for key in totals:
            contractions.setdefault(key,[]).append(m[key]);totals[key]+=scale*m[key];absolute[key]+=abs(scale*m[key])
        fv=np.einsum('aef,fb->abe',a['delta_K'],f,optimize=True)+np.einsum('aef,fb->abe',a['delta_B_forward'],ft,optimize=True)
        fr=np.einsum('aef,fb->abe',a['delta_B_reverse'],f,optimize=True)+np.einsum('aef,fb->abe',a['delta_M'],ft,optimize=True)
        force_value.append(fv);force_rate.append(fr)
        for k in range(2):temporal_force[:,:,j+k]+=scale*(p[k]*fv+v[k]*fr)
        cell_blocks[j]+=signed_two_trace_temporal_block(a,p,v,scale)
        # Every point's total third derivative and off-shell DH contact is
        # stored, all rows, below10MiB. Maxwell/scalar decomposition also
        # survives in every consumed contraction and its point norms.
        for axis in range(3):
            for start in range(0,840,210):
                stop=start+210
                obj={pre+'delta_'+n:a[pre+'delta_'+n][axis,start:stop]for pre in('','intrinsic_off_shell_DH_')for n in PLACEMENTS}
                obj.update(row_start=np.array(start),row_stop=np.array(stop),full_shape=np.array([840,336]),
                    point_index=np.array(i),cell=np.array(j),magnetic_axis=np.array(axis),scale=np.asarray(scale))
                save(f'point_{i:02d}_axis_{axis}_rows_{start:03d}.npz',obj)
        record=dict(point_index=i,cell=j,sigma=float(points['sigma'][i]),source_field_norm=float(np.linalg.norm(f)),
            source_coordinate_rate_norm=float(np.linalg.norm(ft)),source_H_norm=float(np.linalg.norm(a['source_H'])),
            source_H_coordinate_rate_norm=float(np.linalg.norm(a['source_H_coordinate_time'])),
            fixed_geometry_delta_M_norm=float(np.linalg.norm(a['delta_M'])),
            mixed_total_norm=float(np.linalg.norm(m['total'])),mixed_total_weighted_norm=float(np.linalg.norm(scale*m['total'])),
            magnetic_axis_exchange_defect_norm=float(np.linalg.norm(m['literal_magnetic_axis_symmetry_defect'])),
            components={pre or'total':{n:float(np.linalg.norm(a[pre+'delta_'+n]))for n in PLACEMENTS}for pre in prefixes})
        records.append(record);print(json.dumps(dict(stage='actual_causal_signed_D3S_point',side=md['side'],case=md['case'],**record),sort_keys=True),flush=True)
        del a
    for j in range(2):
        for l in range(2):
            for r in range(2):
                for axis in range(3):save(f'cell_{j}_left_{l}_right_{r}_axis_{axis}_temporal_action.npz',dict(
                    action_block=cell_blocks[j,l,r,axis],left_global_trace=np.array(j+l),right_global_trace=np.array(j+r),
                    original_initial_trace_held=np.array(j+l==0 or j+r==0),magnetic_axis=np.array(axis)))
    for l in(1,2):
        for r in(1,2):
            for axis in range(3):
                block=np.zeros((840,336),complex)
                for j in range(2):
                    if j<=l<=j+1 and j<=r<=j+1:block+=cell_blocks[j,l-j,r-j,axis]
                save(f'free_left_{l}_right_{r}_axis_{axis}_action.npz',dict(action_block=block,full_free_shape=np.array([1680,672]),
                    left_trace=np.array(l),right_trace=np.array(r),magnetic_axis=np.array(axis)))
    all_contractions={k:np.asarray(v)for k,v in contractions.items()}
    all_contractions.update({'integrated_'+k:v for k,v in totals.items()})
    all_contractions.update({'uncancelled_point_absolute_'+k:v for k,v in absolute.items()})
    all_contractions.update(point_action_value_force=np.array(force_value),point_action_rate_force=np.array(force_rate),
        original_three_trace_action_source=temporal_force,initial_held_action_source=temporal_force[:,:,0],
        original_free_two_trace_action_source=temporal_force[:,:,1:].reshape(3,3,1680),
        scale=points['scale'],sigma=points['sigma'],cell=points['cell'])
    save('classical_mixed_action_and_source.npz',all_contractions)
    save('same_prefix_existing_unsquared_current_terms.npz',{n:current[n]for n in('total','operator_insertion','right_current_motion','literal_left_motion',
        'total_first','operator_insertion_first','right_current_motion_first','literal_left_motion_first')})
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('consumed executable/source bytes changed')
    summary=lambda a:dict(norm=float(np.linalg.norm(a)),maximum=float(np.max(abs(a))),real_trace=[float(np.trace(x).real)for x in a],
        imaginary_trace=[float(np.trace(x).imag)for x in a])
    result=dict(classification='EVALUATED_ACTUAL_CAUSAL_SIGNED_N1_MAGNETIC_D3S_AND_CLASSICAL_MIXED_ACTION',input_hashes=pins,archives=archives,
        source_folder=source_folder.as_posix(),source_result_sha256=sha256((source/'result.json').read_bytes()).hexdigest(),
        side=md['side'],case=md['case'],stages=stage_inputs,source_points=q,point_records=records,
        action_parameters=rootmd['action_parameters'],field_value_layout=84,odd_source_labels=labels[odd].tolist(),even_target_labels=labels[even].tolist(),
        operator_shape=[3,840,336],free_temporal_operator_shape=[3,1680,672],full_original_At_Gauss_frame_rows_retained=True,
        all15_actual_zero_Cauchy_points_consumed=True,weak_BVP_source_not_consumed=True,source_wall_not_added_twice=True,
        source_only_E_transpose_adapter=True,coefficient_dual='literal analytic transpose; no coefficient conjugation',
        signed_Maxwell_both_angular_sides_curvature_and_scalar_DH_Hdot_quartic_retained=True,
        source_induced_Higgs_retained=True,original_initial_held_face_source_retained=True,
        temporal_measure='saved -i*d_coordinate_time*quadrature_weight; source rates and FE trial rates are coordinate-time rates',
        integrated_mixed_action={pre or'total':{n:summary(totals[pre+n])for n in PLACEMENTS+('total',)}for pre in prefixes},
        integrated_magnetic_axis_exchange_defect_norm=float(np.linalg.norm(totals['total']-totals['total'].swapaxes(1,2))),
        free_even_action_source_norm=float(np.linalg.norm(temporal_force[:,:,1:])),held_initial_even_action_source_norm=float(np.linalg.norm(temporal_force[:,:,0])),
        same_prefix_unsquared_current_terms={n:float(np.linalg.norm(current[n]))for n in('total','operator_insertion','right_current_motion','literal_left_motion')},
        same_prefix_unsquared_source_first_terms={n:[float(np.linalg.norm(current[n+'_first'][k]))for k in range(2)]for n in('total','operator_insertion','right_current_motion','literal_left_motion')},
        other_even_homogeneous_trial_components_zero_only_for_supplied_trial=True,
        field_direction_holds_geometry_and_parameters=True,active_geometry_metric_coframe_and_parameter_variations_not_assigned_zero=True,
        computed_classical_third_action_not_quantum_heat_mean_or_Pauli=True,
        native_positive_factor_or_P_strat_not_identified_with_signed_action=True,
        both_ordered_quantum_inverse_insertions_own_heat_mean_and_overlap_subtraction_not_inferred_from_classical_source=True,
        reached_next_same_action_equation='use the even n0/n2 action force and full directed temporal D3 blocks in the same prescribed-wall signed even action/canonical response; a native own-heat mean requires that operator, source/boundary map and its own heat cotangent on the common exterior/reset domain',
        same_background_overlap_scope='actual homogeneous field source paired with causal B/B on these same stages; no local continuum overlap coefficient or old reference subtotal subtracted',
        reached_physical_normalization_relation=md['reached_physical_normalization_relation'],physical_Bi_Bf_pole_LSZ_or_a_mu_selected=False,
        error_scope='binary full signed D3S action and exact stored point/source placements; finite constant-stage/Hermite/C2/causal ODE/15-point quadrature approximation remains; no action coefficient or outward physical enclosure')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),archives=len(archives),pins=len(pins),
        mixed_action=result['integrated_mixed_action']['total']['total'],free_even_action_source_norm=result['free_even_action_source_norm'])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-folder',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.source_folder,a.output)
