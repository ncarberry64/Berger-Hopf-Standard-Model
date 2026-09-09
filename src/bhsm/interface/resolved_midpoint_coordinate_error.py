"""Keep the retained/complement solve errors separate in a stored pullback."""
import numpy as np
from flint import arb, arb_mat, ctx

from bhsm.interface.current_green_midpoint_coordinate_error import (
    PRECISION, _float_upper, _real_binary64, _squared_norm,
)


def _exact_matrix(values):
    return arb_mat([[arb(float(value)) for value in row] for row in values])


def _block_error_norm(error, start, stop, columns):
    total = arb(0)
    for i in range(start, stop):
        for j in range(columns):
            upper = abs(error[i, j]).upper()
            total += upper * upper
    return total.sqrt().upper()


def _operator_norm_upper(matrix, frobenius_upper):
    # ||A||_2^2 = rho(A A^T) <= ||A A^T||_infinity. Form the
    # signed Gram matrix before taking absolute values, retaining cancellation.
    gram = matrix * matrix.transpose()
    row_upper = max(sum(abs(gram[i, j]) for j in range(gram.ncols())).upper()
                    for i in range(gram.nrows()))
    return min(frobenius_upper, row_upper.sqrt().upper())


def bound_storage_coordinate_cross_error(approximate_norm, error_norm,
                                        output_norm, scalar_column_norm,
                                        projection_error, scalar_addition_error):
    """Cross term when both the UU tensor and its coordinates have errors.

    All six scalar upper bounds require verification by the caller. The result
    is a mapped tensor Frobenius bound, before the pair-input factor two.
    """
    values = [_real_binary64(v, 'nonnegative norm/error bound') for v in (
        approximate_norm, error_norm, output_norm, scalar_column_norm,
        projection_error, scalar_addition_error)]
    if any(v.shape != () or float(v) < 0 for v in values):
        raise ValueError('Finite nonnegative scalar upper bounds required')
    previous = ctx.prec
    ctx.prec = PRECISION
    try:
        a, e, l, ls, q, qs = [arb(float(v)) for v in values]
        return _float_upper((2*a*e + e*e)*(l*q + ls*qs))
    finally:
        ctx.prec = previous


def bound_resolved_coordinate_pullback_error(basis, target, approximate_coordinates,
                                           retained_retained, complement_retained,
                                           complement_complement):
    """Enclose S^-1 M-Xhat directly, then propagate its U/C block norms.

    All six supplied binary64 arrays are exact operands. No direction, tensor,
    output-map construction, or physical neighborhood error is included.
    """
    s, m, x, uu, cu, cc = [
        _real_binary64(value, name) for name, value in (
            ('basis', basis), ('target', target), ('approximate', approximate_coordinates),
            ('UU', retained_retained), ('CU', complement_retained),
            ('CC', complement_complement))]
    if (s.ndim != 2 or s.shape[0] == 0 or s.shape[0] != s.shape[1]
            or m.ndim != 2 or m.shape[0] != s.shape[0] or m.shape[1] == 0
            or x.shape != m.shape or uu.ndim != 3 or cc.ndim != 3):
        raise ValueError('Compatible nonempty square-basis pullback operands required')
    outputs, retained, _ = uu.shape
    complement = cc.shape[1]
    if (outputs == 0 or retained == 0 or complement == 0
            or uu.shape != (outputs, retained, retained)
            or cu.shape != (outputs, complement, retained)
            or cc.shape != (outputs, complement, complement)
            or retained + complement != s.shape[0]):
        raise ValueError('Compatible retained/complement tensor blocks required')
    previous = ctx.prec
    ctx.prec = PRECISION
    try:
        matrix = _exact_matrix(s)
        inverse = matrix.inv()
        identity = arb_mat([[int(i == j) for j in range(s.shape[0])]
                            for i in range(s.shape[0])])
        residual = identity - matrix * inverse
        residual_upper = max(sum(abs(residual[i, j]) for j in range(s.shape[0])).upper()
                             for i in range(s.shape[0]))
        if not (residual_upper.is_finite() and residual_upper < 1):
            raise RuntimeError('Stored basis inverse could not be certified')
        approximate_matrix = _exact_matrix(x)
        error = inverse * _exact_matrix(m) - approximate_matrix
        if not all(error[i, j].is_finite() for i in range(m.shape[0])
                   for j in range(m.shape[1])):
            raise RuntimeError('Coordinate error enclosure is not finite')
        eu = _block_error_norm(error, 0, retained, m.shape[1])
        ec = _block_error_norm(error, retained, s.shape[0], m.shape[1])
        au = _squared_norm(x[:retained]).sqrt().upper()
        ac = _squared_norm(x[retained:]).sqrt().upper()
        def block(matrix, start, stop):
            return arb_mat([[matrix[i, j] for j in range(m.shape[1])]
                            for i in range(start, stop)])

        eu_op = _operator_norm_upper(block(error, 0, retained), eu)
        ec_op = _operator_norm_upper(block(error, retained, s.shape[0]), ec)
        au_op = _operator_norm_upper(block(approximate_matrix, 0, retained), au)
        ac_op = _operator_norm_upper(block(approximate_matrix, retained, s.shape[0]), ac)
        quu, qcu, qcc = [_squared_norm(v).sqrt().upper() for v in (uu, cu, cc)]
        terms = [quu * (2*au_op*eu_op + eu_op*eu_op),
                 2*qcu * (au_op*ec_op + ac_op*eu_op + eu_op*ec_op),
                 qcc * (2*ac_op*ec_op + ec_op*ec_op)]
        return dict(
            scope='RESOLVED_COORDINATE_ERROR_THROUGH_EXACT_STORED_BINARY64_TENSOR_ONLY',
            arithmetic_precision_bits=PRECISION,
            inverse_residual_infinity_upper=_float_upper(residual_upper),
            retained_coordinate_error_frobenius_upper=_float_upper(eu),
            complement_coordinate_error_frobenius_upper=_float_upper(ec),
            approximate_retained_coordinates_frobenius_upper=_float_upper(au),
            approximate_complement_coordinates_frobenius_upper=_float_upper(ac),
            retained_coordinate_error_operator_norm_upper=_float_upper(eu_op),
            complement_coordinate_error_operator_norm_upper=_float_upper(ec_op),
            approximate_retained_coordinates_operator_norm_upper=_float_upper(au_op),
            approximate_complement_coordinates_operator_norm_upper=_float_upper(ac_op),
            tensor_block_frobenius_upper=[_float_upper(v) for v in (quu, qcu, qcc)],
            pullback_error_block_contributions_upper=[_float_upper(v) for v in terms],
            pullback_coordinate_error_frobenius_upper=_float_upper(sum(terms)),
            coordinate_bound_requires_external_verification=False,
            physical_Hessian_error_enclosed=False,
            physical_direction_construction_rounding_enclosed=False,
            pullback_assembly_rounding_enclosed=False,
            causal_transport_enclosed=False, neighborhood_remainder_enclosed=False,
            Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    finally:
        ctx.prec = previous
