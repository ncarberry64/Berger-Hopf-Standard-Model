from bhsm.interface.aether_n3_dynamic_child_wentzell_cauchy_v17_90 import (
    completion_payload,
)


def test_dynamic_child_wentzell_cauchy_law_validates():
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["dynamic_event_to_child_cauchy_law"]
    assert result["Legendre_certificate"]["reduced_rank"] == 2
    assert result["current_Euler_Dirac_field_finite"]
    law = result["dynamic_boundary_law"]
    assert not law["static_W_times_c_equals_zero_required"]
    assert not law["nonzero_momentum_is_a_defect"]
    assert not law["nonzero_time_dependence_is_a_defect"]
    assert not payload["direct_N3_solve_authorized_next"]
