"""Verify additive coupled native current applications and publication bytes."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from importlib.metadata import version
from hashlib import sha256
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import verify_muon_primal_native_action_applications as pub
import verify_muon_same_background_quantum_applications as retained

BASELINE='1aa59cbd9c3299ebca1526af188dcd44a0e3e480'
FOLDER=ROOT/'artifacts/muon_coupled_native_current_applications_20261011'
COMPONENTS=(
 'artifacts/muon_area_endpoint_response_20261011/publication_manifest.json',
 'artifacts/muon_inherited_finite_normal_phase_20261011/publication_manifest.json',
 'artifacts/muon_inherited_finite_normal_phase_20261011/intrinsic_jet_test_verification.json',
 'artifacts/muon_finite_normal_boundary_action_20261011/publication_manifest.json',
 'artifacts/muon_parent_positive_brst_ghost_20261011/publication_manifest.json',
 'artifacts/muon_parent_positive_gauge_form_20261011/manifest.json',
 'artifacts/muon_parent_positive_open_current_20261011/manifest.json',
 'artifacts/muon_parent_positive_coupled_field_20261011/publication_manifest.json',
 'artifacts/muon_intrinsic_scalar_regulator_correction_20261011/publication_manifest.json',
 'artifacts/muon_intrinsic_scalar_temporal_image_20261011/publication_manifest.json',
 'artifacts/muon_intrinsic_open_current_schur_20261011/publication_manifest.json',
 'artifacts/muon_inherited_lepton_time_action_20261011/publication_manifest.json',
 'artifacts/muon_magnetic_full_cutoff_contact_20261011/verification.json',
 'artifacts/muon_profile_preserving_phase_sample_20261011/publication_manifest.json',
 'artifacts/muon_profile_preserving_temporal_weak_action_20261011/publication_manifest.json',
 'artifacts/muon_area_coupled_endpoint_20261011/publication_manifest.json',
 'artifacts/muon_finite_normal_worldvolume_jacobi_20261011/publication_manifest.json',
 'artifacts/muon_parent_positive_coupled_temporal_20261011/publication_manifest.json',
 'artifacts/muon_corrected_profile_magnetic_response_20261011/publication_manifest.json',
 'artifacts/muon_intrinsic_covariant_open_current_jet_20261011/publication_manifest.json',
 'artifacts/muon_common_normal_boundary_form_20261011/publication_manifest.json',
 'artifacts/muon_intrinsic_soft_current_columns_20261011/publication_manifest.json',
 'artifacts/muon_changing_coupled_open_current_20261011/publication_manifest.json',
 'artifacts/muon_same_cell_coefficient_germs_20261011/publication_manifest.json',
 'artifacts/muon_source_directed_temporal_green_20261011/publication_manifest.json',
 'artifacts/muon_even_coupled_temporal_field_20261011/publication_manifest.json',
 'artifacts/muon_even_source_temporal_fermion_20261011/publication_manifest.json',
 'artifacts/muon_coupled_higgs_magnetic_source_20261011/publication_manifest.json',
 'artifacts/muon_intrinsic_normal_coordinate_readout_20261011/publication_manifest.json',
 'artifacts/muon_canonical_retarded_energy_response_20261011/publication_manifest.json',
 'artifacts/muon_paired_local_normal_action_symbol_20261011/publication_manifest.json',
 'artifacts/muon_area_coupled_endpoint_20261011/gamma_0p11_publication_manifest.json',
 'artifacts/muon_magnetic_n5_return_fermion_20261011/publication_manifest.json',
 'artifacts/muon_dirichlet_source_green_collocation_20261011/publication_manifest.json',
 'artifacts/muon_local_charge_matching_response_20261011/publication_manifest.json',
 'artifacts/muon_local_wick_action_20261011/publication_manifest.json',
 'artifacts/muon_coupled_magnetic_field_variation_20261011/publication_manifest.json',
 'artifacts/muon_intrinsic_fermion_wick_application_20261011/publication_manifest.json',
 'artifacts/muon_corrected_chronological_mean_20261011/publication_manifest.json',
 'artifacts/muon_magnetic_n6_return_fermion_20261011/publication_manifest.json',
 'artifacts/muon_changing_closed_fermion_tail_20261011/publication_manifest.json',
 'artifacts/muon_corrected_birth_mean_20261011/publication_manifest.json',
 'artifacts/muon_corrected_birth_canonical_mean_20261011/publication_manifest.json',
 'artifacts/muon_wick_temporal_action_20261011/publication_manifest.json',
 'artifacts/muon_wick_canonical_inverse_20261011/publication_manifest.json',
 'artifacts/muon_joined_chronological_heat_mean_20261011/publication_manifest.json',
 'artifacts/muon_changing_current_energy_moments_20261011/publication_manifest.json',
 'artifacts/muon_changing_zero_energy_moments_20261011/publication_manifest.json',
 'artifacts/muon_continued_current_factor_20261011/publication_manifest.json',
 'artifacts/muon_joined_continued_current_20261011/publication_manifest.json',
 'artifacts/muon_continued_current_boundary_heat_20261011/publication_manifest.json',
 'artifacts/muon_common_y_current_response_20261011/publication_manifest.json',
 'artifacts/muon_joined_common_y_current_20261011/publication_manifest.json',
 'artifacts/muon_corrected_charged_current_cell_20261011/publication_manifest.json',
 'artifacts/muon_joined_normal_current_covector_20261011/publication_manifest.json',
 'artifacts/muon_changing_closed_source_heat_20261011/publication_manifest.json',
 'artifacts/muon_transported_longitudinal_ward_20261011/publication_manifest.json',
 'artifacts/muon_longitudinal_current_tail_diagnostic_20261011/publication_manifest.json',
 'artifacts/muon_normal_current_contraction_maps_20261011/publication_manifest.json',
 'artifacts/muon_continued_action_dual_20261011/publication_manifest.json',
)
PAIRS=(
 ('muon_magnetic_full_cutoff_contact_20261011','run_1','run_2'),
 ('muon_inherited_lepton_time_contact_20261011','run_1','run_2'),
 ('muon_inherited_lepton_temporal_weak_action_20261011','run_1','run_2'),
 ('muon_intrinsic_scalar_regulator_correction_20261011','run_3','run_4'),
 ('muon_intrinsic_scalar_temporal_image_20261011','run_1','run_2'),
 ('muon_intrinsic_open_current_schur_20261011','run_1','run_2'),
 ('muon_parent_positive_brst_ghost_20261011','run_1','run_2'),
 ('muon_parent_positive_gauge_form_20261011','run_1','run_2'),
 ('muon_parent_positive_open_current_20261011','run_3','run_4'),
 ('muon_parent_positive_coupled_field_20261011','run_1','run_2'),
 ('muon_inherited_finite_normal_phase_20261011','run_1','run_2'),
 ('muon_area_endpoint_response_20261011','run_1','run_2'),
 ('muon_profile_preserving_temporal_weak_action_20261011','run_1','run_2'),
 ('muon_area_coupled_endpoint_20261011','run_1','run_2'),
 ('muon_finite_normal_worldvolume_jacobi_20261011','base_run_3','base_run_4'),
 ('muon_finite_normal_worldvolume_jacobi_20261011','area_run_3','area_run_4'),
 ('muon_parent_positive_coupled_temporal_20261011','run_1','run_2'),
 ('muon_corrected_profile_magnetic_response_20261011','run_1','run_2'),
 ('muon_intrinsic_covariant_open_current_jet_20261011','run_1','run_2'),
 ('muon_intrinsic_soft_current_columns_20261011','run_3','run_4'),
 ('muon_intrinsic_soft_constant_columns_20261011','run_2','run_3'),
 ('muon_changing_coupled_open_current_20261011','run_1','run_2'),
 ('muon_same_cell_coefficient_germs_20261011','run_1','run_2'),
 ('muon_source_directed_temporal_green_20261011','run_1','run_2'),
 ('muon_even_coupled_temporal_field_20261011','run_3','run_4'),
 ('muon_even_source_temporal_fermion_20261011','run_1','run_2'),
 ('muon_coupled_higgs_magnetic_source_20261011','run_1','run_2'),
 ('muon_intrinsic_normal_coordinate_readout_20261011','run_1','run_2'),
 ('muon_canonical_retarded_energy_response_20261011','run_1','run_2'),
 ('muon_paired_local_normal_action_symbol_20261011','run_1','run_2'),
 ('muon_magnetic_n5_return_fermion_20261011','run_1','run_2'),
 ('muon_dirichlet_source_green_collocation_20261011','run_2','run_3'),
 ('muon_local_charge_matching_response_20261011','run_1','run_2'),
 ('muon_coupled_magnetic_field_variation_20261011','run_1','run_2'),
 ('muon_intrinsic_fermion_wick_application_20261011','run_1','run_2'),
 ('muon_corrected_profile_mean_load_20261011','run_1','run_2'),
 ('muon_changing_closed_fermion_mean_20261011','run_1','run_2'),
 ('muon_magnetic_n6_return_fermion_20261011','run_1','run_2'),
 ('muon_changing_closed_fermion_tail_20261011','run_1','run_2'),
 ('muon_corrected_birth_mean_20261011','run_1','run_2'),
 ('muon_corrected_birth_canonical_mean_20261011','run_2','run_3'),
 ('muon_wick_temporal_action_20261011','run_2','run_3'),
 ('muon_wick_canonical_inverse_20261011','run_1','run_2'),
 ('muon_joined_chronological_heat_mean_20261011','run_1','run_2'),
 ('muon_changing_current_energy_moments_20261011','run_1','run_2'),
 ('muon_changing_zero_energy_moments_20261011','run_1','run_2'),
 ('muon_continued_current_factor_20261011','run_1','run_2'),
 ('muon_joined_continued_current_20261011','run_1','run_2'),
 ('muon_continued_current_boundary_heat_20261011','run_1','run_2'),
 ('muon_common_y_current_response_20261011','run_2','run_3'),
 ('muon_joined_common_y_current_20261011','run_1','run_2'),
 ('muon_corrected_charged_current_cell_20261011','run_2','run_3'),
 ('muon_joined_normal_current_covector_20261011','run_1','run_2'),
 ('muon_changing_closed_source_heat_20261011','run_1','run_2'),
 ('muon_transported_longitudinal_ward_20261011','run_4','run_5'),
 ('muon_longitudinal_current_tail_diagnostic_20261011','run_3','run_4'),
 ('muon_normal_current_contraction_maps_20261011','run_1','run_2'),
 ('muon_continued_action_dual_20261011','run_1','run_2'),
)
EXTRA=(
 'src/bhsm/interface/muon_magnetic_full_cutoff_contact.py',
 'tests/test_muon_magnetic_full_cutoff_contact.py',
 'scripts/evaluate_muon_magnetic_full_cutoff_contact.py',
 'src/bhsm/interface/muon_inherited_intrinsic_lepton_operator.py',
 'tests/test_muon_inherited_intrinsic_lepton_operator.py',
 'theory/muon_coupled_native_current_applications_20261011.md',
)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--component',action='append',default=[])
    p.add_argument('--stage',action='store_true');p.add_argument('--audits',action='store_true');args=p.parse_args()
    components=COMPONENTS+tuple(args.component);FOLDER.mkdir(exist_ok=True)
    retained.BASELINE=BASELINE;retained.PAIRS=PAIRS;retained.EXTRA=EXTRA+(Path(__file__).relative_to(ROOT).as_posix(),)
    retained.LOG_PREFIXES=('muon_magnetic_full_cutoff_contact_',
        'muon_coupled_native_current_applications_manifest_failed_1.',
        'muon_coupled_native_current_applications_audits_2.')
    reviewed=retained.manifest(components)
    pub.PAIRS=PAIRS;pub.FOLDER=FOLDER;pub.MANIFEST=FOLDER/'publication_manifest.json';pub.VERIFICATION=FOLDER/'verification.json'
    pairs=pub.verify_pairs()
    pub.MANIFEST.write_text(json.dumps(reviewed,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    record=dict(classification='VERIFIED_COUPLED_NATIVE_CURRENT_ACTION_APPLICATIONS',baseline=BASELINE,
        invocation=[sys.executable,*sys.argv],publication_manifest=pub.identity(pub.MANIFEST),
        component_receipts=[pub.identity(ROOT/n)for n in components],independent_byte_replays=pairs,
        runtime=dict(executable=sys.executable,python=sys.version,packages={n:version(n)for n in ('numpy','scipy','pytest','python-flint')}),
        scientific_classification=dict(
            DERIVED='normal material chart and inherited wall/operator jets; proper-clock time contact and weak action; offshell YM/ghost curvature contact; coupled gauge-Higgs and charged-neutral Schur action; finite-c scalar-first correction',
            EVALUATED='complete represented fields/constraints and positive-area response, full18 variable temporal factor, coupled1200 gauge-Higgs field current inverse, exact temporal b² source image, external charged-neutral Green returns and same-background cutoff partial',
            CONTROL_ONLY='explicit finite reference charts, temporal/negative-axis cutoff probes, parameter area family and stored-array inverse arithmetic; none selects a physical cutoff, quantum exterior or fermion state',
            UNEVALUATED='matched differential native completion and signed soft Pauli contribution with overlap, full external pole normalization and complete observable uncertainty; continued internal action production required',
            OWNER_DEFINITION_GAP='none established'),
        complete_observable=False,action_selected=False,Gate7_closed=False,
        finite_norm_or_residual_used_as_anomaly_enclosure=False,
        frozen_predictions_and_prior_milestones_preserved=True)
    if args.stage:
        original=pub.git
        def bounded_git(*argv):
            if argv[:2]==('add','--'):
                batch=[];size=0
                for name in argv[2:]:
                    if batch and size+len(name)+3>10000:original('add','--',*batch);batch=[];size=0
                    batch.append(name);size+=len(name)+3
                return original('add','--',*batch)if batch else b''
            return original(*argv)
        pub.git=bounded_git;pub.stage(reviewed)
    code=0
    if args.audits:
        commands=dict(status=['tools/audit_bhsm_status.py','--format','json'],claims=['tools/audit_forbidden_claims.py','--format','json'],
            frozen=['tools/audit_frozen_prediction_integrity.py','--format','json'],precision=['tools/verify_precision.py'],public=['tools/audit_public_readiness.py','--format','json'])
        with ThreadPoolExecutor(max_workers=5)as pool:outputs=list(pool.map(pub.execute,([sys.executable]+v for v in commands.values())))
        record['publication_audits']=dict(zip(commands,outputs));code=max(r['exit_code']for r in outputs)
    pub.VERIFICATION.write_text(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    if args.stage:
        pub.git('add','--',pub.VERIFICATION.relative_to(ROOT).as_posix())
        if sha256(pub.git('show',':'+pub.VERIFICATION.relative_to(ROOT).as_posix())).hexdigest()!=pub.identity(pub.VERIFICATION)['sha256']:
            raise ValueError('staged verification bytes changed')
    print(json.dumps(dict(files=len(reviewed['files']),verification=pub.identity(pub.VERIFICATION),
        audit_exit_codes={k:v['exit_code']for k,v in record.get('publication_audits',{}).items()}),sort_keys=True))
    return code

if __name__=='__main__':raise SystemExit(main())
