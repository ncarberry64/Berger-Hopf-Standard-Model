import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_action_terms import (  # noqa: E402
    orientation_involution_value,
    orientation_pair_passes,
)


def test_orientation_pair_passes_involution_and_trace_balance():
    assert orientation_involution_value((1, -1)) == pytest.approx(0.0)
    assert orientation_pair_passes((1, -1))


def test_invalid_orientation_eigenvalues_produce_positive_functional():
    assert orientation_involution_value((1, 1)) > 0
    assert orientation_involution_value((2, -1)) > 0
    assert not orientation_pair_passes((1, 1))


def test_empty_orientation_eigenvalues_raise():
    with pytest.raises(ValueError):
        orientation_involution_value(())

