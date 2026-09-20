"""Signed HS transport in fixed retained frames, with both endpoint sides.

These are algebraic identities. A caller must supply uniform enclosures and
their common parameter domain; this module does not certify a physical path.
"""
from flint import arb, arb_mat


def transport_coefficients(QP, Q, E, M, h, A0, U, *, side, frozen_left=None):
    """Return C,D such that the complete block is C+B+D(A-A0).

    B=(2h/3) QP DF_mid U. The endpoint action A=DF_side E and the
    midpoint derivative M must refer to the same physical state family.
    U is an exact proposed input map; its entire mismatch is retained.
    """
    h = arb(h)
    if side not in ('left', 'right') or not h > 0 or not h.rad().is_zero():
        raise ValueError('explicit endpoint side and positive exact step required')
    n, k, outputs = E.nrows(), E.ncols(), Q.nrows()
    if ((QP.nrows(), QP.ncols()) != (outputs, n)
            or Q.ncols() != k
            or (M.nrows(), M.ncols()) != (n, n)
            or any((v.nrows(), v.ncols()) != (n, k) for v in (A0, U))):
        raise ValueError('compatible complete input and output maps required')
    PM = QP*M*(2*h/3)
    sign = 1 if side == 'left' else -1
    coefficient = QP*(h/6)+PM*(sign*h/8)
    if side == 'left':
        if frozen_left is None or (frozen_left.nrows(), frozen_left.ncols()) != (n, n):
            raise ValueError('the retained frozen left Jacobian is required')
        identity = arb_mat(n, n, [int(i == j) for i in range(n) for j in range(n)])
        constant = QP*(frozen_left+identity)*E
    else:
        if frozen_left is not None:
            raise ValueError('a frozen left Jacobian belongs only to the left block')
        constant = Q-QP*E
    fixed = constant+QP*A0*(h/6)+PM*(E/2+A0*(sign*h/8)-U)
    return fixed, coefficient
