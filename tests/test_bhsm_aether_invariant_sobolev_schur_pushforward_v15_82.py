import json

from bhsm.interface.aether_invariant_sobolev_schur_pushforward_v15_82 import (
    completion_payload,
    deterministic_json,
    joint_subcritical_bound,
    near_event_invariant_rows,
    sobolev_schur_rows,
)


def test_invariant_schur_tail_converges_and_null_projection_decouples():
    rows = sobolev_schur_rows()
    assert [row["order"] for row in rows] == list(range(2, 9))
    assert abs(
        rows[-1]["invariant_half_J_Dinv_J"]
        - rows[-2]["invariant_half_J_Dinv_J"]
    ) < 0.01
    assert abs(rows[-1]["smallest_mode_source_projection"]) < 0.01


def test_near_event_full_schur_is_finite_and_joint_bound_subcritical():
    assert max(
        abs(row["invariant_half_J_Dinv_J"])
        for row in near_event_invariant_rows()
    ) < 1.0
    bound = joint_subcritical_bound()
    assert bound["joint_gap_operator_upper_bound"] < 0.01
    assert bound["strictly_subcritical"]
    assert not bound["rank_one_v15_80_crossing_survives"]


def test_payload_is_valid_and_deterministic():
    payload = completion_payload()
    assert payload["validation_passed"]
    encoded = deterministic_json(payload)
    assert encoded == deterministic_json(completion_payload())
    assert json.loads(encoded)["version"] == "v15.82"
