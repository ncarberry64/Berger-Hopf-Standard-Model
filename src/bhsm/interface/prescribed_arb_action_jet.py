"""Retained-action mixed jets with prescribed, possibly varying directions.

This evaluates the existing action expression. It introduces no action term
and no binary64 replacement for Arb arithmetic.
"""
import math
import numpy as np
from flint import arb


def _arb_entries(values):
    array = np.asarray(values, dtype=object)
    result = np.empty(array.shape, dtype=object)
    for index in np.ndindex(array.shape):
        value = array[index]
        value = value if isinstance(value, arb) else arb(float(value))
        if not value.is_finite():
            raise ArithmeticError("prescribed action derivatives must be finite")
        result[index] = value
    return result


def _project(module, mapping, derivatives, axis_sizes):
    """Enclose all prescribed derivative maps in one signed Arb product."""
    keys = sorted(derivatives)
    shapes = [tuple(n if mask & (1 << i) else 1
                    for i, n in enumerate(axis_sizes)) for mask in keys]
    widths = [math.prod(shape) for shape in shapes]
    stacked = np.concatenate([
        derivatives[mask].reshape(module.STATE, width)
        for mask, width in zip(keys, widths, strict=True)
    ], axis=1)
    product = module._array(module._mat(mapping) * module._mat(stacked))
    result = {}; offset = 0
    for mask, shape, width in zip(keys, shapes, widths, strict=True):
        result[mask] = product[:, offset:offset+width].reshape(
            (len(mapping), *shape))
        offset += width
    return result


def prescribed_action_jet(module, state, dense_maps, axis_sizes, derivatives,
                          *, lower_local_axes=True):
    """Return every mixed derivative of the frozen action under a formal jet.

    ``derivatives[mask]`` is a derivative, not a factorial-scaled coefficient.
    Each variable occurs at most once, so their subset algebra has no repeated
    variable factorial. Its shape is (STATE, n0, ..., nr), with ni equal to the
    axis size for a set bit and one otherwise. Unspecified masks are exactly
    zero in this explicitly supplied polynomial path, not missing physical data.

    The caller must supply every nonzero derivative of its chosen path.
    This routine certifies evaluation of that path only. The temporary local
    variable constructor is restored on every exit; use in an isolated process.
    """
    axis_sizes = tuple(axis_sizes)
    if not axis_sizes or any(type(n) is not int or n < 1 for n in axis_sizes):
        raise ValueError("positive integer axis sizes required")
    directions = len(axis_sizes)
    state = _arb_entries(state)
    if state.shape != (module.STATE,):
        raise ValueError("state shape does not match retained action")
    if not derivatives:
        raise ValueError("an explicit nonempty prescribed derivative path is required")
    prepared = {}
    for mask, values in derivatives.items():
        if type(mask) is not int or not 0 < mask < (1 << directions):
            raise ValueError("invalid prescribed derivative mask")
        expected = (module.STATE, *(
            n if mask & (1 << i) else 1 for i, n in enumerate(axis_sizes)))
        values = _arb_entries(values)
        if values.shape != expected:
            raise ValueError(f"derivative {mask} shape must be {expected}")
        prepared[mask] = values
    if len(dense_maps) != module.POINTS:
        raise ValueError("all frozen quadrature maps are required")
    for mapping in dense_maps:
        if np.shape(mapping) != (module.LOCAL, module.STATE):
            raise ValueError("invalid retained quadrature map shape")

    # Obtain the original boundary maps without installing the prescribed jet.
    boundary_maps, _ = module._boundary(state, 0)
    boundary_dense = np.empty((len(boundary_maps), module.STATE), dtype=object)
    boundary_dense.fill(arb(0))
    for row, mapping in enumerate(boundary_maps):
        for column, value in mapping:
            boundary_dense[row, column] += value

    original_variables = module._local_variables
    projected = None

    # A constant input direction enters a local integrand only through its
    # LOCAL-dimensional image. Differentiate in that local basis, then apply
    # its exact stored linear map. Curved directions are never lowered.
    lowered = [i for i, size in enumerate(axis_sizes)
               if lower_local_axes and size > module.LOCAL
               and (1 << i) in prepared
               and all(mask == (1 << i) or not mask & (1 << i)
                       for mask in prepared)]

    def lower(mapping):
        nonlocal projected
        projected = _project(module, mapping, prepared, axis_sizes)
        lifts = {}
        local_size = len(mapping)
        for axis in lowered:
            bit = 1 << axis
            lifts[axis] = module._mat(projected[bit].reshape(
                local_size, axis_sizes[axis])).transpose()
            shape = (local_size, *(
                local_size if i == axis else 1 for i in range(directions)))
            identity = np.empty((local_size, local_size), dtype=object)
            identity.fill(arb(0))
            for i in range(local_size): identity[i, i] = arb(1)
            projected[bit] = identity.reshape(shape)
        return lifts

    def lift(value, lifts):
        if not lifts: return value
        data = list(value.d)
        for mask in range(1, len(data)):
            array = np.asarray(data[mask], dtype=object)
            if array.ndim == 0 and any(mask & (1 << i) for i in lifts):
                if not isinstance(array.item(), arb) or not array.item().is_zero():
                    raise ArithmeticError("unexpected scalar in a lowered tensor derivative")
                shape = tuple(n if mask & (1 << i) else 1
                              for i, n in enumerate(axis_sizes))
                data[mask] = np.full(shape, arb(0), dtype=object)
                continue
            for axis, mapping in lifts.items():
                if not mask & (1 << axis): continue
                array = np.moveaxis(array, axis, 0)
                trailing = array.shape[1:]
                product = module._array(mapping * module._mat(
                    array.reshape(mapping.ncols(), -1)))
                array = np.moveaxis(product.reshape(
                    mapping.nrows(), *trailing), 0, axis)
            data[mask] = array if array.ndim else array.item()
        return module.Mixed(tuple(data))

    def variables(values, count, leg_values):
        if count != directions or leg_values is not None or projected is None:
            raise ValueError("unexpected local-variable call during prescribed evaluation")
        result = []
        for index, value in enumerate(values):
            data = [arb(0) for _ in range(1 << directions)]
            data[0] = value
            for mask, entries in projected.items():
                data[mask] = entries[index]
            result.append(module.Mixed(tuple(data)))
        return result

    module._local_variables = variables
    try:
        bulk = module.Mixed.constant(0, directions)
        inertia = module.Mixed.constant(0, directions)
        for node, mapping in enumerate(dense_maps):
            lifts = lower(mapping)
            term = module._integrand(state, node, directions, None)
            bulk += lift(term.bulk, lifts)
            inertia += lift(term.inertia, lifts)
        # Preserve the exact binary64 constant used by the original producer.
        action = bulk - (0.25 / (2.0 * module.HOPF_ORBIT_VOLUME**2)) / inertia
        lifts = lower(boundary_dense)
        _, boundary = module._boundary(state, directions, None)
        return action + lift(boundary, lifts)
    finally:
        module._local_variables = original_variables


