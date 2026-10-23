"""Verify completed birth, inherited source-on, and corrected face pairs.

This reads the saved applications and never reexecutes an action or ODE.
Earlier corner runs 1/2 are preserved as right-second-source comparisons.
"""
from pathlib import Path
from hashlib import sha256
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENT = dict(PYTHONPATH='src;scripts', OPENBLAS_NUM_THREADS='4', OMP_NUM_THREADS='4')
CASES = ('normal_basis', 'area_source')


def digest(data):
    return sha256(data).hexdigest()


def verify_package(stem, runs, classification, test_files, test_log, scope):
    base = ROOT / f'artifacts/muon_holomorphic_magnetic_{stem}_20261012'
    out = base / 'pair_verification'
    if out.exists():
        raise FileExistsError(f'preserve existing verification: {out}')
    files, pins, commands = {}, {}, []
    first_bytes = None

    def add(path):
        data = path.read_bytes()
        files[path.relative_to(ROOT).as_posix()] = digest(data)
        return data

    for ordinal, number in enumerate(runs):
        folder = base / f'run_{number}'
        data = add(folder / 'result.json')
        report = json.loads(data)
        if report['classification'] != classification:
            raise ValueError('completed application classification required')
        if first_bytes is None:
            first_bytes, original = data, report
        elif data != first_bytes:
            raise ValueError('same completed receipt bytes differ')
        for name, meta in report['archives'].items():
            data = add(folder / name)
            if len(data) != meta['bytes'] or digest(data) != meta['sha256']:
                raise ValueError('saved application archive changed')
            if ordinal and data != (base / f'run_{runs[0]}' / name).read_bytes():
                raise ValueError('same application replay archive bytes differ')
            with np.load(folder / name, allow_pickle=False) as arrays:
                if any(v.dtype.kind in 'fc' and not np.all(np.isfinite(v)) for v in arrays.values()):
                    raise ValueError('nonfinite completed application array')
        for name, h in report['input_hashes'].items():
            if name in pins and pins[name] != h:
                raise ValueError('same application input pin conflict')
            pins[name] = h
        add(ROOT / f'artifacts/muon_holomorphic_magnetic_{stem}_20261012_run_{number}.stdout.txt')
        commands.append(['C:/Python314/python.exe', f'scripts/evaluate_muon_holomorphic_magnetic_{stem}.py',
                         '--output', folder.relative_to(ROOT).as_posix()])

    for name, h in pins.items():
        if digest((ROOT / name).read_bytes()) != h:
            raise ValueError(f'consumed input pin changed: {name}')
    for name in test_files:
        add(ROOT / name)
    stdout = add(ROOT / test_log).decode('utf-8-sig')
    if ' passed in ' not in stdout or 'FAILED' in stdout:
        raise ValueError('actual focused test evidence required')
    add(Path(__file__))
    details = dict()

    if stem == 'birth_matching':
        if original['parent_endpoint_exact_saved_sigma'] != 1.0:
            raise ValueError('saved incoming final face required')
        if not original['source_Hermite_midpoints_not_relabelled_birth']:
            raise ValueError('midpoint and actual birth source scope required')
        if any(original['applications'][c]['conditional_child_launch']['admitted'] for c in CASES):
            raise ValueError('preserve stronger all-coordinate diagnostic failure')
        details.update(
            original_all_coordinate_test_remains_failed=True,
            all_coordinate_failure_does_not_establish_free_domain_or_physical_incompatibility=True,
            prescribed_wall_At_and_dynamic_Pi_maxima_are_named_reaction_directions=True,
            old_fresh_parent_Pi_on_carried_rate_is_constitutive_comparison_only=True,
            legacy_Qt_proper_clock_keys_use_Qt_over_iN_not_Lorentz_Qt_over_N=True)
    elif stem == 'inherited_cauchy':
        if not original['actual_parent_birth_action_reconstituted_at_preserved_free_q_Pi']:
            raise ValueError('fresh actual-born parent constitutive reconstruction required')
        guard = original['declared_absolute_field_domain_tolerance']
        for case in CASES:
            a = original['applications'][case]
            if not (a['source_on_at_birth'] and a['child_C2_pulse_not_restarted'] and a['source_points'] == 20):
                raise ValueError('inherited source-on continuation required')
            if a['free_domain_and_constraint_dual_range_max'] > guard:
                raise ValueError('free original domain or named-dual range audit failed')
            if a['original_propagated_rows_max'] > guard:
                raise ValueError('original propagated row audit failed')
            with np.load(base / f'run_{runs[0]}/{case}_actual_birth_reconstitution_and_source_contacts.npz') as arrays:
                jump = arrays['source_first_inherited_value_jump']
                details[case] = dict(algebraic_At_source_first_value_jump_max=float(np.max(abs(jump[:, :64]))),
                                     dynamic_source_first_value_jump_max=float(np.max(abs(jump[:, 64:]))))
                if details[case]['dynamic_source_first_value_jump_max'] > guard:
                    raise ValueError('dynamic source-first reset trace failed')
        details.update(source_on_free_canonical_target_and_named_boundary_reactions_checked=True,
                       algebraic_At_first_jump_is_not_dynamic_trace_failure=True,
                       initial_source_cotangent_is_signed_endpoint_variation_not_integrated_power=True)
    else:
        if not original['left_and_right_corner_rates_use_their_own_one_sided_source_second_germ']:
            raise ValueError('complete one-sided face rate scope required')
        for case in CASES:
            with np.load(base / f'run_{runs[0]}/{case}_actual_source_corner.npz') as arrays:
                for prefix in ('initial_', 'final_', 'corner_left_', 'corner_right_'):
                    for key in ('total_field', 'total_coordinate_rate', 'canonical_momentum',
                                'total_field_first', 'total_coordinate_rate_first', 'canonical_momentum_first'):
                        if prefix + key not in arrays:
                            raise ValueError('complete exact face and source-first maps required')
                if not np.array_equal(arrays['corner_left_source_Q'], arrays['corner_right_source_Q']):
                    raise ValueError('C1 corner source value differs')
                if not np.array_equal(arrays['corner_left_source_Q_coordinate_rate'], arrays['corner_right_source_Q_coordinate_rate']):
                    raise ValueError('C1 corner source rate differs')
        preserved = ['preserved_shared_right_second_driver.py', 'preserved_source_faces_helper.py']
        for name in preserved:
            add(base / name)
        historical = {}
        for number in (1, 2):
            # Do not select the historical result receipts as authoritative
            # files: their old producer pins are intentionally historical.
            historical[f'run_{number}/result.json'] = digest((base / f'run_{number}/result.json').read_bytes())
            add(ROOT / f'artifacts/muon_holomorphic_magnetic_source_corner_20261012_run_{number}.stdout.txt')
        details.update(authoritative_full_face_pair=list(runs),
                       unselected_historical_result_digests=historical,
                       earlier_corner_runs_1_2_left_At_rate_is_right_source_second_comparison_only=True,
                       earlier_corner_q_Pi_and_source_cotangent_unaffected=True,
                       corner_is_held_coefficient_interface_not_new_physical_stop=True,
                       Lorentz_cotangent_weak_continued_conversion='-i times Lorentz cotangent')

    record = dict(classification='VERIFIED_' + classification.removeprefix('EVALUATED_') + '_PAIR',
                  files=files, input_hashes=pins, all_output_bytes_equal=True,
                  original_result_sha256=digest(first_bytes), commands=commands, environment=ENVIRONMENT,
                  test_command=['C:/Python314/python.exe', '-m', 'pytest', '--noconftest', '-q', *test_files],
                  test_stdout=test_log, applications=original['applications'], role_and_source_audits=details,
                  numerical_actions_not_rerun=True, physical_full226_event_mode_exterior_pole_LSZ_not_completed=True,
                  declared_absolute_field_domain_tolerance_not_a_transferred_physical146_guard=True,
                  scope=scope)
    out.mkdir()
    path = out / 'publication_manifest.json'
    path.write_text(json.dumps(record, sort_keys=True, indent=2, allow_nan=False) + '\n',
                    encoding='utf8', newline='\n')
    return dict(manifest=path.relative_to(ROOT).as_posix(), sha256=digest(path.read_bytes()),
                files=len(files), pins=len(pins), original_result_sha256=digest(first_bytes))


