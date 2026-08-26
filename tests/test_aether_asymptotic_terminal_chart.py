from __future__ import annotations

import math

import numpy as np

from bhsm.interface.aether_asymptotic_terminal_chart import (
    MDIM,
    QDIM,
    compactified_terminal_chart,
    compactified_terminal_chart_jets,
)
from bhsm.interface.weight_seven_transverse_descriptor import ROUND_EXPANSION_RATE


def test_round_expanding_family_maps_to_descriptor_origin() -> None:
    state = np.zeros(2 * QDIM + MDIM)
    state[0] = 2500.0
    state[QDIM] = ROUND_EXPANSION_RATE
    result = compactified_terminal_chart(state)
    assert result["epsilon_underflows_binary64"] is True
    assert abs(result["log_epsilon"] + 2.0 * result["log_R4"]) < 1.0e-12
    assert np.linalg.norm(result["descriptor"]) < 1.0e-12


def test_terminal_chart_first_and_mixed_jets_match_finite_differences() -> None:
    rng = np.random.default_rng(712741)
    state = rng.normal(scale=2.0e-3, size=2 * QDIM + MDIM)
    state[0] = 1.3
    state[QDIM] = ROUND_EXPANSION_RATE + 0.02
    left = rng.normal(scale=0.1, size=state.size)
    right = rng.normal(scale=0.1, size=state.size)
    jets = compactified_terminal_chart_jets(state, left, right)

    h = 2.0e-5
    center = compactified_terminal_chart(state)
    plus_left = compactified_terminal_chart(state + h * left)
    minus_left = compactified_terminal_chart(state - h * left)
    numerical_first = (plus_left["descriptor"] - minus_left["descriptor"]) / (2.0 * h)
    assert np.allclose(numerical_first, jets["D_descriptor_left"], rtol=2.0e-7, atol=2.0e-9)

    pp = compactified_terminal_chart(state + h * left + h * right)
    pm = compactified_terminal_chart(state + h * left - h * right)
    mp = compactified_terminal_chart(state - h * left + h * right)
    mm = compactified_terminal_chart(state - h * left - h * right)
    numerical_mixed = (pp["descriptor"] - pm["descriptor"] - mp["descriptor"] + mm["descriptor"]) / (4.0 * h * h)
    assert np.allclose(numerical_mixed, jets["D2_descriptor_mixed"], rtol=2.0e-4, atol=2.0e-6)

    log_epsilon_first = (plus_left["log_epsilon"] - minus_left["log_epsilon"]) / (2.0 * h)
    assert math.isclose(log_epsilon_first, jets["D_log_epsilon_left"], rel_tol=2.0e-8, abs_tol=2.0e-10)
    assert center["descriptor"].shape == (74,)
