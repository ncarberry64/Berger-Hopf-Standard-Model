"""New signed n1 coefficient epoch at the exact four finite-pole raw stages.

Historical coefficient epochs are searched by full raw equality first. No
historical field, source integration, D5 action or pole is recomputed.
"""
from pathlib import Path
from hashlib import sha256
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import argparse
import json
import sys
import time


def assemble(repository,output):
    import numpy as np
    root,out=Path(repository).resolve(),Path(output).resolve()
    out.mkdir(parents=True,exist_ok=False);sys.path[:0]=[str(root/'src'),str(root/'scripts')]
    from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
    from bhsm.interface.muon_holomorphic_n1_magnetic_action import (
        original_signed_stage,signed_n1_forms,holomorphic_local_B_trace,magnetic_angular_trace,
        original_named_wall_lift,complete_gauge_wall_constraints)
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    pins={};archives={}
    def read(p):
        p=Path(p);pins[str(p)]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_text(encoding='utf8'))
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def save(name,a):
        p=out/name;_compressed_npz(p,a);archives[name]=sha256(p.read_bytes()).hexdigest()
    trial=root/'artifacts/muon_fixed_parent_finite_shooting_20261012/run_1/trial_0000'
    d5=root/'artifacts/muon_trial_d5_trace_action_20261012/trial_0000_corrected_sigma_energy_0_run_2'
    candidate=read(trial/'candidate.npz');d5md=read(d5/'result.json');trialmd=read(trial.parent/'result.json')
    stages=[read(trial/f'stage_{j:04d}.npz')for j in range(2)]
    search=[];old=root/'artifacts/muon_holomorphic_n1_magnetic_action_20261012'
    for p in sorted(old.glob('*/stage_*_actual_magnetic_trace.npz')):
        a=read(p)
        search.append(dict(path=str(p),sha256=pins[str(p)],exact_raw_matches=[j for j,s in enumerate(stages)if np.array_equal(a['source_raw'],s['stage_raw'])],
            minimum_raw_maximum_difference=min(float(np.max(abs(a['source_raw']-s['stage_raw'])))for s in stages)))
    if any(a['exact_raw_matches']for a in search):
        raise RuntimeError('An existing exact raw-stage coefficient epoch must be checked for reuse before assembly')
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=root)
    for p,h in phase['input_hashes'].items():pins[str(root/p)]=h
    rep=phase['representation'];angular=magnetic_angular_trace()
    config=read(root/'artifacts/muon_calibrated_pauli_20261009/inputs.json')
    charge=float(np.sqrt(4*np.pi*config['alpha_consumer']['value']))
    params=trialmd['action_parameters'];records=[]
    affine=lambda a:np.r_[a[37:74],np.zeros(61,complex),a[99],np.zeros(169,complex)]
    for j,s in enumerate(stages):
        begin=time.perf_counter();c=read(d5/f'stage_{j:04d}_current_geometry_normal_and_material_trace.npz')
        raw=s['stage_raw'];clock=c['canonical_raw_coordinate_time_direction']
        if not np.array_equal(raw[260:264],c['intrinsic_H_realified']):raise ValueError('Different D5 intrinsic field')
        for p in (trial/'candidate.npz',trial/f'stage_{j:04d}.npz'):
            rel=p.relative_to(root).as_posix()
            if pins[str(p)]!=d5md['input_hashes'][rel]:raise ValueError('Different finite-pole input stage')
        b=original_signed_stage(raw,clock[:,None],s['parent_source_raw'],affine(candidate['raw_pair'][0])[:,None],
            s['reference_stage_pair'],np.array([affine(a)for a in candidate['reference_pair']])[:,:,None],rep,
            side='child',lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=params['nu_squared_action'])
        f=signed_n1_forms(b,angular)
        Q=holomorphic_local_B_trace(raw,clock[:,None],b['stage'],electric_charge=charge,angular=angular)
        # Only the coordinate maps are shared with earlier stages.
        ids=b['value_permutation'];lifts=b['lifts'];labels=rep['gauge_labels'];frames=set(lifts['frame_indices'].tolist())
        kept=[i for i,k in enumerate(ids)if i not in frames and(k>=80 or not labels[k].get('wall_lift',False))]
        S=np.kron(np.eye(84)[:,kept],np.eye(4));L=np.kron(original_named_wall_lift(rep,ids),np.eye(4))
        C=complete_gauge_wall_constraints(lifts,4)['constraint']
        na=sum(ids[i]<80 and labels[ids[i]]['field']=='A_tau'for i in kept)*4
        if (len(kept),na,S.shape)!=(61,48,(336,244)):raise ValueError('Original field incidence changed')
        save(f'stage_{j:04d}_exact_raw_signed_n1_forms_and_source.npz',dict(
            **{k:v for k,v in f.items()if isinstance(v,np.ndarray)},
            **{k:v for k,v in Q.items()if isinstance(v,np.ndarray)},
            raw268=raw,actual_raw_coordinate_time=clock,parent_raw268=s['parent_source_raw'],reference_raw_pair=s['reference_stage_pair'],
            coordinate_time=s['coordinate_time'],coordinate_step=s['coordinate_step'],
            original_value_permutation=ids,interior_field_lift=S,named_wall_lift=L,wall_and_frame_rows=C,
            coordinate_interior_At_count=np.array(na),angular_derivatives=angular['derivative_matrices']))
        records.append(dict(stage=j,coefficient_dimension=336,interior_dynamic_positions=196,interior_At_Gauss=48,
            full_At_Gauss_rows=64,named_frames=16,independent_wall_plus_frame_rows=92,
            scalar_gauge_cross_norm=float(np.linalg.norm(f['K'][-16:,:-16])),
            background_gauge_norm=float(np.linalg.norm(b['row']['A'])),background_H_norm=float(np.linalg.norm(b['row']['H'])),
            source_Q_norm=float(np.linalg.norm(Q['Q'])),source_Q_clock_norm=float(np.linalg.norm(Q['Q_coordinate_time']))))
        print(json.dumps(dict(assembly_wall_seconds=time.perf_counter()-begin,**records[-1])),flush=True)
    for name,module in list(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and p and Path(p).is_relative_to(root):pins[str(Path(p))]=sha256(Path(p).read_bytes()).hexdigest()
    for p,h in pins.items():
        if sha256(Path(p).read_bytes()).hexdigest()!=h:raise ValueError('Coefficient input changed: '+p)
    result=dict(classification='NEW_EXACT_FOUR_FINITE_POLE_STAGE_SIGNED_N1_WEAK_PROBE_COEFFICIENT_EPOCH',
        records=records,reuse_search=search,input_hashes=pins,archives=archives,
        literal_background_self_fields_retained=True,old_field_response_reused=False,
        newly_assembled_only_two_exact_raw_stage_coefficients=True,
        electric_charge=charge,charge_scope='Existing source convention alpha consumer reused; no new charge calibration or LSZ claim',
        original_H_and_gauge_Gauss_wall_frame_rows_retained=True,
        actual_physical_formed_muon_or_outgoing_exterior_selected=False,
        finite_probe_initial_preparation='New infinitesimal measuring perturbation has zero incoming x/Pi before finite C2 turn-on; this does not zero the supplied background self-field',
        baseline_primal_residual_not_zeroed=True,physical_derivative_admitted=False,matching_correction_applied=False,
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print(json.dumps(dict(result=str(p),sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();assemble(a.repository,a.output)
