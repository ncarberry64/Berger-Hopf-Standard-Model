from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_state_primitives import (  # noqa: E402
    BoundaryState,
    anomaly_bridge_confirmed,
    physical_boundary_state_charge_table,
    t3_y_q_from_boundary_state,
)


EXPECTED_CHARGES = {
    "nu_L": {"T3": Fraction(1, 2), "Y": Fraction(-1, 1), "Q": Fraction(0, 1)},
    "e_L": {"T3": Fraction(-1, 2), "Y": Fraction(-1, 1), "Q": Fraction(-1, 1)},
    "u_L": {"T3": Fraction(1, 2), "Y": Fraction(1, 3), "Q": Fraction(2, 3)},
    "d_L": {"T3": Fraction(-1, 2), "Y": Fraction(1, 3), "Q": Fraction(-1, 3)},
    "nu_R": {"T3": Fraction(0, 1), "Y": Fraction(0, 1), "Q": Fraction(0, 1)},
    "e_R": {"T3": Fraction(0, 1), "Y": Fraction(-2, 1), "Q": Fraction(-1, 1)},
    "u_R": {"T3": Fraction(0, 1), "Y": Fraction(4, 3), "Q": Fraction(2, 3)},
    "d_R": {"T3": Fraction(0, 1), "Y": Fraction(-2, 3), "Q": Fraction(-1, 3)},
}


def test_physical_boundary_state_registry_reproduces_charge_table() -> None:
    table = physical_boundary_state_charge_table(include_nu_r=True)
    assert table == EXPECTED_CHARGES


def test_interface_activity_changes_T3_and_Y_but_preserves_Q() -> None:
    active = BoundaryState("three_channel_active", "hadronic_closure", "upper", "active")
    inactive = BoundaryState(
        "three_channel_active", "hadronic_closure", "upper", "inactive"
    )
    active_charges = t3_y_q_from_boundary_state(active)
    inactive_charges = t3_y_q_from_boundary_state(inactive)
    assert active_charges["T3"] != inactive_charges["T3"]
    assert active_charges["Y"] != inactive_charges["Y"]
    assert active_charges["Q"] == inactive_charges["Q"] == Fraction(2, 3)


def test_boundary_state_registry_confirms_anomaly_bridge() -> None:
    assert anomaly_bridge_confirmed() is True
