"""Spectral candidate for a spherical trust quadratic, not a covariance law.

The mathematical target is the global trust-quadratic solution of the supplied
eigensystem. Floating secular/KKT checks are engineering checks, not rigorous
enclosures. A failed check returns an explicitly unavailable candidate. The
caller must still clip to its original box, test q<0 using its ORIGINAL H and
evaluate its ORIGINAL objective. No Hessian/eigenvalue is replaced or floored.
"""
import math
import numpy as np


def spectral_step(gradient, eigenvalues, eigenvectors, radius, *, max_iterations=256):
    if type(max_iterations) is not int or max_iterations <= 0:
        raise ValueError('Positive finite secular iteration budget required')
    if isinstance(radius, (bool, np.bool_)) or not math.isfinite(radius) or radius <= 0:
        raise ValueError('Positive finite trust radius required')
    raw = [np.asarray(x) for x in (gradient, eigenvalues, eigenvectors)]
    if any(x.dtype.kind not in 'iuf' for x in raw):
        raise ValueError('Finite real eigensystem required')
    g, w, q = [np.array(x, dtype=float, copy=True) for x in raw]
    n = len(g) if g.ndim == 1 else 0
    if not n or w.shape != (n,) or q.shape != (n, n) or not all(np.isfinite(x).all() for x in (g, w, q)) or np.any(w[:-1] > w[1:]):
        raise ValueError('Matched finite ordered eigensystem required')
    info = {'schema': 'bhsm.spectral_trust_step.v1', 'status': 'UNAVAILABLE',
            'scope': 'Step candidate only; trust multiplier is not a Hessian regularizer, covariance or ridge.',
            'secular_iterations': 0, 'eigenvalues_unchanged': w.tolist()}

    def unavailable(reason):
        info.update(status='UNAVAILABLE', reason=reason)
        return None, info

    eps = np.finfo(float).eps
    with np.errstate(over='ignore', invalid='ignore'):
        orthogonality = float(np.max(np.sum(np.abs(q.T @ q - np.eye(n)), axis=1)))
        a = q.T @ g
    if not math.isfinite(orthogonality) or orthogonality > 128 * eps * n or not np.isfinite(a).all():
        return unavailable('EIGENSYSTEM_TRANSFORM_ARITHMETIC_UNRESOLVED')
    base = max(0., -float(w[0]))
    with np.errstate(over='ignore', invalid='ignore'):
        offsets = w - w[0] if w[0] < 0 else w.copy()
    if not np.isfinite(offsets).all() or np.any(offsets < 0):
        return unavailable('NONNEGATIVE_OFFSET_ARITHMETIC_UNRESOLVED')
    norm_a = math.hypot(*map(float, a))
    if not math.isfinite(norm_a):
        return unavailable('TRANSFORMED_GRADIENT_NORM_UNRESOLVED')
    null = offsets == 0.

    def at(shift):
        with np.errstate(over='ignore', divide='ignore', invalid='ignore'):
            den = offsets + shift
            y = np.zeros(n)
            positive = den > 0
            y[positive] = -a[positive] / den[positive]
        if not np.isfinite(den).all() or np.any((~positive) & (a != 0)) or not np.isfinite(y).all():
            return None, None
        return y, math.hypot(*map(float, y))

    def finish(y, shift, status):
        with np.errstate(over='ignore', invalid='ignore'):
            step = q @ y
        if not np.isfinite(step).all():
            return unavailable('STEP_TRANSFORM_UNRESOLVED')
        length = math.hypot(*map(float, step))
        # An orthogonal floating transform may increase the norm by a few ulps.
        # This radial feasibility adjustment changes the candidate, never H.
        adjusted = False
        for _ in range(3):
            if length <= radius:
                break
            target = math.nextafter(float(radius), 0.)
            step *= target / length
            length = math.hypot(*map(float, step))
            adjusted = True
        if not math.isfinite(length) or length > radius:
            return unavailable('REPRESENTED_TRUST_FEASIBILITY_UNRESOLVED')
        with np.errstate(over='ignore', invalid='ignore'):
            actual_y = q.T @ step
            residual = (offsets + shift) * actual_y + a
            quadratic = float(a @ actual_y + .5 * actual_y @ (w * actual_y))
        residual_norm = math.hypot(*map(float, residual))
        operator_scale = max(1., norm_a, float(np.max(offsets + shift)) * radius)
        allowance = 512 * eps * n * operator_scale
        if not np.isfinite(actual_y).all() or not math.isfinite(quadratic) or not math.isfinite(residual_norm) or not math.isfinite(allowance) or residual_norm > allowance:
            return unavailable('ESTIMATED_KKT_ARITHMETIC_UNRESOLVED')
        info.update(status=status, trust_multiplier={'base': base, 'nonnegative_shift': float(shift)},
                    step_norm=length, radius=float(radius), radial_feasibility_adjusted=adjusted,
                    transformed_KKT_residual_norm=residual_norm,
                    estimated_KKT_arithmetic_allowance=allowance,
                    quadratic_in_supplied_eigensystem=quadratic,
                    orthogonality_error=orthogonality,
                    qualification='Finite arithmetic candidate, not a rigorous global or physical certificate; original-H and real-objective caller checks remain mandatory.')
        return step, info

    # Only exact zero in the represented transformed minimum eigenspace is
    # called a hard case. A tiny nonzero component is never relabeled zero.
    if not np.any(a[null] != 0):
        y0, n0 = at(0.)
        if y0 is not None and math.isfinite(n0) and n0 <= radius:
            if w[0] < 0:
                remainder = max(0., 1. - (n0 / radius) ** 2)
                y0[int(np.flatnonzero(null)[0])] += radius * math.sqrt(remainder)
                return finish(y0, 0., 'HARD_CASE_BOUNDARY_CANDIDATE')
            return finish(y0, 0., 'PSD_UNCONSTRAINED_CANDIDATE')

    upper = norm_a / radius
    if not math.isfinite(upper) or upper <= 0:
        return unavailable('POSITIVE_SECULAR_BRACKET_UNREPRESENTABLE')
    lower = 0.
    null_norm = math.hypot(*map(float, a[null]))
    if null_norm > 0:
        lower = null_norm / radius
        if lower == 0 or not math.isfinite(lower):
            return unavailable('NONZERO_MINIMUM_COMPONENT_SHIFT_UNREPRESENTABLE')
        trial_y, trial_norm = at(lower)
        if trial_y is not None and trial_norm <= radius:
            upper, lower = lower, 0.
    right_y, right_norm = at(upper)
    for _ in range(16):
        if right_y is not None and math.isfinite(right_norm) and right_norm <= radius:
            break
        upper *= 2.
        if not math.isfinite(upper):
            return unavailable('FINITE_SECULAR_UPPER_BRACKET_UNRESOLVED')
        right_y, right_norm = at(upper)
    else:
        return unavailable('SECULAR_UPPER_BRACKET_BUDGET_UNRESOLVED')
    tolerance = 128 * eps * radius
    for iteration in range(max_iterations):
        info['secular_iterations'] = iteration
        if radius - right_norm <= tolerance:
            return finish(right_y, upper, 'REGULAR_SECULAR_BOUNDARY_CANDIDATE')
        if lower > 0 and math.log(upper) - math.log(lower) > math.log(4.):
            middle = math.sqrt(lower) * math.sqrt(upper)
        else:
            middle = lower + .5 * (upper - lower)
        if not lower < middle < upper:
            return unavailable('SECULAR_REPRESENTATION_RESOLUTION_UNRESOLVED')
        y, length = at(middle)
        if y is None or not math.isfinite(length) or length > radius:
            lower = middle
        else:
            upper, right_y, right_norm = middle, y, length
    return unavailable('SECULAR_ITERATION_BUDGET_UNRESOLVED')
