"""Bind finite intrinsic-potential and stress applications without a pole claim."""
from hashlib import sha256
from pathlib import Path
import argparse
import json


def bind(repository, output):
    root, out = Path(repository).resolve(), Path(output).resolve()
    if out.exists():
        raise FileExistsError(out)
    base = root / 'artifacts/muon_intrinsic_potential_surface_stress_20261015'
    pins, pairs, results = {}, [], {}

    def pin(path):
        digest = sha256(path.read_bytes()).hexdigest()
        pins[path.relative_to(root).as_posix()] = digest
        return digest

    for name, producer in (
        ('scalar_cutoff', 'bhsm_saved_c2_scalar_cutoff_jets_20261015.py'),
        ('vertical_stress', 'bhsm_c2_vertical_stress_contrast_20261015.py'),
        ('outgoing_subspace', 'bhsm_saved_outgoing_boundary_subspace_sensitivity_20261015.py'),
        ('intrinsic_potential', 'bhsm_intrinsic_neutral_background_potential_20261015.py'),
    ):
        left, right = (base / f'{name}_run_{i}' for i in (1, 2))
        names = {path.name for path in left.iterdir() if path.is_file()}
        if names != {path.name for path in right.iterdir() if path.is_file()}:
            raise ValueError(f'Independent numerical file lists differ: {name}')
        files = {}
        for filename in sorted(names):
            a, b = left / filename, right / filename
            if a.read_bytes() != b.read_bytes():
                raise ValueError(f'Independent numerical pair differs: {name}/{filename}')
            files[filename] = pin(a)
            pin(b)
        result = json.loads((left / 'result.json').read_bytes())
        if result['producer_sha256'] != pin(root / 'audits' / producer):
            raise ValueError(f'Published producer differs: {producer}')
        for group in ('input_hashes', 'retained_operator_input_hashes'):
            for rel, expected in result.get(group, {}).items():
                if pin(root / rel) != expected:
                    raise ValueError(f'Pinned input changed: {rel}')
        if 'array_archive_sha256' in result:
            archives = [filename for filename in names if filename.endswith('.npz')]
            if len(archives) != 1 or files[archives[0]] != result['array_archive_sha256']:
                raise ValueError(f'Array binding differs: {name}')
        pairs.append(dict(kind=name, files=files, physical_full_solve=False))
        results[name] = result
    cutoff, stress, tail, potential = (results[name] for name in (
        'scalar_cutoff', 'vertical_stress', 'outgoing_subspace', 'intrinsic_potential'))
    assert cutoff['physical_full_derivative_passed_2e_minus_10'] is False
    assert stress['full_surface_coefficient_determined'] is False
    assert tail['full_physical_outgoing_derivative_passed'] is False
    assert tail['unknown_terminal_row_is_free_physical_parameter'] is False
    assert potential['physical_lambda_H'] is None
    assert potential['physical_nu_squared'] is None
    assert potential['physical_Higgs_kinetic_Z'] is None
    assert potential['physical_two_spin_normalization'] is None
    assert potential['physical_muon_moment'] is None
    assert potential['temporal_connection_not_removed'] is True
    assert potential['degenerate_spin_modes_not_split_or_deleted'] is True
    assert potential['no_extra_spin_family_or_chirality_multiplicity_inserted'] is True
    assert potential['odd_and_even_label_intersection_empty'] is True
    assert potential['coupled_matching_corrections_applied'] == 0
    assert cutoff['coupled_matching_corrections_applied'] == 0
    assert stress['coupled_matching_corrections'] == tail['coupled_matching_corrections'] == 0
    checks = json.loads((base / 'publication_checks/results.json').read_bytes())
    if len(checks) != 5 or any(check['exit_code'] != 0 for check in checks.values()):
        raise ValueError('Five successful publication audit commands are required')
    for name, check in checks.items():
        if pin(base / 'publication_checks' / f'{name}.log') != check['log_sha256']:
            raise ValueError(f'Publication log differs: {name}')
    cut = root / ('artifacts/muon_baton_zoo_maximal_current_realization_20261013/'
                  'actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/'
                  'actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz')
    if pin(cut) != 'ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b':
        raise ValueError('Authoritative matching cut changed')
    pin(Path(__file__).resolve())
    pin(root / 'tests/test_muon_intrinsic_potential_surface_stress.py')
    for path in sorted(base.rglob('*')):
        if path.is_file() and not path.name.startswith('publication_manifest_run_'):
            pin(path)
    result = dict(
        classification='FINITE_INTRINSIC_HIGGS_POTENTIAL_AUXILIARY_CUTOFF_CONTACTS_AND_SURFACE_STRESS_WITH_OUTGOING_SUBSPACE_READOUT',
        scientific_repeat_pairs=pairs,
        binder_repeat_is_new_scientific_or_physical_solve=False,
        partial_constant_density_identification_is_full_tension_matching=False,
        original_attached_zeta_replaced_not_added=True,
        identical_heat_reference_cancellation_is_current_replacement=False,
        finite_terminal_row_scale_is_physical_moment_dependence=False,
        physical_outgoing_operator_is_free_fitted_boundary_parameter=False,
        absolute_energy_unit_is_prerequisite_for_dimensionless_g=False,
        collider_preparation_history_is_prerequisite_for_intrinsic_pole=False,
        full_physical_Higgs_and_surface_coefficients=None,
        full_physical_real_background_and_outgoing_fields=None,
        full_physical_derivative_passed_at_2e_minus_10=False,
        coupled_matching_corrections_applied=0,
        physical_two_spin_normalization=None,
        physical_muon_magnetic_moment=None,
        original_Maxwell_after_correction=None,
        original226_after_correction=None,
        retained_before_Maxwell_magnitude=2.4777309846820184,
        retained_before_original226_max=9.602842247524184e-7,
        required_original_residual_tolerance=2e-10,
        publication_process_audits_passed=5,
        input_and_publication_hashes=dict(sorted(pins.items())),
    )
    out.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n',
                   encoding='utf8', newline='\n')
    print(json.dumps(dict(file=out.name, sha256=sha256(out.read_bytes()).hexdigest(),
                          scientific_repeat_pairs=4, physical_full_solve=False)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    bind(args.repository, args.output)
