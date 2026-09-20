"""Point covectors for the full coupled unnormalized velocity derivative."""
from flint import arb, arb_mat


def directional_covectors(bordered, hard, border, rate_scale, output):
    """Cancel both directional unknown blocks for one velocity covector.

    `bordered` has +psi in its last column. The physical output is
    output^T (b_u psi + b psi_u + s_u h + s h_u). Covectors are chosen
    exact at the working precision; the returned defects retain rounding.
    This point calculation alone is not a uniform enclosure.
    """
    n = bordered.nrows() - 1
    if (n < 1 or bordered.ncols() != n + 1 or len(hard) != n
            or len(output) != n):
        raise ValueError('complete compatible bordered system required')
    hard = [arb(v) for v in hard]
    output = [arb(v) for v in output]
    border, rate_scale = arb(border), arb(rate_scale)
    if any(not v.is_finite() for v in bordered.entries() + hard + output + [border, rate_scale]):
        raise ValueError('finite anchor operands required')
    right3 = arb_mat(n + 1, 1, [rate_scale*v for v in output]
                    + [sum((output[i]*bordered[i, n] for i in range(n)), arb(0))])
    v3 = [v.mid() for v in bordered.transpose().solve(right3).entries()]
    right2 = arb_mat(n + 1, 1,
                    [border*output[i]-border*v3[i]-v3[n]*hard[i] for i in range(n)] + [arb(0)])
    v2 = [v.mid() for v in bordered.transpose().solve(right2).entries()]
    defect2 = right2 - bordered.transpose()*arb_mat(n + 1, 1, v2)
    defect3 = right3 - bordered.transpose()*arb_mat(n + 1, 1, v3)
    return v2, v3, defect2, defect3
