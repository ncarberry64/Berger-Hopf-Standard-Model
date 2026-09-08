"""Continuous search and exact witnesses for a stored two-radius polynomial.

The supplied binary64 coefficients are treated as exact numbers. This module
does not enclose errors in their construction or prove a physical contraction.
"""
from decimal import Decimal, ROUND_FLOOR, localcontext
from fractions import Fraction
import math

import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp


def _inputs(y, z, c, m, t, ceiling):
    arrays = tuple(np.asarray(a, dtype=float) for a in (y, z, c, m, t))
    if any(a.shape != shape for a, shape in zip(
        arrays, ((2,), (2, 2), (2,), (2,), (2,)), strict=True
    )):
        raise ValueError("Two outputs and two input radii are required")
    if any(not np.all(np.isfinite(a) & (a >= 0)) for a in arrays):
        raise ValueError("Coefficients must be finite and nonnegative")
    if not math.isfinite(ceiling) or ceiling <= 0:
        raise ValueError("The common radius ceiling must be finite and positive")
    return arrays


def _evaluate(y, z, c, m, t, r):
    return [y[i] + sum(z[i][j] * r[j] for j in range(2))
            + c[i] * r[0] * r[0] + 2 * m[i] * r[0] * r[1]
            + t[i] * r[1] * r[1] for i in range(2)]


def exact_self_map_witness(y, z, c, m, t, ceiling, radius):
    """Return exact rational margins, or None if this candidate is not strict."""
    arrays = _inputs(y, z, c, m, t, ceiling)
    r = np.asarray(radius, dtype=float)
    if r.shape != (2,) or not np.all(np.isfinite(r) & (r > 0) & (r <= ceiling)):
        return None
    exact = [np.vectorize(Fraction.from_float, otypes=[object])(a).tolist()
             for a in arrays]
    rational_r = [Fraction.from_float(float(value)) for value in r]
    rhs = _evaluate(*exact, rational_r)
    margins = [rational_r[i] - rhs[i] for i in range(2)]
    if not all(value > 0 for value in margins):
        return None
    return {"radius": r.tolist(), "exact_margin": [str(v) for v in margins],
            "exact_rhs": [str(v) for v in rhs]}


def monotone_ceiling_obstruction(y, z, c, m, t, ceiling, *, iterations=2048):
    """Prove absence of a strict self-map ONLY when a lower iterate hits the cap.

    For nonnegative coefficients F is monotone. Any strict supersolution r
    dominates each lower-rounded iterate from zero, and strictly dominates
    every iterate after the first application. Thus l[n][i] >= ceiling rules
    out a strict supersolution inside the declared ceiling. Stagnation or an
    iteration limit supplies no negative conclusion.
    """
    arrays = _inputs(y, z, c, m, t, ceiling)
    if not isinstance(iterations, int) or iterations < 1:
        raise ValueError("iterations must be a positive integer")
    exact = [np.vectorize(Decimal.from_float, otypes=[object])(a).tolist()
             for a in arrays]
    cap = Decimal.from_float(float(ceiling))
    lower = [Decimal(0), Decimal(0)]
    with localcontext() as context:
        context.prec = 80
        context.rounding = ROUND_FLOOR
        for step in range(1, iterations + 1):
            next_lower = _evaluate(*exact, lower)
            if any(v >= cap for v in next_lower):
                return {"iterations": step, "lower_radius": [str(v) for v in next_lower],
                        "precision_decimal_digits": 80, "rounding": "ROUND_FLOOR"}
            if next_lower == lower:
                break
            lower = next_lower
    return None


def _log_terms(y, z, c, m, t, ceiling):
    """Terms of log(F_i(r)/r_i), with r = ceiling * exp(x).

    Every term is affine before log-sum-exp, making the epigraph search convex.
    Form logs directly to avoid overflow/underflow in coefficient * ceiling.
    """
    unit = np.eye(2)
    result = []
    for i in range(2):
        terms = [(y[i], -math.log(ceiling), -unit[i])]
        terms += [(z[i, j], 0.0, unit[j] - unit[i]) for j in range(2)]
        terms += [(c[i], math.log(ceiling), 2 * unit[0] - unit[i]),
                  (m[i], math.log(ceiling) + math.log(2), unit[0] + unit[1] - unit[i]),
                  (t[i], math.log(ceiling), 2 * unit[1] - unit[i])]
        result.append([(math.log(float(a)) + scale, exponent)
                       for a, scale, exponent in terms if a > 0])
    return result


def continuous_two_radius_screen(y, z, c, m, t, ceiling, *, initial_radius=None,
                                obstruction_iterations=2048):
    """Find a strict exact witness; never interpret optimizer failure as a proof.

    Output status is STORED_POLYNOMIAL_SELF_MAP, STORED_POLYNOMIAL_CAP_OBSTRUCTION,
    or UNRESOLVED. None of these statuses asserts Gate 7 or root nonexistence.
    """
    y, z, c, m, t = _inputs(y, z, c, m, t, ceiling)
    args = (y, z, c, m, t, ceiling)
    boundary = {"exact_stored_binary64_polynomial_only": True,
                "physical_coefficient_errors_enclosed": False,
                "contraction_proved": False, "GATE7_CLOSED": False,
                "root_nonexistence_proved": False, "FULL_BHSM_COMPLETE": False}

    def success(radius):
        witness = exact_self_map_witness(*args, radius)
        return None if witness is None else {
            "status": "STORED_POLYNOMIAL_SELF_MAP", "witness": witness,
            "claim_boundary": boundary}

    for candidate in (initial_radius, [ceiling / 2, ceiling / 2], [ceiling, ceiling]):
        if candidate is not None:
            found = success(candidate)
            if found is not None:
                return found
    obstruction = monotone_ceiling_obstruction(
        *args, iterations=obstruction_iterations)
    if obstruction is not None:
        return {"status": "STORED_POLYNOMIAL_CAP_OBSTRUCTION",
                "obstruction": obstruction, "claim_boundary": boundary}

    terms = _log_terms(*args)
    lower = [math.log(float(v) if v > 0 else math.ulp(0.0)) - math.log(ceiling)
             for v in y]

    def values_and_gradients(x):
        values, gradients = [], []
        for output in terms:
            if not output:
                values.append(-1e300)
                gradients.append(np.zeros(2))
                continue
            exponents = np.asarray([term[1] for term in output])
            logs = np.asarray([term[0] for term in output]) + exponents @ x
            value = logsumexp(logs)
            values.append(value)
            gradients.append(np.exp(logs - value) @ exponents)
        return np.asarray(values), np.asarray(gradients)

    def constraint(v):
        values, _ = values_and_gradients(v[:2])
        return v[2] - values

    def jacobian(v):
        _, gradients = values_and_gradients(v[:2])
        return np.column_stack((-gradients, np.ones(2)))

    start = np.maximum(lower, -np.ones(2))
    result = minimize(
        lambda v: v[2], np.r_[start, max(values_and_gradients(start)[0])],
        jac=lambda v: np.array([0., 0., 1.]), method="SLSQP",
        bounds=[(v, 0.) for v in lower] + [(None, None)],
        constraints={"type": "ineq", "fun": constraint, "jac": jacobian},
        options={"ftol": 1e-12, "maxiter": 300},
    )
    if np.all(np.isfinite(result.x[:2])):
        radius = [min(ceiling, math.exp(math.log(ceiling) + min(0., float(v))))
                  for v in result.x[:2]]
        found = success(radius)
        if found is not None:
            return found
    return {"status": "UNRESOLVED", "optimizer_success": bool(result.success),
            "optimizer_message": str(result.message), "claim_boundary": boundary}
