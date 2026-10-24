"""Bounded one-family point campaign; fresh output and separate native admission.

This supervisor never admits scientific mass/BH acceptance. Native/actual-cadence
execution requires an independently reviewed prospective freeze and root receipt.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read_json(path):
    raw = Path(path).read_bytes()
    return raw, json.loads(raw.decode('utf-8'), parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON: ' + x)))

def plain(value):
    if hasattr(value, 'tolist'):
        return plain(value.tolist())
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError('Nonfinite output is unavailable, not a valid numeric result')
    return value

def write_new(path, data):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(plain(data), stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())

def expired(started, seconds, now=None):
    return (time.monotonic() if now is None else now) - started >= seconds

class AuditFailure(RuntimeError):
    pass

class JournalLatch:
    """A missing trial is a permanent numerical failure, never a retry condition."""
    def __init__(self, stream, max_bytes):
        self.stream, self.max_bytes = stream, max_bytes
        self.failure = None
        self.unrecorded_event = None

    def before_model_call(self):
        if self.failure is not None:
            raise AuditFailure('No further model calls after audit failure: ' + self.failure)

    def append(self, record):
        self.before_model_call()
        try:
            data = json.dumps(plain(record), separators=(',', ':'), allow_nan=False) + '\n'
            if self.stream.tell() + len(data.encode('utf-8')) > self.max_bytes:
                raise AuditFailure('Declared evaluation journal budget exhausted')
            self.stream.write(data)
            self.stream.flush()
        except Exception as exc:
            self.failure = type(exc).__name__ + ': ' + str(exc)
            self.unrecorded_event = record
            raise AuditFailure(self.failure) from exc

    def permits_resolution(self):
        return self.failure is None

def relative_heights(endpoints):
    """Likelihood heights only; neither probability masses nor mode weights."""
    if not endpoints:
        return []
    best = min(float(r['deviance']) for r in endpoints)
    return [{'start_index': r['start_index'], 'phase': r['phase'],
             'deviance': r['deviance'], 'numerically_eligible': r['numerically_eligible'],
             'log_relative_likelihood_height': -.5 * (float(r['deviance']) - best)}
            for r in endpoints]

def validated_start_record(candidate, index, purpose, input_sha256):
    if not isinstance(candidate, dict) or type(candidate.get('start_index')) is not int or candidate['start_index'] != index or candidate.get('purpose') != purpose or candidate.get('input_sha256') != input_sha256:
        raise ValueError('Worker terminal identity mismatch')
    return candidate

def validated_point_outcome(candidate, purpose, input_sha256):
    if not isinstance(candidate, dict) or candidate.get('schema') != 'bhsm.known2023.ST6.point_outcome.v1' or candidate.get('purpose') != purpose or candidate.get('input_sha256') != input_sha256:
        raise ValueError('Worker outcome identity mismatch')
    if 'accepted_mass_interval' not in candidate or candidate['accepted_mass_interval'] is not None or candidate.get('known_black_hole_recovery_accepted') is not False:
        raise ValueError('Point campaign cannot assert accepted physical recovery')
    records = candidate.get('all16_starts')
    if not isinstance(records, list) or len(records) != 16:
        raise ValueError('Every frozen start requires a terminal record')
    for k, record in enumerate(records):
        validated_start_record(record, k, purpose, input_sha256)
    return candidate

def binding(path, expected):
    raw, freeze = read_json(path)
    if digest(raw) != expected:
        raise ValueError('Prospective freeze changed')
    for record in freeze['source_files']:
        data = Path(record['path']).read_bytes()
        if len(data) != record['bytes'] or digest(data) != record['sha256']:
            raise ValueError('Pinned scientific source changed: ' + record['path'])
    data = Path(freeze['input']['path']).read_bytes()
    if len(data) != freeze['input']['bytes'] or digest(data) != freeze['input']['sha256']:
        raise ValueError('Frozen campaign input differs')
    if freeze['configuration']['starts'] != 16 or freeze['configuration']['candidate'] != 'ST6_SEEING':
        raise ValueError('Unreviewed candidate/seed count')
    if freeze['purpose'] not in ('WHOLLY_INVENTED', 'AUTHENTIC2023', 'ACTUAL_CADENCE_CONTROL'):
        raise ValueError('Explicit registered purpose required')
    return freeze, data

def admission(args, freeze):
    if freeze['purpose'] == 'WHOLLY_INVENTED':
        if freeze.get('native_fit_admitted') is not False:
            raise ValueError('Wholly invented freeze must state no native admission')
        return None
    if args.admission is None or args.admission_sha256 is None:
        raise ValueError('Separate exact root execution-admission receipt required')
    raw, record = read_json(args.admission)
    if digest(raw) != args.admission_sha256 or record.get('schema') != 'bhsm.known2023.native_execution_admission.v1':
        raise ValueError('Execution admission differs')
    if record.get('execution_admitted') is not True or record.get('purpose') != freeze['purpose'] or record.get('prospective_freeze_sha256') != args.freeze_sha256 or record.get('input_sha256') != freeze['input']['sha256']:
        raise ValueError('Execution admission does not bind this exact purpose/source/input')
    peer = record['independent_review']
    if digest(Path(peer['path']).read_bytes()) != peer['sha256']:
        raise ValueError('Independent review receipt changed')
    return record

def worker(args, freeze, raw, initial):
    # Imports happen only after complete source/input/admission checks.
    import numpy as np
    import scipy
    import astropy
    from scipy.optimize import minimize
    from known2023_student_model_v1 import Known2023StudentModel
    from periodic_chart_v1 import native_from_chart, chart_seed
    from bounded_trust_polish_v1 import polish_score
    out = args.output
    config = freeze['configuration']
    actual_runtime = {'python': sys.version.split()[0], 'numpy': np.__version__, 'scipy': scipy.__version__, 'astropy': astropy.__version__}
    if actual_runtime != freeze['runtime']:
        raise ValueError('Runtime differs from the exact reviewed campaign: ' + repr(actual_runtime))
    registry = {}
    if freeze.get('control_registry'):
        record = freeze['control_registry']
        registry_raw, registry = read_json(record['path'])
        if digest(registry_raw) != record['sha256']:
            raise ValueError('Control registry changed')
    model = Known2023StudentModel(raw, purpose=freeze['purpose'], expected_sha256=freeze['input']['sha256'],
        core_path=freeze['core_path'], student_directory=freeze['student_directory'], control_registry=registry,
        numerical_time_origin=config['numerical_time_origin_jd_tdb'], angular_reference=config['angular_reference_jd_tdb'])
    seeds = list(model.seeds())
    if len(seeds) != 16:
        raise ValueError('All16 frozen sign/angle seed modes are mandatory')
    write_new(out / 'SEEDS_AND_DOMAIN_v1.json', {'seeds': seeds, 'lower': model.lower, 'upper': model.upper, 'scales': model.scales, 'parameter_names': model.parameter_names, 'purpose': freeze['purpose'], 'reference_is_not_a_prior': True})
    zlower, zupper = model.lower / model.scales, model.upper / model.scales
    scalar_count = len(model.tp) + len(model.ya)
    journal_path = out / 'ALL_EVALUATIONS_v1.jsonl'
    records, trials, endpoints, all_endpoints = [], [], [], []
    calls = optimizer_model_calls = endpoint_model_calls = 0
    with journal_path.open('x', encoding='utf-8', newline='\n') as journal:
        audit = JournalLatch(journal, config['journal_max_bytes'])
        def event(record):
            audit.append(record)

        def map_state(z, free_angle=False):
            z = np.asarray(z, dtype=float)
            x = z * model.scales
            for j in range(len(x)):
                if j==3:
                    continue
                if z[j] == zlower[j]:
                    x[j] = model.lower[j]
                elif z[j] == zupper[j]:
                    x[j] = model.upper[j]
            inside=[model.lower[j]<=x[j]<=model.upper[j] for j in range(len(x)) if j!=3]
            if not np.isfinite(x).all() or not all(inside) or (not free_angle and not -np.pi<=x[3]<=np.pi):
                raise ValueError('Numerical proposal cannot be represented in exact domain; no interior snapping')
            return x

        def score(x, gradient):
            value = np.asarray(gradient) * model.scales
            for j in range(len(value)):
                if j == 3:  # Angle is periodic, not a physical one-sided edge.
                    continue
                if (x[j] == model.lower[j] and value[j] > 0) or (x[j] == model.upper[j] and value[j] < 0):
                    value[j] = 0.
            return float(np.max(np.abs(value)))

        for k, seed in enumerate(seeds):
            started = time.monotonic()
            start_record = {'start_index': k, 'seed': seed, 'phases': [], 'purpose': freeze['purpose'], 'input_sha256': freeze['input']['sha256']}
            current,chart_center = chart_seed(seed)
            start_record['chart_center_angle_rad']=chart_center
            for phase, method, iterations, normalized in (
                ('LBFGSB_SCALED', 'L-BFGS-B', 600, True),
                ('SLSQP_SCALED', 'SLSQP', 800, True),
                ('LBFGSB_FULL_DEVIANCE_POLISH', 'L-BFGS-B', 400, False),
                ('GRADIENT_TRUST_POLISH', 'SCORE_NEWTON', 16, False),
            ):
                phase_path = out / f'start_{k:02d}_{phase}.json'
                if not audit.permits_resolution():
                    record = {'start_index': k, 'phase': phase, 'status': 'NOT_RUN_LATCHED_JOURNAL_AUDIT_FAILURE', 'numerically_eligible': False, 'audit_failure': audit.failure}
                    start_record['phases'].append(record); write_new(phase_path, record)
                    continue
                if expired(initial, config['worker_wall_seconds']) or expired(started, config['per_start_wall_seconds']):
                    record = {'start_index': k, 'phase': phase, 'status': 'NOT_RUN_DECLARED_WALL_BUDGET'}
                    start_record['phases'].append(record); write_new(phase_path, record)
                    continue
                model.verify_snapshot()
                last_valid = None
                phase_evals = 0
                def evaluate(z):
                    nonlocal calls, last_valid, phase_evals, optimizer_model_calls
                    if expired(initial, config['worker_wall_seconds']) or expired(started, config['per_start_wall_seconds']):
                        raise TimeoutError('Declared point/start wall budget')
                    calls += 1; phase_evals += 1
                    x = None
                    try:
                        chart_state = map_state(z, free_angle=method=='SCORE_NEWTON')
                        x = native_from_chart(chart_state,chart_center,model.lower,model.upper)
                        audit.before_model_call()
                        optimizer_model_calls += 1
                        value = model.evaluate(x)
                    except Exception as exc:
                        event({'event': 'EVALUATION_FAILED', 'call': calls, 'start_index': k, 'phase': phase, 'raw_scaled_state': z, 'physical_state': x, 'error_type': type(exc).__name__, 'error': str(exc)})
                        raise
                    full_score = score(x, value['gradient'])
                    row = {'event': 'VALID_EVALUATION', 'call': calls, 'start_index': k, 'phase': phase, 'raw_scaled_state': z, 'chart_state': chart_state, 'chart_center_angle_rad': chart_center, 'physical_state': x, 'deviance': value['negative_two_log_likelihood'], 'full_gradient': value['gradient'], 'full_scaled_projected_score': full_score, 'linear_profile_identified': value['linear_profile_identified'], 'linear_profile_rank': value['linear_profile_rank'], 'linear_profile_projected_score': value['linear_profile_projected_score'], 'feature_knots': value['feature_knot_source_ids']}
                    trials.append({'deviance': row['deviance'], 'call': calls})
                    last_valid = (chart_state.copy(), value)
                    event(row)
                    divisor = scalar_count if normalized else 1.
                    return value['negative_two_log_likelihood'] / divisor, value['gradient'] * model.scales / divisor
                try:
                    options = {'maxiter': iterations, 'ftol': 1e-12}
                    if method == 'L-BFGS-B':
                        options.update(gtol=1e-8 if normalized else 1e-6, maxls=50, maxfun=4 * iterations)
                        if not normalized:
                            options['ftol'] = 2.3e-15
                    polish=None
                    if method=='SCORE_NEWTON':
                        plo,phi=model.lower.copy(),model.upper.copy();plo[3],phi[3]=-np.inf,np.inf
                        def native_chart_score(point):
                            d,g=evaluate(point/model.scales)
                            return d,g/model.scales
                        polish=polish_score(native_chart_score,current,plo,phi,model.scales,max_iterations=16,score_tolerance=.02,difference_step=1e-4,max_scaled_step=1.)
                        current=map_state(polish['state']/model.scales,free_angle=True)
                        optimizer_success=bool(polish['declared_score_reached']);message=polish['status']
                    else:
                        result = minimize(evaluate, current / model.scales, jac=True, method=method, bounds=list(zip(zlower, zupper)), options=options)
                        current = map_state(result.x)
                        optimizer_success=bool(result.success);message=str(result.message)
                    if expired(initial, config['worker_wall_seconds']) or expired(started, config['per_start_wall_seconds']):
                        raise TimeoutError('Declared point/start wall budget before endpoint re-evaluation')
                    audit.before_model_call()
                    endpoint_model_calls += 1
                    native=native_from_chart(current,chart_center,model.lower,model.upper)
                    detail = model.evaluate(native, details=True)
                    endpoint_score = score(native, detail['gradient'])
                    eligible = endpoint_score <= .02 and detail['linear_profile_identified'] and not detail['feature_knot_source_ids']
                    record = {'start_index': k, 'phase': phase, 'status': 'RETURNED', 'optimizer_success': optimizer_success, 'message': message, 'evaluations': phase_evals, 'state': native, 'chart_state': current, 'chart_center_angle_rad': chart_center, 'gradient_trust_polish': polish, 'deviance': detail['negative_two_log_likelihood'], 'full_scaled_projected_score': endpoint_score, 'numerically_eligible': bool(eligible), 'detail': detail}
                    record['exact_nonlinear_analysis_contacts'] = [{'parameter': model.parameter_names[j], 'side': 'LOWER' if native[j] == model.lower[j] else 'UPPER', 'role': 'PERIODIC_ANGLE_SEAM' if j == 3 else 'DECLARED_ANALYSIS_DOMAIN_NOT_PHYSICAL_CONFIDENCE_LIMIT'} for j in range(len(native)) if native[j] == model.lower[j] or native[j] == model.upper[j]]
                    record['linear_analysis_contacts'] = detail['linear_profile']['active_bounds']
                    record['individual_parameter_identifiability'] = 'NOT_CERTIFIED_BY_POINT_STATIONARITY'
                    all_endpoints.append(record)
                    trials.append({'deviance': record['deviance'], 'endpoint_start_index': k, 'endpoint_phase': phase})
                    if eligible:
                        endpoints.append(record)
                except Exception as exc:
                    record = {'start_index': k, 'phase': phase, 'status': 'PHASE_FAILED', 'error_type': type(exc).__name__, 'error': str(exc), 'evaluations': phase_evals, 'last_valid_state': last_valid[0] if last_valid is not None else None, 'last_valid_deviance': last_valid[1]['negative_two_log_likelihood'] if last_valid is not None else None, 'numerically_eligible': False}
                    if last_valid is not None:
                        current = last_valid[0].copy()
                model.verify_snapshot()
                write_new(phase_path, record)
                start_record['phases'].append({j: v for j, v in record.items() if j != 'detail'})
            start_record['has_eligible_endpoint'] = any(p.get('numerically_eligible') is True for p in start_record['phases'])
            records.append(start_record)
            write_new(out / f'start_{k:02d}_terminal.json', start_record)
        selected = min(endpoints, key=lambda r: (r['deviance'], r['full_scaled_projected_score'], r['start_index'], r['phase'])) if endpoints else None
        all_starts_eligible = all(r['has_eligible_endpoint'] for r in records) and len(records) == 16
        lower = []
        if selected is not None:
            tolerance = 1e-8 * max(1., abs(selected['deviance']))
            lower = [r for r in trials if r['deviance'] < selected['deviance'] - tolerance]
        resolved = selected is not None and all_starts_eligible and not lower and audit.permits_resolution()
        model.verify_snapshot()
        outcome = {'schema': 'bhsm.known2023.ST6.point_outcome.v1', 'purpose': freeze['purpose'], 'input_sha256': freeze['input']['sha256'], 'status': 'NUMERICAL_POINT_RESOLVED_CONDITIONAL_ONLY' if resolved else 'NUMERICALLY_UNRESOLVED', 'all16_starts': records, 'all_starts_have_eligible_endpoint': all_starts_eligible, 'eligible_endpoints': len(endpoints), 'all_phase_endpoint_relative_likelihood_heights': relative_heights(all_endpoints), 'heights_are_not_mode_probabilities_or_posterior_weights': True, 'known_lower_feasible_trials': lower, 'total_optimizer_objective_attempts': calls, 'model_call_counts': {'optimizer': optimizer_model_calls, 'endpoint': endpoint_model_calls}, 'completed_endpoint_re_evaluations': len(all_endpoints), 'elapsed_seconds': time.monotonic() - initial, 'selected': selected, 'accepted_mass_interval': None, 'known_black_hole_recovery_accepted': False, 'adequacy': 'NOT_REFIT_CALIBRATED', 'coverage': 'NOT_CALIBRATED', 'qualification': 'A conditional point and one numerical control cannot establish observational adequacy or mass interval coverage. All failed starts/phases and lower trials remain. No literature mass was fitted.'}
        outcome['journal_audit_failure'] = audit.failure
        outcome['unrecorded_event_retained_outside_exhausted_journal'] = audit.unrecorded_event
        outcome['numerical_method']='SEED_CENTERED_FULL2PI_CHART_AND_FIXED_GRADIENT_TRUST_POLISH_v1'
        write_new(out / 'POINT_OUTCOME_v1.json', outcome)
    return 0

def main():
    initial = time.monotonic()  # Includes parsing/binding/preflight and setup.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', type=Path, required=True)
    parser.add_argument('--freeze-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--admission', type=Path)
    parser.add_argument('--admission-sha256')
    parser.add_argument('--_worker', action='store_true')
    args = parser.parse_args()
    freeze, raw = binding(args.freeze, args.freeze_sha256)
    admission(args, freeze)
    if args._worker:
        return worker(args, freeze, raw, initial)
    # Refusal of an old directory cannot modify it or enter a fallback writer.
    args.output.mkdir(parents=False, exist_ok=False)
    write_new(args.output / 'ALL16_INITIAL_LEDGER_v1.json', [{'start_index': k, 'status': 'NOT_STARTED', 'purpose': freeze['purpose'], 'input_sha256': freeze['input']['sha256']} for k in range(16)])
    with (args.output / 'input.original.json').open('xb') as stream:
        stream.write(raw)
    with (args.output / 'freeze.original.json').open('xb') as stream:
        stream.write(args.freeze.read_bytes())
    cmd = [sys.executable, '-B', str(Path(__file__).resolve()), '--_worker', '--freeze', str(args.freeze), '--freeze-sha256', args.freeze_sha256, '--output', str(args.output)]
    if args.admission:
        cmd += ['--admission', str(args.admission), '--admission-sha256', args.admission_sha256]
    env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONNOUSERSITE='1')
    env.pop('PYTHONPATH', None)
    timed_out = False
    with (args.output / 'worker.stdout.log').open('xb') as stdout, (args.output / 'worker.stderr.log').open('xb') as stderr:
        if expired(initial, freeze['configuration']['supervisor_wall_seconds']):
            write_new(args.output / 'SUPERVISOR_TERMINAL_v1.json', {'schema': 'bhsm.known2023.ST6.point_supervisor.v1', 'purpose': freeze['purpose'], 'input_sha256': freeze['input']['sha256'], 'execution_complete': False, 'status': 'NOT_STARTED_PREFLIGHT_WALL_BUDGET', 'accepted_mass_interval': None, 'known_black_hole_recovery_accepted': False})
            return 1
        process = subprocess.Popen(cmd, stdout=stdout, stderr=stderr, env=env, cwd=Path(__file__).resolve().parent)
        while process.poll() is None:
            if expired(initial, freeze['configuration']['supervisor_wall_seconds']):
                timed_out = True
                process.kill()
                break
            time.sleep(.1)
        returncode = process.wait()
    integrity_error = None
    try:
        binding(args.freeze, args.freeze_sha256)
    except Exception as exc:
        integrity_error = type(exc).__name__ + ': ' + str(exc)
    exists = (args.output / 'POINT_OUTCOME_v1.json').exists()
    terminal_ledger = []
    for k in range(16):
        path = args.output / f'start_{k:02d}_terminal.json'
        record = {'start_index': k, 'status': 'NOT_COMPLETED_WORKER_FAILURE', 'purpose': freeze['purpose'], 'input_sha256': freeze['input']['sha256']}
        if path.exists():
            try:
                _, candidate = read_json(path)
                record = validated_start_record(candidate, k, freeze['purpose'], freeze['input']['sha256'])
            except Exception as exc:
                record.update(status='INVALID_WORKER_TERMINAL_RETAINED', error_type=type(exc).__name__, error=str(exc))
        terminal_ledger.append(record)
    write_new(args.output / 'ALL16_FINAL_LEDGER_v1.json', terminal_ledger)
    if exists:
        try:
            _, result = read_json(args.output / 'POINT_OUTCOME_v1.json')
            validated_point_outcome(result, freeze['purpose'], freeze['input']['sha256'])
        except Exception as exc:
            integrity_error = (integrity_error or '') + '; INVALID_POINT_OUTCOME: ' + type(exc).__name__ + ': ' + str(exc)
    receipt = {'schema': 'bhsm.known2023.ST6.point_supervisor.v1', 'purpose': freeze['purpose'], 'input_sha256': freeze['input']['sha256'], 'prospective_freeze_sha256': args.freeze_sha256, 'worker_returncode': returncode, 'hard_worker_timeout': timed_out, 'source_integrity_error': integrity_error, 'point_outcome_present': exists, 'execution_complete': returncode == 0 and not timed_out and integrity_error is None and exists, 'accepted_mass_interval': None, 'known_black_hole_recovery_accepted': False, 'elapsed_seconds': time.monotonic() - initial}
    write_new(args.output / 'SUPERVISOR_TERMINAL_v1.json', receipt)
    print(json.dumps(receipt))
    return 0 if receipt['execution_complete'] else 1

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise
