"""Midpoint proposals for independently verified interval eigenpair boxes.

Only the approximation uses the midpoint matrix. Acceptance always uses the
complete matrix family, through the existing normalized eigenpair verifier.
"""
from contextlib import contextmanager
import math
import numpy as np
from flint import arb, arb_mat, ctx
from bhsm.interface.arb_eigenpair_inclusion import verify_eigenpair_box


def _bordered(h, p, lam):
    n = h.nrows()
    result = arb_mat(n+1, n+1)
    for i in range(n):
        for j in range(n):
            result[i, j] = h[i, j] - (lam if i == j else 0)
        result[i, n] = -p[i, 0]
        result[n, i] = p[i, 0]
    return result


def propose(matrix, reference, *, selected, max_attempts=16):
    """Return a proved normalized pair or fail without narrowing the matrix.

    Fixed midpoint Newton steps provide a center. Coordinate radii start from
    its preconditioned interval residual and grow using failed inclusion rows.
    Growth is a proposal heuristic, never a substitute for strict inclusion.
    """
    a = np.asarray(matrix, dtype=object)
    ref = np.asarray(reference, dtype=float)
    if (a.ndim != 2 or a.shape[0] != a.shape[1] or not a.shape[0]
            or ref.shape != (a.shape[0],) or not np.isfinite(ref).all()
            or type(selected) is not int or not 0 <= selected < a.shape[0]
            or type(max_attempts) is not int or max_attempts < 1):
        raise ValueError('finite reference, square matrix and valid index required')
    n = a.shape[0]
    h = arb_mat(n, n, [arb(x) for x in a.flat])
    if not all(x.is_finite() for x in h.entries()):
        raise ValueError('finite matrix family required')
    center = arb_mat(n, n, [x.mid() for x in h.entries()])
    numeric = np.array([float(x) for x in center.entries()]).reshape(n, n)
    eigenvalues, vectors = np.linalg.eigh(numeric)
    seed = vectors[:, selected]
    if seed @ ref < 0:
        seed = -seed
    p = arb_mat(n, 1, [arb(float(x)) for x in seed])
    lam = arb(float(eigenvalues[selected]))
    for _ in range(4):
        residual = center*p - lam*p
        rhs = arb_mat(n+1, 1, [-x for x in residual.entries()]
                      + [-(p.transpose()*p)[0, 0]/2 + arb(1)/2])
        try:
            step = _bordered(center, p, lam).solve(rhs)
        except (ZeroDivisionError, ValueError) as error:
            raise ArithmeticError('singular midpoint eigenpair proposal') from error
        p = arb_mat(n, 1, [(p[i, 0]+step[i, 0]).mid() for i in range(n)])
        lam = (lam+step[n, 0]).mid()
    norm = (p.transpose()*p)[0, 0].sqrt()
    if not norm > 0:
        raise ArithmeticError('nonzero proposal center required')
    p = arb_mat(n, 1, [(x/norm).mid() for x in p.entries()])
    inverse = _bordered(center, p, lam).inv()
    fixed = arb_mat(n+1, n+1, [x.mid() for x in inverse.entries()])
    residual = h*p - lam*p
    rhs = arb_mat(n+1, 1, residual.entries()+[(p.transpose()*p)[0, 0]/2-arb(1)/2])
    correction = fixed*rhs
    floor = arb(2)**(-ctx.prec//2)
    matrix_scale = max([abs(x).upper() for x in center.entries()]+[floor])
    radii = [max(2*abs(correction[i, 0]).upper(), floor*(1 if i < n else matrix_scale))
             for i in range(n+1)]
    diagnostics = dict(
        matrix_max_radius_upper_rational=str(max(x.rad() for x in h.entries()).upper().fmpq()),
        matrix_max_midpoint_abs_upper_rational=str(matrix_scale.upper().fmpq()),
        initial_vector_radius_max_upper_rational=str(max(radii[:n]).upper().fmpq()),
        initial_eigenvalue_radius_upper_rational=str(radii[n].upper().fmpq()),
        midpoint_selected_eigenvalue_rational=str(lam.fmpq()))
    centers = p.entries()+[lam]
    report = None
    attempts = []
    failure_reason = 'attempt_limit'
    for attempt in range(max_attempts):
        # This is a bounded proposal search, not a theorem that a larger box
        # cannot work. Avoid letting a diverging heuristic obscure the last
        # finite failed inclusion report with a binary64 diagnostic overflow.
        if any(r > 1 for r in radii[:n]):
            failure_reason = 'proposal_vector_radius_exceeds_search_limit'
            break
        boxes = [c+arb(0, r) for c, r in zip(centers, radii, strict=True)]
        if not all(x.is_finite() for x in boxes):
            failure_reason = 'nonfinite_proposed_box'
            break
        try:
            report = verify_eigenpair_box(a, boxes[:n], boxes[n], precision=ctx.prec)
        except RuntimeError as error:
            if 'not finite in binary64' not in str(error):
                raise
            failure_reason = 'inclusion_diagnostic_exceeds_binary64_range'
            break
        attempts.append(dict(attempt=attempt+1,
            maximum_image_radius_ratio_upper=report['maximum_image_radius_ratio_upper'],
            weighted_contraction_upper=report['weighted_contraction_upper']))
        if report['validation_passed']:
            residual_norm = sum((abs(x).upper()**2 for x in residual.entries()), arb(0)).sqrt()
            # No positive gap claim is made. The caller separately proves index
            # and orientation; these legacy diagnostic fields do not certify it.
            return np.array(boxes[:n], dtype=object), boxes[n], 0., math.nextafter(float(residual_norm.upper()), math.inf)
        ratios = [row['image_radius_ratio_upper'] for row in report['rows']]
        if not all(math.isfinite(x) for x in ratios):
            failure_reason = 'nonfinite_inclusion_ratio'
            break
        radii = [r*arb(1.25*x) if x >= 1 else r
                 for r, x in zip(radii, ratios, strict=True)]
    error = ArithmeticError('uniform eigenpair proposal failed independent inclusion')
    error.eigenpair_inclusion = dict(report or {}, proposal_failure_reason=failure_reason,
        proposal_attempts=attempts, proposal_diagnostics=diagnostics, proposal_search_exhausted=True,
        matrix_family_singularity_proved=False, FULL_BHSM_COMPLETE=False)
    raise error


@contextmanager
def use_uniform_proposal(cert, *, selected=24):
    """Install a process-local proposal; the caller must also verify index."""
    original = cert._eigenline
    def proposal(hessian, midpoint, reference):
        return propose(hessian[cert.QDIM:, cert.QDIM:], reference, selected=selected)
    cert._eigenline = proposal
    try:
        yield
    finally:
        cert._eigenline = original
