import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_action_terms import (  # noqa: E402
    cyclic_closure_value,
    cyclic_three_channel_passes,
)


def test_cyclic_three_channel_diagnostic_passes():
    assert cyclic_closure_value(3, 3) == pytest.approx(0.0)
    assert cyclic_three_channel_passes(3)


def test_cyclic_nonmatching_order_fails_with_positive_penalty():
    assert cyclic_closure_value(2, 3) > 0
    assert cyclic_closure_value(4, 3) > 0
    assert not cyclic_three_channel_passes(4)


def test_invalid_cyclic_order_raises():
    with pytest.raises(ValueError):
        cyclic_closure_value(3, 1)

