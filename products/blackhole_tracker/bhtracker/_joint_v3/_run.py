"""Owned finite research worker; all objective attempts are durably recorded."""
import math
from pathlib import Path
import os
import time


def worker(workspace):
    from .. import known_system_v3 as api
    import numpy as np
    from .periodic_chart_v1 import native_from_chart
    from .bounded_negative_curvature_trust_v6 import minimize
    path = Path(workspace).resolve()
    plan = api._parse((path / 'PLAN.json').read_bytes())
    raw = api._validated_plan(plan)
    limits = plan['resources']; started = time.monotonic()
    full_count = covariance_count = 0
    written = (path / 'PLAN.json').stat().st_size
    failure = None; rows = []
    journal = (path / 'ALL_OBJECTIVE_STAGES.jsonl').open('xb')

    def save_event(event):
        nonlocal written, failure
        if failure is not None: raise OSError(failure)
        try:
            blob = api._encode(event)
            if written + len(blob) > limits['max_workspace_bytes']:
                raise OSError('Declared audit/result storage capacity reached')
            journal.write(blob); journal.flush(); os.fsync(journal.fileno()); written += len(blob)
        except Exception as exc:
            failure = type(exc).__name__ + ': ' + str(exc)
            raise

    def global_guard():
        if failure is not None: raise OSError(failure)
        if time.monotonic() - started >= limits['wall_seconds']:
            raise TimeoutError('Declared whole-worker time reached')

    try:
        global_guard(); save_event({'stage': 'MODEL_CONSTRUCTION_PLANNED', 'input_sha256': api._sha(raw)})
        model = api._model(raw, plan['settings'])
        global_guard(); save_event({'stage': 'MODEL_CONSTRUCTION_RETURNED',
            'input_sha256': api._sha(raw), 'parameter_names': list(model.parameter_names),
            'observer_array_sha256': {n: api._sha(getattr(model.data, n).tobytes()) for n in ('ep', 'ea', 'eref')}})
        for spec in plan['cases']:
            case_started = time.monotonic(); case_calls = case_covariances = 0
            replays = []; trials = []; first = None
            row = {**spec, 'status': 'UNKNOWN_NOT_STARTED', **api.FLAGS}

            def wall_guard():
                global_guard()
                if time.monotonic() - case_started >= limits['case_seconds']:
                    raise TimeoutError('Declared case time reached')

            def full_guard():
                wall_guard()
                if case_calls >= limits['full_calls_per_case'] or full_count >= limits['full_calls_total']:
                    raise RuntimeError('Declared full-state evaluation count reached')

            try:
                full_guard(); model.verify_snapshot(); api.verify_sources()
                zero = tuple(spec['zero_components'])
                active = np.asarray(model.active_optimizer_indices(zero), dtype=int)
                physical_start = np.asarray(spec['state'], dtype=float)
                base = physical_start.copy(); center = float(base[3]); base[3] = 0.
                lo, hi = model.lower.copy(), model.upper.copy(); lo[3], hi[3] = -math.pi, math.pi

                def physical_evaluation(physical, role):
                    nonlocal full_count, covariance_count, case_calls, case_covariances
                    full_guard(); full_count += 1; case_calls += 1
                    context = {'case_id': spec['case_id'], 'full_call': full_count,
                               'case_call': case_calls, 'role': role}
                    save_event({**context, 'stage': 'FULL_PLANNED', 'state': physical.tolist()})
                    local_audit = []
                    def audit(event):
                        nonlocal covariance_count, case_covariances
                        if event['stage'] == 'PLANNED':
                            wall_guard()
                            if covariance_count >= limits['covariance_calls_total']:
                                save_event({**context, **event, 'stage': 'NOT_STARTED_BUDGET'})
                                raise RuntimeError('Declared covariance evaluation count reached')
                            covariance_count += 1; case_covariances += 1
                        save_event({**context, **event})
                        local_audit.append(event)
                        if event['stage'] == 'PLANNED':
                            try: wall_guard()
                            except Exception:
                                save_event({**context, **event, 'stage': 'ABORTED_BEFORE_COMPUTATION'})
                                raise
                        if event['stage'] == 'RETURNED':
                            trials.append({**context, **event})
                    try:
                        wall_guard()
                        result = model.evaluate(physical, details=True, zero_components=zero,
                                                objective_audit=audit)
                        try: wall_guard()
                        except Exception:
                            save_event({**context, 'stage': 'FULL_RESULT_AFTER_DEADLINE', 'state': physical.tolist(),
                                        'value': result['negative_two_log_likelihood'], 'gradient': result['gradient']})
                            raise
                        save_event({**context, 'stage': 'FULL_RETURNED', 'state': physical.tolist(),
                                    'value': result['negative_two_log_likelihood'], 'gradient': result['gradient']})
                        return result, local_audit
                    except Exception as exc:
                        if failure is None:
                            save_event({**context, 'stage': 'FULL_FAILED', 'state': physical.tolist(),
                                        'error_type': type(exc).__name__, 'error': str(exc)})
                        raise

                first, first_audit = physical_evaluation(physical_start.copy(), 'EXACT_REQUESTED_START')
                row['exact_requested_start'] = {'state': physical_start.tolist(),
                    'value': first['negative_two_log_likelihood'], 'full_gradient_newly_evaluated': True}
                def evaluate(y, role):
                    state = base.copy(); state[active] = y
                    physical = native_from_chart(state, center, model.lower, model.upper)
                    result, audit = physical_evaluation(physical, role)
                    return result, physical, audit
                def fun(y):
                    result, _, _ = evaluate(y, 'SOLVER')
                    return result['negative_two_log_likelihood'], result['gradient'][active]
                solved = minimize(fun, base[active], lo[active], hi[active], scale=model.scales[active],
                    max_iterations=limits['max_iterations'], max_calls=limits['full_calls_per_case'] - 3,
                    seconds=max(.001, limits['case_seconds'] - (time.monotonic() - case_started)),
                    **{k: v for k, v in plan['method'].items() if k != 'hyper_step'})
                row['solver'] = solved
                for role in ('terminal', 'lowest_observed'):
                    own = solved.get(role)
                    if own is None: continue
                    result, physical, audit = evaluate(np.asarray(own['physical_state'], float), 'OWN_' + role)
                    projected = result['gradient'][active] * model.scales[active]
                    for k, j in enumerate(active):
                        if j != 3 and ((physical[j] == model.lower[j] and result['gradient'][j] > 0) or
                                       (physical[j] == model.upper[j] and result['gradient'][j] < 0)):
                            projected[k] = 0.
                    score = float(np.max(np.abs(projected)))
                    saved = api._saved_envelope(raw, plan['settings'], plan['input_summary'], model, result, audit)
                    replays.append({'role': role, 'saved_state': saved, 'projected_scaled_score': score,
                        'lower_completed_internal_values': [
                            {'full_call': t['full_call'], 'kind': t['kind'], 'state': t['state'],
                             'raw_delta': t['negative_two_log_likelihood'] - result['negative_two_log_likelihood']}
                            for t in trials if t['negative_two_log_likelihood'] < result['negative_two_log_likelihood']],
                        'stationary_candidate_only': bool(score <= .02 and result['linear_profile_identified'] and
                                                            result['linear_profile_projected_score'] <= 1e-9),
                        'minimum_adequacy_coverage_acceptance': False})
                model.verify_snapshot(); api.verify_sources(); wall_guard(); row['status'] = 'RETURNED'
            except Exception as exc:
                row.update(status='FAILED_OR_UNRESOLVED', error_type=type(exc).__name__, error=str(exc))
            row.update(full_calls=case_calls, covariance_calls=case_covariances,
                       replayed_states=replays, all_completed_internal_values=trials,
                       seconds=time.monotonic() - case_started)
            blob = api._encode(row)
            if failure is None and written + len(blob) <= limits['max_workspace_bytes']:
                with (path / (spec['case_id'] + '.json')).open('xb') as stream:
                    stream.write(blob); stream.flush(); os.fsync(stream.fileno()); written += len(blob)
            else:
                # A bounded terminal summary is outside the working-evidence cap.
                # All durable objective-prefix bytes remain untouched.
                row = {**spec, 'status': 'UNKNOWN_STORAGE_LIMIT', 'full_calls': case_calls,
                       'covariance_calls': case_covariances, 'error': failure or 'Case result exceeds remaining storage', **api.FLAGS}
                api._write_new(path / (spec['case_id'] + '.json'), row)
            rows.append({'case_id': spec['case_id'], 'status': row['status'],
                         'full_calls': case_calls, 'covariance_calls': case_covariances})
            if failure is not None: break
        global_guard()
    except Exception as exc:
        if failure is None: failure = type(exc).__name__ + ': ' + str(exc)
    finally:
        journal.close()
    api._write_new(path / 'WORKER.json', {'schema': 'bhtracker.known_system_v3.worker.v1',
        'full_calls': full_count, 'covariance_calls': covariance_count,
        'count_scope': 'Durable planned attempts; actual computations may be fewer after an abort',
        'rows': rows, 'failure': failure, 'seconds': time.monotonic() - started, **api.FLAGS})
    return 0 if failure is None else 1