def main():
    specifications = [
        ('birth_matching', (1, 2), 'EVALUATED_ACTUAL_BIRTH_MAGNETIC_FIELD_SOURCE_AND_TEMPORAL_MATCHING',
         ['tests/test_muon_holomorphic_magnetic_birth_matching.py'],
         'artifacts/muon_holomorphic_magnetic_birth_matching_tests_20261012.stdout.txt',
         'Exact saved finite parent face and fresh actual-birth source comparisons; stronger all-coordinate diagnostic remains failed. Wall/frame reaction roles are interpreted by the subsequent source-on application.'),
        ('inherited_cauchy', (1, 2), 'EVALUATED_ACTUAL_BORN_PRESCRIBED_SOURCE_COTANGENT_AND_INHERITED_CHILD_CURRENT',
         ['tests/test_muon_holomorphic_magnetic_inherited_cauchy.py',
          'tests/test_muon_holomorphic_magnetic_birth_source_contacts.py'],
         'artifacts/muon_holomorphic_magnetic_inherited_cauchy_final_tests_20261012.stdout.txt',
         'Fresh-born parent/child free canonical reconstitution, named boundary source cotangents and source-on child continuation/current on the declared held-coefficient finite prefix. Fixed Hermite/time/action approximation and physical matching scope remain explicit.'),
        ('source_corner', (3, 4), 'EVALUATED_INHERITED_MAGNETIC_COEFFICIENT_CORNER_SOURCE_COTANGENT',
         ['tests/test_muon_holomorphic_magnetic_source_faces.py'],
         'artifacts/muon_holomorphic_magnetic_source_faces_one_sided_tests_20261012.stdout.txt',
         'Complete initial/final and both coefficient-corner face maps on the source-on prefix; one-sided source second germs are derivatives of the declared C1 interpolant. Deterministic replay is not an action/physical outward enclosure.'),
    ]
    combined = ROOT / 'artifacts/muon_holomorphic_magnetic_birth_source_20261012/pair_verification'
    # Preflight all destinations before writing any verification output.
    if combined.exists():
        raise FileExistsError('preserve existing combined replay evidence')
    for stem, *_ in specifications:
        if (ROOT / f'artifacts/muon_holomorphic_magnetic_{stem}_20261012/pair_verification').exists():
            raise FileExistsError('preserve existing paired verification')
    results = {s[0]: verify_package(*s) for s in specifications}
    files, pins = {}, {}
    for result in results.values():
        path = ROOT / result['manifest']
        report = json.loads(path.read_bytes())
        files[result['manifest']] = digest(path.read_bytes())
        for name, h in report['files'].items():
            if name in files and files[name] != h:
                raise ValueError('combined file hash conflict')
            files[name] = h
        for name, h in report['input_hashes'].items():
            if name in pins and pins[name] != h:
                raise ValueError('combined actual input pin conflict')
            pins[name] = h
    combined.mkdir(parents=True)
    path = combined / 'publication_manifest.json'
    record = dict(classification='VERIFIED_ACTUAL_BIRTH_INHERITED_MAGNETIC_SOURCE_AND_CORRECTED_FACE_PAIRS',
                  packages=results, files=files, input_hashes=pins, all_output_bytes_equal=True,
                  environment=ENVIRONMENT, numerical_actions_not_rerun=True,
                  verifier_command=['C:/Python314/python.exe', Path(__file__).relative_to(ROOT).as_posix()],
                  historical_corner_result_json_not_selected=True,
                  scope='Completed same-input replay evidence for the conditional field-sector birth/source-on/face applications; no physical full226, event/exterior/pole/LSZ or action-accuracy enclosure.')
    path.write_text(json.dumps(record, sort_keys=True, indent=2, allow_nan=False) + '\n',
                    encoding='utf8', newline='\n')
    results['combined'] = dict(manifest=path.relative_to(ROOT).as_posix(), sha256=digest(path.read_bytes()),
                              files=len(files), pins=len(pins))
    print(json.dumps(results, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
