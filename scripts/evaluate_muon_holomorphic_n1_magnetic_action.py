"""Apply the original signed magnetic trace on actual changing canonical stages."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_holomorphic_n1_magnetic_action import (
    original_signed_stage,magnetic_angular_trace,holomorphic_local_B_trace,
    signed_n1_forms,signed_n1_form_first,known_wall_source_weak_response,
    magnetic_unsquared_unit_em_current,
)
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
from bhsm.interface.muon_holomorphic_n1_magnetic_cauchy import causal_prescribed_magnetic_prefix
from bhsm.interface.muon_holomorphic_current_source import two_term_complex_sum


def materialize(source_folder,side,case,output):
    src=ROOT/source_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve every signed magnetic application')
    pins={};archives={}
    def read(p,expected=None):
        p=ROOT/p if not p.is_absolute()else p
        if not p.is_relative_to(ROOT):raise ValueError('source belongs to the same calling checkout')
        data=p.read_bytes();digest=sha256(data).hexdigest();pins[p.relative_to(ROOT).as_posix()]=digest
        if expected is not None and digest!=expected:raise ValueError('same changing stage archive changed')
        if p.suffix=='.json':return json.loads(data)
        with np.load(p,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    md=read(src/'result.json')
    # Only the original field/radial coordinate representation is reused.
    # No saved old phase field, current, magnetic response or Green enters.
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=ROOT)
    pins.update(phase['input_hashes']);rep=phase['representation']
    config=read(Path('artifacts/muon_calibrated_pauli_20261009/inputs.json'))
    electric_charge=float(np.sqrt(4*np.pi*config['alpha_consumer']['value']))
    parameters=md['action_parameters'];angular=magnetic_angular_trace()
    names=sorted(n for n in md['archives']if n.startswith(side+'_')and n.endswith('_'+case+'_source_response.npz'))
    if len(names)!=2:raise ValueError('the completed actual equal-step two-stage arm is required')
    # Pin imported executable bytes BEFORE any action/response work.
    for n,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if n.startswith('bhsm.')and p:
            p=Path(p)
            if p.is_relative_to(ROOT):pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    focused=(Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_holomorphic_n1_magnetic_action.py',
        'tests/test_muon_complex_n1_literal_action.py','tests/test_muon_complex_n1_row_polynomial.py',
        'tests/test_muon_holomorphic_n1_magnetic_cauchy.py','tests/test_muon_n1_magnetic_current_independent.py',
        'tests/test_muon_holomorphic_n1_magnetic_current_first.py')
    for rel in focused:pins[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    out.mkdir(parents=True);bindings=[];forms=[];first_forms=[];sources=[];steps=[];records=[]
    def save(name,obj):
        p=out/name;_compressed_npz(p,{k:v for k,v in obj.items()if isinstance(v,np.ndarray)})
        if p.stat().st_size>=10*1024**2:raise ValueError('split original source/current operands below10MiB')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    for j,name in enumerate(names):
        a=read(src/name,md['archives'][name]['sha256']);directions=lambda n:np.stack((a[n+'_high'],a[n+'_low']),axis=-1)
        b=original_signed_stage(a['stage_raw'],directions('stage_raw_direction'),a['parent_source_stage_raw'],
            directions('parent_source_stage_raw_direction'),a['reference_stage_pair'],directions('reference_stage_direction'),
            rep,side='parent'if side=='incoming'else'child',lambda_H=rep['scalar_matching']['lambda_H'],
            nu_squared_action=parameters['nu_squared_action'])
        f=signed_n1_forms(b,angular);df=signed_n1_form_first(b,angular)
        s=holomorphic_local_B_trace(a['stage_raw'],directions('stage_raw_direction'),b['stage'],
            electric_charge=electric_charge,angular=angular)
        save(f'stage_{j}_original_signed_forms.npz',f)
        for k,label in enumerate(('high','low')):
            save(f'stage_{j}_original_signed_forms_first_{label}.npz',{n:v[k]for n,v in df.items()if isinstance(v,np.ndarray)and n!='row_polynomial_coefficient_scales'})
        save(f'stage_{j}_actual_magnetic_trace.npz',dict(s,coordinate_time=a['coordinate_time'],coordinate_time_step=a['coordinate_time_step'],
            angular_derivatives=angular['derivative_matrices'],source_raw=a['stage_raw'],source_direction_high=a['stage_raw_direction_high'],
            source_direction_low=a['stage_raw_direction_low'],row_polynomial_coefficient_scales=df['row_polynomial_coefficient_scales']))
        bindings.append(b);forms.append(f);first_forms.append(df);sources.append(s);steps.append(complex(a['coordinate_time_step']))
        records.append(dict(stage_index=j,source_archive=name,Q_norm=float(np.linalg.norm(s['Q'])),Qt_norm=float(np.linalg.norm(s['Q_coordinate_time'])),
            Q_first_high_norm=float(np.linalg.norm(s['Q_first'][0])),Q_first_low_norm=float(np.linalg.norm(s['Q_first'][1])),
            K_norm=float(np.linalg.norm(f['K'])),M_norm=float(np.linalg.norm(f['M'])),H_gauge_cross_norm=float(np.linalg.norm(f['K'][-16:,:-16]))))
        print(json.dumps(dict(stage='actual_signed_n1_field_and_B_trace',side=side,case=case,**records[-1]),sort_keys=True),flush=True)
    response=known_wall_source_weak_response(forms,first_forms,np.array(steps),sources,rep,bindings[0]['value_permutation'])
    save('original_prescribed_magnetic_response.npz',response)
    point={n:np.array([r[n]for r in response['point_sources']])for n in response['point_sources'][0]}
    save('complete_magnetic_value_rate_source_points.npz',point)
    current=magnetic_unsquared_unit_em_current(bindings,np.array(steps),response)
    for name in ('total','operator_insertion','right_current_motion','literal_left_motion'):
        hi,lo=two_term_complex_sum(current[name+'_first'][0],current[name+'_first'][1])
        current[name+'_first_combined_high']=hi;current[name+'_first_combined_low']=lo
    save('actual_magnetic_unsquared_unit_EM_current.npz',current)
    # Explicitly restore future-coordinate order for the incoming path.
    order=np.array([1,0])if side=='incoming'else np.array([0,1])
    future_steps=-np.array(steps)[order]if side=='incoming'else np.array(steps)[order]
    future_bindings=[bindings[j]for j in order];future_forms=[forms[j]for j in order];future_sources=[sources[j]for j in order]
    causal=causal_prescribed_magnetic_prefix(future_forms,future_steps,future_sources,rep,bindings[0]['value_permutation'],
        forms_first=[first_forms[j]for j in order])
    save('actual_zero_Cauchy_magnetic_prefix.npz',dict(causal,original_stage_order=order,future_coordinate_steps=future_steps))
    causal_points={n:np.array([r[n]for r in causal['point_sources']])for n in causal['point_sources'][0]}
    save('actual_zero_Cauchy_magnetic_source_points.npz',causal_points)
    causal_current=magnetic_unsquared_unit_em_current(future_bindings,future_steps,causal)
    for name in ('total','operator_insertion','right_current_motion','literal_left_motion'):
        hi,lo=two_term_complex_sum(causal_current[name+'_first'][0],causal_current[name+'_first'][1])
        causal_current[name+'_first_combined_high']=hi;causal_current[name+'_first_combined_low']=lo
    save('actual_zero_Cauchy_magnetic_unit_EM_current.npz',causal_current)
    for n,module in sorted(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if n.startswith('bhsm.')and p:
            p=Path(p)
            if p.is_relative_to(ROOT):
                rel=p.relative_to(ROOT).as_posix();pins.setdefault(rel,sha256(p.read_bytes()).hexdigest())
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=v for p,v in pins.items()):raise ValueError('same source/producer bytes changed')
    maxima=lambda key:float(np.max(abs(response[key])))
    result=dict(classification='EVALUATED_CHANGING_CANONICAL_SIGNED_N1_PRESCRIBED_MAGNETIC_ACTION_AND_UNSQUARED_EM_CURRENT',
        input_hashes=pins,archives=archives,source_folder=source_folder.as_posix(),side=side,case=case,stages=records,
        original_field_layout=84,angular_harmonics=4,field_rows_per_trace=336,At_Gauss_rows_per_trace=64,
        named_central_Ar_frame_rows_per_trace=16,independent_gauge_wall_rows_per_trace=76,
        all20_gauge_wall_components_prescribed=True,H_natural_and_full_gauge_H_cross_retained=True,
        original_rows_max=maxima('original_rows'),original_first_rows_max=maxima('original_first_rows'),
        bordered_Gauss_balance_rows_max=maxima('bordered_Gauss_balance_rows'),
        unbordered_Gauss_action_rows_max=maxima('unbordered_Gauss_rows'),
        unbordered_free_interior_rows_max=maxima('unbordered_free_interior_rows'),
        unbordered_free_interior_Gauss_rows_max=maxima('unbordered_free_interior_Gauss_rows'),
        original_rowwise_balance_estimate_max=maxima('original_rowwise_balance_estimate'),
        wall_reaction_norm=float(np.linalg.norm(response['wall_reactions'])),frame_reaction_norm=float(np.linalg.norm(response['frame_reactions'])),
        full_wall_value_defect_max=float(np.max(abs(point['original_full_wall_rows']))),
        full_wall_rate_defect_max=float(np.max(abs(point['original_full_wall_rate_rows']))),
        H_response_norm=float(np.linalg.norm(response['field_coefficients'][:,-16:])),
        response_norm=float(np.linalg.norm(response['field_coefficients'])),
        response_first_high_norm=float(np.linalg.norm(response['field_coefficients_first'][0])),
        response_first_low_norm=float(np.linalg.norm(response['field_coefficients_first'][1])),
        unused_affine_source_corner_jump_norm=float(np.linalg.norm(response['unused_stage_affine_wall_corner_jump'])),
        actual_source_single_Hermite_and_its_derivative=True,C2_ramp_duration_fraction=.25,initial_B_value_and_rate_zero=True,
        computational_coordinate_step_orientation=side+' '+('negative backward prefix'if side=='incoming'else'positive outgoing prefix'),
        initial_unknown_field_held_zero_final_natural=True,retarded_zero_Cauchy_not_substituted=True,
        electric_charge=electric_charge,eR4_squared_half_source_count=1,
        actual_magnetic_current_norm=float(np.linalg.norm(current['total'])),
        current_terms={n:float(np.linalg.norm(current[n]))for n in('operator_insertion','right_current_motion','literal_left_motion')},
        weak_current_first_high_norm=float(np.linalg.norm(current['total_first'][0])),
        weak_current_first_low_norm=float(np.linalg.norm(current['total_first'][1])),
        finite_causal_prefix_original_stage_order=order.tolist(),incoming_future_direction_reconstructed=side=='incoming',
        causal_initial_x_p_zero=True,causal_numerical_rows_max=causal['original_reconstructed_rows_max'],
        causal_momentum_kind=causal['canonical_momentum_kind'],
        causal_interior_Gauss_rows_max=float(np.max(abs(causal_points['original_At_interior_Gauss_rows']))),
        causal_all_wall_value_rows_max=float(np.max(abs(causal_points['original_full_wall_rows']))),
        causal_all_wall_rate_rows_max=float(np.max(abs(causal_points['original_full_wall_rate_rows']))),
        causal_unbordered_At_wall_and_frame_reactions_retained=True,
        causal_final_state_norm=float(np.linalg.norm(causal['final_reduced_canonical_state'])),
        causal_magnetic_current_norm=float(np.linalg.norm(causal_current['total'])),
        causal_current_terms={n:float(np.linalg.norm(causal_current[n]))for n in('operator_insertion','right_current_motion','literal_left_motion')},
        causal_current_first_high_norm=float(np.linalg.norm(causal_current['total_first'][0])),
        causal_current_first_low_norm=float(np.linalg.norm(causal_current['total_first'][1])),
        causal_current_first_terms={n:[float(np.linalg.norm(causal_current[n+'_first'][k]))for k in range(2)]
            for n in('operator_insertion','right_current_motion','literal_left_motion')},
        causal_vs_weak_current_difference_norm=float(np.linalg.norm(causal_current['total']-current['total'])),
        causal_vs_weak_current_difference_is_not_a_residual_error_bound=True,
        mixed_current_keeps_both_Green_responses_and_Higgs_charge_Hessian=True,
        causal_background_source_first_response_executed=True,
        causal_final_state_first_high_norm=float(np.linalg.norm(causal['final_reduced_canonical_state_first'][0])),
        causal_final_state_first_low_norm=float(np.linalg.norm(causal['final_reduced_canonical_state_first'][1])),
        causal_first_Gauss_rows_max=float(np.max(abs(causal_points['original_first_At_Gauss_rows']))),
        causal_first_full_reconstructed_rows_max=float(np.max(abs(causal_points['original_first_reconstructed_rows']))),
        causal_original_action_force_max=float(np.max(abs(causal_points['original_action_force']))),
        causal_original_canonical_momentum_time_max=float(np.max(abs(causal_points['canonical_momentum_time']))),
        causal_original_row_uncancelled_scale_max=float(np.max(causal_points['original_row_uncancelled_scale'])),
        causal_original_rowwise_balance_estimate_max=float(np.max(abs(causal_points['original_reconstructed_rows'])/
            (causal_points['original_row_uncancelled_scale']+np.finfo(float).tiny))),
        causal_reduced_source_value_max=float(np.max(abs(causal_points['canonical_reduced_source_value']))),
        causal_reduced_source_momentum_max=float(np.max(abs(causal_points['canonical_reduced_source_rate']))),
        causal_child_initial_state_separate_control_not_fitted_birth_reset=True,
        unit_Haar_phi0=1.,fermion_source_shells=[0,1],full18_all_families_neutral_returns=True,
        actual_left_current_is_supplied_unit_EM_test_transpose=True,
        old_magnetic_fields_or_positive_reference_operator_consumed=False,
        representation_only_reused_from_frozen_coordinate_seed=True,
        stage_source_high_low_acted_before_products=True,row_polynomial_derivative_degree=5,
        source_quadrature_points=len(point['sigma']),fixed_stage_source_force_Gauss_degree=9,
        physical_retarded_magnetic_initial_adiabatic_state='finite initial-zero canonical prefix evaluated; next action-owned birth/reset propagation and adiabatic/soft exterior trace, not an independent datum request',
        quantum_contact_both_loop_insertions_own_mean_overlap_or_normalized_Gamma2_not_completed=True,
        reached_physical_normalization_relation='Gamma2(E)=Bi(E)+Bf(E)U(E); Gamma2(Epole)R=0, L Gamma2(Epole)=0, Z=L Gamma2_E R; these physical action/exterior rows are not Gamma_initial=I',
        next_physical_source_equation='admitted coupled birth/formation trace and adiabatic exterior continuation must supply Bi/Bf and their B/source contacts, then -Z^-1 L Gamma2_B R; no fitted pole or current norm substitute',
        physical_Bi_Bf_pole_spin_LSZ_charge_or_Pauli_selected=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary signed field/action source equation and declared finite C2/Hermite prefix current; no chronological continuum, physical source/event/exterior/native uncertainty enclosure')
    path=out/'result.json';path.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(path.read_bytes()).hexdigest(),original_rows_max=result['original_rows_max'],
        field_norm=result['response_norm'],H_norm=result['H_response_norm'],current_norm=result['actual_magnetic_current_norm'])),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-folder',type=Path,required=True)
    p.add_argument('--side',choices=('incoming','outgoing'),required=True);p.add_argument('--case',choices=('normal_basis','area_source'),required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();materialize(a.source_folder,a.side,a.case,a.output)
