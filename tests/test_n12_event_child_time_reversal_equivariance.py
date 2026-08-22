import json
from pathlib import Path

import numpy as np

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    constraint_residual,
)
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import dimensions


ROOT = Path(__file__).resolve().parents[1]


def test_constraint_and_momentum_rows_have_exact_reversal_parity() -> None:
    order = 3
    size = dimensions(order)
    qdim = size["coordinates"]
    q = np.linspace(-0.012, 0.016, qdim)
    velocity = np.linspace(-0.019, 0.023, qdim)
    multipliers = np.linspace(-0.008, 0.01, size["multipliers"])
    reversed_multipliers = multipliers.copy()
    reversed_multipliers[order:] *= -1.0

    residual = constraint_residual(
        order, q, velocity, multipliers, points=48
    )
    reversed_residual = constraint_residual(
        order, q, -velocity, reversed_multipliers, points=48
    )
    row_signs = np.concatenate((
        np.ones(order), -np.ones(order), np.ones(1)
    ))
    assert np.allclose(
        reversed_residual, row_signs * residual, rtol=2e-10, atol=2e-10
    )

    jet = exact_full_action_jet_at_state(
        order, q, velocity, multipliers, points=48
    )
    reversed_jet = exact_full_action_jet_at_state(
        order, q, -velocity, reversed_multipliers, points=48
    )
    momentum = jet.gradient[qdim:2 * qdim]
    reversed_momentum = reversed_jet.gradient[qdim:2 * qdim]
    assert np.allclose(
        reversed_momentum, -momentum, rtol=2e-10, atol=2e-10
    )


def test_event_child_equivariance_gate_is_fail_closed() -> None:
    artifact = json.loads(
        (ROOT / "artifacts" / "intrinsic_state_selection"
         / "BHSM_N12_EVENT_CHILD_TIME_REVERSAL_EQUIVARIANCE_GATE.json").read_text(
            encoding="utf-8"
        )
    )

    assert artifact["validation_passed"] is True
    assert artifact["zero_set_result"]["global_branch_uniqueness_claimed"] is False
    assert artifact["physical_domain"]["formal_reversal_is_gauge"] is False
    assert artifact["physical_domain"][
        "R_related_states_physically_identified"
    ] is False
    assert artifact["action_selection_consequence"][
        "one_temporal_chirality_sector_action_selected_by_current_equations"
    ] is False
    assert artifact["action_selection_consequence"][
        "temporal_chirality_sectors_quotiented"
    ] is False
    assert artifact["action_selection_consequence"]["new_sign_gate_allowed"] is False
    assert artifact["shortest_owned_flagship_path"][
        "numerical_crossing_orientation_may_select_state"
    ] is False
