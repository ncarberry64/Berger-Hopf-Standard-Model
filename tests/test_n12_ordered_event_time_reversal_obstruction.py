import json
from pathlib import Path

import numpy as np

from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import dimensions


ROOT = Path(__file__).resolve().parents[1]


def test_exact_retained_action_jet_has_time_reversal_congruence() -> None:
    order = 3
    size = dimensions(order)
    qdim = size["coordinates"]
    mdim = size["multipliers"]
    q = np.linspace(-0.015, 0.012, qdim)
    velocity = np.linspace(-0.021, 0.018, qdim)
    multipliers = np.linspace(-0.009, 0.011, mdim)

    reversed_velocity = -velocity
    reversed_multipliers = multipliers.copy()
    reversed_multipliers[order:] *= -1.0

    jet = exact_full_action_jet_at_state(
        order, q, velocity, multipliers, points=48
    )
    reversed_jet = exact_full_action_jet_at_state(
        order, q, reversed_velocity, reversed_multipliers, points=48
    )
    signs = np.concatenate((
        np.ones(qdim),
        -np.ones(qdim),
        np.ones(order),
        -np.ones(order),
    ))

    assert np.isclose(jet.value, reversed_jet.value, rtol=0.0, atol=2e-12)
    assert np.allclose(
        reversed_jet.gradient, signs * jet.gradient, rtol=2e-11, atol=2e-11
    )
    assert np.allclose(
        reversed_jet.hessian,
        signs[:, None] * jet.hessian * signs[None, :],
        rtol=2e-10,
        atol=2e-10,
    )


def test_event_forward_shortcut_gate_is_fail_closed() -> None:
    artifact = json.loads(
        (ROOT / "artifacts" / "intrinsic_state_selection"
         / "BHSM_N12_ORDERED_EVENT_TIME_REVERSAL_OBSTRUCTION.json").read_text(
            encoding="utf-8"
        )
    )

    assert artifact["validation_passed"] is True
    assert artifact["event_transport"][
        "global_strict_sign_on_R_invariant_set_possible"
    ] is False
    assert artifact["component_scope"][
        "component_restricted_sign_disproved_without_component_topology"
    ] is False
    assert artifact["component_scope"][
        "formal_reflection_sectors_physically_quotiented"
    ] is False
    assert artifact["component_scope"]["one_sector_action_selected"] is False
    assert artifact["involution"]["is_gauge"] is False
    assert artifact["flagship_chain"][
        "event_forward_shortcut_adjudicated"
    ] is True
    assert artifact["flagship_chain"][
        "numerical_trajectory_campaign_authorized"
    ] is False
