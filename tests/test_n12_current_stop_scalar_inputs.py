"""Sign, coverage, and translated inclusion checks for the scalar input packet."""
from fractions import Fraction
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"scripts"))
from materialize_n12_current_stop_scalar_inputs import (
    exact_action_distance_upper, scalar_replay, strict_root_bracket,
)


def test_exact_midpoint_root_keeps_strict_sign_bracket():
    lo, hi = strict_root_bracket([Fraction(1), Fraction(-2)], iterations=40)
    assert lo < Fraction(1, 2) < hi
    assert 1-2*lo > 0 > 1-2*hi
    assert hi-lo <= Fraction(1, 2**40)


def test_all_prefix_cells_and_whole_terminal_cell_are_consumed():
    coefficients = np.zeros((2, 7))
    coefficients[:, 0] = [2.0, -5.0]
    report = scalar_replay(np.array([1.0, 3.0, -2.0]), coefficients,
                           np.array([0.0, .5, 1.0]), 1)
    assert report["validation_passed"]
    assert report["complete_preterminal_intervals"] == 1
    assert report["terminal_native_action_interval"] == [.5, 1.0]
    assert report["terminal_root_action_interval"][0] < .8 < report["terminal_root_action_interval"][1]
    assert report["terminal_scalar_derivative_per_action_interval"][1] < 0


def test_earlier_nonpositive_cell_is_not_promoted_to_first_hit():
    coefficients = np.zeros((2, 7))
    coefficients[:, 0] = [2.0, -5.0]
    report = scalar_replay(np.array([-1.0, 3.0, -2.0]), coefficients,
                           np.array([0.0, .5, 1.0]), 1)
    assert not report["validation_passed"]
    assert not report["validation"]["all_complete_preterminal_center_cells_positive"]


def test_weighted_binary64_translation_is_outward():
    upper, _ = exact_action_distance_upper(np.array([0.0, 0.0]), np.array([3.0, 4.0]), np.ones(2))
    assert upper >= 5.0
    assert upper < 5.0+1e-13
