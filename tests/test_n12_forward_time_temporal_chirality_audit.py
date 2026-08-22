import json
from pathlib import Path

import numpy as np

from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import dimensions
from scripts.audit_n12_radial_diffeo_noether_compatibility import (
    _ward_shift_covectors,
)


ROOT = Path(__file__).resolve().parents[1]


def test_forward_time_temporal_chirality_gate_does_not_quotient_or_select() -> None:
    artifact = json.loads(
        (ROOT / "artifacts" / "intrinsic_state_selection"
         / "BHSM_N12_FORWARD_TIME_TEMPORAL_CHIRALITY_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )

    assert artifact["validation_passed"] is True
    assert artifact["physical_time"]["orientation"] == "FORWARD"
    assert artifact["physical_time"]["formal_reversal_is_gauge"] is False
    assert artifact["event_to_child_conclusion"][
        "one_temporal_chirality_sector_action_selected"
    ] is False
    assert artifact["event_to_child_conclusion"][
        "two_sectors_may_be_quotiented"
    ] is False
    assert artifact["candidate_invariant_audit"]["ordered_event_transport"][
        "status"
    ] == "ACTION_OWNED_LABEL_NOT_ACTION_SELECTED_SIGN"
    assert artifact["candidate_invariant_audit"]["ordered_event_transport"][
        "former_label_status"
    ] == "UNDEFINED_AT_EXACT_SINGULAR_EVENT"
    assert artifact["flagship_consequence"]["numerical_campaign_authorized"] is False


def test_requested_orientation_candidates_have_fail_closed_classification() -> None:
    artifact = json.loads(
        (ROOT / "artifacts" / "intrinsic_state_selection"
         / "BHSM_N12_FORWARD_TIME_TEMPORAL_CHIRALITY_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    audit = artifact["candidate_invariant_audit"]

    assert audit["eta_clock_shift_current"]["sign_selected_by_shift_constraint"] is False
    assert audit["canonical_momentum_and_symplectic_orientation"][
        "distinguishes_forward_time_sectors"
    ] is True
    assert audit["canonical_momentum_and_symplectic_orientation"][
        "outgoing_sign_selected"
    ] is False
    assert audit["Hopf_boundary_attachment_topology"][
        "retained_correlation_with_temporal_chirality"
    ] is False
    assert audit["future_oriented_clock"][
        "selects_initial_velocity_momentum_or_shift_sign"
    ] is False


def test_eta_clock_and_geometric_shift_covectors_are_formal_reflection_odd() -> None:
    order = 3
    size = dimensions(order)
    q = np.linspace(-0.01, 0.012, size["coordinates"])
    velocity = np.linspace(-0.015, 0.017, size["coordinates"])
    multipliers = np.linspace(-0.008, 0.009, size["multipliers"])
    reflected_multipliers = multipliers.copy()
    reflected_multipliers[order:] *= -1.0

    original = _ward_shift_covectors(
        order, q, velocity, multipliers, points=64
    )
    reflected = _ward_shift_covectors(
        order, q, -velocity, reflected_multipliers, points=64
    )

    assert np.isclose(original["inertia"], reflected["inertia"], atol=1e-13)
    for key in ("eta_clock", "geometric_momentum", "total"):
        assert np.allclose(
            original[key], -reflected[key], rtol=2e-12, atol=2e-12
        )
