from __future__ import annotations

import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_collective_curvature_threshold import (  # noqa: E402
    branch_type_multiplier,
    collective_curvature_effective,
    effective_dark_curvature,
    log_threshold,
    positive_part,
    threshold_mass,
)


def test_positive_part_threshold_behavior() -> None:
    assert positive_part(-2.5) == 0.0
    assert positive_part(0.0) == 0.0
    assert positive_part(2.5) == 2.5


def test_log_threshold_is_scale_compressed() -> None:
    assert log_threshold(0.0) == 0.0
    assert log_threshold(1.0) > log_threshold(0.0)
    assert log_threshold(10.0) > log_threshold(2.0)
    assert log_threshold(10.0) < 10.0


def test_branch_type_multiplier_handles_pure_and_mixed_modes() -> None:
    b_fiber = 0.5
    b_base = 0.25
    assert branch_type_multiplier(False, False, b_fiber, b_base) == 1.0
    assert math.isclose(branch_type_multiplier(True, False, b_fiber, b_base), math.exp(b_fiber))
    assert math.isclose(branch_type_multiplier(False, True, b_fiber, b_base), math.exp(b_base))
    assert math.isclose(
        branch_type_multiplier(True, True, b_fiber, b_base),
        math.exp(b_fiber + b_base),
    )


def test_collective_curvature_effective_field() -> None:
    result = collective_curvature_effective(
        K_self=[1.0, 2.0],
        coupling_matrix=[[0.0, 0.5], [1.0, 0.0]],
        masses=[4.0, 6.0],
        K_boundary=[0.25, 0.5],
        K_envelope=1.0,
    )
    assert result == [5.25, 7.5]


def test_threshold_mass_opens_only_above_threshold() -> None:
    assert threshold_mass(0.9, 1.0, scale=2.0) == 0.0
    assert threshold_mass(1.5, 1.0, scale=2.0, power=2.0, response=3.0) == 1.5


def test_effective_dark_curvature_is_residual_diagnostic() -> None:
    assert effective_dark_curvature(10.0, 7.0) == 3.0
    assert effective_dark_curvature(7.0, 7.0) == 0.0
    assert effective_dark_curvature(5.0, 7.0) == -2.0
