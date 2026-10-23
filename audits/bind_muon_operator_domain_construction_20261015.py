"""Bind constructed interface components without admitting a physical solve."""
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys


def bind(repository, output):
    root, out = Path(repository).resolve(), Path(output).resolve()
    if out.exists():
        raise FileExistsError(out)
    base = root/'artifacts/muon_operator_domain_construction_20261015'
    pins, pairs, results = {}, [], {}

    def pin(path):
        digest = sha256(path.read_bytes()).hexdigest()
        pins[path.relative_to(root).as_posix()] = digest
        return digest

    for name, producer, module in (
        ('regular_brst', 'bhsm_regular_reset_brst_domain_20261015.py', 'muon_regular_reset_brst_domain.py'),
        ('surface_incidence', 'bhsm_surface_incidence_second_jet_20261015.py', 'muon_surface_incidence_second_jet.py'),
    ):
        a, b = (base/f'{name}_run_{index}/result.json' for index in (1, 2))
        if a.read_bytes() != b.read_bytes():
            raise ValueError(f'Independent component controls differ: {name}')
        digest = pin(a)
        pin(b)
        result = json.loads(a.read_bytes())
        if result['producer_sha256'] != pin(root/'audits'/producer):
            raise ValueError(f'Published component producer differs: {producer}')
        if result['module_sha256'] != pin(root/'src/bhsm/interface'/module):
            raise ValueError(f'Published component source differs: {module}')
        if name == 'regular_brst':
            owner = root/'src/bhsm/interface/gauge_connection_reset_bundle_lift_adjudication.py'
            assert pin(owner) == result['affine_owner_sha256']
            assert result['physical_incidence_packet_consumed'] is False
            assert result['full_derivative_at_2e_minus_10_passed'] is False
            assert result['coupled_corrections'] == 0
            assert result['spin_normalization_evaluated'] is False
            assert result['muon_magnetic_moment'] is None
        else:
            for rel, expected in result['owner_source_hashes'].items():
                assert pin(root/rel) == expected, rel
            assert result['physical_carrier_or_gamma_selected'] is False
            assert result['physical_microscopic_operator_selected'] is False
            assert result['full_derivative_2e_minus_10_passed'] is False
            assert result['coupled_matching_corrections'] == 0
            assert result['physical_spin_normalization'] is None
            assert result['physical_muon_magnetic_moment'] is None
        assert result['physical_outgoing_domain_evaluated'] is False
        results[name] = result
        pairs.append(dict(component=name, result_sha256=digest,
                          physical_field_or_history_solve=False))
    sys.path.insert(0, str(root/'src'))
    from bhsm.interface.muon_native_dirac_hamiltonian import canonical_product_factor_contract
    native = canonical_product_factor_contract()
    assert native['factor_temporal_native_binding'] is None
    assert native['Lorentz_to_native_analytic_continuation_automatically_asserted'] is False
    assert native['heat_invocation_permitted'] is False
    for name in (
        'ae4_stratified_dirac_zeta_induced_owner', 'ae4_branch_relative_support_transition',
        'ae31_c2_intrinsic_m4_lepton_action', 'ae31_c2_lepton_composite_mixing_structure',
        'ae31_c2_chiral_green_domain', 'aether_quantum_functional_accounting_v16_00',
        'covariant_bubble_interface_mechanics', 'muon_native_dirac_hamiltonian',
        'muon_intrinsic_fermion_wick_application', 'muon_local_wick_action',
        'muon_native_product_factor_graph', 'muon_magnetic_mixed_green',
        'muon_unsquared_physical_boundary_pole',
    ):
        pin(root/'src/bhsm/interface'/(name+'.py'))
    checks = json.loads((base/'publication_checks/results.json').read_bytes())
    if len(checks) != 5 or any(check['exit_code'] != 0 for check in checks.values()):
        raise ValueError('Five successful publication audit commands required')
    for name, check in checks.items():
        assert pin(base/'publication_checks'/(name+'.log')) == check['log_sha256']
    cut = root/('artifacts/muon_baton_zoo_maximal_current_realization_20261013/'
                'actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/'
                'actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz')
    assert pin(cut) == 'ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b'
    pin(Path(__file__).resolve())
    pin(root/'tests/test_muon_operator_domain_construction.py')
    for path in sorted(base.rglob('*')):
        if path.is_file() and not path.name.startswith('publication_manifest_run_'):
            pin(path)
    result = dict(
        classification='CONSTRUCTED_REGULAR_FP_DOMAIN_AND_GEOMETRIC_SECOND_INCIDENCE_COMPONENTS_WITH_EXACT_MATCHING_MAPS',
        independent_component_control_pairs=pairs,
        controls_are_physical_background_or_domain_inputs=False,
        binder_repeat_is_new_physical_or_component_control_solve=False,
        full_nonlinear_or_diffeomorphism_BRST_complex_constructed=False,
        native_factor_temporal_binding_evaluated=False,
        actual_physical_positive_stratified_operator_realized=False,
        actual_full_outgoing_domain_realized=False,
        physical_Higgs_and_surface_coefficients=None,
        full_physical_derivative_passed_at_2e_minus_10=False,
        coupled_matching_corrections_applied=0,
        physical_two_spin_normalization=None, physical_muon_magnetic_moment=None,
        new_physical_field_integrations=0, completed_campaign_replays=0,
        original_Maxwell_after_correction=None, original226_after_correction=None,
        retained_before_Maxwell_magnitude=2.4777309846820184,
        retained_before_original226_max=9.602842247524184e-7,
        required_original_residual_tolerance=2e-10,
        publication_process_audits_passed=5,
        source_and_publication_hashes=dict(sorted(pins.items())),
    )
    out.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n',
                   encoding='utf8', newline='\n')
    print(json.dumps(dict(file=out.name, sha256=sha256(out.read_bytes()).hexdigest(),
                          component_pairs=2, physical_operator_realized=False)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    bind(args.repository, args.output)
