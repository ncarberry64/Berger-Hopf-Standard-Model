"""Exact local input projection for formal anchor jets, without remainders."""
from contextlib import contextmanager
import numpy as np
from flint import arb, arb_mat
from bhsm.interface.input_linear_anchor_jet import InputLinearJet, ScalarJet
from bhsm.interface.input_linear_anchor_jet import input_linear_anchor_action as dense_action
from bhsm.interface.coupled_action_output_adjoint import FirstJet


@contextmanager
def input_linear_anchor_action(module):
    with dense_action(module):
        original = module._contracted_action

        def contracted(state_values, raw_legs, dense_maps):
            selected = [i for i, leg in enumerate(raw_legs)
                        if any(isinstance(v, InputLinearJet) for v in leg)]
            if not selected:
                return original(state_values, raw_legs, dense_maps)
            if len(selected) != 1:
                raise ValueError('exactly one formal input leg required')
            axis = selected[0]
            template = next(v for v in raw_legs[axis] if isinstance(v, InputLinearJet))
            dimension, derivatives = template.c.ncols(), template.a.nrows()
            if dimension <= module.LOCAL:
                return original(state_values, raw_legs, dense_maps)
            input_matrix = arb_mat(module.STATE, dimension)
            for i, value in enumerate(raw_legs[axis]):
                if isinstance(value, InputLinearJet):
                    if (value.c.ncols() != dimension or value.a.nrows() != derivatives
                            or any(not v.is_zero() for v in value.a.entries())):
                        raise ValueError('base-constant formal input map required')
                    for j in range(dimension):
                        input_matrix[i, j] = value.c[0, j]
                elif isinstance(value, FirstJet):
                    if not value.c.is_zero() or any(not v.is_zero() for v in value.a.entries()):
                        raise ValueError('homogeneous formal input leg required')
                elif not arb(value).is_zero():
                    raise ValueError('homogeneous formal input leg required')
            state = [module._a(v) for v in state_values]
            count = len(raw_legs)
            units = np.array([InputLinearJet(
                arb_mat(1, module.LOCAL, [arb(i == j) for j in range(module.LOCAL)]),
                arb_mat(derivatives, module.LOCAL)) for i in range(module.LOCAL)], dtype=object)
            bulk = module.Mixed.constant(0, count)
            inertia = module.Mixed.constant(0, count)
            for node in range(module.POINTS):
                local = []
                for leg_index, leg in enumerate(raw_legs):
                    if leg_index == axis:
                        local.append(units)
                    else:
                        local.append(np.array([
                            sum((arb(float(mapping[j]))*leg[j] for j in np.flatnonzero(mapping)), arb(0))
                            for mapping in dense_maps[node]], dtype=object))
                mapping = arb_mat(module.LOCAL, module.STATE, [arb(float(v)) for v in dense_maps[node].flat])
                pullback = mapping*input_matrix
                term = module._integrand(state, node, count, local)

                def restore(jet):
                    return module.Mixed(tuple(InputLinearJet(value.c*pullback, value.a*pullback)
                        if isinstance(value, InputLinearJet) else value for value in jet.d))

                bulk += restore(term.bulk)
                inertia += restore(term.inertia)
            action = bulk-(0.25/(2.0*module.HOPF_ORBIT_VOLUME**2))/inertia
            _, boundary = module._boundary(state, count, raw_legs)
            return (action+boundary).d[-1]

        module._contracted_action = contracted
        try:
            yield
        finally:
            module._contracted_action = original
