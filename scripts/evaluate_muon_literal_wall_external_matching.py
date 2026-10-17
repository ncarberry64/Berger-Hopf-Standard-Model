"""Apply the corrected coupled current to its full external pole matching jet."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from evaluate_muon_coupled_lorentz_radial_green import encode
from evaluate_muon_reached_trace_action import deterministic_archive
from bhsm.interface.muon_literal_wall_external_matching import paired_physical_y_wall_current,full_c6_positive_pole_jet,normalized_pole_spin_covectors
from bhsm.interface.muon_inherited_normal_readout_frame import phase_normal_readout_frame
from bhsm.interface.muon_profile_preserving_phase_sample import profile_preserving_lepton_sample
from bhsm.interface.muon_birth_finite_normal_trace_graph import pointwise_finite_normal_action
from bhsm.interface.muon_birth_inherited_finite_normal_phase import inherited_child_finite_normal_action
from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from bhsm.interface.muon_coupled_lorentz_field_symbol import coupled_field_symbol
from bhsm.interface.muon_coupled_lorentz_radial_green import coupled_radial_trace_application
from bhsm.interface.muon_static_coupled_charged_current import static_coupled_charged_current
from bhsm.interface.muon_coupled_tensor_decay_rate import tensor_tree_decay_rate,temporal_charged_current_series
from bhsm.interface.muon_tensor_lifetime_unit_matching import temporal_tensor_lifetime_match


def materialize(output):
    out=Path(output);out=out if out.is_absolute()else ROOT/out
    if out.exists():raise FileExistsError('preserve prior pole/current matching applications')
    refs={};arrays={};records=[]
    def pin(p,expected=None):
        p=Path(p);p=p if p.is_absolute()else ROOT/p;h=sha256(p.read_bytes()).hexdigest()
        if expected is not None and h!=expected:raise ValueError('same corrected action input changed: '+str(p))
        refs[p.relative_to(ROOT).as_posix()]=h;return p
    def read(p,expected=None):
        with np.load(pin(p,expected),allow_pickle=False)as f:return{k:f[k].copy()for k in f.files}
    source=ROOT/'artifacts/muon_literal_euclidean_wall_y_response_20261011/run_1'
    md=json.loads(pin(source/'result.json').read_bytes())
    if md['classification']!='EVALUATED_SHARED_Y_LITERAL_COUPLED_WALL_CURRENT_AND_ENERGY_COEFFICIENTS':raise ValueError('literal same coupled Clifford current required')
    refs.update(md['input_hashes'])
    cfg=json.loads(pin('artifacts/muon_calibrated_pauli_20261009/inputs.json').read_bytes())
    v=cfg['selected_consumer_values'];M=v['m_mu_GeV']['value'];me=v['m_e_GeV']['value']
    charge=float(np.sqrt(4*np.pi*cfg['alpha_consumer']['value']))
    tau=cfg['primary_measurements']['positive_muon_lifetime']['value']*1e-12;hbar=float(cfg['unit_convention']['hbar_GeV_s'])
    wall=ROOT/'artifacts/muon_literal_euclidean_wall_action_20261011/run_2'
    wm=json.loads(pin(wall/'result.json').read_bytes())
    for side in('incoming','outgoing'):
        phase,_=retained_input(side,refs);frame=phase_normal_readout_frame(phase,family=1,electric_charge=charge)
        actual_operator=profile_preserving_lepton_sample(phase,0.)['operator']
        raw=frame['raw_fields'];rep=phase['representation'];params=phase['receipt']['action_parameters']
        # The lifetime normalization is re-evaluated at this SAME external
        # observation germ.  Older true-endpoint v/y are not grafted here.
        w=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],source_value=raw[98],source_rate=raw[99])
        N,R=float(w['induced_lapse'].value),float(w['R4'].value)
        action=(pointwise_finite_normal_action(raw,rep,**params)if side=='incoming'else
            inherited_child_finite_normal_action(raw,0.,phase['arrays']['initial_pair'],phase['arrays']['reference_pair'],rep,**params))
        symbol=coupled_field_symbol(action,rep,lapse=N,H=raw[260:264])
        C,Q,T,r,F=(symbol[k]for k in('proper_frequency_coefficients','field_quotient_lift','joint_trace_map','scalar_radial_source','central_radial_frame_rows'))
        green=coupled_radial_trace_application(C,Q,T,r,F,frequency=0.)
        current=static_coupled_charged_current(green['joint_wall_Green'],frame['arguments']['H'],radius=R,lapse=N,family=1,out_family=2)
        tensor=current['full_charged_current_tensor'];static=tensor_tree_decay_rate(tensor,muon_mass_GeV=M,electron_mass_GeV=me,radial_order=24)
        seed=(static['tree_rate_coefficient_GeV5']*tau/hbar)**.25
        series=temporal_charged_current_series(C,Q,T,current['charged_current_right_vertices'],current['charged_current_left_vertices'],maximum_frequency=M/(.99*seed))
        matched=temporal_tensor_lifetime_match(tensor,series['temporal_current_coefficients'],muon_mass_GeV=M,electron_mass_GeV=me,lifetime_seconds=tau,hbar_GeV_seconds=hbar)
        energy_unit=matched['conditional_E_kappa_GeV'];calls=matched.pop('evaluated_rate_calls')
        prefix=side+'_';arrays[prefix+'observation_raw_fields']=raw;arrays[prefix+'observation_H']=frame['arguments']['H'];arrays[prefix+'conditional_rate_calls']=calls
        for name,obj in(('symbol',symbol),('current',current),('series',series)):
            arrays.update({prefix+name+'_'+k:a for k,a in obj.items()if isinstance(a,np.ndarray)})
        print(json.dumps(dict(stage='same_external_germ_complete_tensor_matching',side=side,E=energy_unit,VA_remainder=current['VA_relative_remainder']),sort_keys=True),flush=True)
        c=read(source/(side+'_coefficients.npz'),md['archives'][side+'_coefficients.npz']['sha256'])
        gn=side+'_cells_2_field_original_action_Green.npz';GB=read(wall/gn,wm['archives'][gn]['sha256'])['original_action_Green']
        app=paired_physical_y_wall_current(c,GB,y_middle=c['family_Y'][0],y_light=c['family_Y'][1])
        arrays.update({prefix+k:a for k,a in app.items()if isinstance(a,np.ndarray)})
        for family,part,mass in((1,app['middle'],M/energy_unit),(2,app['light'],me/energy_unit)):
            pole=full_c6_positive_pole_jet(frame['arguments']['H'],part['self_energy_zero'],part['self_energy_first'],family=family,matched_mass_action=mass)
            spin=normalized_pole_spin_covectors(pole,electric_charge=charge);pfx=prefix+'family_'+str(family)+'_'
            ids=np.array([2*family,2*family+1,6+2*family,7+2*family,12+2*family,13+2*family])
            full_body=actual_operator['H_can'][np.ix_(ids,ids)]
            body_pole=full_c6_positive_pole_jet(frame['arguments']['H'],part['self_energy_zero'],part['self_energy_first'],family=family,matched_mass_action=mass,tree_body=full_body)
            body_spin=normalized_pole_spin_covectors(body_pole,electric_charge=charge)
            arrays[pfx+'self_energy_zero']=part['self_energy_zero'];arrays[pfx+'self_energy_first']=part['self_energy_first']
            for label,obj in(('mass_only_pole',pole),('mass_only_spin',spin),('actual_body_pole',body_pole),('actual_body_spin',body_spin)):
                arrays.update({pfx+label+'_'+k:a for k,a in obj.items()if isinstance(a,np.ndarray)})
            record=dict(side=side,family=family,physical_Y=float(c['family_Y'][family-1]),conditional_action_mass=mass,
                conditional_lifetime_match=matched,current_full_tensor_VA_remainder=current['VA_relative_remainder'],
                self_energy_zero_norm=float(np.linalg.norm(part['self_energy_zero'])),self_energy_first_norm=float(np.linalg.norm(part['self_energy_first'])),
                mass_matching_load=pole['isotropic_mass_matching_load'],complex_spin_pole_remainder_norm=float(np.linalg.norm(pole['remaining_complex_spin_pole_matrix'])),
                kinetic_matching_load=pole['isotropic_kinetic_matching_load'],complex_kinetic_remainder_norm=float(np.linalg.norm(pole['remaining_complex_kinetic_matrix'])),
                current_normalization_residual_max=float(np.max(abs(spin['pole_current_normalization_residual']))),
                full_C6_positive_inverse_identity_residual_max=float(np.max(abs(pole['full_C6_to_positive_inverse_residual']))),
                source_residual_max=part['original_fermion_source_residual_max'],
                complement_condition_number=pole['complementary_block_condition_number'],
                mass_only_normal_symbol_Wilson_matching_not_performed=True,
                actual_tree_body_minus_fixed_Y_norm=float(np.linalg.norm(full_body-body_pole['fixed_Y_operator'])),
                actual_body_charged_upper_test_pole_matrix_norm=float(np.linalg.norm(body_pole['matched_positive_inverse'])),
                actual_body_current_normalization_residual_max=float(np.max(abs(body_spin['pole_current_normalization_residual']))),
                actual_body_full_inverse_identity_residual_max=float(np.max(abs(body_pole['full_C6_to_positive_inverse_residual']))))
            records.append(record);print(json.dumps(encode(dict(stage='literal_full_C6_external_matching',**record)),sort_keys=True),flush=True)
    for name in('muon_literal_wall_external_matching','muon_c6_external_pole_jet','muon_literal_euclidean_wall_y_response',
        'muon_magnetic_open_lepton_vertex','muon_native_dirac_hamiltonian','muon_inherited_normal_readout_frame','muon_profile_preserving_phase_sample',
        'muon_tensor_lifetime_unit_matching','muon_coupled_tensor_decay_rate','muon_coupled_lorentz_field_symbol',
        'muon_coupled_lorentz_radial_green','muon_static_coupled_charged_current'):
        pin('src/bhsm/interface/'+name+'.py')
    for name in('tests/test_muon_literal_wall_external_matching.py',Path(__file__).relative_to(ROOT).as_posix(),
        'scripts/evaluate_muon_reached_trace_action.py','scripts/evaluate_muon_continued_current_factor.py','scripts/evaluate_muon_coupled_lorentz_radial_green.py'):pin(name)
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('corrected current matching input changed')
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays);p=out/'application.npz'
    if p.stat().st_size>10*1024*1024:raise ArithmeticError('split archives rather than pruning')
    result=dict(classification='EVALUATED_LITERAL_COUPLED_CLIFFORD_CURRENT_EXTERNAL_POLE_RESIDUE_AND_SAME_GERM_LIFETIME_MATCHING',
        records=records,input_hashes=refs,archive=dict(path=p.name,bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest()),
        source_graph='one original natural-wall672 inverse, actual continued Clifford internal fermion and literal dual; fixed-Y evaluated exactly; c0 Gaussian -1',
        observation_graph='represented incoming/child birth observation with cell-held v/y; complete original84 tensor lifetime equation evaluated at this same germ',
        local_pole_equation='Actual constant-angular tree Hcan and mass-only normal-symbol pencils both exported; fullC6 Schur over four complement fibers retains complex matrix loads. Charged-upper tests are not selected physical pole states.',
        mass_only_matching_scope='Removing connection terms from the constant-angular current requires an actual Wilson/normal-symbol transform. This application explicitly does not assert that map.',
        pole_residue_equation='ell S6_prime r=I by analytic S_plus_prime inverse square root; residual S_plus(m) exported',
        charge_matching_required_vertex='Gamma_temporal=-e*S6_prime on the full charged matching lift; actual sourced gauge-orbit Ward completion not inferred from this requirement',
        mass_or_kinetic_counterterms_applied=False,Yukawa_fitted=False,measured_anomaly_consumed=False,
        physical_decay_scale_selected=False,physical_external_LSZ_identified=False,physical_native_cutoff_identified=False,
        same_background_overlap_subtracted=False,physical_F2=None,physical_a_mu=None,physical_g_mu=None,
        uncertainty_scope='binary exact-stored finite current/polynomial and external first-energy jet. Neither pole noncentral/imaginary remainder, nonVA radiative decay, spatial-momentum/domain complement, finite-c regulator, nor continuation/physical errors are set zero.',
        next_consumed_equation='apply each same-source magnetic placement between exported normalized literal left/right tests, add matching Ward/kinetic contact, and subtract only the matching local graph; complete actual pole remainder and finite-c/relative exterior contribution remain in that projected equation')
    rp=out/'result.json';rp.write_text(json.dumps(encode(result),indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(result_sha256=sha256(rp.read_bytes()).hexdigest(),archive=result['archive'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(materialize(a.output),sort_keys=True))
