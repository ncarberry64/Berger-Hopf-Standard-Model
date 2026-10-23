"""Bind full retained D5 component checks without promoting physical gates."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import subprocess


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def staged_blobs(root, paths):
    raw = subprocess.check_output(['git', 'cat-file', '--batch'], cwd=root,
        input=''.join(':' + rel + '\n' for rel in paths).encode())
    result, offset = {}, 0
    for rel in paths:
        end = raw.index(b'\n', offset)
        header = raw[offset:end].split()
        if len(header) != 3 or header[1] != b'blob':
            raise ValueError('Required staged input missing: ' + rel)
        size = int(header[2])
        result[rel] = raw[end + 1:end + 1 + size]
        offset = end + 2 + size
    if offset != len(raw):
        raise ValueError('Unexpected staged source batch remainder')
    return result


def bind(repository, output):
    root, out = Path(repository).resolve(), Path(output).resolve()
    if out.exists():
        raise FileExistsError(out)
    base = root / 'artifacts/muon_full_d5_differential_assembly_20261016'
    a, b = (base / ('application_run_' + str(i)) / 'result.json' for i in (1, 2))
    if a.read_bytes() != b.read_bytes():
        raise ValueError('Independent D5 applications differ')
    app = json.loads(a.read_bytes())
    assert len(app['records']) == 8
    assert {r['full_retained_fibre_count'] for r in app['records']} == {384, 1920}
    assert not app['selected_node_action_is_radial_quadrature']
    assert not app['full_physical_derivative_at_2e_minus10_passed']
    assert app['coupled_corrections'] == 0 and app['physical_muon_magnetic_moment'] is None
    assert all(not r['actual_wall_included'] and not r['saved_radial_inclusion_called_sigma_normalized']
               for r in app['records'])
    tests = json.loads((base / 'tests.json').read_bytes())
    assert tests['total_passed'] == 5 and not tests['full_physical_derivative_pass']
    source_pins, numerical_pins = {}, {}
    wanted = app['input_and_source_sha256']
    staged = staged_blobs(root, sorted(wanted))
    for rel, expected in sorted(wanted.items()):
        raw, blob = (root / rel).read_bytes(), staged[rel]
        if sha256(raw).hexdigest() != expected:
            raise ValueError('Consumed source/input changed: ' + rel)
        if not rel.endswith('.py'):
            if raw != blob:
                raise ValueError('Numerical input bytes differ from staged bytes: ' + rel)
            numerical_pins[rel] = expected
        else:
            if raw == blob:
                recipe = 'identity'
            elif b'\r\n' not in blob and raw == blob.replace(b'\n', b'\r\n'):
                recipe = 'replace every staged LF with CRLF'
            else:
                raise ValueError('Source byte representation not reproducible: ' + rel)
            source_pins[rel] = dict(actual_consumed_byte_sha256=expected,
                staged_byte_sha256=sha256(blob).hexdigest(), reconstruction=recipe)
    assert digest(base / 'muon_m8_r85_to_full_d5_assembly_20261016.txt') == (
        'c4e36d1b4c7257a52d89948fa1dd4fc5b1ed72520c24c6eafa373196bffe4948')
    assert digest(base / 'muon_real_d5_native_factor_ellipticity_20261016.txt') == (
        'f5318eb414cee96f4f979c4af160bb30b06e92de3c27a3965d7ff52eaaea067a')
    cited = ['src/bhsm/interface/' + name for name in (
        'muon_owned_native_product_connection.py', 'muon_native_dirac_hamiltonian.py',
        'muon_native_product_factor_graph.py', 'ae4_current_c2_factorized_hs_calderon.py',
        'muon_holomorphic_d5_trace_action.py')]
    cited_staged, cited_text = staged_blobs(root, cited), {}
    for rel in cited:
        text = (root / rel).read_bytes().replace(b'\r\n', b'\n')
        if text != cited_staged[rel].replace(b'\r\n', b'\n'):
            raise ValueError('Cited source has unpublished code changes: ' + rel)
        cited_text[rel] = sha256(text).hexdigest()
    checks = json.loads((base / 'publication_checks/results.json').read_bytes())
    assert len(checks) == 5 and all(r['exit_code'] == 0 for r in checks.values())
    for name, check in checks.items():
        assert digest(base / 'publication_checks' / (name + '.log')) == check['log_sha256']
    pins = {p.relative_to(root).as_posix(): digest(p) for p in sorted(base.rglob('*'))
            if p.is_file() and not p.name.startswith('publication_manifest_run_')}
    pins[Path(__file__).resolve().relative_to(root).as_posix()] = digest(Path(__file__).resolve())
    prior = root / 'artifacts/muon_m8_m5_geometric_operator_20261016/publication_manifest_run_1.json'
    assert digest(prior) == 'da5a0deac714d6ee2da63117900feb107e26b76d2771aac4f7230be30ad4f521'
    pins[prior.relative_to(root).as_posix()] = digest(prior)
    cut = root / ('artifacts/muon_baton_zoo_maximal_current_realization_20261013/'
        'actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/'
        'actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz')
    assert digest(cut) == 'ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b'
    fields = ('ordered_action_comparison', 'phase_first_comparison',
              'all_fibre_point_expression_comparison', 'selected_point_action_comparison')
    result = dict(
        classification='FULL384_D5_DIFFERENTIAL_ASSEMBLY_ON_FROZEN_COEFFICIENT_FIELDS',
        independent_application_pair=dict(paths=[a.relative_to(base).as_posix(), b.relative_to(base).as_posix()],
            sha256=digest(a), byte_identical=True),
        component_tests_passed=5, publication_audits_passed=5,
        full_family_particle_conjugate_angular_rows_retained=True,
        actual_sigma_eta_time_shift_spin_and_retained_gauge_terms_preserved=True,
        real_regular_D5_local_plus_factor_density_pairing_and_scalar_positive_principal_constructed=True,
        Hermitian_W_or_zero_eta_is_required_for_this_local_positive_product=False,
        local_native_time_connection_or_Wick_choice_left_as_free_parameter=False,
        full_stratified_domain_or_relative_determinant_equality_proved=False,
        direct_phase_coefficient_contraction_preserves_nonzero_small_term=True,
        weak_left_source_conjugated=False,
        same_E_Lorentz_phase_is_native_or_total_physical_energy_derivative=False,
        full_physical_background_or_outgoing_operator_solved=False,
        physical_radial_and_angular_convergence_pass=False,
        full_physical_E_B_source_domain_derivative_at_2e_minus10_pass=False,
        coupled_matching_corrections_applied=0,
        physical_two_spin_normalization=None, physical_muon_magnetic_moment=None,
        Maxwell_after_correction=None, original226_after_correction=None,
        retained_before_Maxwell_magnitude=2.4777309846820184,
        retained_before_original226_max=9.602842247524184e-7,
        required_full_physical_tolerance=2e-10,
        selected_node_diagnostic_is_a_radial_integral=False,
        new_history_stage_profile_D5_or_radial_integrations=0,
        literal_original_owner_max_comparison_absolute=max(r[k]['absolute'] for r in app['records'] for k in fields),
        literal_original_owner_max_comparison_scaled=max(r[k]['scaled'] for r in app['records'] for k in fields),
        source_byte_reconstruction=dict(sorted(source_pins.items())),
        numerical_input_byte_hashes=dict(sorted(numerical_pins.items())),
        cited_source_LF_hashes=dict(sorted(cited_text.items())),
        cited_source_hash_rule='read-only CRLF-normalized text verified against staged code; not a numerical input-byte hash rule',
        current_artifact_byte_hashes=dict(sorted(pins.items())),
        authoritative_original_cut_sha256=digest(cut),
    )
    out.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + '\n',
                   encoding='utf8', newline='\n')
    print(json.dumps(dict(sha256=digest(out), source_pins=len(source_pins),
                         numerical_pins=len(numerical_pins), artifact_pins=len(pins))))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository', required=True)
    p.add_argument('--output', required=True)
    args = p.parse_args()
    bind(args.repository, args.output)
