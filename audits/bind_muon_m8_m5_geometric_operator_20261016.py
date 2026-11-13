"""Bind evaluated M8 geometry; never promote a partial jet to a physical gate."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import subprocess


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def bind(repository, output):
    root, out = Path(repository).resolve(), Path(output).resolve()
    if out.exists():
        raise FileExistsError(out)
    base = root / 'artifacts/muon_m8_m5_geometric_operator_20261016'
    pairs = {}
    for name, files in (
        ('scalar_application', ['application_run_1/result.json', 'application_run_2/result.json']),
        ('independent_MP64_controls', ['application_run_1/controls.json', 'application_run_2/controls.json']),
        ('full16_KK_application', ['KK_application_run_1/result.json', 'KK_application_run_2/result.json']),
    ):
        a, b = (base / p for p in files)
        if a.read_bytes() != b.read_bytes():
            raise ValueError('Independent executions differ: ' + name)
        pairs[name] = dict(paths=files, sha256=digest(a), byte_identical=True)
    scalar = json.loads((base / 'application_run_1/result.json').read_bytes())
    kk = json.loads((base / 'KK_application_run_1/result.json').read_bytes())
    tests = json.loads((base / 'tests.json').read_bytes())
    assert tests['total_passed'] == 8 and not tests['full_physical_derivative_pass']
    assert len(scalar['records']) == len(kk['records']) == 8
    assert not scalar['partial_source_is_energy_or_measuring_B']
    assert not kk['full_physical_outgoing_derivative_at_2e_minus10_passed']
    assert scalar['coupled_corrections'] == kk['coupled_corrections'] == 0
    assert scalar['physical_muon_magnetic_moment'] is None
    # Preserve ACTUAL consumed source-byte identities. The explicit recipe
    # below reconstructs those text bytes from the staged Git source. No
    # array/NPZ/numerical-input bytes are normalized or replaced.
    source_reconstruction, consumed_non_source = {}, {}
    for payload in (scalar, kk):
        for rel, expected in payload['input_and_source_sha256'].items():
            path = root / rel
            raw = path.read_bytes()
            if sha256(raw).hexdigest() != expected:
                raise ValueError('Consumed input/source changed: ' + rel)
            staged = subprocess.check_output(['git', 'show', ':' + rel], cwd=root)
            if not rel.endswith('.py'):
                if staged != raw:
                    raise ValueError('Numerical input differs from staged bytes: ' + rel)
                consumed_non_source[rel] = expected
                continue
            if raw == staged:
                recipe = 'identity'
            elif b'\r\n' not in staged and raw == staged.replace(b'\n', b'\r\n'):
                recipe = 'replace every staged LF with CRLF'
            else:
                raise ValueError('Consumed source is not exactly reproducible from staged source: ' + rel)
            source_reconstruction[rel] = dict(actual_consumed_byte_sha256=expected,
                staged_byte_sha256=sha256(staged).hexdigest(), reconstruction=recipe)
    proof = base / 'muon_m8_geometric_dirac_hopf_incidence_20261016.txt'
    assert digest(proof) == '03542fb51de07c2909917481ef4dc07068c59204de92a13c1342d93a8efc9903'
    checks = json.loads((base / 'publication_checks/results.json').read_bytes())
    assert len(checks) == 5 and all(r['exit_code'] == 0 for r in checks.values())
    for name, check in checks.items():
        assert digest(base / 'publication_checks' / (name + '.log')) == check['log_sha256']
    pins = {}
    for path in sorted(base.rglob('*')):
        if path.is_file() and not path.name.startswith('publication_manifest_run_'):
            pins[path.relative_to(root).as_posix()] = digest(path)
    pins[Path(__file__).resolve().relative_to(root).as_posix()] = digest(Path(__file__).resolve())
    cut = root / ('artifacts/muon_baton_zoo_maximal_current_realization_20261013/'
        'actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/'
        'actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz')
    if digest(cut) != 'ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b':
        raise ValueError('Authoritative cut changed')
    result = dict(
        classification='M8_M5_GEOMETRIC_DIRAC_COEFFICIENTS_AND_FULL16_KK_CONTACTS_EVALUATED',
        independent_execution_pairs=pairs, component_tests_passed=8, publication_audits_passed=5,
        source_axes='saved canonical coordinate-time x and declared partial qb0/raw25 y',
        supplied_fixed_rawtime_mixed_source_is_physical_E_B=False,
        original_all_seven_spatial_and_time_shift_principals_retained=True,
        full_vertical_DF_and_spin_preserved=True, normalized_fiber_density_cancellation_evaluated=True,
        M8_M5_normalized_fiber_coefficient_identities_evaluated=True,
        full_R85_native_graded_carrier_and_complement_solved=False,
        M8_spin_block_is_required_new_muon_particle_carrier=False,
        full384_D5_muon_operator_can_be_assembled_independently_of_new_M8_particle_assignment=True,
        scalar_saved_germ_direct_original_Jet100_max_scaled=max(v['scaled'] for r in scalar['records']
            for c in r['direct_original_Jet100_comparisons'].values() for v in c.values()),
        scalar_saved_germ_cancellation_max_raw=max(v for r in scalar['records']
            for c in r['helper_identity_rows'].values() for v in c.values()),
        KK_saved_germ_full_vs_upper_ordering_max=max(v for r in kk['records']
            for v in r['full_vs_upper_ordered_KK_residual'].values()),
        full_physical_operator_background_outgoing_E_B_domain_derivative_pass=False,
        full_physical_radial_and_angular_convergence_pass=False,
        coupled_matching_corrections_applied=0,
        retained_before_Maxwell_magnitude=2.4777309846820184,
        retained_before_original226_max=9.602842247524184e-7,
        Maxwell_after_correction=None, original226_after_correction=None,
        required_full_physical_tolerance=2e-10,
        physical_two_spin_normalization=None, physical_muon_magnetic_moment=None,
        new_history_stage_profile_D5_or_radial_integrations=0,
        actual_consumed_source_byte_reconstruction=dict(sorted(source_reconstruction.items())),
        actual_consumed_non_source_byte_hashes=dict(sorted(consumed_non_source.items())),
        current_artifact_byte_hashes=dict(sorted(pins.items())),
        authoritative_original_cut_sha256=digest(cut),
    )
    out.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + '\n',
                   encoding='utf8', newline='\n')
    print(json.dumps(dict(sha256=digest(out), source_pins=len(source_reconstruction),
        numerical_pins=len(consumed_non_source), artifact_pins=len(pins))))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository', required=True)
    p.add_argument('--output', required=True)
    args = p.parse_args()
    bind(args.repository, args.output)
