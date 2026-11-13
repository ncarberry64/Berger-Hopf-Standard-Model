"""Stable fixed-Y coefficients of a source-directed first-order action.

Every coefficient is obtained from the same Y0 action solve. Odd powers
are retained. This does not replace the loop's relative heat domain by a
retarded inverse or assert an external pole state.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import lu_factor, lu_solve
from flint import arb, acb_mat, ctx
from .muon_native_even_y_remainder_certificate import (
    _acb_matrix, _frobenius_upper, _record)


def block_bidiagonal(diagonal, lower):
    d, l = (np.asarray(a, complex) for a in (diagonal, lower))
    if d.ndim != 3 or d.shape != l.shape or d.shape[1] != d.shape[2] or not np.isfinite([d, l]).all():
        raise ValueError('one finite same-domain diagonal/lower block per time cell required')
    steps, n, _ = d.shape
    a = np.zeros((steps*n, steps*n), complex)
    for j in range(steps):
        a[j*n:(j+1)*n, j*n:(j+1)*n] = d[j]
        if j:
            a[j*n:(j+1)*n, (j-1)*n:j*n] = l[j]
    return a


def common_y_inverse_action(A0, A1, rhs_coefficients, *, order=4):
    """Solve (A0+y A1)u(y)=sum y^k r_k, retaining literal coefficients."""
    a, b, r = (np.asarray(x, complex) for x in (A0, A1, rhs_coefficients))
    if (a.ndim != 2 or a.shape[0] != a.shape[1] or b.shape != a.shape
            or r.ndim != 3 or r.shape[1] != len(a) or not np.isfinite([a, b]).all()
            or not np.isfinite(r).all() or type(order) is not int or order < len(r)-1):
        raise ValueError('complete common action, polynomial sources and retained order required')
    lu = lu_factor(a)
    u = np.zeros((order+1, *r.shape[1:]), complex)
    residual = u.copy()
    for k in range(order+1):
        source = r[k].copy() if k < len(r) else np.zeros_like(r[0])
        if k:
            source -= b @ u[k-1]
        u[k] = lu_solve(lu, source)
        residual[k] = a @ u[k] - source
    return dict(coefficients=u, recurrence_residuals=residual,
        coefficient_recursion='A0 u_k=r_k-A1 u_(k-1); u_-1=0',
        no_physical_Y_family_inverse_subtraction=True)


def common_y_rectangular_source_jet(target_A0, target_A1, source_coefficients,
        action_direction_coefficients, rhs_direction_coefficients, *, order):
    """Apply all placements of -A_t^-1 D A_s^-1 plus changed source.

    The left-current variation is contracted separately by
    polynomial_current_pairing. Target and source angular images may
    differ; they must be supplied by the actual action producer.
    """
    a, b = (np.asarray(x, complex) for x in (target_A0, target_A1))
    u, d, r = (np.asarray(x, complex) for x in
        (source_coefficients, action_direction_coefficients, rhs_direction_coefficients))
    if (u.ndim != 3 or d.ndim != 3 or r.ndim != 3 or d.shape[1:] != (len(a), u.shape[1])
            or r.shape[1:] != (len(a), u.shape[2]) or len(u) <= order
            or not np.isfinite([u]).all() or not np.isfinite(d).all() or not np.isfinite(r).all()):
        raise ValueError('same literal rectangular action and right-source jet required')
    effective = np.zeros((order+1, len(a), u.shape[2]), complex)
    for k in range(order+1):
        if k < len(r):
            effective[k] += r[k]
        for j in range(min(k+1, len(d))):
            effective[k] -= d[j] @ u[k-j]
    result = common_y_inverse_action(a, b, effective, order=order)
    result['effective_source_coefficients'] = effective
    return result


def polynomial_current_pairing(left_coefficients, response_coefficients):
    """Contract literal left maps; their adjoints belong to the producer."""
    l, u = (np.asarray(x, complex) for x in (left_coefficients, response_coefficients))
    if l.ndim != 3 or u.ndim != 3 or l.shape[2] != u.shape[1]:
        raise ValueError('compatible literal left current and response coefficients required')
    out = np.zeros((len(u), l.shape[1], u.shape[2]), complex)
    for k in range(len(u)):
        for j in range(min(k+1, len(l))):
            out[k] += l[j] @ u[k-j]
    return out


def paired_fixed_y_polynomial(coefficients, middle_y, light_y):
    """Middle-minus-light without subtracting the shared order-zero term."""
    c = np.asarray(coefficients, complex)
    m, e = float(middle_y), float(light_y)
    if c.ndim < 1 or not np.isfinite(c).all() or not np.isfinite([m, e]).all():
        raise ValueError('finite action coefficients and fixed family Y required')
    out = np.zeros_like(c[0])
    for k in range(1, len(c)):
        difference = (m-e)*sum(m**j*e**(k-1-j) for j in range(k))
        out += difference*c[k]
    return out


def exact_stored_inverse_tail(A0, A1, rhs, fixed_y, *, order, computed_coefficients=None, precision_bits=192):
    """Certify finite stored-action Neumann tail and computed coefficient errors.

    This certificate excludes the production of the matrix entries and
    the temporal/domain continuum. It does not bound a Pauli anomaly.
    """
    a, b, r = (np.asarray(x, complex) for x in (A0, A1, rhs))
    if r.ndim != 2 or r.shape[0] != len(a):
        raise ValueError('literal Y-independent source action required')
    z = lu_solve(lu_factor(a), np.eye(len(a)))
    with ctx.workprec(precision_bits):
        aa, bb, rr, zz = (_acb_matrix(x) for x in (a, b, r, z))
        defect = _frobenius_upper(acb_mat(np.eye(len(a)).tolist()) - zz*aa)
        if not defect < 1:
            raise ArithmeticError('common stored-action inverse could not be certified')
        beta = (_frobenius_upper(zz*bb)/(1-defect)).upper()
        initial = (_frobenius_upper(zz*rr)/(1-defect)).upper()
        inverse_norm = (_frobenius_upper(zz)/(1-defect)).upper()
        errors = []
        if computed_coefficients is not None:
            u = np.asarray(computed_coefficients, complex)
            if u.shape != (order+1, *r.shape) or not np.isfinite(u).all():
                raise ValueError('all computed common action coefficients required')
            previous = None
            error = arb(0)
            for k in range(order+1):
                current = _acb_matrix(u[k])
                residual = aa*current - (rr if k == 0 else -bb*previous)
                error = (inverse_norm*_frobenius_upper(residual) + beta*error).upper()
                errors.append(error)
                previous = current
        tails = []
        for y in fixed_y:
            ratio = arb(abs(float(y)))*beta
            if not ratio < 1:
                raise ArithmeticError('fixed family lies outside the certified Neumann disk')
            tails.append(dict(Y=float(y), ratio=_record(ratio),
                response_tail_upper=_record(initial*ratio**(order+1)/(1-ratio)),
                computed_polynomial_error_upper=_record(sum(arb(abs(float(y)))**k*e for k, e in enumerate(errors))) if errors else None))
        paired_error = None
        if errors and len(fixed_y) == 2:
            m, e = (arb(float(y)) for y in fixed_y)
            # The computed common u0 is the identical object in both
            # families. Its direct error cancels, while its propagated
            # contribution is already present in errors[k>0].
            paired_error = _record(sum(abs(m**k-e**k).abs_upper()*errors[k] for k in range(1, order+1)))
        return dict(precision_bits=precision_bits, inverse_defect=_record(defect),
            inverse_times_Y1_norm_upper=_record(beta), Y0_response_norm_upper=_record(initial),
            computed_coefficient_error_uppers=[_record(e) for e in errors],
            paired_computed_polynomial_error_upper=paired_error,
            fixed_family_tails=tails, order=order,
            scope='exact stored finite first-order action and source only; entry production, temporal complement, current contraction and native domain excluded')


def certify_current_pairing(left, coefficients, paired_value, fixed_y, response_certificate,
        *, precision_bits=192):
    """Carry the stored response certificate through its literal current."""
    l, u, p = (np.asarray(x, complex) for x in (left, coefficients, paired_value))
    if len(fixed_y) != 2 or l.shape[1] != u.shape[1] or p.shape != (l.shape[0], u.shape[2]):
        raise ValueError('same paired response and literal current map required')
    with ctx.workprec(precision_bits):
        ll = _acb_matrix(l)
        m, e = (arb(float(y)) for y in fixed_y)
        exact_polynomial = acb_mat(u.shape[1], u.shape[2])
        for k in range(1, len(u)):
            exact_polynomial += _acb_matrix(u[k])*(m**k-e**k)
        contraction_error = _frobenius_upper(ll*exact_polynomial-_acb_matrix(p))
        response_error = arb(response_certificate['paired_computed_polynomial_error_upper']['arb'])
        tails = sum(arb(r['response_tail_upper']['arb']) for r in response_certificate['fixed_family_tails'])
        upper = contraction_error+_frobenius_upper(ll)*(response_error+tails)
        return dict(paired_current_binary_contraction_error=_record(contraction_error),
            paired_current_total_stored_arithmetic_and_Y_tail_upper=_record(upper),
            source_scope=response_certificate['scope'],
            no_continuum_or_physical_Pauli_enclosure=True)
