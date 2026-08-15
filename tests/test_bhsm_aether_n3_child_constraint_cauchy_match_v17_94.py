from bhsm.interface.aether_n3_child_constraint_cauchy_match_v17_94 import (
    completion_payload,
)


def test_child_constraint_cauchy_match_reclassifies_fixed_trace_projection():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["status"] == "RECLASSIFIED"
    result = payload["child_constraint_cauchy_match"]
    projection = result["constraint_projection"]
    assert len(projection["projected_child_constraint_residual"]) == 7
    assert projection["projected_child_maximum_constraint_residual"] < 1.0e-8
    cauchy = result["attachment_cauchy_match"]
    assert cauchy["momentum_matching_residual_norm"] > 1.0
    assert cauchy["F_child_scalar_flux_residual_norm"] > 1.0
    assert not result["complete_scalar_child_map"]["closed"]
    assert not payload["direct_N3_solve_authorized_next"]
