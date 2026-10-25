"""Explicit Gaussian/spectral research API; no legacy fallback or BH acceptance.

Only the versioned 2023 benchmark and explicitly registered simulations are
admitted. General user joint data continue to use their separately declared
interfaces. Planning never requires an internal paper-workflow permission file.
"""
import argparse
import base64
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import zipfile

ENGINE = 'known2023-gaussian-v4-spectral-v6.portable.v1'
INPUT_LIMIT = 32_000_000
STRUCTURE_LIMIT = 134217728
ARCHIVE_LIMIT = 536870912
EXPANDED_LIMIT = 1077936128
SOURCE_MANIFEST_SHA256 = '066d60841591ddfdba91e06f9ba16856a8e9b8ee6a570d69ee08699834a9329e'
NATIVE_SHA256 = 'd2409db410e113872781494ca4d73db57d2a44fd65146c4e7ec2f40828448428'
FORMAL_SOURCE = 'https://github.com/ncarberry64/Berger-Hopf-Standard-Model'
REQUIRED = ('numpy', 'scipy', 'astropy', 'celerite2')
FLAGS = {'publication_hold': 'HOLD', 'scientific_acceptance': False,
         'known_black_hole_recovery_accepted': False, 'accepted_mass_interval': None}


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _read_file(path, limit=STRUCTURE_LIMIT):
    path = Path(path)
    size = path.stat().st_size
    if not 0 < size <= limit: raise ValueError('File exceeds the declared read limit')
    with path.open('rb') as stream: raw = stream.read(limit + 1)
    if len(raw) != size or len(raw) > limit: raise ValueError('File size changed while reading')
    return raw


def _file_record(path):
    digest = hashlib.sha256(); size = 0
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            digest.update(block); size += len(block)
    return {'bytes': size, 'sha256': digest.hexdigest()}


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def _parse(raw):
    if type(raw) is not bytes or not 0 < len(raw) <= STRUCTURE_LIMIT:
        raise ValueError('Nonempty structured JSON within the declared read limit required')
    value = json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs,
                       parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON: ' + x)))
    def check(v):
        if type(v) is float and not math.isfinite(v):
            raise ValueError('Nonfinite JSON value')
        if type(v) is dict:
            for child in v.values(): check(child)
        elif type(v) is list:
            for child in v: check(child)
    check(value)
    return value


def _native(value):
    if hasattr(value, 'tolist'):
        return _native(value.tolist())
    if type(value) is dict:
        return {str(k): _native(v) for k, v in value.items()}
    if type(value) in (tuple, list):
        return [_native(v) for v in value]
    return value


