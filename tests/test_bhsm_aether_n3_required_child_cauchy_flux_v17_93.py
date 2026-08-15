from bhsm.interface.aether_n3_required_child_cauchy_flux_v17_93 import (
    completion_payload,
)


def test_required_child_cauchy_flux_validates():
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["required_complete_child_cauchy_flux"]
    assert len(result["required_child_projected_flux"]) == 2
    assert result["finite_difference"]["state_dependent_lift_recomputed_at_both_sides"]
    child = result["F_child_scalar"]
    assert child["required_flux_derived_algebraically"]
    assert not child["physical_target_promotable"]
    assert child["event_local_maximum_constraint_residual"] > 1.0
    assert child["actual_reconstructed_child_flux"] == "OPEN"
    assert not child["static_zero_flux_required"]
    assert not payload["direct_N3_solve_authorized_next"]
