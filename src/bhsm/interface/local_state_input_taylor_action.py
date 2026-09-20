"""Experimental local state compression with exact common-state pullback.

Only the local remainder sees independent normalized scalar coordinates.
Every affine state coefficient is restored before bulk and global inertia
are assembled. Original physical parameters and the boundary remain intact.
"""
from contextlib import contextmanager
import hashlib
from pathlib import Path
import numpy as np
from flint import arb, arb_mat
from bhsm.interface.shared_action_taylor import Taylor, TaylorDomain
from bhsm.interface.input_linear_taylor import InputLinearTaylor
import bhsm.interface.local_input_taylor_action_fast as input_action

INPUT_ACTION_SHA256 = 'A00276735242AC5985212D4A50EB192E3CE447002E8B8AC3DCDC52F3BBC71EAD'


@contextmanager
def input_linear_taylor_action(module):
    if hashlib.sha256(Path(input_action.__file__).read_bytes()).hexdigest().upper() != INPUT_ACTION_SHA256:
        raise ValueError('reviewed input compression required')
    with input_action.input_linear_taylor_action(module):
        original_integrand = module._integrand
        original_variables = module._local_variables

        def integrand(state, node, directions, leg_values=None):
            if leg_values is None:
                return original_integrand(state, node, directions, leg_values)
            captured = {}

            def variables(values, count, legs):
                flat = list(values)+[v for leg in legs for v in leg]
                domains = [v.domain for v in flat if isinstance(v, (Taylor, InputLinearTaylor))]
                if not domains:
                    return original_variables(values, count, legs)
                original_domain = domains[0]
                if any(d is not original_domain for d in domains):
                    raise ValueError('one common original state domain required')
                active = []
                for v in flat:
                    if isinstance(v, InputLinearTaylor):
                        if not v.r.is_zero() or any(not x.is_zero() for x in v.a.entries()):
                            raise ValueError('state-constant local input leg required')
                    if isinstance(v, Taylor) and not v.linear_bound().is_zero():
                        active.append(v)
                size = max(1, len(active))
                if size >= original_domain.dimension:
                    return original_variables(values, count, legs)
                domain = TaylorDomain([(0, size, 'box')], size)
                transform = arb_mat(size, original_domain.dimension)
                cursor = 0

                def compress(value):
                    nonlocal cursor
                    if isinstance(value, InputLinearTaylor):
                        return InputLinearTaylor(domain, value.c,
                            arb_mat(size, value.c.ncols()), value.r, value.input_groups)
                    if not isinstance(value, Taylor):
                        return value
                    width = value.linear_bound()
                    coefficients = [arb(0)]*size
                    if not width.is_zero():
                        coefficients[cursor] = width
                        for j in range(original_domain.dimension):
                            transform[cursor, j] = value.a[0, j]/width
                        cursor += 1
                    return Taylor(domain, value.c, arb_mat(1, size, coefficients), value.r)

                mapped_values = [compress(v) for v in values]
                mapped_legs = [np.array([compress(v) for v in leg], dtype=object) for leg in legs]
                captured.update(original=original_domain, compressed=domain, transform=transform)
                return original_variables(mapped_values, count, mapped_legs)

            module._local_variables = variables
            try:
                term = original_integrand(state, node, directions, leg_values)
            finally:
                module._local_variables = original_variables
            if not captured:
                return term
            transform = captured['transform']

            def restore(jet):
                values = []
                for value in jet.d:
                    if isinstance(value, InputLinearTaylor):
                        if value.domain is not captured['compressed']:
                            raise ValueError('unexpected local input-state domain')
                        value = InputLinearTaylor(captured['original'], value.c,
                            transform.transpose()*value.a, value.r, value.input_groups)
                    elif isinstance(value, Taylor):
                        if value.domain is not captured['compressed']:
                            raise ValueError('unexpected local scalar-state domain')
                        value = Taylor(captured['original'], value.c, value.a*transform, value.r)
                    values.append(value)
                return module.Mixed(tuple(values))

            return module.LocalTerm(term.maps, term.values, restore(term.bulk), restore(term.inertia))

        module._integrand = integrand
        try:
            yield
        finally:
            module._integrand = original_integrand
            module._local_variables = original_variables