def batched_scalar_curvature(module, state, dense_maps, raw_u, raw_v,
                             p, p_u, p_v, p_uv, last, last_u, last_v, last_uv):
    """D3(action)[p,p,last] and its u, v, uv derivatives in one action call."""
    count = np.shape(raw_v)[1]
    axes = (1, 1, 2, 1, count)
    values = {}

    def put(mask, value):
        shape = (module.STATE, *(
            n if mask & (1 << i) else 1 for i, n in enumerate(axes)))
        values[mask] = np.asarray(value, dtype=object).reshape(shape)

    for bit in (1, 2):
        put(bit, p)
        put(bit | 8, p_u)
        put(bit | 16, p_v)
        put(bit | 8 | 16, p_uv)
    put(4, last); put(4 | 8, last_u)
    # The existing kernel flattens STATE x count x 2 with paired columns.
    last_v = np.asarray(last_v, dtype=object).reshape(module.STATE, count, 2)
    last_uv = np.asarray(last_uv, dtype=object).reshape(module.STATE, count, 2)
    put(4 | 16, np.swapaxes(last_v, 1, 2))
    put(4 | 8 | 16, np.swapaxes(last_uv, 1, 2))
    put(8, raw_u); put(16, raw_v)
    result = prescribed_action_jet(module, state, dense_maps, axes, values)
    return (np.asarray(result.d[7], dtype=object).reshape(2),
            np.asarray(result.d[15], dtype=object).reshape(2),
            np.asarray(result.d[23], dtype=object).reshape(2, count).T,
            np.asarray(result.d[31], dtype=object).reshape(2, count).T)


def batched_fixed_contractions(module, state, dense_maps, output, fixed, u, v):
    """D3[output,fixed,u/v] and D4[output,fixed,u,v] in one action call."""
    axes = (output.shape[1], fixed.shape[1], 1, v.shape[1])
    values = {}
    for index, value in enumerate((output, fixed, u, v)):
        shape = (module.STATE, *(
            n if index == j else 1 for j, n in enumerate(axes)))
        values[1 << index] = np.asarray(value, dtype=object).reshape(shape)
    result = prescribed_action_jet(module, state, dense_maps, axes, values)
    return (np.asarray(result.d[7], dtype=object).reshape(axes[:2]),
            np.asarray(result.d[11], dtype=object).reshape(*axes[:2], axes[3]),
            np.asarray(result.d[15], dtype=object).reshape(*axes[:2], axes[3]))


def batched_first_variation_contractions(module, state, dense_maps, output,
                                        p_v, q_v, h_v, p_u, q_u, h_u, u, v):
    """Group three same-order contractions for each outer physical direction."""
    count = v.shape[1]
    varied_v = np.stack((p_v, q_v, h_v), axis=1).reshape(module.STATE, 3*count)
    varied_u = np.column_stack((p_u, q_u, h_u))
    first = affine_action_contraction(module, state, dense_maps, output,
                                      varied_v, u).reshape(output.shape[1], 3, count)
    second = affine_action_contraction(module, state, dense_maps, output,
                                       varied_u, v).reshape(output.shape[1], 3, count)
    return tuple(first[:, i, :] for i in range(3)) + tuple(
        second[:, i, :] for i in range(3))


def affine_action_contraction(module, state, dense_maps, *legs):
    """An ordinary multilinear action derivative with local-axis lowering."""
    axes = tuple(1 if np.ndim(value) == 1 else np.shape(value)[1] for value in legs)
    values = {}
    for index, value in enumerate(legs):
        shape = (module.STATE, *(
            n if index == j else 1 for j, n in enumerate(axes)))
        values[1 << index] = np.asarray(value, dtype=object).reshape(shape)
    return np.asarray(prescribed_action_jet(
        module, state, dense_maps, axes, values).d[-1], dtype=object)
