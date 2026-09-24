"""The arbitrary-input anchor derivative must match retained contractions."""
import importlib.util
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx

from bhsm.interface.input_linear_anchor_jet import ScalarJet, InputLinearJet, input_linear_anchor_action


def test_retained_action_with_two_shared_input_components():
    ctx.prec = 128
    path = Path(__file__).resolve().parents[1]/'scripts/certify_n12_gate7_accepted_replay_center_outward_74d.py'
    spec = importlib.util.spec_from_file_location('_input_linear_anchor_parent', path)
    parent = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = parent
    spec.loader.exec_module(parent)
    state = np.array([ScalarJet(arb(0), arb_mat([[arb(i == 0)]])) for i in range(98)], dtype=object)
    point = np.array([arb(0)]*98, dtype=object)
    left = np.array([arb(i == 37) for i in range(98)], dtype=object)
    inputs = np.array([InputLinearJet(arb_mat([[arb(i == 37), arb(i == 38)]]), arb_mat(1, 2))
                       for i in range(98)], dtype=object)
    maps = [parent._dense_mapping(parent._integrand(point, n, 0).maps) for n in range(parent.POINTS)]
    original = parent._a, parent.Mixed, parent._local_variables
    with input_linear_anchor_action(parent):
        value = parent._contracted_action(state, [left, inputs], maps)
    assert (parent._a, parent.Mixed, parent._local_variables) == original
    state_axis = np.array([arb(i == 0) for i in range(98)], dtype=object)
    for j in range(2):
        direction = np.array([arb(i == 37+j) for i in range(98)], dtype=object)
        expected = parent._contracted_action(point, [left, direction], maps)
        derivative = parent._contracted_action(point, [left, direction, state_axis], maps)
        assert value.c[0, j].overlaps(expected)
        assert value.a[0, j].overlaps(derivative)

import pytest


@pytest.fixture(autouse=True)
def restore_arb_precision():
    previous = ctx.prec
    try:
        yield
    finally:
        ctx.prec = previous
