"""Bind the real-route reconciliation and exact normalized seam response."""
from pathlib import Path
from hashlib import sha256
import argparse
import json


def bind(repository, output):
    root, out = Path(repository).resolve(), Path(output).resolve()
    if out.exists():
        raise FileExistsError(out)
    base = root/'artifacts/muon_real_seam_boundary_response_20261015'
    pins, pairs = {}, []

    def pin(path, expected=None):
        value = sha256(path.read_bytes()).hexdigest()
        if expected is not None and value != expected:
            raise ValueError('Consumed science input changed: '+str(path))
        pins[path.relative_to(root).as_posix()] = value
        return value

    for name, hash_key in (('application', 'input_hashes'), ('controls', 'source_sha256')):
        a, b = (base/f'{name}_run_{i}/result.json' for i in (1, 2))
        if a.read_bytes() != b.read_bytes():
            raise ValueError('Nonidentical independent result pair: '+name)
        value = pin(a)
        pin(b)
        result = json.loads(a.read_bytes())
        for rel, expected in result[hash_key].items():
            pin(root/rel, expected)
        if name == 'application':
            assert result['full_point_trace_seam_c45_already_supplied'] is True
            assert result['artificial_complex_corner_match_required_for_physical_prediction'] is False
            assert result['physical_full_outgoing_derivative_at_2e_minus_10_passed'] is False
            assert result['coupled_matching_corrections_applied'] == 0
            assert result['physical_two_spin_normalization'] is None
            assert result['physical_muon_magnetic_moment'] is None
            assert result['new_D5_profile_source_history_integrations'] == 0
            assert len(result['records']) == 2
            for item in result['records']:
                assert item['full_field_count'] == 768
                assert item['normalized_trace_count'] == 18
                assert item['retained_complementary_field_rows'] == 750
                assert item['inverse_partial_EH_norm'] > 0
        else:
            assert result['physical_control_state'] is False
            assert max(result['independent_literal_full_seam_MP64_solution_max_errors'].values()) < 1e-12
        pairs.append(dict(kind=name, result_sha256=value, physical_derivative_gate=False))
    checks = json.loads((base/'publication_checks/results.json').read_bytes())
    if len(checks) != 5 or any(item['exit_code'] for item in checks.values()):
        raise ValueError('Five successful publication audits required')
    for name, item in checks.items():
        pin(base/'publication_checks'/(name+'.log'), item['log_sha256'])
    pin(Path(__file__).resolve())
    for name in ('muon_owned_native_product_connection', 'muon_transported_native_pairing',
                 'muon_native_dual_density_graph', 'muon_joint_variational_attachment',
                 'ae4_stratified_dirac_zeta_induced_owner', 'aether_quantum_functional_accounting_v16_00'):
        pin(root/'src/bhsm/interface'/(name+'.py'))
    cut = root/('artifacts/muon_baton_zoo_maximal_current_realization_20261013/'
                'actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/'
                'actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz')
    pin(cut, 'ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b')
    for path in sorted(base.rglob('*')):
        if path.is_file() and not path.name.startswith('publication_manifest_run_'):
            pin(path)
    result = dict(
        classification='REAL_DOMAIN_ROUTE_AND_EXACT_EXISTING_NORMALIZED_HIGGS_SEAM_RESPONSE',
        independent_result_pairs=pairs,
        binder_repetition_is_physical_solve=False,
        older_c45_absence_contract_superseded_on_owned_point_trace_sector=True,
        artificial_complex_corner_Hilbert_match_is_universal_physical_gate=False,
        physical_closed_common_operator_and_exterior_realized=False,
        physical_full_derivative_at_2e_minus_10_passed=False,
        physical_radial_and_full_angular_convergence_established=False,
        coupled_matching_corrections_applied=0,
        physical_two_spin_normalization=None, physical_muon_magnetic_moment=None,
        original_Maxwell_after_correction=None, original226_after_correction=None,
        retained_before_Maxwell_magnitude=2.4777309846820184,
        retained_before_original226_max=9.602842247524184e-7,
        required_original_residual_tolerance=2e-10,
        new_source_D5_profile_or_history_integrations=0,
        full_native_E1_determined_from_one_point_logdet=False,
        component_tests_passed=4, publication_audits_passed=5,
        source_and_publication_hashes=dict(sorted(pins.items())),
    )
    out.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False)+'\n',
                   encoding='utf8', newline='\n')
    print(json.dumps(dict(pins=len(pins), sha256=sha256(out.read_bytes()).hexdigest())))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    bind(args.repository, args.output)
