from bhsm.interface.aether_n3_eta_boundary_transversality_v16_10 import (
    completion_payload,
)


def test_n3_eta_boundary_is_transverse_and_not_a_dirac_zero():
    payload = completion_payload()
    row = payload["boundary_transversality"]
    assert payload["validation_passed"]
    assert row["constraint_Jacobian_rank"] == 7
    assert row["directional_eta_margin_rate"] < -1.0
    assert row["Euler_Dirac_system_regular_at_domain_exit"]
    assert not row["smooth_classical_in_domain_continuation_exists"]
