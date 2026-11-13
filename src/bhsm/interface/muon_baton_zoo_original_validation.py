"""Independent original Maxwell rows and source/domain derivative admission.

The Maxwell evaluator below uses literal component curvatures, rather than
the analytic action/Hessian assembly used by the chronological producer.
All fields, field derivatives, tests and metric densities are mandatory.
The derivative comparison only admits a derivative when the supplied fresh
original evaluator retains all five required matching contributions.
Neither function chooses a history, source germ or terminal boundary.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
import numpy as np


CONTRIBUTIONS = ("terminal_return", "source_binding", "bulk_operator",
                 "port_conversion", "domain_motion")
IDENTITY_KEYS = ("action", "primal", "coefficients", "domain", "source_germ",
                 "terminal_germ")


def _finite(value, shape=None):
    array = np.asarray(value, dtype=complex)
    if (shape is not None and array.shape != shape) or not np.isfinite(array).all():
        raise ValueError("finite complete same-domain component arrays required")
    return array


def _commutator(left, right):
    # Literal unit-Tr16 real-component Lie bracket, extended analytically.
    result = np.zeros(np.broadcast_shapes(left.shape, right.shape), complex)
    result[..., 0] = (left[..., 1]*right[..., 2]-left[..., 2]*right[..., 1])/np.sqrt(2)
    result[..., 1] = (left[..., 2]*right[..., 0]-left[..., 0]*right[..., 2])/np.sqrt(2)
    result[..., 2] = (left[..., 0]*right[..., 1]-left[..., 1]*right[..., 0])/np.sqrt(2)
    return result


def _magnetic(connection, angular):
    magnetic = 2*connection[..., 2:, :].copy()
    # eps_ijk E_j A_k + .5 eps_ijk [A_j,A_k], with every pair retained.
    for i, j, k in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
        magnetic[..., i, :] += angular[..., j, k+2, :]-angular[..., k, j+2, :]
        magnetic[..., i, :] += _commutator(connection[..., j+2, :], connection[..., k+2, :])
    return magnetic


def independent_original_maxwell_weak(*, connection, time_derivative,
        radial_derivative, angular_derivative, tests, tests_time,
        tests_radial, tests_angular, metric_densities, quadrature):
    """Evaluate literal complex Euler weak rows and canonical momenta.

    Field axes are ``(point,5,4)``, test axes ``(point,test,5,4)``;
    angular derivatives insert a length-three angular axis before ``5,4``.
    The five metric densities are electric, radial, angular,
    electric-radial and shift. Quadrature includes the owned normalization.
    Total connections must include the inherited background exactly once.
    No Hilbert conjugation, sourced Gauss replacement or endpoint is added.
    """
    a = _finite(connection)
    if a.ndim != 3 or a.shape[1:] != (5, 4):
        raise ValueError("complete five-component connection required")
    count = len(a)
    at, ar = (_finite(v, a.shape) for v in (time_derivative, radial_derivative))
    ea = _finite(angular_derivative, (count, 3, 5, 4))
    v = _finite(tests)
    if v.ndim != 4 or v.shape[0] != count or v.shape[2:] != (5, 4):
        raise ValueError("complete indexed five-component tests required")
    nt = v.shape[1]
    vt, vr = (_finite(x, v.shape) for x in (tests_time, tests_radial))
    ev = _finite(tests_angular, (count, nt, 3, 5, 4))
    d = _finite(metric_densities, (count, 5))
    w = _finite(quadrature, (count,))
    e, r, angular, k, beta = d.T

    x = at[:, 1]-ar[:, 0]+_commutator(a[:, 0], a[:, 1])
    t = at[:, 2:]-ea[:, :, 0]+_commutator(a[:, 0, None], a[:, 2:])
    z = ar[:, 2:]-ea[:, :, 1]+_commutator(a[:, 1, None], a[:, 2:])
    b = _magnetic(a, ea)
    dx = vt[:, :, 1]-vr[:, :, 0]+_commutator(v[:, :, 0], a[:, None, 1])+_commutator(a[:, None, 0], v[:, :, 1])
    dt = vt[:, :, 2:]-ev[:, :, :, 0]+_commutator(v[:, :, 0, None], a[:, None, 2:])+_commutator(a[:, None, 0, None], v[:, :, 2:])
    dz = vr[:, :, 2:]-ev[:, :, :, 1]+_commutator(v[:, :, 1, None], a[:, None, 2:])+_commutator(a[:, None, 1, None], v[:, :, 2:])
    db = 2*v[:, :, 2:].copy()
    for i, j, l in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
        db[:, :, i] += ev[:, :, j, l+2]-ev[:, :, l, j+2]
        db[:, :, i] += (_commutator(v[:, :, j+2], a[:, None, l+2])
                        +_commutator(a[:, None, j+2], v[:, :, l+2]))
    y = t-beta[:, None, None]*z
    dy = dt-beta[:, None, None, None]*dz
    inner = lambda left, right: np.sum(left[:, None]*right, axis=tuple(range(2, right.ndim)))
    point_rows = (k[:, None]*inner(x, dx)+e[:, None]*inner(y, dy)
                  -r[:, None]*inner(z, dz)-angular[:, None]*inner(b, db))
    rows = np.sum(w[:, None]*point_rows, axis=0)
    pt = np.zeros_like(a)
    pr = np.zeros_like(a)
    pt[:, 1] = k[:, None]*x
    pt[:, 2:] = e[:, None, None]*y
    pr[:, 0] = -k[:, None]*x
    pr[:, 2:] = -e[:, None, None]*beta[:, None, None]*y-r[:, None, None]*z
    scalar = np.sum(w*(k*np.sum(x*x, axis=1)+e*np.sum(y*y, axis=(1, 2))
                      -r*np.sum(z*z, axis=(1, 2))-angular*np.sum(b*b, axis=(1, 2))))/2
    return dict(original_weak_rows=rows, original_action_value=scalar,
                point_weak_rows=point_rows, temporal_momentum=pt,
                radial_momentum=pr, canonical_endpoint_contacts_added=False,
                analytic_components_conjugated=False,
                physical_terminal_domain_or_full_zoo_selected=False)


def independent_original_maxwell_momentum_rate(*, connection, time_derivative,
        radial_derivative, angular_derivative, connection_rate,
        time_derivative_rate, radial_derivative_rate, angular_derivative_rate,
        metric_densities, metric_density_rates):
    """Literal total time derivative of canonical Maxwell momentum.

    Inputs are the actual time derivative of each original field operand,
    including inherited-source motion once. The momentum is differentiated
    componentwise, without an action Hessian, a source derivative helper or
    an endpoint contact. All components and density-rate terms are retained.
    """
    a = _finite(connection)
    if a.ndim != 3 or a.shape[1:] != (5, 4):
        raise ValueError("complete five-component connection required")
    n = len(a)
    at, ar, ad, atd, ard = (_finite(v, a.shape) for v in (
        time_derivative, radial_derivative, connection_rate,
        time_derivative_rate, radial_derivative_rate))
    ea, ead = (_finite(v, (n, 3, 5, 4)) for v in (angular_derivative, angular_derivative_rate))
    d, dd = (_finite(v, (n, 5)) for v in (metric_densities, metric_density_rates))
    e, _, _, k, beta = d.T
    ed, _, _, kd, bd = dd.T
    x = at[:, 1]-ar[:, 0]+_commutator(a[:, 0], a[:, 1])
    xd = atd[:, 1]-ard[:, 0]+_commutator(ad[:, 0], a[:, 1])+_commutator(a[:, 0], ad[:, 1])
    t = at[:, 2:]-ea[:, :, 0]+_commutator(a[:, 0, None], a[:, 2:])
    td = atd[:, 2:]-ead[:, :, 0]+_commutator(ad[:, 0, None], a[:, 2:])+_commutator(a[:, 0, None], ad[:, 2:])
    z = ar[:, 2:]-ea[:, :, 1]+_commutator(a[:, 1, None], a[:, 2:])
    zd = ard[:, 2:]-ead[:, :, 1]+_commutator(ad[:, 1, None], a[:, 2:])+_commutator(a[:, 1, None], ad[:, 2:])
    y = t-beta[:, None, None]*z
    yd = td-bd[:, None, None]*z-beta[:, None, None]*zd
    result = np.zeros_like(a)
    result[:, 1] = kd[:, None]*x+k[:, None]*xd
    result[:, 2:] = ed[:, None, None]*y+e[:, None, None]*yd
    return result


def compare_original_equation_direction(*, original: Callable[[float], Mapping],
        claimed: Mapping[str, object], steps: Sequence[float],
        coefficient_identity: Mapping[str, str], relative_tolerance: float,
        absolute_tolerance: float):
    """Compare a claimed derivative against fresh ORIGINAL equation values.

    The callback evaluates a complete perturbed physical trajectory/domain
    at one real direction parameter; it cannot return a differentiated
    assembly helper. Its ``identity`` pins the unperturbed action/primal,
    coefficient set and source/terminal germs, while ``contributions``
    contains all five unsummed original-equation contributions. Explicit
    zero arrays require action-owned provenance supplied by the callback.
    Step controls are numerical evidence, never an outward enclosure.
    """
    if set(claimed) != set(CONTRIBUTIONS):
        raise ValueError("all five independently owned derivative contributions required")
    if set(coefficient_identity) != set(IDENTITY_KEYS) or not all(coefficient_identity.values()):
        raise ValueError("same primal/action/domain/germ identities required")
    sizes = tuple(float(h) for h in steps)
    if len(sizes) < 3 or any(not np.isfinite(h) or h <= 0 for h in sizes):
        raise ValueError("at least three positive finite derivative steps required")
    if any(b >= a for a, b in zip(sizes, sizes[1:])):
        raise ValueError("derivative steps must strictly decrease")
    if not np.isfinite([relative_tolerance, absolute_tolerance]).all() or min(relative_tolerance, absolute_tolerance) < 0:
        raise ValueError("declared finite nonnegative tolerances required")
    exact = {name: _finite(claimed[name]) for name in CONTRIBUTIONS}
    shape = exact[CONTRIBUTIONS[0]].shape
    if any(a.shape != shape for a in exact.values()):
        raise ValueError("every contribution must use the same original residual rows")

    def evaluate(epsilon):
        result = original(epsilon)
        if result.get("identity") != dict(coefficient_identity):
            raise ValueError("perturbation changed original primal/action/domain/germ identity")
        if result.get("evaluation_owner") != "fresh_original_equations":
            raise ValueError("fresh original-equation evaluation owner required")
        parts = result.get("contributions", {})
        if set(parts) != set(CONTRIBUTIONS):
            raise ValueError("original evaluator omitted a required contribution")
        if not result.get("zero_contribution_provenance_complete", False):
            raise ValueError("unproved zero contribution or reference fallback prohibited")
        return {name: _finite(parts[name], shape) for name in CONTRIBUTIONS}

    evaluate(0.)
    records, derivatives = [], []
    previous = None
    claimed_total = sum(exact.values())
    for h in sizes:
        plus, minus = evaluate(h), evaluate(-h)
        fresh = {name: (plus[name]-minus[name])/(2*h) for name in CONTRIBUTIONS}
        total = sum(fresh.values())
        records.append(dict(step=h, contributions={name: dict(
            derivative=fresh[name], difference=fresh[name]-exact[name],
            absolute_error=float(np.linalg.norm(fresh[name]-exact[name])),
            relative_error=float(np.linalg.norm(fresh[name]-exact[name])/
                                 max(np.linalg.norm(fresh[name]), np.finfo(float).tiny)))
            for name in CONTRIBUTIONS}, total_derivative=total,
            total_difference=total-claimed_total,
            total_absolute_error=float(np.linalg.norm(total-claimed_total)),
            step_difference=None if previous is None else float(np.linalg.norm(total-previous))))
        derivatives.append(fresh)
        previous = total
    # A cancellation in the sum cannot hide a bad individual contribution.
    last_two_pass = all(np.linalg.norm(fresh[name]-exact[name]) <= absolute_tolerance
                       +relative_tolerance*np.linalg.norm(fresh[name])
                       for fresh in derivatives[-2:] for name in CONTRIBUTIONS)
    return dict(records=records, derivative_admitted=bool(last_two_pass),
                comparison_owner="independent_fresh_original_equations",
                coefficient_identity=dict(coefficient_identity),
                outward_error_enclosure=False,
                nonlinear_correction_allowed=bool(last_two_pass))
