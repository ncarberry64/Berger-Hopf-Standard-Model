from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/flagship_integration"


def _load(name: str) -> dict:
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def test_terminal_directed_center_and_radii_close() -> None:
    center = _load("BHSM_N12_FINITE_TERMINAL_DIRECTED_CENTER.json")
    radii = _load("BHSM_N12_FINITE_TERMINAL_RADII_CERTIFICATE.json")
    assert center["validation_passed"] is True
    assert center["terminal_normal_dimension"] == 58
    assert center["directed_Y_upper"] < 1.0e-12
    assert center["directed_Z0_upper"] < 1.0e-5
    assert radii["validation_passed"] is True
    assert radii["radii_polynomial"]["root_ball_closed"] is True
    assert radii["radii_polynomial"]["value_at_candidate_radius"] < 0.0
    assert radii["radii_polynomial"][
        "contraction_bound_Z0_plus_Z2_r"
    ] < 1.0
    assert radii["proof_boundary"][
        "global_or_universal_terminal_reachability"
    ] == "NOT_CLAIMED"


def test_terminal_component_margins_close() -> None:
    for name in (
        "BHSM_N12_FINITE_TERMINAL_EVENT_EIGENLINE_BALL.json",
        "BHSM_N12_FINITE_TERMINAL_CHILD_EIGENLINE_BALL.json",
        "BHSM_N12_FINITE_TERMINAL_BORDERED_RELATIVE_BALL.json",
    ):
        assert _load(name)["validation_passed"] is True
    margin = _load("BHSM_N12_FINITE_TERMINAL_MARGIN_TRANSFER.json")
    assert margin["validation_passed"] is True
    assert margin["transferred_margins"][
        "event_and_child_Legendre_positive"
    ] is True
    assert "SUPERSEDED" in margin["status"]


def test_terminal_orientation_is_strict_and_nonuniversal() -> None:
    orientation = _load("BHSM_N12_FINITE_TERMINAL_ORIENTATION_CERTIFICATE.json")
    assert orientation["validation_passed"] is True
    assert orientation["center_cubic"]["upper"] < 0.0
    assert orientation["root_cubic_transfer"]["root_c_psi_upper"] < 0.0
    assert orientation["root_forcing_transfer"]["root_b_psi_lower"] > 0.0
    assert orientation["validation"][
        "terminal_hitting_product_is_strictly_negative"
    ] is True
    assert orientation["consequence"][
        "universal_terminal_reachability"
    ] == "NOT_REQUIRED_NOT_CLAIMED"
    assert orientation["claim_boundary"]["Gate7"] == (
        "ACTIVE_FINITE_ENDPOINT_ZERO_SOURCE_FORCE"
    )
    assert orientation["FULL_BHSM_COMPLETE"] is False
