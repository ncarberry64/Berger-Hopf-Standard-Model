"""Bind the conditional seam graph, corrected germs and preserved failure."""
from pathlib import Path
from hashlib import sha256
import argparse
import json


def bind(repository, output):
    root, dest = Path(repository).resolve(), Path(output).resolve()
    if dest.exists():
        raise FileExistsError(dest)
    base = root / 'artifacts/muon_isotropic_seam_domain_20261016'
    pins, pairs = {}, []

    def pin(path, expected=None):
        actual = sha256(path.read_bytes()).hexdigest()
        if expected is not None and actual != expected:
            raise ValueError('Consumed source/input changed: ' + str(path))
        pins[path.relative_to(root).as_posix()] = actual
        return actual

    for name, runs, key in (('application', (2, 3), 'input_hashes'),
                            ('controls', (1, 2), 'source_sha256')):
        paths = [base / f'{name}_run_{n}/result.json' for n in runs]
        if paths[0].read_bytes() != paths[1].read_bytes():
            raise ValueError('Independent result pair differs: ' + name)
        report = json.loads(paths[0].read_bytes())
        digest = pin(paths[0])
        pin(paths[1])
        for rel, expected in report[key].items():
            pin(root / rel, expected)
        if name == 'application':
            assert report['adopted_full_physical_domain'] is False
            assert report['full_physical_derivative_at_2e_minus_10_passed'] is False
            assert report['physical_energy_or_field_derivatives_evaluated'] is False
            assert report['coupled_matching_corrections_applied'] == 0
            assert report['normalized_physical_spin_states'] is None
            assert report['physical_muon_magnetic_moment'] is None
            assert report['new_profile_D5_source_or_history_integrations'] == 0
            for row in report['records']:
                assert (row['common_full_field_count'], row['selected_trace_count'],
                        row['complementary_common_trace_count']) == (384, 18, 348)
                assert row['actual_wall_radius_jet_rebuilt_from_original_stage_raw'] is True
                assert row['interior_quadrature_endpoint_substituted_for_wall'] is False
                assert row['surface_density_source_match_abs'] == 0
                assert row['original_particle_Green_first_match_max'] < 2e-10
                assert max(row['literal_Cayley_comparison_max'].values()) < 2e-10
                assert row['transfer_mixed_time_H_norm'] > 0
        else:
            assert report['physical_control_state'] is False
            assert report['physical_domain_adoption'] is None
            assert max(report['independent_literal_MP64_Cayley_errors'].values()) < 1e-13
        pairs.append(dict(kind=name, runs=list(runs), result_sha256=digest,
                          physical_derivative_gate=False))

    failed = base / 'application_run_1'
    failure = json.loads((failed / 'result.json').read_bytes())
    assert max(r['surface_density_source_match_abs'] for r in failure['records']) > 8e-7
    assert max(r['original_particle_Green_first_match_max'] for r in failure['records']) > .001
    aliases = {
        'audits/bhsm_isotropic_seam_saved_germs_20261016.py': failed / 'producer_at_failure.py',
        'src/bhsm/interface/muon_isotropic_seam_transfer.py': failed / 'seam_helper_at_failure.py',
    }
    for rel, expected in failure['input_hashes'].items():
        pin(aliases.get(rel, root / rel), expected)
    pin(failed / 'result.json')
    checks = json.loads((base / 'publication_checks/results.json').read_bytes())
    assert len(checks) == 5 and all(not v['exit_code'] for v in checks.values())
    for name, record in checks.items():
        pin(base / 'publication_checks' / (name + '.log'), record['log_sha256'])
    pin(base / 'muon_eta_seam_all_angular_transversality_20261016.txt',
        '98e25bfa7e6cc8a1ea4a85690f95b0635e548785d35cb9edd04477a1e1383b9a')
    pin(Path(__file__).resolve())
    pin(root / ('artifacts/muon_baton_zoo_maximal_current_realization_20261013/'
                'actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/'
                'actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz'),
        'ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b')
    for path in sorted(base.rglob('*')):
        if path.is_file() and not path.name.startswith('publication_manifest_run_'):
            pin(path)
    payload = dict(
        classification='CONDITIONAL_NILPOTENT_ETA_SEAM_AND_ALL_ANGULAR_PRINCIPAL_THEOREM',
        independent_result_pairs=pairs,
        preserved_failed_input_location_application=True,
        failure_source_relocation={rel: path.relative_to(root).as_posix() for rel, path in aliases.items()},
        full_distributional_extension_not_broken_piece_symmetrization=True,
        literal_older_full_value_glue_reconciled_with_interacting_domain=False,
        new_free_seam_parameter_or_average_required=False,
        real_scalar_Higgs_all_angular_principal_transversality_derived=True,
        uniform_continuum_smoothing_or_retarded_exterior_convergence_proved=False,
        adopted_full_physical_operator_domain=False,
        physical_energy_field_outgoing_derivative_at_2e_minus_10_passed=False,
        physical_radial_and_full_angular_numerical_convergence=False,
        coupled_matching_corrections_applied=0,
        physical_spin_normalization=None, physical_muon_magnetic_moment=None,
        Maxwell_after_correction=None, all226_after_correction=None,
        retained_before_Maxwell_magnitude=2.4777309846820184,
        retained_before_original226_max=9.602842247524184e-7,
        required_original_physical_tolerance=2e-10,
        component_tests_passed=4, publication_audits_passed=5,
        new_D5_profile_source_or_history_integrations=0,
        binder_serialization_is_physical_solve=False,
        source_and_publication_hashes=dict(sorted(pins.items())),
    )
    dest.write_text(json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + '\n',
                    encoding='utf8', newline='\n')
    print(json.dumps(dict(pins=len(pins), sha256=sha256(dest.read_bytes()).hexdigest())))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    bind(args.repository, args.output)
