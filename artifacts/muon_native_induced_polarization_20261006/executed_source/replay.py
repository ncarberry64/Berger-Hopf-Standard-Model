"""New cache-based source-form evaluations; no old production replay.

Use a fresh output. Full native induced polarization is not supplied by the
finite carrier contact or compact weak elements computed here.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface import muon_native_induced_polarization as impl
from control_muon_induced_heat import execute_control


def save(path,value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8')


def load(path):
    with np.load(path,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def run(output):
    if output.exists():raise FileExistsError('Fresh output required; preserve prior evidence')
    output.mkdir(parents=True);start=time.perf_counter()
    base=ROOT/'artifacts/muon_native_photon_response_20261006/run_1'
    paths=dict(component=base/'component_action_and_current.npz',frame=base/'enriched_frame.npz',
        source=ROOT/'artifacts/muon_matched_mechanical_source_20261002/replay_reference/matched_source_and_weak_actions.npz',
        parent=ROOT/'artifacts/muon_parent_source_contact_20261003/replay_reference/parent_source_contact.npz',
        rate=ROOT/'artifacts/muon_parent_source_rate_20261003/replay_reference/parent_source_rate_corrected.npz',
        rate_contract=ROOT/'artifacts/muon_exterior_face_source_20261002/replay_reference/result.json',
        frozen=ROOT/'artifacts/muon_source_jet_20261002/frozen_local.json',
        owner=ROOT/'src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',
        extension=ROOT/'src/bhsm/interface/muon_source_weak_extension.py',
        fixed_trace=ROOT/'src/bhsm/interface/aether_unified_m5_m4_pushforward_v15_69.py',
        source_compiler=ROOT/'src/bhsm/interface/muon_parent_source_contact.py',
        scalar_impedance=ROOT/'src/bhsm/interface/covariant_bubble_interface_mechanics.py',
        threshold=ROOT/'src/bhsm/interface/action_extension_ae2_nonfermion_threshold.py',
        relative_zeta=ROOT/'src/bhsm/interface/completion/stratified_dirac_zeta_micro_source_v14_63.py',
        relative_boundary=ROOT/'src/bhsm/interface/completion/boundary_triple_heat_semigroup_v14_65.py',
        kernel=ROOT/'src/bhsm/interface/arb_heat_pencil_contractions.py',
        builder=Path(impl.__file__),control=ROOT/'scripts/control_muon_induced_heat.py',replay=Path(__file__))
    hashes={k:dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for k,p in paths.items()}
    git=lambda *args:subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    save(output/'input_hashes.json',hashes)
    save(output/'starting_revision.json',dict(HEAD=git('rev-parse','HEAD'),branch=git('branch','--show-current'),
        scientific_reference='524ed90689bd5923c249bba2e699abf627e703cd',
        working_tree_status=git('status','--short'),intentional_differences='new source-form/length-jet work only'))
    (output/'starting_diff.patch').write_text(git('diff','--binary')+'\n',encoding='utf8')
    component,frame,source,parent,rate=[load(paths[k]) for k in ('component','frame','source','parent','rate')]
    save(output/'checkpoint.json',dict(stage='read frozen inputs; no prior producer or solve rerun'))
    actions,checks=impl.affine_cut_jets(component,frame['M_orthonormal_frame'],source,parent)
    np.savez_compressed(output/'affine_source_contacts.npz',**actions)
    save(output/'checkpoint.json',dict(stage='new local32x8x64x64 contact evaluated; NOT a heat trace'))
    weak,weak_checks=impl.compact_weak_first_jets(actions['real_test_frame'],component,source,parent,rate)
    np.savez_compressed(output/'compact_weak_first_jets.npz',**weak)
    checks.update(weak_checks)
    local=impl.local_subtraction_component(component,actions['real_test_frame'],actions['local_Riesz_current_coordinates'])
    old_coordinates=(frame['M_orthonormal_frame'].conj().T@component['K_per_kappa1']@
        (component['source_inclusion']@actions['local_Riesz_current_coordinates']))
    same=actions['real_frame_from_frozen_coordinates'].conj().T@old_coordinates
    residual=float(np.linalg.norm(local-same))
    # Floating consistency tolerance is propagated from the measured change-
    # of-frame residual, not advertised as a certified native error bound.
    allowance=float(checks['same_frozen_span_residual']*
        np.linalg.norm(component['K_per_kappa1']@(component['source_inclusion']@actions['local_Riesz_current_coordinates'])))
    np.savez_compressed(output/'owned_local_angular_operand.npz',
        angular_Maxwell_curvature_per_kappa1=local,same_operand_in_frozen_coordinates=old_coordinates)
    checks.update(local_subtraction_same_frame_residual=residual,
                  propagated_change_of_frame_allowance=allowance)
    control=execute_control();save(output/'arithmetic_control.json',control)
    length=dict(rule='F=I-C=0, E=I(tau_star), ell=1/E, c=ell^2',
        scope='conditional simple persistent first-future/support crossing; no new surface chosen',
        tau_v='-F_v/F_tau',tau_J='-F_J/F_tau',
        tau_vJ='-(F_vJ+F_tau_v*tau_J+F_tau_J*tau_v+F_tau_tau*tau_v*tau_J)/F_tau',
        E_v='I_v+I_tau*tau_v',E_J='I_J+I_tau*tau_J',
        E_vJ='I_vJ+I_tau_v*tau_J+I_tau_J*tau_v+I_tau_tau*tau_v*tau_J+I_tau*tau_vJ',
        ell_v='-E_v/E^2',ell_J='-E_J/E^2',ell_vJ='2E_vE_J/E^3-E_vJ/E^2',
        c_v='-2E_v/E^3',c_J='-2E_J/E^3',c_vJ='6E_vE_J/E^4-2E_vJ/E^3',
        jets=dict(ell='UNEVALUATED',ell_v='UNEVALUATED',ell_J='UNEVALUATED',ell_vJ='UNEVALUATED'),
        zero_jet_theorem=False,absolute_physical_length_selected=False,
        lower_limit_mixed='-c_v STr(e^-cP P_J)/2-c_J STr(e^-cP P_v)/2+T(c)c_vJ/(2c)-(STr(P e^-cP)/c+T(c)/c^2)c_v c_J/2',
        no_source_independence_inferred_from_fixed_geometry=True)
    save(output/'length_jets.json',length)
    completion=dict(status='UNEVALUATED',owner='same AE4 relative-zeta/logarithmic plus eta/phase completion',
        exact_recovered_historical_identity='logdet_zeta(P/mu^2)=-zeta_P_prime(0)-2 log(mu) zeta_P(0)',
        scope='historical supplied-operator identity, not an extra determinant added to finite E1',
        current_relative_reference_subtraction_phase_source_actions_supplied=False,
        no_relative_boundary_diamond_substitute=True,numerical_contribution=None)
    save(output/'relative_completion.json',completion)
    ledger={name:dict(status='UNEVALUATED',value=None) for name in
        ('primitive_Maxwell','common_A_background','Higgs_gauge_local_mixed','gauge_fixing_ghost',
         'induced_heat','relative_zeta_eta','domain_interface','completion')}
    ledger['primitive_Maxwell'].update(evaluated_operand='owned_local_angular_operand.npz; angular Maxwell and background curvature contact per inherited kappa1 only',
        ownership='OWNED_LOCAL; subtraction from the full Gamma Hessian remains UNEVALUATED',
        full_primitive_diagnostic_subtracted=False)
    ledger['common_A_background']['shared_with']='primitive angular curvature subterm; not another addend'
    domain={name:dict(first_jet='UNEVALUATED',mixed_jet='UNEVALUATED') for name in
            ('reset','material_interface','canonical_stop','BRST_quotient','global_source_pullback')}
    domain['compact_fixed_test_pairing']=dict(first_jet='EXACT_ZERO',mixed_jet='EXACT_ZERO',
        proof='fixed unreduced fields/metric/frame at cut; geometric volume/Cauchy weights contain no b')
    domain['local_affine_D_vJ']=dict(mixed_jet='EXACT_ZERO',proof='local connection insertion linear in fixed-frame b; no source-dependent carrier U')
    save(output/'contribution_ownership.json',ledger);save(output/'domain_pairing_jets.json',domain)
    missing=impl.first_length_response();save(output/'one_explicit_unprovided_operand.json',missing)
    result=dict(classification='EVALUATED_LOCAL_SOURCE_CONTACT_AND_COMPACT_WEAK_JETS__NOT_NATIVE_HEAT',
        target='same-owner R_ind(v,J)',target_evaluated=False,
        new_objects=['local affine mixed contact in real32 test frame,8 saved b directions and full64 carrier',
                     'factorized complex-bilinear extension to all224 reached current labels',
                     'unreduced compact K_v/K_J amplitude and BOTH time-jet weak cross rows',
                     'same-frame already-owned angular subtraction operand',
                     'implicit crossing/lower-limit length jets; energy response not supplied'],
        checks=checks,arithmetic_control=control,
        P0_identity='D_strat_dagger D_strat on the inherited zero-mode/BRST quotient',
        local_K_v='D_v_dagger D0+D0_dagger D_v evaluated on compact parent p_A,phi tests',
        local_K_vJ='D_v_dagger D_J+D_J_dagger D_v; local affine D_vJ=0 only',
        local_contact_pairing='unit normalized Haar; full64 spin/carrier, Euclidean fibre adjoint appropriate to supplied Ddagger D form; no physical graded trace',
        native_P_v=None,native_P_J=None,native_P_vJ=None,
        source=dict(coordinate='b; beta=T_b b; A_Q=sqrt2 beta',Dirac_vertex_action_index=False,
            current_direction='S solve(Sdagger S,current_covector)/M_geom at the cut, not raw covector',
            all_current_labels=224,all_test_directions=32,old_response_space_enriched=False),
        pairing=dict(local_unreduced_M_v='EXACT_ZERO',local_unreduced_M_J='EXACT_ZERO',local_unreduced_M_vJ='EXACT_ZERO',
            reduced_moving_Gram_jets='UNEVALUATED',moving_mass_control_terms_both_retained=True),
        length=length,relative_completion=completion,ownership=ledger,domain=domain,
        bulk_heat=dict(contact=None,paired=None,full=None,physical_default_length_used=False,
            primitive_Lorentz_inserted_as_native=False,finite_source_harmonics_do_not_imply_finite_rank=True,
            native_complement_bound=None),
        error_scope=dict(new_source_and_weak_jets='binary64 consistency only; inherited frozen right-cell/Gauss parent-component model',
            time_history_integral_evaluated=False,new_native_numerical_bound=None,
            control_Arb_intervals='exact supplied three-dimensional arithmetic-control matrices only',
            old_consumed_certificate='frozen unchanged; not reused as a bound for new source/heat actions',
            H_rate='corrected cached source time jet consumed; inherited rate and body/interpolation errors remain distinct'),
        downstream=dict(completed_photon_response=None,family_mixed_native_heat=None),
        one_explicit_unprovided_operand=missing,frozen_local=json.loads(paths['frozen'].read_text()),
        physical_a_mu=None,physical_g_mu=None,physical_transfer_directions=0,
        execution=dict(previous_production_replays=0,previous_shifted_solves=0,
            new_native_heat_applications=0,new_physical_operator_spectra=0,
            arithmetic_control_dimension=3,elapsed_seconds=time.perf_counter()-start))
    save(output/'result.json',result)
    save(output/'checkpoint.json',dict(id='BHSM_MUON_UNREDUCED_SOURCE_CONTACT_LENGTH_JETS_20261006',
        stage='new local actions evaluated; full native heat remains unevaluated',
        result='result.json',next_explicit_operand=missing['operand'],physical_a_mu=None))
    save(output/'output_hashes.json',{p.name:sha(p) for p in sorted(output.iterdir()) if p.is_file()})
    print(json.dumps(dict(output=str(output),checks=checks,control_max_difference=control['max_fixed_method_difference'],
        target_evaluated=False,seconds=result['execution']['elapsed_seconds'])))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
