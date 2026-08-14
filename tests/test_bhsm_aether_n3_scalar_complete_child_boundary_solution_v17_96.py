from bhsm.interface.aether_n3_scalar_complete_child_boundary_solution_v17_96 import (
    completion_payload,
)


def test_scalar_complete_child_boundary_solution_closes_only_owned_block():
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["scalar_complete_child_boundary_solution"]
    scalar = result["F_child_scalar"]
    assert scalar["maximum_trace_residual"] < 2.0e-9
    assert scalar["maximum_constraint_residual"] < 1.0e-9
    assert scalar["attachment_momentum_residual_norm"] < 1.0e-7
    assert scalar["dynamic_flux_residual_envelope"] < 2.0e-5
    assert result["child_state"]["eta_Legendre_minimum"]["minimum"] > 0.0
    assert result["child_state"]["velocity_norm"] > 1.0
    assert not result["complete_F_child_ledger"]["complete_F_child_closed"]
    assert not payload["direct_N3_solve_authorized_next"]
