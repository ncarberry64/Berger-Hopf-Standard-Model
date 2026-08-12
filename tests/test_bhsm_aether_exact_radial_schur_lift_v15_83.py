import json

from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    angular_selection_theorem,
    completion_payload,
    deterministic_json,
    exact_radial_rows,
)


def test_exact_hessian_sequence_keeps_every_near_null_direction():
    rows = exact_radial_rows()
    assert [row["order"] for row in rows] == list(range(2, 13))
    assert all(abs(row["full_half_J_Dinv_J"]) < 2.0 for row in rows)
    assert all("smallest_mode_source_projection" in row for row in rows)


def test_lowest_killing_spinor_has_no_nonaxisymmetric_source_tail():
    theorem = angular_selection_theorem()
    assert theorem["non_axisymmetric_Schur_tail"] == 0.0
    assert theorem["cohomogeneity_one_sector_complete_for_this_quadratic_source"]


def test_payload_is_valid_and_deterministic():
    payload = completion_payload()
    assert payload["validation_passed"]
    encoded = deterministic_json(payload)
    assert encoded == deterministic_json(completion_payload())
    assert json.loads(encoded)["version"] == "v15.83"
