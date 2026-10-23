"""Bind the exact native conormal construction without admitting a prediction."""
from hashlib import sha256
from pathlib import Path
import argparse
import json


def bind(repository, output):
    root, out = Path(repository).resolve(), Path(output).resolve()
    if out.exists():
        raise FileExistsError(out)
    base = root/'artifacts/muon_native_conormal_operator_20261015'
    pins = {}

    def pin(path, expected=None):
        value = sha256(path.read_bytes()).hexdigest()
        if expected is not None and value != expected:
            raise ValueError(f'Consumed input changed: {path}')
        pins[path.relative_to(root).as_posix()] = value
        return value

    first, second = (base/f'application_run_{i}/result.json' for i in (1, 2))
    if first.read_bytes() != second.read_bytes():
        raise ValueError('Independent actual coefficient applications differ')
    value = pin(first)
    pin(second)
    application = json.loads(first.read_bytes())
    for rel, expected in application['input_hashes'].items():
        pin(root/rel, expected)
    assert application['coefficient_nodes'] == 3832
    assert application['point_fiber_components'] == 18
    assert application['derived_real_common_A_native_temporal_binding_already_available'] is True
    assert application['full_physical_outgoing_derivative_at_2e_minus_10_passed'] is False
    assert application['coupled_matching_corrections_applied'] == 0
    assert application['physical_two_spin_normalization'] is None
    assert application['physical_muon_magnetic_moment'] is None
    assert application['new_field_or_history_integrations'] == 0
    assert application['old_campaign_replays'] == 0
    assert application['maxima']['literal_generator_relative'] < 1e-12
    assert application['maxima']['real_axis_Green_identity_relative'] < 1e-12
    checks = json.loads((base/'publication_checks/results.json').read_bytes())
    if len(checks) != 5 or any(item['exit_code'] for item in checks.values()):
        raise ValueError('All five publication audits must pass')
    for name, item in checks.items():
        pin(base/'publication_checks'/(name+'.log'), item['log_sha256'])
    pin(root/'src/bhsm/interface/muon_reflected_native_conormal_graph.py')
    pin(root/'tests/test_muon_reflected_native_conormal_graph.py')
    pin(Path(__file__).resolve())
    for path in sorted(base.rglob('*')):
        if path.is_file() and not path.name.startswith('publication_manifest_run_'):
            pin(path)
    result = dict(
        classification='EXACT_EXISTING_NATIVE_FORM_CONORMAL_REALIZATION_AND_COMMON_DOMAIN_CONSTRUCTION',
        independent_actual_application_pair_sha256=value,
        actual_frozen_coefficient_nodes=3832,
        full_point_fiber_components=18,
        retained_derived_temporal_connection_available=True,
        component_jet_tests_passed=5, publication_audits_passed=5,
        binder_repeat_is_new_physical_calculation=False,
        physical_common_P_strat_and_domain_realized=False,
        physical_outgoing_energy_and_field_derivative_passed_at_2e_minus_10=False,
        physical_full_angular_and_radial_convergence_established=False,
        coupled_matching_corrections_applied=0,
        physical_two_spin_normalization=None, physical_muon_magnetic_moment=None,
        original_Maxwell_after_correction=None, original226_after_correction=None,
        retained_before_Maxwell_magnitude=2.4777309846820184,
        retained_before_original226_max=9.602842247524184e-7,
        required_original_residual_tolerance=2e-10,
        original_analytic_corner_pairing_declared_physically_failed=False,
        new_field_or_history_integrations=0, completed_campaign_replays=0,
        source_and_publication_hashes=dict(sorted(pins.items())),
    )
    out.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False)+'\n',
                   encoding='utf8', newline='\n')
    print(json.dumps(dict(file=out.name, pins=len(pins),
                         sha256=sha256(out.read_bytes()).hexdigest())))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    bind(args.repository, args.output)
