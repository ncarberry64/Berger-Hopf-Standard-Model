"""Propagate local error balls through exact stored causal maps at 512 bits."""
from __future__ import annotations

import numpy as np
from flint import arb, arb_mat, ctx

from bhsm.interface.current_green_midpoint_coordinate_error import (
    PRECISION, _float_upper, _real_binary64,
)


def _norm_upper(matrix):
    """Outward operator bound, also valid for interval-valued products."""
    absolute = [[abs(matrix[i, j]).upper() for j in range(matrix.ncols())]
                for i in range(matrix.nrows())]
    squared = sum(x*x for row in absolute for x in row)
    one = max(sum(row[j] for row in absolute).upper()
              for j in range(matrix.ncols()))
    infinity = max(sum(row).upper() for row in absolute)
    return min(squared.sqrt().upper(), (one*infinity).sqrt().upper())


def transport_local_errors(maps, local_bounds, block_size=10):
    """Bound z[k+1]=P[k]z[k]+d[k], z[0]=0, ||d[k]|| <= local_bounds[k].

    Products retain their signed entries within each block and between block
    boundaries. Only independent source errors are joined by triangle bounds.
    The result also applies to a uniform quadratic error coefficient: divide
    each local response by the same squared block-sup input radius.

    All binary64 inputs are exact here. The caller owns the local bounds and
    physical map construction. No physical Hessian or full proof is certified.
    """
    matrices = _real_binary64(maps, 'causal maps')
    bounds = _real_binary64(local_bounds, 'local bounds')
    if (matrices.ndim != 3 or min(matrices.shape) == 0
            or matrices.shape[1] != matrices.shape[2]
            or bounds.shape != (matrices.shape[0],) or np.any(bounds < 0)):
        raise ValueError('nonempty square maps and matching nonnegative bounds required')
    if (isinstance(block_size, bool) or not isinstance(block_size, (int, np.integer))
            or block_size < 1):
        raise ValueError('positive integer block size required')
    previous = ctx.prec
    ctx.prec = PRECISION
    try:
        count, dimension, _ = matrices.shape
        identity = arb_mat(np.eye(dimension, dtype=int).tolist())
        exact = [arb_mat(m.tolist()) for m in matrices]
        errors = [arb(float(x)) for x in bounds]
        starts = list(range(0, count, block_size))
        macro_maps, macro_errors = [], []
        prefix_norm = [arb(1)] * (count+1)
        partial = [arb(0)] * (count+1)
        for start in starts:
            stop = min(start+block_size, count)
            prefix = identity
            for node in range(start+1, stop+1):
                prefix = exact[node-1] * prefix
                prefix_norm[node] = _norm_upper(prefix)
                # Source s is injected after map P[s]. Its suffix starts
                # with P[s+1], never with P[s]. An empty suffix has norm 1.
                suffix, radius = identity, errors[node-1]
                for source in range(node-2, start-1, -1):
                    suffix = suffix * exact[source+1]
                    radius += _norm_upper(suffix) * errors[source]
                partial[node] = radius.upper()
            macro_maps.append(prefix)
            macro_errors.append(partial[stop])

        boundary = [arb(0)]
        for target in range(len(starts)):
            suffix, radius = identity, macro_errors[target]
            for source in range(target-1, -1, -1):
                suffix = suffix * macro_maps[source+1]
                radius += _norm_upper(suffix) * macro_errors[source]
            boundary.append(radius.upper())

        result = [0.0] * (count+1)
        for block, start in enumerate(starts):
            stop = min(start+block_size, count)
            for node in range(start+1, stop):
                result[node] = _float_upper(prefix_norm[node]*boundary[block]+partial[node])
            result[stop] = _float_upper(boundary[block+1])
        return dict(
            scope='LOCAL_ERROR_BALLS_THROUGH_EXACT_STORED_CAUSAL_MAPS_ONLY',
            arithmetic_precision_bits=PRECISION, block_size=int(block_size),
            node_error_norm_upper=result,
            maximum_node_error_norm_upper=max(result),
            local_error_bounds_require_external_verification=True,
            physical_Hessian_error_enclosed=False,
            map_construction_rounding_enclosed=False,
            center_covariance_rounding_enclosed=False,
            neighborhood_remainder_enclosed=False,
            Gate7_closed=False, FULL_BHSM_COMPLETE=False,
        )
    finally:
        ctx.prec = previous
