from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_state_primitives import (  # noqa: E402
    BoundaryState,
    integer_primitives_from_boundary_state,
    physical_boundary_state_registry,
    validate_boundary_state,
)


def test_valid_boundary_states_map_to_expected_integer_primitives() -> None:
    cases = {
        BoundaryState("three_channel_active", "hadronic_closure", "upper", "active"): {
            "C": 1,
            "ell": 0,
            "sigma": 1,
            "w": 1,
        },
        BoundaryState("single_channel_boundary", "leptonic_closure", "lower", "inactive"): {
            "C": 0,
            "ell": 1,
            "sigma": -1,
            "w": 0,
        },
    }
    for state, expected in cases.items():
        assert integer_primitives_from_boundary_state(state) == expected


def test_physical_registry_contains_expected_states() -> None:
    states = physical_boundary_state_registry(include_nu_r=True)
    assert states["nu_L"] == BoundaryState(
        "single_channel_boundary", "leptonic_closure", "upper", "active"
    )
    assert states["e_L"] == BoundaryState(
        "single_channel_boundary", "leptonic_closure", "lower", "active"
    )
    assert states["u_L"] == BoundaryState(
        "three_channel_active", "hadronic_closure", "upper", "active"
    )
    assert states["d_L"] == BoundaryState(
        "three_channel_active", "hadronic_closure", "lower", "active"
    )
    assert states["nu_R"] == BoundaryState(
        "single_channel_boundary", "leptonic_closure", "upper", "inactive"
    )


def test_invalid_boundary_states_raise_value_error() -> None:
    with pytest.raises(ValueError, match="invalid channel_class"):
        validate_boundary_state(
            BoundaryState("bad", "leptonic_closure", "upper", "active")
        )
    with pytest.raises(ValueError, match="invalid closure_class"):
        validate_boundary_state(
            BoundaryState("single_channel_boundary", "bad", "upper", "active")
        )
    with pytest.raises(ValueError, match="invalid orientation"):
        validate_boundary_state(
            BoundaryState("single_channel_boundary", "leptonic_closure", "bad", "active")
        )
    with pytest.raises(ValueError, match="invalid interface_activity"):
        validate_boundary_state(
            BoundaryState("single_channel_boundary", "leptonic_closure", "upper", "bad")
        )
