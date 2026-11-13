"""Bind real open-form/action components without promoting physical gates.

Consumed numerical bytes are exact. Historical source checkout CRLF is
reconstructed explicitly from index LF where necessary, never normalized
as if it were an actual numerical input. The preserved failed chart has
two exact source aliases, not an edited or silently repaired receipt.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import subprocess


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def staged_blobs(root, paths):
    paths = list(paths)
    raw = subprocess.check_output(['git', 'cat-file', '--batch'], cwd=root,
        input=''.join(':' + rel + '\n' for rel in paths).encode())
    result, offset = {}, 0
    for rel in paths:
        end = raw.index(b'\n', offset)
        header = raw[offset:end].split()
        if len(header) != 3 or header[1] != b'blob':
            raise ValueError('Required index blob missing: ' + rel)
        size = int(header[2])
        result[rel] = raw[end + 1:end + 1 + size]
        offset = end + 2 + size
    if offset != len(raw):
        raise ValueError('Unexpected index batch remainder')
    return result


def read_pair(base, prefix, archive):
    left, right = (base / (prefix + str(i)) for i in (1, 2))
    hashes = {}
    for name in ('result.json', archive):
        a, b = left / name, right / name
        if a.read_bytes() != b.read_bytes():
            raise ValueError('Independent applications differ: ' + prefix + name)
        hashes[name] = digest(a)
    return json.loads((left / 'result.json').read_bytes()), dict(
        independent_runs=[left.name, right.name], byte_identical=True,
        exact_byte_sha256=hashes)


def bind(repository, output):
    root, out = Path(repository).resolve(), Path(output).resolve()
    if out.exists():
        raise FileExistsError(out)
    base = root / 'artifacts/muon_real_coupled_open_operator_20261016'
    pairs = {
        'normal_chart_failure': ('normal_chart_failure_run_', 'actual_real_coefficients_and_normal_squares.npz'),
        'combined_f_eta_open_form': ('open_form_run_', 'application.npz'),
        'full_D5_source_first': ('source_first_run_', 'application.npz'),
        'two_arm_temporal_action': ('temporal_action_run_', 'application.npz'),
    }
    apps, pair_evidence = {}, {}
    for key, (prefix, archive) in pairs.items():
        apps[key], pair_evidence[key] = read_pair(base, prefix, archive)
    failure, form, source, temporal = (apps[k] for k in pairs)
    assert failure['classification'] == 'PRESERVED_ACTUAL_REAL_FULL_CAP_SIGMA_NORMAL_REJECTION'
    assert not failure['full_D5_or_original_action_globally_undefined_inferred']
    assert len(failure['records']) == 6
    assert all(r['sigma_normal_exception'] is not None for r in failure['records'])
    assert form['classification'] == 'REAL_SAVED_FULL384_D5_OPEN_TENSOR_PRODUCT_FORMS'
    assert form['angular_count'] == 5 and form['radial_order'] == 4
    assert form['both_one_sided_temporal_conormals_assembled']
    assert not form['normalized_seam_bound_to_bulk_form']
    assert form['normal_mode_wall_values_uL_uR'] is None
    assert not form['spacelike_unit_normal_or_Gaussian_chart_extended_through_cap']
    assert not form['nonunitary_sin_f_transform_used_to_delete_eta']
    assert not form['polar_sin_f_zero_domain_regularization_proved']
    assert not form['physical_derivative_at_2e_minus10_passed']
    assert form['coupled_corrections'] == 0
    assert source['classification'] == 'ACTUAL_REAL_FULL384_D5_FROZEN_CELL_SOURCE_FIRST_APPLICATION'
    assert len(source['records']) == 8
    assert {r['full_fibre_count'] for r in source['records']} == {384, 1920}
    assert not source['physical_E_B_or_outgoing_domain_derivative']
    assert source['exact_phase_partial_and_time_phase_mixed_retained']
    assert not source['independent_left_conjugated']
    assert not source['source_coefficients_conjugated']
    assert not source['full_physical_derivative_at_2e_minus10']
    assert source['coupled_corrections'] == 0
    assert all(r['core_radial_count'] == 4 and r['separate_actual_wall_count'] == 1
               and r['minimum_actual_core_Q_f'] < 0 for r in source['records'])
    assert temporal['classification'] == 'ACTUAL_REAL_FULL_TWO_ARM_WHOLE_TEMPORAL_CLASSICAL_READOUT'
    assert temporal['full_original_radial_and_cap_rule_preserved']
    assert not temporal['full_physical_derivative_at_2e_minus10_passed']
    assert temporal['newton_or_matching_corrections'] == 0
    assert all(r['original_radial_nodes'] == 48 and r['original_cap_quadrature'] == 48
               and r['exact_response_normalization_rule'] == 96 for r in temporal['records'])
    assert all(r['native_application'] is None and r['boundary_application'] is None
               and r['extra_constraint_application'] is None for r in temporal['records'])
    tests = json.loads((base / 'tests.json').read_bytes())
    assert tests['total_passed'] == 16 and tests['exit_code'] == 0
    assert not tests['full_physical_derivative_pass']
    tested_blobs = staged_blobs(root, sorted(tests['tested_source_hashes']))
    for rel, expected in tests['tested_source_hashes'].items():
        assert digest(root / rel) == expected
        assert tested_blobs[rel] == (root / rel).read_bytes()

    base_rel = base.relative_to(root).as_posix()
    aliases = {
        'WORK/bhsm_real_full_d5_open_form_20261016.py': base_rel + '/normal_chart_failure_run_1/failed_requested_full_cap_producer.py',
        'WORK/bhsm_real_d5_normal_chart_failure_20261016.py': base_rel + '/archived_sources/bhsm_real_d5_normal_chart_failure_20261016.py',
    }
    wanted = {}
    for app in apps.values():
        for rel, expected in app['input_and_source_sha256'].items():
            target = aliases.get(rel, rel)
            if target.startswith('repo/'):
                target = target.removeprefix('repo/')
            if target.startswith('WORK/'):
                raise ValueError('Unresolved noncanonical input path: ' + target)
            if target in wanted and wanted[target] != expected:
                raise ValueError('Consumed bytes differ across applications: ' + target)
            wanted[target] = expected
    staged = staged_blobs(root, sorted(wanted))
    source_pins, numerical_pins = {}, {}
    for rel, expected in sorted(wanted.items()):
        raw, blob = (root / rel).read_bytes(), staged[rel]
        if sha256(raw).hexdigest() != expected:
            raise ValueError('Consumed source/input changed: ' + rel)
        if not rel.endswith('.py'):
            if raw != blob:
                raise ValueError('Numerical input bytes differ from index bytes: ' + rel)
            numerical_pins[rel] = expected
            continue
        if raw == blob:
            recipe = 'identity'
        elif b'\r\n' not in blob and raw == blob.replace(b'\n', b'\r\n'):
            recipe = 'replace every staged LF with CRLF'
        else:
            raise ValueError('Source checkout is not exactly reconstructible: ' + rel)
        source_pins[rel] = dict(actual_consumed_byte_sha256=expected,
            staged_byte_sha256=sha256(blob).hexdigest(), reconstruction=recipe)

    cited = ['src/bhsm/interface/' + name for name in (
        'aether_eta_wall_material_response_v15_26.py',
        'muon_holomorphic_d5_trace_action.py', 'muon_parent_positive_coupled_temporal.py',
        'muon_parent_positive_brst_ghost.py', 'universal_brst_quotient.py',
        'ae4_stratified_dirac_zeta_induced_owner.py',
        'aether_quantum_functional_accounting_v16_00.py',
        'aether_common_quantum_superdeterminant_v15_96.py',
        'aether_einstein_cartan_joint_pushforward_v15_75.py',
        'muon_parent_gauge_geometry_correction.py')]
    cited += ['src/bhsm/interface/completion/foundational_dirac_spin_glue_v14_45.py',
              'src/bhsm/interface/master_action/reduction.py']
    cited_blobs = staged_blobs(root, cited)
    cited_hashes = {}
    for rel in cited:
        text = (root / rel).read_bytes().replace(b'\r\n', b'\n')
        if text != cited_blobs[rel].replace(b'\r\n', b'\n'):
            raise ValueError('Cited source has unpublished code edits: ' + rel)
        cited_hashes[rel] = sha256(text).hexdigest()

    checks = json.loads((base / 'publication_checks/results.json').read_bytes())
    assert len(checks) == 5 and all(r['exit_code'] == 0 for r in checks.values())
    for name, record in checks.items():
        assert digest(base / 'publication_checks' / (name + '.log')) == record['log_sha256']
    pins = {p.relative_to(root).as_posix(): digest(p) for p in sorted(base.rglob('*'))
            if p.is_file() and not p.name.startswith('publication_manifest_run_')}
    pins[Path(__file__).resolve().relative_to(root).as_posix()] = digest(Path(__file__).resolve())
    previous = root / 'artifacts/muon_full_d5_differential_assembly_20261016/publication_manifest_run_1.json'
    assert digest(previous) == '921561bd22cd3a42e177232815de55ca97dd208566834f60f38ab3a8b463e792'
    pins[previous.relative_to(root).as_posix()] = digest(previous)
    cut = root / ('artifacts/muon_baton_zoo_maximal_current_realization_20261013/'
        'actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/'
        'actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz')
    assert digest(cut) == 'ea02ed6aee45310c5651fef5c8f103e868007d4f125582ab2b64ff7651f76b2b'
    sweep = [x['relative_to_nonzero_directional'] for r in temporal['records']
             for x in r['literal_directional_step_sweep']]
    result = dict(
        classification='REAL_FULL_D5_COMBINED_ETA_OPEN_FORM_SOURCE_FIRST_AND_TWO_ARM_CLASSICAL_COMPONENTS',
        independent_scientific_application_pairs=pair_evidence,
        component_tests_passed=16, publication_audits_passed=5,
        first_combined_test_session_guard_failure_preserved=True,
        combined_f_eta_removes_artificial_global_unit_normal_guard=True,
        full_spacelike_normal_chart_constructed=False,
        eta_spin_gauge_temporal_source_terms_preserved=True,
        all_families_particle_conjugate_and_both_sheets_retained=True,
        actual_SH_form_is_nonzero_and_once_only=True,
        normalized_SH_domain_bound_to_bulk=False,
        all_temporal_and_radial_endpoint_trial_coefficients_free=True,
        unspecified_physical_loads_replaced_by_zero=False,
        full_normal_mode_wall_values_uL_uR=None,
        default_two_arm_owner_rejects_unequal_coordinate_steps=True,
        source_clock_incidence_is_same_as_action_measure_weight=False,
        temporal_literal_step_sweep_min_relative=min(sweep),
        temporal_literal_step_sweep_max_relative=max(sweep),
        temporal_all_sweep_errors_at_required_tolerance=all(x <= 2e-10 for x in sweep),
        full_D5_supplied_coefficient_first_MP64_max_scaled=source['worst_MP64_scaled'],
        full_D5_independent_literal_value_max_scaled=source['worst_literal_value_scaled'],
        source_first_axis_is_actual_solved_physical_energy_or_field=False,
        actual_legacy_Higgs_inputs_are_native_matched_coefficients=False,
        full_common_graded_operator_domain_and_native_force_solved=False,
        continuous_physical_mean_or_outgoing_fields_solved=False,
        physical_radial_angular_or_outgoing_convergence_pass=False,
        full_physical_E_B_source_domain_derivative_at_2e_minus10_pass=False,
        required_full_physical_tolerance=2e-10,
        coupled_matching_corrections_applied=0,
        Maxwell_after_correction=None, original226_after_correction=None,
        physical_two_spin_normalization=None, physical_muon_magnetic_moment=None,
        retained_before_Maxwell_magnitude=2.4777309846820184,
        retained_before_original226_max=9.602842247524184e-7,
        preserved_failure_source_aliases=aliases,
        input_pin_path_namespace={'repo/': 'repository root; path prefix only, no input-byte transformation'},
        source_byte_reconstruction=dict(sorted(source_pins.items())),
        numerical_input_byte_hashes=dict(sorted(numerical_pins.items())),
        cited_source_LF_hashes=dict(sorted(cited_hashes.items())),
        cited_source_hash_rule='read-only CRLF-normalized text checked against index; never a numerical input normalization rule',
        current_artifact_byte_hashes=dict(sorted(pins.items())),
        authoritative_original_cut_sha256=digest(cut),
    )
    out.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + '\n',
                   encoding='utf8', newline='\n')
    print(json.dumps(dict(sha256=digest(out), source_pins=len(source_pins),
        numerical_pins=len(numerical_pins), artifact_pins=len(pins))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    bind(args.repository, args.output)
