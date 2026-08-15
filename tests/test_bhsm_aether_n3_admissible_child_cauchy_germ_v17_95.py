from bhsm.interface.aether_n3_admissible_child_cauchy_germ_v17_95 import (
    completion_payload,
)


def test_admissible_child_cauchy_germ_is_not_prematurely_promoted():
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["admissible_child_cauchy_germ"]
    germ = result["child_Cauchy_germ"]
    assert germ["maximum_trace_residual"] < 1.0e-10
    assert germ["maximum_constraint_residual"] < 5.0e-10
    assert germ["momentum_residual_norm"] < 1.0e-9
    assert germ["eta_Legendre_minimum"]["minimum"] > 0.0
    assert germ["nonzero_velocity_norm"] > 1.0
    assert result["F_child_scalar"]["dynamic_flux_residual_norm"] > 1.0
    assert not result["complete_child_status"]["complete_F_child_closed"]
    assert not payload["direct_N3_solve_authorized_next"]
