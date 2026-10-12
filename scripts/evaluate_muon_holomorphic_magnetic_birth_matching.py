"""Apply original magnetic field birth rows to causal parent and actual source germs."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_holomorphic_n1_magnetic_action import (
    original_signed_stage,signed_n1_forms,holomorphic_local_B_trace,magnetic_angular_trace,
    original_named_wall_lift,complete_gauge_wall_constraints)
from bhsm.interface.muon_holomorphic_n1_magnetic_cauchy import magnetic_trace_time_germ
from bhsm.interface.muon_holomorphic_magnetic_birth_matching import (
    signed_field_face_reconstruction,inherited_birth_interior_reconstitution,original_birth_field_rows)
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve actual magnetic birth applications')
    pins={};archives={}
    def read(p,expected=None):
        p=ROOT/p if not p.is_absolute()else p
        if not p.is_relative_to(ROOT):raise ValueError('same calling checkout inputs required')
        b=p.read_bytes();h=sha256(b).hexdigest();pins[p.relative_to(ROOT).as_posix()]=h
        if expected is not None and h!=expected:raise ValueError('same retained birth/source archive pin differs')
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    rootfolder=ROOT/'artifacts/muon_changing_canonical_source_20261012/run_3';rm=read(rootfolder/'result.json')
    tf=ROOT/'artifacts/muon_coupled_reset_canonical_trace_20261012/run_1';tm=read(tf/'result.json');trace=read(tf/'application.npz',tm['archives']['application.npz']['sha256'])
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=ROOT)
    pins.update(phase['input_hashes']);rep=phase['representation'];P=phase['coordinates']['lift']
    params=rm['action_parameters'];rawpair=trace['raw_pair'];refs=trace['reference_pair'];angular=magnetic_angular_trace()
    config=read(Path('artifacts/muon_calibrated_pauli_20261009/inputs.json'));charge=float(np.sqrt(4*np.pi*config['alpha_consumer']['value']))
    cases=[]
    for case in('normal_basis','area_source'):
        parentsource=read(rootfolder/f'{case}_consumed_birth_parent_source.npz',rm['archives'][f'{case}_consumed_birth_parent_source.npz']['sha256'])
        childsource=read(rootfolder/f'{case}_consumed_birth_child_source.npz',rm['archives'][f'{case}_consumed_birth_child_source.npz']['sha256'])
        rawdirs=[np.column_stack([P@s['direction_'+label]for label in('high','low')])for s in(parentsource,childsource)]
        births=[];bornforms=[];borngerms=[]
        for arm in(0,1):
            b=original_signed_stage(rawpair[arm],rawdirs[arm],rawpair[0],rawdirs[0],refs,np.zeros((2,268,2),complex),rep,
                side='parent'if arm==0 else'child',lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=params['nu_squared_action'])
            births.append(b);bornforms.append(signed_n1_forms(b,angular));borngerms.append(holomorphic_local_B_trace(rawpair[arm],rawdirs[arm],b['stage'],electric_charge=charge,angular=angular))
        loaded=[]
        for side in('incoming','outgoing'):
            folder=ROOT/f'artifacts/muon_holomorphic_n1_magnetic_action_20261012/{side}_{case}_run_1';md=read(folder/'result.json')
            for p,h in md['input_hashes'].items():
                if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('retained actual causal input changed')
                pins[p]=h
            get=lambda name:read(folder/name,md['archives'][name]['sha256'])
            prefix=get('actual_zero_Cauchy_magnetic_prefix.npz');order=prefix['original_stage_order']
            sources=[get(f'stage_{j}_actual_magnetic_trace.npz')for j in order]
            forms=[get(f'stage_{j}_original_signed_forms.npz')for j in order]
            loaded.append(dict(prefix=prefix,sources=sources,forms=forms,source_folder=folder.relative_to(ROOT).as_posix()))
        cases.append((case,births,bornforms,borngerms,loaded,rawdirs))
    for n,m in sorted(sys.modules.items()):
        p=getattr(m,'__file__',None)
        if n.startswith('bhsm.')and p:
            p=Path(p)
            if p.is_relative_to(ROOT):pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_holomorphic_magnetic_birth_matching.py'):
        pins[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    out.mkdir(parents=True)
    def save(name,a):
        p=out/name;_compressed_npz(p,{n:v for n,v in a.items()if isinstance(v,np.ndarray)})
        if p.stat().st_size>=10*1024**2:raise ValueError('compact source/matching data below10MiB required')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    maximum=lambda a:float(np.max(abs(a)))
    metric=lambda a:dict(norm=float(np.linalg.norm(a)),maximum=maximum(a),worst_flat_index=int(np.argmax(abs(a))),
        worst_complex=[float(a.ravel()[np.argmax(abs(a))].real),float(a.ravel()[np.argmax(abs(a))].imag)])
    reports={};guard=2e-10
    for case,births,bornforms,bornsource,loaded,rawdirs in cases:
        incoming,outgoing=loaded;prefix=incoming['prefix'];S=prefix['original_interior_field_lift'];na=48;nd=S.shape[1]-na
        ids=births[0]['value_permutation'];lifts=births[0]['lifts'];L=np.kron(original_named_wall_lift(rep,ids),np.eye(4));W=np.kron(lifts['W'],np.eye(4))
        C=complete_gauge_wall_constraints(lifts,4)['constraint'];frame=np.kron(np.eye(84)[lifts['frame_indices']],np.eye(4))
        parentwall=magnetic_trace_time_germ(1.,incoming['sources'],sum(prefix['future_coordinate_steps']))
        parent=signed_field_face_reconstruction(incoming['forms'][-1],S,L,parentwall,prefix['final_reduced_canonical_state'],na)
        childwall=magnetic_trace_time_germ(0.,outgoing['sources'],sum(outgoing['prefix']['future_coordinate_steps']))
        childzero=signed_field_face_reconstruction(outgoing['forms'][0],S,L,childwall,outgoing['prefix']['initial_reduced_canonical_state'],na)
        reset=original_birth_field_rows(parent,childzero,ids,rep['gauge_labels'])
        face_dual=parent['canonical_momentum']-childzero['canonical_momentum']
        reset.update(named_central_Ar_temporal_dual=frame@face_dual,
            declared_prescribed_wall_lift_temporal_dual=L.T@face_dual,
            temporal_dual_in_named_constraint_coordinates=np.linalg.solve(C@C.T,C@face_dual),
            named_frame_field_indices=(np.asarray(lifts['frame_indices'])[:,None]*4+np.arange(4)).ravel())
        parent['all_wall_value_residual']=W@parent['total_field']-parentwall[0].reshape(80,3)
        parent['all_wall_rate_residual']=W@parent['total_coordinate_rate']-parentwall[1].reshape(80,3)
        parent['named_central_Ar_value_rows']=frame@parent['total_field'];parent['named_central_Ar_rate_rows']=frame@parent['total_coordinate_rate']
        parent['wall_frame_Euler_reactions']=np.linalg.solve(C@C.T,C@parent['original_unbordered_Euler_rows'])
        parent['original_reconstructed_Euler_rows']=parent['original_unbordered_Euler_rows']-C.T@parent['wall_frame_Euler_reactions']
        # Actual birth is rawpair at t=0, NOT a midpoint relabeled a face.
        # Re-evaluate original momenta on those fresh rows, preserving the
        # integrated parent's full field/rate as the comparison state.
        fresh_parent=dict(total_field=parent['total_field'],total_coordinate_rate=parent['total_coordinate_rate'],
            canonical_momentum=bornforms[0]['M']@parent['total_coordinate_rate']+bornforms[0]['B_reverse']@parent['total_field'],
            original_action_force=bornforms[0]['K']@parent['total_field']+bornforms[0]['B_forward']@parent['total_coordinate_rate'])
        comparisons={
            'parent_endpoint_source_minus_fresh_birth_Q':parentwall[0]-bornsource[0]['Q'],
            'parent_endpoint_source_rate_minus_fresh_birth_Qt':parentwall[1]-bornsource[0]['Q_coordinate_time'],
            'fresh_child_minus_parent_birth_Q':bornsource[1]['Q']-bornsource[0]['Q'],
            'fresh_child_minus_parent_birth_Qt':bornsource[1]['Q_coordinate_time']-bornsource[0]['Q_coordinate_time'],
            'child_zero_restart_source_minus_fresh_birth_Q':childwall[0]-bornsource[1]['Q'],
            'child_zero_restart_source_rate_minus_fresh_birth_Qt':childwall[1]-bornsource[1]['Q_coordinate_time'],
            'parent_Qt_proper_clock':parentwall[1]/(1j*births[0]['stage']['induced_lapse'].item()),
            'fresh_parent_birth_Qt_proper_clock':bornsource[0]['Q_coordinate_time']/(1j*births[0]['stage']['induced_lapse'].item()),
            'fresh_child_birth_Qt_proper_clock':bornsource[1]['Q_coordinate_time']/(1j*births[1]['stage']['induced_lapse'].item()),
            'fresh_parent_momentum_minus_integrated_target':fresh_parent['canonical_momentum']-parent['canonical_momentum'],
            'fresh_parent_original_all_At_Gauss_rows':fresh_parent['original_action_force'][:64],
            'inherited_parent_dynamic_value_source_residual':W@parent['total_field']-bornsource[1]['Q'].reshape(80,3)}
        dynamic=np.r_[reset['original_dynamic_field_indices'],reset['original_Higgs_field_indices']]
        source_value_compatible=maximum(comparisons['inherited_parent_dynamic_value_source_residual'])<=guard
        launch=None;launchreport=dict(attempted=False,admitted=False,reason='fresh child source value does not match retained parent field trace')
        if source_value_compatible:
            # Q/Qt comes from the actual birth action. No arbitrary Qtt is
            # supplied, and no At-time tangent/exterior response is invented.
            launch=inherited_birth_interior_reconstitution(bornforms[1],S,L,parent['total_field'],parent['canonical_momentum'],
                (bornsource[1]['Q'],bornsource[1]['Q_coordinate_time']),na)
            launch.update(original_all_At_Gauss_rows=launch['original_action_force'][:64],
                inherited_dynamic_value_rows=launch['inherited_field_value_residual'][dynamic],
                inherited_dynamic_momentum_rows=launch['inherited_canonical_momentum_residual'][dynamic],
                all_wall_value_rows=W@launch['total_field']-bornsource[1]['Q'].reshape(80,3),
                all_wall_rate_rows=W@launch['total_coordinate_rate']-bornsource[1]['Q_coordinate_time'].reshape(80,3),
                named_central_Ar_rows=frame@launch['total_field'],named_central_Ar_rate_rows=frame@launch['total_coordinate_rate'])
            rows=np.r_[launch['inherited_dynamic_value_rows'].ravel(),launch['inherited_dynamic_momentum_rows'].ravel(),
                launch['original_all_At_Gauss_rows'].ravel(),launch['all_wall_value_rows'].ravel(),launch['all_wall_rate_rows'].ravel()]
            launchreport=dict(attempted=True,admitted=maximum(rows)<=guard,original_all_rows_max=maximum(rows),
                original_dynamic_value=metric(launch['inherited_dynamic_value_rows']),original_dynamic_momentum=metric(launch['inherited_dynamic_momentum_rows']),
                original_all_At_Gauss=metric(launch['original_all_At_Gauss_rows']),interior_Gauss=metric(launch['original_interior_Gauss_rows']),
                interior_momentum=metric(launch['original_interior_momentum_rows']),
                reason='all unbordered original rows guard, not interior/frame balance, determines admission')
        save(case+'_parent_finite_prefix_face.npz',parent);save(case+'_child_zero_Cauchy_control_face.npz',childzero)
        save(case+'_actual_birth_source_and_original_reset_rows.npz',dict(comparisons,**reset,raw_pair=rawpair,reference_pair=refs,
            parent_raw_source_first=rawdirs[0],child_raw_source_first=rawdirs[1],parent_fresh_Q=bornsource[0]['Q'],child_fresh_Q=bornsource[1]['Q'],
            parent_fresh_Qt=bornsource[0]['Q_coordinate_time'],child_fresh_Qt=bornsource[1]['Q_coordinate_time'],
            parent_fresh_Q_first=bornsource[0]['Q_first'],child_fresh_Q_first=bornsource[1]['Q_first'],
            parent_fresh_Qt_first=bornsource[0]['Q_coordinate_time_first'],child_fresh_Qt_first=bornsource[1]['Q_coordinate_time_first'],
            value_permutation=ids,original_interior_field_lift=S,actual_parent_birth_momentum=fresh_parent['canonical_momentum']))
        if launch is not None:save(case+'_conditional_inherited_child_constitutive_face.npz',launch)
        report=dict(case=case,source_folders=[a['source_folder']for a in loaded],
            original_zero_child_reset_rows={k:metric(reset[k])for k in('gauge_trace','Higgs_trace','gauge_temporal_dual','Higgs_temporal_dual')},
            declared_named_frame_temporal_dual=metric(reset['named_central_Ar_temporal_dual']),
            declared_prescribed_wall_lift_temporal_dual=metric(reset['declared_prescribed_wall_lift_temporal_dual']),
            source_comparisons={k:metric(v)for k,v in comparisons.items()},
            parent_original_interior_Gauss_max=maximum(parent['original_interior_Gauss_rows']),
            parent_original_interior_momentum_max=maximum(parent['original_interior_momentum_rows']),
            parent_original_reconstructed_Euler_max=maximum(parent['original_reconstructed_Euler_rows']),
            parent_wall_frame_Euler_reaction_norm=float(np.linalg.norm(parent['wall_frame_Euler_reactions'])),
            parent_full_field_norm=float(np.linalg.norm(parent['total_field'])),parent_full_momentum_norm=float(np.linalg.norm(parent['canonical_momentum'])),
            source_value_compatible=source_value_compatible,conditional_child_launch=launchreport,
            matched_child_propagation_executed=False)
        reports[case]=report;print(json.dumps(report,sort_keys=True),flush=True)
        if launchreport['admitted']:
            raise RuntimeError('admitted child requires immediate source-on continuation; do not freeze at launch only')
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('actual source/action byte changed')
    result=dict(classification='EVALUATED_ACTUAL_BIRTH_MAGNETIC_FIELD_SOURCE_AND_TEMPORAL_MATCHING',input_hashes=pins,archives=archives,
        applications=reports,action_parameters=params,original_guard=guard,
        parent_endpoint_exact_saved_sigma=1.,child_restart_control_sigma=0.,fresh_birth_raw_time=0.,
        source_Hermite_midpoints_not_relabelled_birth=True,own_parent_Lorentz_momentum_not_joint_endpoint_grafted=True,
        original_fixed_affine_trace_B_derivative_zero_at_held_geometry=True,temporal_dual='Pi_parent-Pi_child in original dynamic64/H4 rows',
        no_fitted_Q_Hermite_shift_or_childzero_matching_assumed=True,
        parent_dynamic_q_and_canonical_Pi_targets_preserved=True,
        wall_frame_and_all_At_Gauss_defects_retained=True,
        named_frame_and_prescribed_wall_dual_coordinates_separated_from_free_interior_natural_rows=True,
        next_action='coupled magnetic birth/source solve must satisfy original dynamic64/H4 value and temporal-dual rows plus the same fresh source Q/Qt and all original Gauss/frame/wall contacts; then propagate the on-at-birth source through actual child stages without restarting the C2 pulse',
        no_native_heat_pole_LSZ_charge_or_physical_muon_selected=True,
        scope='held-geometry original n1 magnetic field birth application on actual raw pair, with retained finite incoming prefix and explicit source/stage discrepancy; no physical event/exterior selection or action accuracy enclosure')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),archives=len(archives),pins=len(pins))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();materialize(a.output)
