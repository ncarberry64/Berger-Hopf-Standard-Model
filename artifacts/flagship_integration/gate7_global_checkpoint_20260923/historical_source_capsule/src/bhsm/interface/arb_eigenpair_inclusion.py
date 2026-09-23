"""Verify proposed normalized eigenpair balls without assuming a floating gap."""
import numpy as np
from flint import arb, arb_mat, ctx
from bhsm.interface.current_green_midpoint_coordinate_error import _float_upper


def verify_eigenpair_box(matrix, vector, eigenvalue, *, precision=512, exact_radii=None):
    """Prove a unique normalized real eigenpair in the supplied box.

    For every fixed real matrix in ``matrix``, verify that a preconditioned
    Newton map sends the proposed vector/eigenvalue box strictly into itself
    and contracts in its radius-weighted infinity norm. No eigenvalue gap or
    floating eigensolver result is a proof input. This does not identify the
    eigenpair's index, physical branch, or continuation between parameter boxes.
    """
    if type(precision) is not int or precision < 64:
        raise ValueError('at least 64 bits of arithmetic precision required')
    previous = ctx.prec
    ctx.prec = precision
    try:
        h = np.asarray(matrix, dtype=object)
        p = np.asarray(vector, dtype=object)
        if h.ndim != 2 or h.shape[0] < 1 or h.shape[0] != h.shape[1] or p.shape != (h.shape[0],):
            raise ValueError('square nonempty matrix and matching vector required')
        n = h.shape[0]
        h = arb_mat(n, n, [arb(v) for v in h.flat])
        proposed = [arb(v) for v in p] + [arb(eigenvalue)]
        if not all(v.is_finite() for v in h.entries()+proposed):
            raise ValueError('finite matrix and eigenpair balls required')
        radii = [v.rad() for v in proposed]
        if exact_radii is not None:
            supplied = [arb(v) for v in exact_radii]
            if (len(supplied) != n+1 or any(not r.is_finite() or not r.rad().is_zero()
                    or r <= 0 or r > outer for r, outer in zip(supplied, radii))):
                raise ValueError('exact positive target radii enclosed by the supplied balls required')
            radii = supplied
        if not all(r > 0 for r in radii):
            raise ValueError('strictly positive proposed radii required')
        midpoint = [v.mid() for v in proposed]
        p0 = arb_mat(n, 1, midpoint[:n])
        lam = midpoint[n]
        jacobian = arb_mat(n+1, n+1)
        center_jacobian = arb_mat(n+1, n+1)
        for i in range(n):
            for j in range(n):
                jacobian[i,j] = h[i,j] - (proposed[n] if i == j else 0)
                center_jacobian[i,j] = h[i,j].mid() - (lam if i == j else 0)
            jacobian[i,n] = -proposed[i]
            jacobian[n,i] = proposed[i]
            center_jacobian[i,n] = -midpoint[i]
            center_jacobian[n,i] = midpoint[i]
        try:
            inverse = center_jacobian.inv()
        except (ValueError, ZeroDivisionError) as error:
            raise ArithmeticError('singular eigenpair center Jacobian') from error
        if not all(v.is_finite() for v in inverse.entries()):
            raise ArithmeticError('nonfinite eigenpair center inverse')
        # The fixed preconditioner is an exact dyadic matrix, not an interval
        # chosen independently at each point of the proposed eigenpair box.
        preconditioner = arb_mat(n+1, n+1, [v.mid() for v in inverse.entries()])
        f = h*p0 - lam*p0
        residual = arb_mat(n+1, 1, f.entries()+[(p0.transpose()*p0)[0,0]/2-arb(1)/2])
        step = -preconditioner*residual
        defect = arb_mat(np.eye(n+1, dtype=int).tolist()) - preconditioner*jacobian
        rows = []
        for i, radius in enumerate(radii):
            variation = sum((abs(defect[i,j]).upper()*radii[j] for j in range(n+1)), arb(0))
            image = abs(step[i,0]).upper()+variation
            rows.append(dict(coordinate=i,
                weighted_derivative_row_upper=_float_upper(variation/radius),
                image_radius_ratio_upper=_float_upper(image/radius),
                strict_margin_lower=str((radius-image).lower().fmpq())))
        contraction = max(r['weighted_derivative_row_upper'] for r in rows)
        inclusion = max(r['image_radius_ratio_upper'] for r in rows)
        passed = contraction < 1 and inclusion < 1
        return dict(scope='NORMALIZED_REAL_EIGENPAIR_INCLUSION_IN_SUPPLIED_BALLS_ONLY',
            precision_bits=precision, matrix_dimension=n, rows=rows,
            target_midpoints_rational=[str(v.fmpq()) for v in midpoint],
            target_radii_rational=[str(v.fmpq()) for v in radii],
            weighted_contraction_upper=contraction, maximum_image_radius_ratio_upper=inclusion,
            strict_self_inclusion=bool(inclusion < 1), contraction=bool(contraction < 1),
            normalized_eigenpair_enclosed=bool(passed), validation_passed=bool(passed),
            floating_spectral_gap_assumed=False, full_spectrum_certified=False,
            physical_branch_identification_certified=False,
            physical_Hessian_campaign_certified=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    finally:
        ctx.prec = previous
