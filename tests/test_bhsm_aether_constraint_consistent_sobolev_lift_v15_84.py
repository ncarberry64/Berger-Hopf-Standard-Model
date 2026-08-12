import json

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    completion_payload,
    constraint_consistent_rows,
    deterministic_json,
)


def test_every_nested_state_satisfies_all_reduced_constraints():
    rows = constraint_consistent_rows()
    assert [row["order"] for row in rows] == list(range(2, 9))
    assert all(row["scaled_maximum_constraint_residual"] < 1.0e-8 for row in rows)


def test_invariant_schur_is_evaluated_only_after_projection():
    rows = constraint_consistent_rows()
    assert all(abs(row["invariant_half_J_Dinv_J"]) < 1.0e5 for row in rows)
    assert all(row["condition_number"] > 1.0 for row in rows)


def test_payload_is_valid_and_deterministic():
    payload = completion_payload()
    assert payload["validation_passed"]
    encoded = deterministic_json(payload)
    assert encoded == deterministic_json(completion_payload())
    assert json.loads(encoded)["version"] == "v15.84"
