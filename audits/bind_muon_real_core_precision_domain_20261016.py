"""Bind fixed-form quadrature, full supplied-germ MP and local-center controls."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import numpy as np

from bind_muon_real_coupled_open_operator_20261016 import staged_blobs, digest
from bhsm_real_open_form_radial_quadrature_20261016 import matrix


def pair(base, prefix, files):
    a, b = (base / (prefix + str(i)) for i in (1, 2))
    hashes = {}
    for name in files:
        if (a / name).read_bytes() != (b / name).read_bytes():
            raise ValueError('Independent controls differ: ' + prefix + name)
        hashes[name] = digest(a / name)
    return json.loads((a / 'result.json').read_bytes()), dict(
        directories=[a.name, b.name], exact_byte_sha256=hashes,
        independent_executions_byte_identical=True)


def bind(repository, output):
    root, out = Path(repository).resolve(), Path(output).resolve()
    if out.exists():
        raise FileExistsError(out)
    base = root / 'artifacts/muon_real_core_precision_domain_20261016'
    polar, pe = pair(base, 'polar_center_run_', ['result.json', 'controls.npz'])
    mp, me = pair(base, 'source_first_mp_run_', ['result.json'])
    radial, re = pair(base, 'radial_comparison_run_', ['result.json'])
    full32, fe = pair(base / 'streaming_controls', 'full_batch_32_reference_run_',
                      ['result.json', 'application.npz'])
    assert polar['schema'] == 'bhsm-real-d5-polar-center-source-controls-v1'
    assert len(polar['angular_records']) == 20 and len(polar['frame_records']) == 20
    assert polar['strong_operator_domain_distinct']
    assert polar['polar_spin_frame_is_unitary']
    assert not polar['scalar_sin_f_similarity_is_unitary']
    assert polar['theorem_angular_output_untruncated']
    assert not polar['global_native_or_outgoing_domain_completed']
    assert polar['matching_correction_count'] == 0 and polar['magnetic_moment_prediction'] is None
    assert mp['classification'] == 'INDEPENDENT_MP80_100_FULL384_SUPPLIED_GERM_FORM_FIRST_CONTROL'
    assert len(mp['records']) == 8
    assert mp['full_supplied_germ_contracted_form_first_at_2e_minus10']
    assert mp['binary64_failed_sweep_preserved_unchanged']
    assert not mp['selected_favorable_step']
    assert not mp['physical_E_B_outgoing_or_domain_derivative_at_2e_minus10']
    assert not mp['full_operator_norm_derivative_certificate']
    assert mp['coupled_corrections'] == 0
    mp_absolute = max(p['components'][name]['binary64_first']['absolute']
        for record in mp['records'] for p in record['precisions']
        for name in ('weak', 'positive', 'phase'))
    assert mp_absolute <= 2e-10
    assert radial['classification'] == 'FIXED_P1_OPEN_FORM_RADIAL_QUADRATURE_SENSITIVITY_ONLY'
    assert radial['radial_orders'] == [4, 8, 16, 32, 64]
    assert radial['matrix_count'] == 40 and all(radial['held_operands_exactly_equal'].values())
    assert not radial['physical_radial_convergence_passed']
    assert not radial['physical_derivative_at_2e_minus10_passed']
    assert radial['coupled_corrections'] == 0
    last = radial['transitions'][-1]
    assert (last['left_rule'], last['right_rule']) == (32, 64)
    frob = last['maximum_symmetric_relative_difference']
    scaled = max(x['maximum_entrywise_absolute_or_relative_difference']
                 for x in last['matrices'].values())
    absolute = max(x['maximum_absolute_entry_difference'] for x in last['matrices'].values())
    assert frob <= 2e-10 and scaled <= 2e-10
    assert radial['transitions'][0]['maximum_symmetric_relative_difference'] > 2e-10
    reference32 = base / 'streaming_controls/full_batch_32_reference_run_1/application.npz'
    assert digest(reference32) == radial['provenance']['32']['reference_application_sha256']
    with np.load(reference32, allow_pickle=False) as full_archive, np.load(
            base / 'radial_rule_32_run_1/application.npz', allow_pickle=False) as compact_archive:
        names = [key[:-6] for key in full_archive.files if key.endswith('_shape')]
        assert len(names) == 40
        assert all((matrix(full_archive, name) - matrix(compact_archive, name)).nnz == 0
                   for name in names)

    aliases = {'WORK/bhsm_real_open_form_streaming_20261016.py':
        base.relative_to(root).as_posix() + '/archived_sources/streaming_WORK_source_snapshot_9cee0456.py'}
    wanted = {}

    def include(items):
        for rel, expected in items.items():
            target = aliases.get(rel, rel)
            if target.startswith('repo/'):
                target = target.removeprefix('repo/')
            if target.startswith('WORK/'):
                raise ValueError('Unresolved historical source alias: ' + target)
            if target in wanted and wanted[target] != expected:
                raise ValueError('Source/input bytes disagree between components: ' + target)
            wanted[target] = expected

    include(polar['source_pins'])
    include(mp['input_and_source_sha256'])
    include(full32['input_and_source_sha256'])
    for run in (1, 2):
        directory = base / f'streaming_controls/full_batch_32_reference_run_{run}'
        for name in ('application.npz', 'result.json'):
            include({(directory / name).relative_to(root).as_posix(): digest(directory / name)})
    for provenance in radial['provenance'].values():
        include(provenance['canonical_producer_and_input_sha256'])
        for directory in provenance['independent_repeat_paths']:
            for name, key in (('application.npz', 'application_sha256'), ('result.json', 'result_sha256')):
                include({directory + '/' + name: provenance[key]})
    for control in radial['streaming_controls'].values():
        include({control['path']: control['result_sha256']})
        receipt = control['receipt']
        include(receipt.get('input_and_source_sha256', receipt.get('source_and_input_sha256')))
    compare_path = 'audits/bhsm_real_open_form_radial_quadrature_20261016.py'
    include({compare_path: radial['comparison_source_sha256']})
    blobs = staged_blobs(root, sorted(wanted))
    sources, numerical = {}, {}
    for rel, expected in sorted(wanted.items()):
        raw, blob = (root / rel).read_bytes(), blobs[rel]
        if sha256(raw).hexdigest() != expected:
            raise ValueError('Consumed operand changed: ' + rel)
        if not rel.endswith('.py'):
            if raw != blob:
                raise ValueError('Numerical bytes differ from index: ' + rel)
            numerical[rel] = expected
        else:
            if raw == blob:
                recipe = 'identity'
            elif b'\r\n' not in blob and raw == blob.replace(b'\n', b'\r\n'):
                recipe = 'replace every staged LF with CRLF'
            else:
                raise ValueError('Source checkout is not exactly reconstructible: ' + rel)
            sources[rel] = dict(actual_consumed_byte_sha256=expected,
                staged_byte_sha256=sha256(blob).hexdigest(), reconstruction=recipe)
    checks = json.loads((base / 'publication_checks/results.json').read_bytes())
    assert len(checks) == 5 and all(x['exit_code'] == 0 for x in checks.values())
    for name, record in checks.items():
        assert digest(base / 'publication_checks' / (name + '.log')) == record['log_sha256']
    pins = {p.relative_to(root).as_posix(): digest(p) for p in sorted(base.rglob('*'))
            if p.is_file() and not p.name.startswith('publication_manifest_run_')}
    for path in (Path(__file__).resolve(), root / 'audits/bind_muon_real_coupled_open_operator_20261016.py'):
        pins[path.relative_to(root).as_posix()] = digest(path)
    previous = root / 'artifacts/muon_real_coupled_open_operator_20261016/publication_manifest_run_1.json'
    assert digest(previous) == '5e2b1700f473f14b4e004e21cceea2f74f42832aa1c0e770496579fe42bbc152'
    pins[previous.relative_to(root).as_posix()] = digest(previous)
    result = dict(classification='FIXED_REAL_CORE_QUADRATURE_PRECISION_AND_CONDITIONAL_CENTER_FORM_DOMAIN',
        independent_control_pairs=dict(polar_center=pe, supplied_germ_MP=me,
            radial_comparison=re, full_batch_32_reference=fe),
        five_publication_audits_passed=True,
        conditional_regular_center_form_closure_constructed=True,
        extra_origin_point_boundary_parameter_required_by_that_closure=False,
        smooth_form_core_is_everywhere_strong_operator_domain=False,
        scalar_sin_f_similarity_used_to_delete_eta=False,
        retained_angular_spin_branches_and_both_charge_sheets=True,
        center_uniform_leading_form_constant=polar['coercivity']['uniform_form_lower_constant'],
        supplied_germ_MP80_100_form_first_at_2e_minus10=True,
        supplied_germ_max_first_relative=mp['worst_binary64_first_relative_to_nonzero_derivative'],
        supplied_germ_max_first_absolute=mp_absolute,
        MP80_100_max_first_relative=mp['worst_MP80_MP100_first_relative'],
        failed_binary64_difference_steps_preserved=True,
        fixed_P1_form_32_to_64_max_Frobenius_relative=frob,
        fixed_P1_form_32_to_64_max_entrywise_scaled=scaled,
        fixed_P1_form_32_to_64_max_absolute_entry_change=absolute,
        fixed_P1_quadrature_32_to_64_passes_stated_scaled_2e_minus10_checks=True,
        fixed_P1_quadrature_absolute_entry_changes_all_below_2e_minus10=(absolute <= 2e-10),
        quadrature_convergence_is_physical_radial_space_or_state_convergence=False,
        full_common_graded_native_operator_and_domain_solved=False,
        full_physical_outgoing_E_B_source_domain_derivative_at_2e_minus10=False,
        coupled_matching_corrections_applied=0,
        physical_two_spin_normalization=None, physical_muon_magnetic_moment=None,
        Maxwell_after_correction=None, original226_after_correction=None,
        retained_before_Maxwell_magnitude=2.4777309846820184,
        retained_before_original226_max=9.602842247524184e-7,
        required_physical_tolerance=2e-10,
        historical_source_aliases=aliases,
        numerical_input_byte_hashes=dict(sorted(numerical.items())),
        source_byte_reconstruction=dict(sorted(sources.items())),
        current_artifact_byte_hashes=dict(sorted(pins.items())))
    out.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n',
                   encoding='utf8', newline='\n')
    print(json.dumps(dict(sha256=digest(out), source_pins=len(sources),
                         numerical_pins=len(numerical), artifact_pins=len(pins))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    bind(args.repository, args.output)
