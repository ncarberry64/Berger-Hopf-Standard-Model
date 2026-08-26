import json
from pathlib import Path

import numpy as np

from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import (
    exact_full_action_jet_at_state,
)
from bhsm.interface.aether_retained_action_tensor_interval import (
    DirectedInterval,
    interval_tensor_norm_upper,
    retained_action_tensor_interval,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_C2_FULLY_REDUCED_SIGNED_ROW_CERTIFICATE.json"
BORDERED = BASE / "BHSM_N12_C2_BORDERED_HARD_RESPONSE_MATRIX.npz"


def test_directed_interval_primitives_are_outward() -> None:
    x = DirectedInterval.hull(1.0, 1.0)
    y = DirectedInterval.hull(3.0, 3.0)
    quotient = (x * y + x) / y
    exact = 4.0 / 3.0
    assert quotient.lo <= exact <= quotient.hi
    assert interval_tensor_norm_upper(DirectedInterval.hull([-1.0, 2.0], [1.0, 3.0])) >= 3.0


def test_point_interval_contains_independent_exact_action_direction() -> None:
    with np.load(BORDERED) as data:
        state = np.asarray(data["center_state"], dtype=float)
        weights = np.asarray(data["state_weights"], dtype=float)
    direction = np.zeros(state.size)
    direction[86] = 1.0
    interval = retained_action_tensor_interval(
        12, state, state, [direction], points=96,
    )
    jet = exact_full_action_jet_at_state(
        12, state[:37], state[37:74], state[74:], points=96,
    )
    exact = float(np.asarray(jet.gradient) @ (direction / weights))
    assert float(interval.lo) <= exact <= float(interval.hi)


def test_fully_reduced_row_certificate_is_fail_closed() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["fully_reduced_cb_row_2_norm_upper"] < payload[
        "rigorous_resolving_row_norm_ceiling"
    ]
    assert payload["row_to_ceiling_ratio"] < 0.2
    assert payload["adjudication"]["dominant_bc_row"] == (
        "CERTIFIED_BELOW_RESOLVING_CEILING"
    )
    assert payload["adjudication"]["nested_hard_adjoint_vectors_required"] is False
    assert payload["adjudication"]["s_suppressed_hard_response_row"] == "OPEN"
    assert payload["adjudication"]["signed_D_Y_Delta_on_exact_family"] == (
        "OPEN_PENDING_s_HARD_ROW"
    )
    assert payload["adjudication"]["Gate7"] == "OPEN"
    assert payload["adjudication"]["Gate8"] == "LOCKED"
    assert payload["FULL_BHSM_COMPLETE"] is False
