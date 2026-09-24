import importlib.util
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.input_linear_taylor import InputLinearTaylor
from bhsm.interface.local_input_taylor_action_fast import input_linear_taylor_action as reference
from bhsm.interface.local_state_input_taylor_action import input_linear_taylor_action as compressed


def test_common_state_pullback_preserves_derivatives_and_pointwise_remainder():
    previous = ctx.prec
    try:
        ctx.prec = 128
        path = Path(__file__).resolve().parents[1]/'scripts/certify_n12_gate7_accepted_replay_center_outward_74d.py'
        spec = importlib.util.spec_from_file_location('_state_compression_parent', path)
        parent = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = parent
        spec.loader.exec_module(parent)
        domain = TaylorDomain([(0, 60, 'box')], 60)
        state = np.array([domain.affine(0, [arb('1e-6') if j == i % 3 else arb(0)
                                           for j in range(60)]) for i in range(98)], dtype=object)
        leg = np.array([domain.affine(int(i == 37), [arb('1e-7') if j == i % 2 else arb(0)
                                                   for j in range(60)]) for i in range(98)], dtype=object)
        positions = [0, 37, 74]+list(range(1, 14))
        inputs = np.array([InputLinearTaylor(domain,
            arb_mat(1, 16, [int(i == j) for j in positions]), arb_mat(60, 16)) for i in range(98)], dtype=object)
        point = np.array([arb(0)]*98, dtype=object)
        maps = [parent._dense_mapping(parent._integrand(point, n, 0).maps) for n in range(parent.POINTS)]
        original_integrand, original_variables = parent._integrand, parent._local_variables
        for legs in ([inputs], [leg, inputs], [leg, leg, inputs]):
            with reference(parent): old = parent._contracted_action(state, legs, maps)
            with compressed(parent): new = parent._contracted_action(state, legs, maps)
            assert old.c.overlaps(new.c) and old.a.overlaps(new.a)
            for theta in (-1, 1):
                actual_state = np.array([v.c+theta*sum(v.a.entries(), arb(0)) for v in state], dtype=object)
                actual_leg = np.array([v.c+theta*sum(v.a.entries(), arb(0)) for v in leg], dtype=object)
                for j in (0, 1, 2):
                    axis = arb_mat(16, 1, [int(i == j) for i in range(16)])
                    raw = np.array([arb(int(i == positions[j])) for i in range(98)], dtype=object)
                    target = parent._contracted_action(actual_state, [actual_leg]*(len(legs)-1)+[raw], maps)
                    model = new.at_input(axis)
                    enclosure = model.c+theta*sum(model.a.entries(), arb(0))+arb(0, model.r)
                    assert enclosure.contains(target)
            assert parent._integrand is original_integrand
            assert parent._local_variables is original_variables
    finally:
        ctx.prec = previous
