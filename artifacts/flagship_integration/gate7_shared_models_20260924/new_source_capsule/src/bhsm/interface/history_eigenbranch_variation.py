"""Hermite--Simpson domains and componentwise anchored eigenbranch tests."""
from flint import arb
from bhsm.interface.affine_eigenpair_contraction import nonlinear_eigenpair_variation


def hermite_history(left, right, left_rate, right_rate, step, tau):
    """Cubic Hermite history, with the large straight-line terms canceled first.

    At tau=1/2 this is exactly the repository's physical HS midpoint. Rates
    and states must be in the same coordinates and retain their parameter IDs.
    """
    if not len(left) == len(right) == len(left_rate) == len(right_rate):
        raise ValueError('matching state and rate dimensions required')
    result = []
    for a, b, f, g in zip(left, right, left_rate, right_rate, strict=True):
        delta = b-a
        bend = (1-tau)*(step*f-delta)-tau*(step*g-delta)
        result.append(a+tau*delta+tau*(1-tau)*bend)
    return result


def row_certificate(Y_anchor, defect, inverse, weights, residual_variation,
                    hessian_variation, reference, eigenpair_center):
    """Use the saved point defect plus NEW segment terms, not q0 plus q0 again.

    Y_anchor safely bounds the point residual, although it also contains the
    inherited local state contribution. Uniformly enlarging the eigenpair
    witness changes no physical radius and needs no new action contraction.
    Hessian variation is linear in its eta box; the exact border term is
    quadratic in witness radii, as in the existing affine Banach certificate.
    """
    n = len(weights)
    if n != 62 or len(residual_variation) != n or len(hessian_variation) != n:
        raise ValueError('complete bordered row operands required')
    D = [sum((abs(defect[i, j]).upper()*weights[j] for j in range(n)), arb(0)).upper()
         for i in range(n)]
    N = nonlinear_eigenpair_variation(inverse, weights)
    Y = [(y+s).upper() for y, s in zip(Y_anchor, residual_variation, strict=True)]
    fixed = max(((d+s)/w).upper() for d, s, w in zip(D, hessian_variation, weights, strict=True))
    alpha = arb(1)
    if fixed < 1:
        y = max((v/w).upper() for v, w in zip(Y, weights, strict=True))
        alpha = max(arb(1), (2*y/(1-fixed)).upper())
    rows = []
    for i in range(n):
        radius = alpha*weights[i]
        variation = (alpha*(D[i]+hessian_variation[i])+alpha**2*N[i]).upper()
        rows.append(dict(coordinate=i, residual_upper=Y[i],
            preconditioned_H_variation_upper=(alpha*hessian_variation[i]).upper(),
            point_defect_upper=(alpha*D[i]).upper(),
            eigenpair_and_normalization_border_upper=(alpha**2*N[i]).upper(),
            total_derivative_variation_upper=variation,
            weighted_contraction_upper=(variation/radius).upper(),
            inclusion_margin_lower=(radius-Y[i]-variation).lower(),
            contraction_margin_lower=(radius-variation).lower()))
    orientation = (sum((eigenpair_center[i]*reference[i] for i in range(61)), arb(0))
                   -alpha*sum((weights[i]*abs(reference[i]).upper() for i in range(61)), arb(0))).lower()
    return dict(rows=rows, eigenpair_witness_scale=alpha,
        preconditioned_H_variation_norm_upper=max((s/w).upper() for s, w in zip(hessian_variation, weights, strict=True)),
        fixed_point_defect_plus_H_variation_upper=fixed,
        contraction_upper=max(r['weighted_contraction_upper'] for r in rows),
        contraction_margin_lower=(1-max(r['weighted_contraction_upper'] for r in rows)).lower(),
        original_reference_overlap_lower=orientation,
        validation_passed=bool(orientation>0 and all(r['inclusion_margin_lower']>0 and r['contraction_margin_lower']>0 for r in rows)))
