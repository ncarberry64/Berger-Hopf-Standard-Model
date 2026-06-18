import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_action_terms import (  # noqa: E402
    combined_action_diagnostic,
    excess_gap_penalty,
    selected_low_energy_dims,
    topographic_branch_label,
    topographic_eigenvalue,
)


def test_excess_gap_penalty_zero_for_low_energy_dims_and_positive_above():
    for d in [1, 2, 3]:
        assert excess_gap_penalty(d) == pytest.approx(0.0)
    for d in [4, 5, 8]:
        assert excess_gap_penalty(d) > 0


def test_topographic_branch_labels():
    assert topographic_branch_label(1) == "reference"
    assert topographic_branch_label(2) == "orientation"
    assert topographic_branch_label(3) == "cyclic"
    assert topographic_branch_label(4) == "excess"


def test_selected_low_energy_dims_use_combined_diagnostics():
    assert selected_low_energy_dims(8) == [1, 2, 3]
    assert combined_action_diagnostic(4)["selected_low_energy"] is False


def test_topographic_eigenvalue_uses_stable_positive_convention():
    assert topographic_eigenvalue(0) == pytest.approx(0.0)
    assert topographic_eigenvalue(2, B=1.0) == pytest.approx(20.0)
    with pytest.raises(ValueError):
        topographic_eigenvalue(1, B=-1.0)

