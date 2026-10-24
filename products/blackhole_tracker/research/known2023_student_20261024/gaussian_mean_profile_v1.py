"""Finite active-face solution of a supplied positive-covariance mean problem.

No observation reader, variance floor, confidence interval or BH classification.
Only explicitly bounded linear coefficients are enumerated; all others are free.
"""
import itertools
import numpy as np

class ProfileUnresolved(RuntimeError):
    pass

def _reject_booleans(value):
    if isinstance(value, (bool, np.bool_)):
        raise ValueError('Boolean is not a physical numeric input')
    if isinstance(value, dict):
        for child in value.values():
            _reject_booleans(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _reject_booleans(child)
    elif isinstance(value, np.ndarray) and value.dtype.kind in ('b', 'O'):
        for child in value.flat:
            _reject_booleans(child)

def profile_mean(design, target, bounds, *, fixed=None, score_tolerance=1e-9):
    for value in (design, target, bounds, fixed or {}, score_tolerance):
        _reject_booleans(value)
    if np.asarray(design).dtype.kind not in 'iuf' or np.asarray(target).dtype.kind not in 'iuf':
        raise ValueError('Real numeric matrix and target required')
    if not np.isfinite(score_tolerance) or score_tolerance <= 0:
        raise ValueError('Positive finite score tolerance required')
    a, y = np.asarray(design, dtype=float), np.asarray(target, dtype=float)
    if a.ndim != 2 or y.shape != (a.shape[0],) or not np.isfinite(a).all() or not np.isfinite(y).all():
        raise ValueError('Finite supplied whitened matrix and target required')
    n = a.shape[1]
    fixed = dict(fixed or {})
    bounds = dict(bounds)
    if len(bounds) > 3:
        raise ValueError('This declared small-face provider supports at most3 bounded coefficients')
    for j, pair in bounds.items():
        if type(j) is not int or not 0 <= j < n or len(pair) != 2 or not np.isfinite(pair).all() or pair[0] >= pair[1]:
            raise ValueError('Finite ordered bounds with integer column index required')
    for j, value in fixed.items():
        if type(j) is not int or not 0 <= j < n or isinstance(value, (bool, np.bool_)) or not np.isfinite(value):
            raise ValueError('Finite explicitly fixed coefficient required')
        if j in bounds and not bounds[j][0] <= value <= bounds[j][1]:
            raise ValueError('Fixed coefficient lies outside declared physical analysis domain')
    scale = np.linalg.norm(a, axis=0)
    if not np.isfinite(scale).all() or np.any((scale == 0) & np.any(a != 0, axis=0)):
        raise ProfileUnresolved('Column norm outside supported finite arithmetic; no physical row/column is dropped')
    positive = scale > 0
    normalized = a[:, positive] / scale[positive]
    full_rank = int(np.linalg.matrix_rank(normalized, tol=1e-11 * np.linalg.norm(normalized, 2))) if normalized.size else 0
    varied = [j for j in sorted(bounds) if j not in fixed]
    records, candidates = [], []
    for face in itertools.product(('FREE', 'LOWER', 'UPPER'), repeat=len(varied)):
        locked = dict(fixed)
        for j, side in zip(varied, face):
            if side != 'FREE':
                locked[j] = bounds[j][0 if side == 'LOWER' else 1]
        free = [j for j in range(n) if j not in locked]
        beta = np.zeros(n)
        for j, value in locked.items():
            beta[j] = value
        rhs = y - a @ beta
        if free:
            free_scale = scale[free]
            nonzero = free_scale > 0
            solve = np.zeros(len(free))
            reduced = a[:, np.asarray(free)[nonzero]] / free_scale[nonzero]
            if reduced.shape[1]:
                solution, _, rank, _ = np.linalg.lstsq(reduced, rhs, rcond=1e-11)
                solve[nonzero] = solution / free_scale[nonzero]
            else:
                rank = 0
            beta[free] = solve
        else:
            rank = 0
        record = {'face': dict(zip(map(str, varied), face)), 'free_rank': int(rank), 'free_column_count': len(free)}
        if not all(bounds[j][0] <= beta[j] <= bounds[j][1] for j in bounds):
            record.update(status='INFEASIBLE_FREE_SOLUTION')
            records.append(record)
            continue
        residual = a @ beta - y
        gradient = a.T @ residual
        projected = gradient.copy()
        for j in fixed:
            projected[j] = 0.
        for j, pair in bounds.items():
            if (beta[j] == pair[0] and gradient[j] >= 0.) or (beta[j] == pair[1] and gradient[j] <= 0.):
                projected[j] = 0.
        # A zero column has exact zero score; it remains nonidentified, not floored.
        normalized_score = np.zeros(n)
        normalized_score[positive] = projected[positive] / scale[positive]
        score = float(np.max(np.abs(normalized_score), initial=0.) / max(1., np.linalg.norm(residual)))
        cost = float(residual @ residual)
        if not np.isfinite([score, cost]).all() or not np.isfinite(beta).all():
            raise ProfileUnresolved('Nonfinite face arithmetic')
        record.update(status='KKT_ADMITTED' if score <= score_tolerance else 'KKT_UNRESOLVED', cost=cost, column_normalized_projected_score=score)
        records.append(record)
        if score <= score_tolerance:
            candidates.append((cost, len(locked), tuple(face), beta, residual, score))
    if not candidates:
        raise ProfileUnresolved('No feasible active face passed the supplied KKT tolerance')
    best = min(candidates, key=lambda item: item[:3])
    cost, _, face, beta, residual, score = best
    return {'coefficients': beta, 'residual': residual, 'quadratic': cost,
            'full_column_rank': full_rank, 'column_count': n,
            'linear_parameters_identified': full_rank == n,
            'column_normalized_projected_score': score,
            'active_bounds': [{'column': j, 'side': 'LOWER' if beta[j] == pair[0] else 'UPPER'} for j, pair in bounds.items() if beta[j] in pair],
            'fixed_columns': dict(fixed), 'all_faces': records,
            'qualification': 'Supplied positive-covariance Gaussian mean profile only. Rank deficiency is retained; no covariance or physical confidence interval is manufactured.'}
