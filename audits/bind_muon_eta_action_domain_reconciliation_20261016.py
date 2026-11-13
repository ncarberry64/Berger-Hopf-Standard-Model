"""Bind source-level domain reconciliation; no new physical solver run."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import subprocess


def bind(repository, output):
    root, out = Path(repository).resolve(), Path(output).resolve()
    if out.exists():
        raise FileExistsError(out)
    base = root / 'artifacts/muon_eta_action_domain_reconciliation_20261016'
    pins, sources = {}, {}

    def pin(path, expected=None):
        actual = sha256(path.read_bytes()).hexdigest()
        if expected is not None and actual != expected:
            raise ValueError('Published artifact changed: ' + str(path))
        pins[path.relative_to(root).as_posix()] = actual

    proof_pins = {
        'muon_eta_action_domain_reconciliation_20261016.txt': '6e6275a969e59863b3022e1fc9e8104bd39dd5927acd545084b5797b1fb9cec4',
        'muon_h4_output_and_no_doublecount_20261016.txt': '3b2d5ff834a02748158e5657428630aaf7d851e3bef97747c76242e10229bafc',
        'muon_eta_seam_native_square_domain_20261016.txt': '294f6ff89d4d0d762a0841c3b9c233c3fb21eaf51efe42f8977797d3debb6e8a',
        'muon_full_d5_eta_current_pairing_20261016.txt': '1c838014855b6203110c31d701d4eefcbc5833e78839aa33e8da1c38f483d9a5',
    }
    for name, expected in proof_pins.items():
        pin(base / name, expected)
    checks = json.loads((base / 'publication_checks/results.json').read_bytes())
    assert len(checks) == 5 and all(not r['exit_code'] for r in checks.values())
    for name, record in checks.items():
        pin(base / 'publication_checks' / (name + '.log'), record['log_sha256'])
    prior = root / 'artifacts/muon_isotropic_seam_domain_20261016/publication_manifest_run_1.json'
    pin(prior, 'ce9fc2609968d0f108934bdd9e046139bde4f079f7da8571b0f62209d401b2b6')
    old = json.loads(prior.read_bytes())
    assert old['coupled_matching_corrections_applied'] == 0
    assert old['physical_muon_magnetic_moment'] is None
    for name in ('application_run_2', 'application_run_3', 'controls_run_1', 'controls_run_2'):
        path = prior.parent / name / 'result.json'
        pin(path, old['source_and_publication_hashes'][path.relative_to(root).as_posix()])
    for name in (
        'completion/foundational_dirac_spin_glue_v14_45.py',
        'aether_unified_m5_m4_pushforward_v15_69.py',
        'ae4_stratified_dirac_zeta_induced_owner.py',
        'muon_full_d5_localized_lepton_trace.py',
        'muon_holomorphic_d5_trace_action.py',
        'muon_owned_native_product_connection.py',
        'muon_native_dirac_hamiltonian.py',
        'muon_reflected_native_conormal_graph.py',
        'aether_eta_wall_material_response_v15_26.py',
        'aether_hybrid_standard_model_bundle_v15_53.py',
    ):
        rel = 'src/bhsm/interface/' + name
        # These are cited source texts, not numerical inputs newly consumed
        # by a science application. Normalize CRLF only, explicitly, to
        # make their read-only source identities checkout-independent.
        working = (root / rel).read_bytes().replace(b'\r\n', b'\n')
        committed = subprocess.check_output(['git', 'show', 'HEAD:' + rel], cwd=root).replace(b'\r\n', b'\n')
        if working != committed:
            raise ValueError('Cited source has unpublished code changes: ' + rel)
        sources[rel] = sha256(working).hexdigest()
    pin(Path(__file__).resolve())
    for path in sorted(base.rglob('*')):
        if path.is_file() and not path.name.startswith('publication_manifest_run_'):
            pin(path)
    result = dict(
        classification='LITERAL_ETA_ACTION_RECONCILIATION_AND_NATIVE_ADJOINT_SQUARE_DOMAIN',
        actual_eta_action_is_ordered_left_D_right=True,
        broken_piece_symmetrized_factor_two_is_an_active_eta_fork=False,
        local_distributional_jump_fixed_without_new_coupling_or_average=True,
        old_spin_equal_value_statement_scoped_to_geometry_and_free_kinetic=True,
        canonical_maximal_bulk_L2_component_constructed_under_regular_assumptions=True,
        H4_flux_output_constructed_without_second_D4_kinetic=True,
        complete_native_H4_physical_energy_allocation_evaluated=False,
        native_square_conormal_transfer='diag(S,S_inverse_dagger)',
        full_eta_nonHermitian_body_and_metric_adjoint_contacts_preserved=True,
        native_normal_positive_factor_preserves_owned_normalization=True,
        scalar_eta_normal_cancellation_alone_selects_chirality=False,
        actual_SM_chiral_representation_already_owned=True,
        global_extra_particles_or_theory_failure_claimed=False,
        full_common_microscopic_operator_background_and_outgoing_realization=False,
        full_physical_E_B_domain_derivative_at_2e_minus_10_passed=False,
        physical_radial_and_full_angular_numerical_convergence=False,
        coupled_matching_corrections_applied=0,
        original_Maxwell_after_correction=None, original226_after_correction=None,
        retained_before_Maxwell_magnitude=2.4777309846820184,
        retained_before_original226_max=9.602842247524184e-7,
        required_original_physical_tolerance=2e-10,
        physical_two_spin_normalization=None, physical_muon_magnetic_moment=None,
        new_science_applications_or_integrations=0,
        prior_component_tests_passed=8, publication_audits_passed=5,
        current_artifact_byte_hashes=dict(sorted(pins.items())),
        cited_source_LF_hashes=dict(sorted(sources.items())),
        cited_source_hash_rule='CRLF-normalized read-only source text, verified against committed code; not a numerical-input hash rule',
    )
    out.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + '\n', encoding='utf8', newline='\n')
    print(json.dumps(dict(artifact_pins=len(pins), cited_sources=len(sources), sha256=sha256(out.read_bytes()).hexdigest())))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    bind(args.repository, args.output)
