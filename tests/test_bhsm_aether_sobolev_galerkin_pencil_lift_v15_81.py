import json

from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    completion_payload,
    convergence_rows,
    deterministic_json,
    dimensions,
)


def test_nested_dimensions_and_branch_tracking():
    assert dimensions(2)["Dirac_pencil"] == 11
    assert dimensions(4)["Dirac_pencil"] == 21
    rows = convergence_rows()
    assert [row["order"] for row in rows] == [2, 3, 4]
    assert all(row["embedding_overlap"] > 0.25 for row in rows[1:])


def test_soft_source_is_evaluated_at_every_order():
    rows = convergence_rows()
    assert all(abs(row["g_s0"]) < 10.0 for row in rows)
    assert all(row["condition_number"] > 1.0 for row in rows)


def test_payload_is_valid_and_deterministic():
    payload = completion_payload()
    assert payload["validation_passed"]
    encoded = deterministic_json(payload)
    assert encoded == deterministic_json(completion_payload())
    assert json.loads(encoded)["version"] == "v15.81"
