import math
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_action_terms import (  # noqa: E402
    canonical_phase_for_dim,
    phase_closure_passes,
    phase_closure_value,
)


def test_phase_closure_vanishes_at_canonical_phase():
    for d in [1, 2, 3, 8]:
        theta = canonical_phase_for_dim(d)
        assert phase_closure_value(d, theta) == pytest.approx(0.0, abs=1e-12)
        assert phase_closure_passes(d, theta)


def test_phase_closure_positive_off_closure():
    assert phase_closure_value(3, 2 * math.pi / 3 + 0.1) > 0
    assert not phase_closure_passes(3, 2 * math.pi / 3 + 0.1)


def test_phase_closure_rejects_invalid_dimension():
    with pytest.raises(ValueError):
        canonical_phase_for_dim(0)

