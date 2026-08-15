from bhsm.interface.aether_sampled_event_shell_pushforward_v15_74 import (
    completion_payload,
    sampled_rows,
)


def test_actual_weighted_stiffness_softens() -> None:
    rows = sampled_rows()
    assert rows[-1]["lowest_transverse_stiffness"] < rows[0]["lowest_transverse_stiffness"]
    assert rows[-1]["lowest_electric_stiffness"] < rows[0]["lowest_electric_stiffness"]


def test_same_operator_lr_bound_strengthens_but_does_not_cross() -> None:
    rows = sampled_rows()
    assert rows[-1]["up_channel_norm_upper_bound"] > rows[0]["up_channel_norm_upper_bound"]
    assert max(row["up_channel_norm_upper_bound"] for row in rows) < 1.0


def test_payload_validates() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert not payload["claim_boundary"]["joint_crossing_found_on_controlled_branch"]
