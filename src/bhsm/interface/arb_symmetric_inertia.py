"""Verified inertia and eigenvalue index for real symmetric matrix enclosures."""
import numpy as np
from flint import arb, arb_mat, ctx
from bhsm.interface.current_green_midpoint_coordinate_error import _real_binary64


def symmetric_enclosure(matrix):
    values = np.asarray(matrix, dtype=object)
    if values.ndim != 2 or values.shape[0] == 0 or values.shape[0] != values.shape[1]:
        raise ValueError('nonempty square symmetric matrix enclosure required')
    result = np.array([arb(v) for v in values.flat], dtype=object).reshape(values.shape)
    if not all(v.is_finite() for v in result.flat):
        raise ValueError('finite matrix entries required')
    for i in range(len(result)):
        for j in range(i):
            # The domain is the real symmetric matrices enclosed entrywise.
            # Reject an empty symmetric domain instead of proving vacuously.
            value = result[i, j].intersection(result[j, i])
            result[i, j] = value
            result[j, i] = value
    return result


def shifted_inertia(matrix, shift, *, basis=None, precision=512):
    """Count signs of H-shift*I uniformly over a symmetric interval family.

    A fixed exact binary64 basis may improve conditioning. Its determinant
    must exclude zero in Arb; no floating orthogonality is assumed. Symmetric
    elimination uses only pivots whose sign is strictly established. Failure
    of a 1x1 pivot strategy is unresolved, not a claim of singularity.
    """
    if type(precision) is not int or precision < 64:
        raise ValueError('at least 64 bits of precision required')
    previous = ctx.prec
    ctx.prec = precision
    try:
        h = symmetric_enclosure(matrix)
        n = len(h)
        threshold = arb(shift)
        if not threshold.is_finite() or not threshold.rad().is_zero():
            raise ValueError('exact finite shift required')
        b = np.eye(n) if basis is None else _real_binary64(basis, 'basis')
        if b.shape != (n, n):
            raise ValueError('square matching basis required')
        change = arb_mat(b.tolist())
        determinant = change.det()
        if not determinant.is_finite() or determinant.contains(0):
            raise ArithmeticError('basis nonsingularity unresolved')
        original = arb_mat(n, n, list(h.flat))
        transformed = change.transpose()*original*change-threshold*(change.transpose()*change)
        work = symmetric_enclosure(np.array(transformed.entries(), dtype=object).reshape(n, n))
        order = list(range(n))
        rows = []
        negative = 0
        for k in range(n):
            candidates = [j for j in range(k, n) if work[j, j] > 0 or work[j, j] < 0]
            if not candidates:
                raise ArithmeticError(f'symmetric inertia unresolved at pivot {k}; no signed 1x1 pivot')
            chosen = max(candidates, key=lambda j: abs(work[j, j]).lower())
            if chosen != k:
                work[[k, chosen], :] = work[[chosen, k], :]
                work[:, [k, chosen]] = work[:, [chosen, k]]
                order[k], order[chosen] = order[chosen], order[k]
            pivot = work[k, k]
            is_negative = bool(pivot < 0)
            negative += is_negative
            rows.append(dict(step=k, basis_coordinate=order[k], sign=-1 if is_negative else 1,
                pivot_lower_rational=str(pivot.lower().fmpq()), pivot_upper_rational=str(pivot.upper().fmpq())))
            for i in range(k+1, n):
                factor = work[i, k]/pivot
                for j in range(i, n):
                    value = work[i, j]-factor*work[j, k]
                    work[i, j] = value
                    work[j, i] = value
        return dict(scope='INERTIA_OF_REAL_SYMMETRIC_ENTRYWISE_MATRIX_ENCLOSURE',
            precision_bits=precision, dimension=n, shift_rational=str(threshold.fmpq()),
            negative=negative, positive=n-negative, zero=0, pivots=rows,
            basis_nonsingularity_verified=True, floating_orthogonality_assumed=False,
            inertia_verified=True, physical_branch_continuation_certified=False,
            Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    finally:
        ctx.prec = previous


def isolate_index(matrix, lower, upper, expected_index, *, basis=None, precision=512):
    """Verify exactly one eigenvalue, of the requested zero-based index, inside."""
    n = np.asarray(matrix).shape[0]
    if type(expected_index) is not int or not 0 <= expected_index < n:
        raise ValueError('valid zero-based eigenvalue index required')
    previous = ctx.prec
    ctx.prec = precision
    try:
        lo, hi = arb(lower), arb(upper)
        if not lo < hi:
            raise ValueError('strictly ordered eigenvalue endpoints required')
        left = shifted_inertia(matrix, lo, basis=basis, precision=precision)
        right = shifted_inertia(matrix, hi, basis=basis, precision=precision)
        count = right['negative']-left['negative']
        passed = count == 1 and left['negative'] == expected_index
        return dict(scope='ISOLATED_EIGENVALUE_INDEX_IN_REAL_SYMMETRIC_MATRIX_ENCLOSURE',
            expected_zero_based_index=expected_index, enclosed_eigenvalue_count=count,
            index_below_lower_endpoint=left['negative'], lower_inertia=left, upper_inertia=right,
            validation_passed=bool(passed), floating_spectral_gap_assumed=False,
            physical_branch_continuation_certified=False,
            Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    finally:
        ctx.prec = previous