def _encode(value):
    return (json.dumps(_native(value), sort_keys=True, separators=(',', ':'),
                       ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')


def _finite(value, label):
    if type(value) not in (int, float):
        raise ValueError(label + ' must be a real number')
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError(label + ' is unrepresentable') from exc
    if not math.isfinite(result):
        raise ValueError(label + ' must be finite')
    return result


def _registry(value):
    if value is None: return {}
    if type(value) is not dict or set(value) - {'wholly_invented_sha256', 'actual_cadence_sha256'}:
        raise ValueError('Explicit simulation hash registry required')
    result = {}
    for key, hashes in value.items():
        if type(hashes) is not list or len(hashes) > 128 or any(
                type(h) is not str or len(h) != 64 or any(c not in '0123456789abcdef' for c in h) for h in hashes):
            raise ValueError('Registry entries must be SHA256 strings')
        result[key] = list(hashes)
    return result


def verify_sources():
    """Bind every private installed source; no optional scientific imports."""
    root = Path(__file__).resolve().parent / '_joint_v3'
    path = root / 'SOURCE_MANIFEST_v1.json'
    raw = path.read_bytes()
    if _sha(raw) != SOURCE_MANIFEST_SHA256:
        raise ValueError('Installed engine source manifest differs')
    manifest = _parse(raw)
    if manifest.get('engine') != ENGINE:
        raise ValueError('Wrong engine source identity')
    for record in manifest['files']:
        name = record['filename']
        if Path(name).name != name or not name.endswith('.py'):
            raise ValueError('Invalid installed source role')
        blob = (root / name).read_bytes()
        if len(blob) != record['bytes'] or _sha(blob) != record['sha256']:
            raise ValueError('Installed scientific source differs: ' + name)
    return manifest


def source_identity():
    verify_sources()
    return {'engine': ENGINE, 'private_manifest_sha256': SOURCE_MANIFEST_SHA256,
            'public_api_sha256': _sha(Path(__file__).read_bytes())}


def runtime():
    packages = {}
    for name in REQUIRED:
        try: packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: packages[name] = None
    return {'python': platform.python_version(), 'implementation': platform.python_implementation(),
            'platform': sys.platform, 'byteorder': sys.byteorder, 'packages': packages,
            'observer_ephemeris': 'astropy builtin Earth-minus-Sun, JD_TDB'}


def availability():
    value = runtime()
    missing = [key for key, version in value['packages'].items() if version is None]
    return {'engine': ENGINE, 'available': not missing, 'missing_dependencies': missing,
            'runtime': value, 'source_identity': source_identity(), 'formal_source': FORMAL_SOURCE,
            'supported_input': 'Exact versioned 2023 benchmark or explicitly registered simulations; not general joint input',
            'BHSM': 'One gravitational exterior interpreted as BHSM surface topography, counted once; no microscopic interface or horizon identified.', **FLAGS}


def validate_benchmark(raw, *, purpose, control_registry=None):
    """Admission/metadata only; registry declarations are not validation evidence."""
    registry = _registry(control_registry)
    if type(raw) is not bytes or not 0 < len(raw) <= INPUT_LIMIT:
        raise ValueError('Original benchmark JSON must fit the 32,000,000-byte input resource limit')
    digest = _sha(raw) if type(raw) is bytes else None
    if purpose == 'AUTHENTIC2023' and digest != NATIVE_SHA256:
        raise ValueError('Only the exact versioned 2023 benchmark bytes are admitted')
    document = _parse(raw)
    native = document
    if purpose == 'WHOLLY_INVENTED':
        if (digest not in registry.get('wholly_invented_sha256', []) or
                document.get('simulation_only') is not True or document.get('native_files') or
                document.get('data_version') != 'SYNTHETIC_KNOWN2023_ST6_CONTROL_v1'):
            raise ValueError('Explicitly registered wholly invented input required')
    elif purpose == 'ACTUAL_CADENCE_CONTROL':
        if (digest not in registry.get('actual_cadence_sha256', []) or
                document.get('schema') != 'bhsm.known2023.generated_control.v1' or
                document.get('scope') != 'CONDITIONAL_SIMULATION_AT_AUTHENTIC_CADENCE' or
                document.get('simulation_only') is not True):
            raise ValueError('Registered actual-cadence simulation required')
        parent = base64.b64decode(document['parent_native_bytes_base64'], validate=True)
        if _sha(parent) != NATIVE_SHA256 or document.get('parent_native_sha256') != NATIVE_SHA256:
            raise ValueError('Actual-cadence parent identity differs')
        native = _parse(parent)
        for field, generated in [('photometry', 'generated_photometry'), ('astrometry', 'generated_astrometry')]:
            if [r['source_row_id'] for r in native[field]] != [r['parent_source_row_id'] for r in document[generated]]:
                raise ValueError('Generated row identities/order differ from their parent')
    elif purpose == 'AUTHENTIC2023':
        if native.get('data_version') != 'OGLE-Mroz2022-corrected_LamLu2023v2-HST21-MAST82.v1' or native.get('simulation_only') is True:
            raise ValueError('Native benchmark version or purpose differs')
    else:
        raise ValueError('General user joint input is not this benchmark adapter')
    if native.get('schema') != 'bhtracker.native_joint_mass.v1' or native.get('time_coordinate') != 'JD_TDB':
        raise ValueError('Explicit versioned JD_TDB joint input required')
    photo, angular = native['photometry'], native['astrometry']
    if not photo or not angular:
        raise ValueError('Both measured channels are required')
    if len(photo) > 25000 or len(angular) > 128:
        raise ValueError('Whole input exceeds this benchmark adapter resource domain; no rows are dropped')
    for rows in (photo, angular):
        ids = [r['source_row_id'] for r in rows]
        if any(type(i) is not str or not i for i in ids) or len(set(ids)) != len(ids):
            raise ValueError('Unique explicit source-row identities required')
    for row in photo:
        for key in ('time_jd_tdb', 'magnitude', 'magnitude_error'): _finite(row[key], key)
        if row['magnitude_error'] <= 0: raise ValueError('Positive supplied photometric errors required')
    for row in angular:
        for key in ('north_mas', 'east_mas', 'north_error_mas', 'east_error_mas'): _finite(row[key], key)
        if min(row['north_error_mas'], row['east_error_mas']) <= 0:
            raise ValueError('Positive supplied angular errors required; no replacement floor')
        if not row['exposure_midpoints_jd_tdb']:
            raise ValueError('Explicit actual exposure-time samples required')
        for t in row['exposure_midpoints_jd_tdb']: _finite(t, 'exposure time')
    instruments = list(dict.fromkeys(r['instrument'] for r in photo))
    if set(instruments) != {'OGLE', 'HST_F606W', 'HST_F814W'}:
        raise ValueError('This versioned benchmark adapter requires its three explicit instrument groups')
    return {'input_sha256': digest, 'canonical_input_sha256': _sha(_encode(document)),
            'purpose': purpose, 'data_version': native['data_version'], 'photometric_rows': len(photo),
            'angular_rows': len(angular), 'instruments': instruments,
            'time_coordinate': 'JD_TDB', 'clock_or_error_corrections_added': False,
            'calibration_scope': 'Conditional working-law research; registration is not calibration', **FLAGS}


def _settings(purpose, control_registry, numerical_time_origin, angular_reference):
    return {'purpose': purpose, 'control_registry': _registry(control_registry),
            'numerical_time_origin': _finite(numerical_time_origin, 'numerical origin'),
            'angular_reference': _finite(angular_reference, 'angular reference')}


def _model(raw, settings):
    state = availability()
    if not state['available']:
        raise RuntimeError('Install the joint-research extra; missing: ' + ', '.join(state['missing_dependencies']))
    validate_benchmark(raw, purpose=settings['purpose'], control_registry=settings['control_registry'])
    from ._joint_v3.known2023_student_model_v2 import Known2023StudentModel
    from ._joint_v3.gaussian_joint_model_v4 import GaussianJointModel
    from ._joint_v3._bindings import check_live_source
    root = Path(__file__).resolve().parent / '_joint_v3'
    adapter = Known2023StudentModel(raw, purpose=settings['purpose'], expected_sha256=_sha(raw),
        core_path=root / 'core_snapshot_v2.py', student_directory=root,
        control_registry=settings['control_registry'], numerical_time_origin=settings['numerical_time_origin'],
        angular_reference=settings['angular_reference'])
    model = GaussianJointModel(adapter)
    for name, module in tuple(sys.modules.items()):
        if name.startswith(__package__ + '._joint_v3.') and getattr(module, '__file__', None):
            check_live_source(module)
    model.verify_snapshot()
    return model


def _envelope(kind, payload):
    result = {'schema': kind, 'engine': ENGINE, **payload, **FLAGS}
    result['integrity_sha256'] = _sha(_encode(result))
    return result


def _check_envelope(value, schema):
    if type(value) is not dict or value.get('schema') != schema or value.get('engine') != ENGINE:
        raise ValueError('Wrong research engine envelope')
    copy = dict(value); claimed = copy.pop('integrity_sha256', None)
    if claimed != _sha(_encode(copy)) or any(value.get(k) != v for k, v in FLAGS.items()):
        raise ValueError('Envelope integrity or scientific HOLD differs')
    if value['source_identity'] != source_identity():
        raise ValueError('Engine sources differ from the saved result')
    raw = base64.b64decode(value['input_base64'], validate=True)
    summary = validate_benchmark(raw, purpose=value['settings']['purpose'], control_registry=value['settings']['control_registry'])
    if summary != value['input_summary']:
        raise ValueError('Input summary differs')
    return raw


def evaluate_saved_state(raw, state, *, purpose, control_registry=None, zero_components=(),
                         numerical_time_origin=2455765., angular_reference=2456000.):
    """One bounded saved-state evaluation; no optimization or interval inference."""
    settings = _settings(purpose, control_registry, numerical_time_origin, angular_reference)
    summary = validate_benchmark(raw, purpose=purpose, control_registry=control_registry)
    model = _model(raw, settings)
    audit = []
    result = model.evaluate(state, zero_components=zero_components, details=True, objective_audit=audit.append)
    model.verify_snapshot(); verify_sources()
    return _saved_envelope(raw, settings, summary, model, result, audit)


def _saved_envelope(raw, settings, summary, model, result, audit):
    return _envelope('bhtracker.known_system_v3.saved_state.v1', {
        'source_identity': source_identity(), 'runtime': runtime(), 'input_summary': summary,
        'input_base64': base64.b64encode(raw).decode('ascii'), 'settings': settings,
        'result': _native(result), 'objective_stages': _native(audit),
        'observer_array_sha256': {n: _sha(getattr(model.data, n).tobytes()) for n in ('ep', 'ea', 'eref')},
        'scope': 'One saved full state with up to nine internal covariance values; no optimization or scientific acceptance'})


def verify_replay(value, *, mode='integrity'):
    """Integrity is not scientific authentication; numerical mode never optimizes."""
    if mode not in ('integrity', 'numerical'): raise ValueError('Explicit replay mode required')
    raw = _check_envelope(value, 'bhtracker.known_system_v3.saved_state.v1')
    state = value['result']['complete_evaluated_state']
    expected_names = ['t0_offset_days', 'log_tE_days', 'u0_heliocentric', 'angle_source_minus_lens_rad', 'pi_E'] + [n + '_source_fraction' for n in value['input_summary']['instruments']] + ['log_matern_sigma_mag', 'log_matern_rho_days', 'log_sho_sigma_mag', 'log_sho_omega_rad_per_day']
    if (state['parameter_names'] != expected_names or state['input_sha256'] != _sha(raw) or
            state['numerical_time_origin_jd'] != value['settings']['numerical_time_origin'] or
            state['angular_reference_jd'] != value['settings']['angular_reference'] or
            state['t0_offset_days'] != state['state'][0]):
        raise ValueError('Saved coordinate/input lineage differs')
    verification = {'mode': 'INTEGRITY_ONLY' if mode == 'integrity' else 'NUMERICAL_SAVED_STATE_REPLAY',
                    'requested_mode': mode, 'passed': True, 'optimization_calls': 0,
                    'numerical_full_states': 0, 'scope': 'Stored content consistency; not authentication or calibration'}
    if mode == 'numerical':
        if value['runtime'] != runtime():
            raise ValueError('Numerical runtime differs; cross-runtime scientific equivalence is not certified')
        replay = evaluate_saved_state(raw, state['state'], zero_components=state['zero_components'], **value['settings'])
        verification.update(passed=(_encode(replay['result']) == _encode(value['result']) and
                                   replay['observer_array_sha256'] == value['observer_array_sha256']), numerical_full_states=1,
            scope='Exact represented saved-state comparison on the recorded runtime; no minimum, coverage or recovery certification')
    return {'verification': verification, 'input_summary': value['input_summary'], **FLAGS}


def plan_run(raw, cases, *, purpose, control_registry=None, numerical_time_origin=2455765.,
             angular_reference=2456000., resources=None):
    """User-chosen states and bounded resources; creating a plan runs no model."""
    settings = _settings(purpose, control_registry, numerical_time_origin, angular_reference)
    summary = validate_benchmark(raw, purpose=purpose, control_registry=control_registry)
    if type(cases) is not list or not 1 <= len(cases) <= 128:
        raise ValueError('Explicit roster of 1..128 states required; no implicit mass seeds')
    n = 9 + len(summary['instruments']); roster = []
    for index, case in enumerate(cases):
        if type(case) is not dict or set(case) != {'state', 'zero_components'}:
            raise ValueError('Each case requires exactly state and zero_components')
        if type(case['state']) is not list or len(case['state']) != n:
            raise ValueError('State must match the declared instrument/parameter order')
        values = [_finite(v, 'state') for v in case['state']]
        zero = case['zero_components']
        if type(zero) is not list or any(z not in ('matern', 'sho') for z in zero) or len(set(zero)) != len(zero):
            raise ValueError('Distinct explicit covariance zero-components required')
        roster.append({'case_id': 'case_%04d' % index, 'state': values, 'zero_components': list(zero)})
    limits = {'max_iterations': 64, 'full_calls_per_case': 2002, 'full_calls_total': 16016,
              'covariance_calls_total': 144144, 'case_seconds': 240, 'wall_seconds': 2100,
              'max_workspace_bytes': 1073741824}
    if resources is not None:
        if type(resources) is not dict or set(resources) - set(limits): raise ValueError('Unknown resource control')
        for name, v in resources.items():
            if type(v) is not int or not 1 <= v <= limits[name]: raise ValueError('Positive resource controls may only reduce the declared caps')
            limits[name] = v
    if limits['full_calls_per_case'] < 4: raise ValueError('At least four full-state calls per case required')
    if limits['max_workspace_bytes'] < 65536: raise ValueError('At least 65536 working-evidence bytes required')
    return _envelope('bhtracker.known_system_v3.plan.v1', {'source_identity': source_identity(),
        'runtime': runtime(), 'input_summary': summary, 'input_base64': base64.b64encode(raw).decode('ascii'),
        'settings': settings, 'cases': roster, 'resources': limits,
        'method': {'projected_score_tolerance': .02, 'hessian_step': 3e-5, 'hyper_step': 2e-5,
                   'initial_radius': .5, 'maximum_radius': 4., 'promotion_objective_tolerance': 1e-7,
                   'max_probe_promotions': 8},
        'scope': 'Finite research search; explicit run action required. Stationarity is not a minimum/global/coverage certificate.'})


def _validated_plan(plan, *, require_runtime=True):
    raw = _check_envelope(plan, 'bhtracker.known_system_v3.plan.v1')
    if require_runtime and plan['runtime'] != runtime(): raise ValueError('Plan runtime changed; create a new explicit plan')
    cases = [{'state': c['state'], 'zero_components': c['zero_components']} for c in plan['cases']]
    rebuilt = plan_run(raw, cases, resources=plan['resources'], **plan['settings'])
    if not require_runtime:
        rebuilt['runtime'] = plan['runtime']
        rebuilt.pop('integrity_sha256')
        rebuilt['integrity_sha256'] = _sha(_encode(rebuilt))
    if _encode(rebuilt) != _encode(plan):
        raise ValueError('Plan method, state, domain or resource contract differs')
    return raw


def _write_new(path, value):
    with Path(path).open('xb') as stream:
        stream.write(_encode(value)); stream.flush(); os.fsync(stream.fileno())


def run_plan(plan, workspace):
    """Explicit run action in a fresh directory; installed subprocess, no retry."""
    _validated_plan(plan)
    if len(_encode(plan)) + 65536 > plan['resources']['max_workspace_bytes']:
        raise ValueError('Plan and minimum evidence reserve exceed the workspace budget')
    path = Path(workspace).resolve(); path.mkdir(parents=True, exist_ok=False)
    _write_new(path / 'PLAN.json', plan)
    env = os.environ.copy()
    for name in ('PYTHONPATH', 'PYTHONHOME'): env.pop(name, None)
    env.update(PYTHONNOUSERSITE='1', PYTHONDONTWRITEBYTECODE='1', OMP_NUM_THREADS='1',
               OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1')
    command = [sys.executable, '-I', '-B', '-m', 'bhtracker.known_system_v3', '_worker', str(path)]
    timeout = cancelled = False
    with (path / 'worker.stdout.log').open('xb') as stdout, (path / 'worker.stderr.log').open('xb') as stderr:
        process = subprocess.Popen(command, cwd=path, env=env, stdout=stdout, stderr=stderr)
        try: code = process.wait(timeout=plan['resources']['wall_seconds'] + 60)
        except subprocess.TimeoutExpired:
            process.kill(); code = process.wait(); timeout = True
        except KeyboardInterrupt:
            cancelled = True
            process.terminate()
            try: code = process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill(); code = process.wait(timeout=5)
    records = []
    for case in plan['cases']:
        item = path / (case['case_id'] + '.json')
        if item.exists():
            row = _parse(_read_file(item))
            if row.get('case_id') != case['case_id'] or row.get('state') != case['state'] or row.get('zero_components') != case['zero_components']:
                raise ValueError('Worker case identity differs')
            records.append({'case_id': case['case_id'], 'status': row['status'],
                            'file': item.name, **_file_record(item),
                            'full_calls': row.get('full_calls'), 'covariance_calls': row.get('covariance_calls')})
        else:
            records.append({**case, 'status': 'UNKNOWN_CANCELLED' if cancelled else 'UNKNOWN_NOT_COMPLETED'})
    result = {'schema': 'bhtracker.known_system_v3.run.v1', 'engine': ENGINE, 'plan_sha256': _sha(_encode(plan)),
              'worker_returncode': code, 'timeout': timeout, 'cancelled': cancelled,
              'status': 'CANCELLED_PARTIAL' if cancelled else 'STOPPED_PARTIAL' if timeout or code else 'FINITE_EXECUTION_RETURNED',
              'cases': records,
              'source_identity': source_identity(), 'scope': 'Finite bounded search; all failures/unattempted cases retained', **FLAGS}
    _write_new(path / 'RUN.json', result)
    return result


def export_workspace(workspace, output, *, max_archive_bytes=ARCHIVE_LIMIT):
    """Bounded file export; no execution or arbitrary directory traversal."""
    path = Path(workspace).resolve(); destination = Path(output).resolve()
    if destination.exists() or destination.is_relative_to(path):
        raise ValueError('Choose a new archive outside the workspace')
    if type(max_archive_bytes) is not int or not 1 <= max_archive_bytes <= ARCHIVE_LIMIT:
        raise ValueError('Explicit archive cap up to 512 MiB required')
    plan = _parse(_read_file(path / 'PLAN.json')); _check_envelope(plan, 'bhtracker.known_system_v3.plan.v1')
    names = ['PLAN.json', 'RUN.json', 'WORKER.json', 'ALL_OBJECTIVE_STAGES.jsonl', 'worker.stdout.log', 'worker.stderr.log'] + [c['case_id'] + '.json' for c in plan['cases']]
    roster = []
    for name in names:
        file = path / name
        if file.is_symlink(): raise ValueError('Symlink workspace member is unsupported')
        if file.is_file(): roster.append({'path': name, **_file_record(file)})
    if 'RUN.json' not in {r['path'] for r in roster}: raise ValueError('Export requires a terminal run')
    manifest_blob = _encode({'schema': 'bhtracker.known_system_v3.export.v1', 'files': roster, **FLAGS})
    if (any(r['path'].endswith('.json') and r['bytes'] > STRUCTURE_LIMIT for r in roster) or
            len(manifest_blob) > STRUCTURE_LIMIT or sum(r['bytes'] for r in roster) + len(manifest_blob) > EXPANDED_LIMIT):
        raise ValueError('Workspace exceeds the verifier expanded/structured-content limits; no archive written')
    try:
        with zipfile.ZipFile(destination, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=5) as archive:
            for record in roster:
                archive.write(path / record['path'], record['path'])
                if destination.stat().st_size > max_archive_bytes: raise ValueError('Archive exceeds declared cap; workspace preserved')
            archive.writestr('MANIFEST.json', manifest_blob)
        if destination.stat().st_size > max_archive_bytes: raise ValueError('Archive exceeds declared cap; workspace preserved')
    except Exception:
        # A partial export remains available as evidence; never overwrite it.
        raise
    return {'path': str(destination), **_file_record(destination),
            'scope': 'Content transport, not scientific authentication', **FLAGS}


def replay_export(archive_path, *, mode='integrity', max_saved_states=16, wall_seconds=120):
    """Read a bounded allowlisted archive without extraction or executing code.

    Numerical mode re-evaluates saved own states only. Budget omissions are
    explicit UNKNOWN records and make complete verification false.
    """
    if mode not in ('integrity', 'numerical'): raise ValueError('Explicit replay mode required')
    if type(max_saved_states) is not int or not 1 <= max_saved_states <= 256:
        raise ValueError('Saved-state replay budget must be 1..256')
    if type(wall_seconds) is not int or not 1 <= wall_seconds <= 120:
        raise ValueError('Replay cooperative time budget must be 1..120 seconds')
    file = Path(archive_path)
    if file.stat().st_size > ARCHIVE_LIMIT: raise ValueError('Archive exceeds 512 MiB')
    started = time.monotonic(); outcomes = []; evaluated = 0
    with zipfile.ZipFile(file) as archive:
        members = archive.infolist(); names = [m.filename for m in members]
        if len(names) != len(set(names)) or len(names) > 135 or sum(m.file_size for m in members) > EXPANDED_LIMIT:
            raise ValueError('Duplicate members or expanded archive limit exceeded')
        if any(m.flag_bits & 1 or m.is_dir() or m.filename != Path(m.filename).name or
               ((m.external_attr >> 16) & 0o170000) not in (0, 0o100000) for m in members):
            raise ValueError('Only unencrypted regular allowlisted members are supported')
        def read_json(name):
            if archive.getinfo(name).file_size > STRUCTURE_LIMIT: raise ValueError('Structured member exceeds limit')
            return _parse(archive.read(name))
        manifest = read_json('MANIFEST.json')
        if manifest.get('schema') != 'bhtracker.known_system_v3.export.v1' or any(manifest.get(k) != v for k, v in FLAGS.items()):
            raise ValueError('Wrong export manifest or scientific HOLD')
        plan = read_json('PLAN.json'); _validated_plan(plan, require_runtime=False)
        allowed = {'PLAN.json', 'RUN.json', 'WORKER.json', 'ALL_OBJECTIVE_STAGES.jsonl', 'worker.stdout.log', 'worker.stderr.log'} | {c['case_id'] + '.json' for c in plan['cases']}
        records = manifest['files']; recorded = [r['path'] for r in records]
        if len(recorded) != len(set(recorded)) or set(recorded) != set(names) - {'MANIFEST.json'} or set(recorded) - allowed:
            raise ValueError('Manifest/member allowlist differs')
        for record in records:
            digest = hashlib.sha256(); size = 0
            with archive.open(record['path']) as stream:
                for block in iter(lambda: stream.read(1048576), b''):
                    size += len(block); digest.update(block)
            if size != record['bytes'] or digest.hexdigest() != record['sha256']:
                raise ValueError('Export member hash differs: ' + record['path'])
        run = read_json('RUN.json')
        if (run.get('schema') != 'bhtracker.known_system_v3.run.v1' or run.get('engine') != ENGINE or
                run.get('source_identity') != source_identity() or run.get('plan_sha256') != _sha(_encode(plan)) or
                any(run.get(k) != v for k, v in FLAGS.items())):
            raise ValueError('Run/plan identity or scientific HOLD differs')
        for case in plan['cases']:
            name = case['case_id'] + '.json'
            if name not in recorded:
                outcomes.append({'case_id': case['case_id'], 'status': 'UNKNOWN_NOT_COMPLETED'}); continue
            item = read_json(name)
            if any(item.get(k) != case[k] for k in ('case_id', 'state', 'zero_components')):
                raise ValueError('Saved case identity differs')
            for saved in item.get('replayed_states', []):
                label = {'case_id': case['case_id'], 'role': saved['role']}
                envelope = saved['saved_state']
                if (any(envelope.get(k) != plan[k] for k in
                        ('input_base64', 'input_summary', 'settings', 'runtime', 'source_identity')) or
                        envelope.get('result', {}).get('complete_evaluated_state', {}).get('zero_components') != case['zero_components']):
                    raise ValueError('Saved state is not bound to the enclosing plan input/settings/runtime/case face')
                if mode == 'numerical' and (evaluated >= max_saved_states or time.monotonic() - started >= wall_seconds):
                    outcomes.append({**label, 'status': 'UNKNOWN_REPLAY_BUDGET'}); continue
                if mode == 'numerical': evaluated += 1  # Count attempts even when a provider refuses.
                try:
                    verification = verify_replay(saved['saved_state'], mode=mode)
                    late = time.monotonic() - started >= wall_seconds
                    outcomes.append({**label, 'status': 'UNKNOWN_REPLAY_DEADLINE' if late else
                        'PASS' if verification['verification']['passed'] else 'FAILED_OR_UNRESOLVED',
                        'verification': verification, 'computed_result_after_deadline': late})
                except (ValueError, RuntimeError, FloatingPointError) as exc:
                    outcomes.append({**label, 'status': 'FAILED_OR_UNRESOLVED', 'error_type': type(exc).__name__, 'error': str(exc)})
            if not item.get('replayed_states'):
                outcomes.append({'case_id': case['case_id'], 'status': 'UNKNOWN_NO_SAVED_OWN_STATE'})
    deadline_exceeded = time.monotonic() - started >= wall_seconds
    return {'verification': {'mode': 'INTEGRITY_ONLY' if mode == 'integrity' else 'NUMERICAL_SAVED_STATE_REPLAY',
            'requested_mode': mode, 'passed': bool(outcomes) and not deadline_exceeded and all(r['status'] == 'PASS' for r in outcomes),
            'archive_integrity_passed': True, 'numerical_full_state_attempts': evaluated, 'optimization_calls': 0,
            'deadline_exceeded': deadline_exceeded,
            'scope': 'Allowlisted content and bounded saved-state replay; no refitting, minimum, coverage or scientific authentication'},
            'outcomes': outcomes, **FLAGS}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('inspect')
    for name in ('validate', 'evaluate', 'plan'):
        p = sub.add_parser(name); p.add_argument('input', type=Path)
        p.add_argument('--purpose', choices=['AUTHENTIC2023', 'WHOLLY_INVENTED', 'ACTUAL_CADENCE_CONTROL'], required=True)
        p.add_argument('--registry', type=Path); p.add_argument('--output', type=Path)
        if name == 'evaluate': p.add_argument('--state', type=Path, required=True)
        if name == 'plan': p.add_argument('--cases', type=Path, required=True)
    p = sub.add_parser('run'); p.add_argument('plan', type=Path); p.add_argument('--workspace', type=Path, required=True)
    p = sub.add_parser('replay'); p.add_argument('result', type=Path); p.add_argument('--mode', choices=['integrity', 'numerical'], required=True)
    p = sub.add_parser('export'); p.add_argument('workspace', type=Path); p.add_argument('--output', type=Path, required=True)
    p.add_argument('--max-archive-bytes', type=int, default=ARCHIVE_LIMIT)
    p = sub.add_parser('_worker'); p.add_argument('workspace', type=Path)
    args = parser.parse_args(argv)
    if args.command == '_worker':
        from ._joint_v3._run import worker
        return worker(args.workspace)
    if args.command == 'inspect': result = availability()
    elif args.command in ('validate', 'evaluate', 'plan'):
        raw = _read_file(args.input, INPUT_LIMIT); registry = _parse(_read_file(args.registry)) if args.registry else None
        options = {'purpose': args.purpose, 'control_registry': registry}
        if args.command == 'validate': result = validate_benchmark(raw, **options)
        elif args.command == 'evaluate':
            spec = _parse(_read_file(args.state)); result = evaluate_saved_state(raw, spec['state'], zero_components=spec['zero_components'], **options)
        else: result = plan_run(raw, _parse(_read_file(args.cases)), **options)
    elif args.command == 'run': result = run_plan(_parse(_read_file(args.plan)), args.workspace)
    elif args.command == 'replay':
        result = replay_export(args.result, mode=args.mode) if zipfile.is_zipfile(args.result) else verify_replay(_parse(_read_file(args.result)), mode=args.mode)
    else: result = export_workspace(args.workspace, args.output, max_archive_bytes=args.max_archive_bytes)
    if getattr(args, 'output', None) and args.command != 'export': _write_new(args.output, result)
    else: print(_encode(result).decode('utf-8'), end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
