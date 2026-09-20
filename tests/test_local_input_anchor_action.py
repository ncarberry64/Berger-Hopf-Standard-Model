import importlib.util
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx
from bhsm.interface.input_linear_anchor_jet import ScalarJet, InputLinearJet
from bhsm.interface.local_input_anchor_action import input_linear_anchor_action


def test_local_anchor_projection_retains_full_action_and_base_derivatives():
    previous = ctx.prec
    try:
        ctx.prec = 128
        path = Path(__file__).resolve().parents[1]/'scripts/certify_n12_gate7_accepted_replay_center_outward_74d.py'
        spec = importlib.util.spec_from_file_location('_local_anchor_action_parent', path)
        parent = importlib.util.module_from_spec(spec);sys.modules[spec.name] = parent
        spec.loader.exec_module(parent)
        point = np.array([arb(0)]*98, dtype=object)
        state = np.array([ScalarJet(arb(0), arb_mat([[arb(i == 0)]])) for i in range(98)], dtype=object)
        u = np.array([InputLinearJet(arb_mat(1, 16, [arb(i == 37+j) for j in range(16)]), arb_mat(1, 16))
                      for i in range(98)], dtype=object)
        left = np.array([arb(i == 37) for i in range(98)], dtype=object)
        maps = [parent._dense_mapping(parent._integrand(point, node, 0).maps) for node in range(parent.POINTS)]
        original = parent._contracted_action
        for order in (1, 2, 3):
            with input_linear_anchor_action(parent):
                value = parent._contracted_action(state, [left]*(order-1)+[u], maps)
            for column in (0, 3, 15):
                raw = np.array([arb(i == 37+column) for i in range(98)], dtype=object)
                direction = np.array([arb(i == 0) for i in range(98)], dtype=object)
                assert value.c[0, column].overlaps(original(point, [left]*(order-1)+[raw], maps))
                assert value.a[0, column].overlaps(original(point, [left]*(order-1)+[raw, direction], maps))
        assert parent._contracted_action is original
        changing_left = np.array([ScalarJet(arb(i == 37), arb_mat([[arb(i == 38)]]))
                                  for i in range(98)], dtype=object)
        with input_linear_anchor_action(parent):
            value = parent._contracted_action(state, [changing_left, changing_left, u], maps)
        direction = np.array([arb(i == 0) for i in range(98)], dtype=object)
        left_change = np.array([arb(i == 38) for i in range(98)], dtype=object)
        for column in (0, 3, 15):
            raw = np.array([arb(i == 37+column) for i in range(98)], dtype=object)
            expected = original(point, [left, left, raw, direction], maps)
            expected += 2*original(point, [left_change, left, raw], maps)
            assert value.a[0, column].overlaps(expected)
    finally:
        ctx.prec = previous
