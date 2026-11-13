"""Bind new coefficient components without promoting a physical prediction."""
from hashlib import sha256
from pathlib import Path
import argparse
import json


def bind(repository, output):
    root, out = Path(repository).resolve(), Path(output).resolve()
    if out.exists():
        raise FileExistsError(out)
    base = root / 'artifacts/muon_scalar_surface_derivation_20261015'
    pins, pairs, results = {}, [], {}

    def pin(path):
        digest = sha256(path.read_bytes()).hexdigest()
        pins[path.relative_to(root).as_posix()] = digest
        return digest

    for name, producer in (
        ('quartic', 'bhsm_current_c2_e1_quartic_20261015.py'),
        ('graded_coarea', 'bhsm_c2_graded_surface_volume_component_20261015.py'),
        ('area_inertia', 'bhsm_original_area_inertia_contact_20261015.py'),
    ):
        left, right = (base / f'{name}_run_{i}' for i in (1, 2))
        names = {p.name for p in left.iterdir() if p.is_file()}
        if names != {p.name for p in right.iterdir() if p.is_file()}:
            raise ValueError(f'Numerical file lists differ: {name}')
        files = {}
        for filename in sorted(names):
            a, b = left / filename, right / filename
            if a.read_bytes() != b.read_bytes():
                raise ValueError(f'Nonidentical independent pair: {name}/{filename}')
            files[filename] = pin(a)
            pin(b)
        result = json.loads((left / 'result.json').read_bytes())
        if result['producer_sha256'] != pin(root / 'audits' / producer):
            raise ValueError(f'Published producer differs: {producer}')
        for rel, expected in result['input_hashes'].items():
            if pin(root / rel) != expected:
                raise ValueError(f'Pinned input changed: {rel}')
        if 'array_archive_sha256' in result:
            archives = [k for k in names if k.endswith('.npz')]
            if len(archives) != 1 or files[archives[0]] != result['array_archive_sha256']:
                raise ValueError(f'Array archive binding differs: {name}')
        results[name] = result
        pairs.append(dict(kind=name, files=files, physical_full_solve=False))

    quartic, coarea, inertia = (results[k] for k in ('quartic', 'graded_coarea', 'area_inertia'))
    assert quartic['physical_lambda_H'] is None
    assert quartic['physical_nu_squared'] is None
    assert quartic['physical_Higgs_Z'] is None
    assert quartic['physical_muon_moment'] is None
    assert quartic['coupled_matching_corrections_applied'] == 0
    assert coarea['physical_surface_gamma_derived'] is False
    assert coarea['physical_outgoing_E_B_derivative_gate_passed'] is False
    assert coarea['numerical_ell_star_or_alpha_FSC_assigned'] is False
    assert coarea['coupled_matching_corrections'] == 0
    assert inertia['physical_real_fields_or_outgoing_solution_constructed'] is False
    assert inertia['physical_full_derivative_passed_2e_minus_10'] is False
    assert inertia['physical_two_spin_normalization'] is None
    assert inertia['physical_muon_magnetic_moment'] is None
    assert inertia['coupled_matching_corrections_applied'] == 0

    checks = json.loads((base / 'publication_checks/results.json').read_bytes())
    if len(checks) != 5 or any(check['exit_code'] != 0 for check in checks.values()):
        raise ValueError('All five publication audit commands must succeed')
    for name, check in checks.items():
        if pin(base / 'publication_checks' / f'{name}.log') != check['log_sha256']:
            raise ValueError(f'Publication log differs: {name}')
    cut = root / ('artifacts/muon_baton_zoo_maximal_current_realization_20261013/'
                  'actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/'
                  'actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz')
    if pin(cut) != 'ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b':
        raise ValueError('Authoritative original matching cut changed')
    pin(Path(__file__).resolve())
    pin(root / 'tests/test_muon_scalar_surface_derivation.py')
    for path in sorted(base.rglob('*')):
        if path.is_file() and not path.name.startswith('publication_manifest_run_'):
            pin(path)
    result = dict(
        classification='EVALUATED_FINITE_SCALAR_AND_LOCAL_SURFACE_COMPONENTS_WITH_PHYSICAL_COMPLETION_OPEN',
        scientific_repeat_pairs=pairs,
        binder_repeat_is_new_independent_scientific_or_physical_solve=False,
        scalar_fourth_variation_per_declared_chirality_and_core_block=True,
        chirality_channels_are_physical_muon_spin_states=False,
        actual_full_Higgs_mass_quartic_and_surface_coefficients_evaluated=False,
        physical_real_coupled_fields_and_outgoing_domain_evaluated=False,
        full_physical_derivative_passed_at_2e_minus_10=False,
        coupled_matching_corrections_applied=0,
        physical_two_spin_normalization=None,
        physical_muon_magnetic_moment=None,
        dimensionless_g_has_no_absolute_energy_unit_gate=True,
        intrinsic_pole_requires_collider_history=False,
        original_Maxwell_after_correction=None,
        original226_after_correction=None,
        retained_before_Maxwell_magnitude=2.4777309846820184,
        retained_before_original226_max=9.602842247524184e-7,
        retained_before_original226_row='226 common_normal_temporal_dual[0]',
        required_original_residual_tolerance=2e-10,
        test_result='3 fresh numerical tests passed; literal E1, coarea jets and MP area derivative',
        publication_process_audits_passed=5,
        input_and_publication_hashes=dict(sorted(pins.items())),
    )
    out.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + '\n',
                   encoding='utf-8', newline='\n')
    print(json.dumps(dict(file=out.name, sha256=sha256(out.read_bytes()).hexdigest(),
                          numerical_pairs=3, physical_full_solve=False)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    bind(args.repository, args.output)
