from scripts.derive_n12_analytic_local_block_center_lift import build_payload


def test_analytic_local_block_payload_validates():
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["analytic_preconditioned_local_block_lift"] == "DERIVED"
    assert payload["converged_tail"]["directed_interval_certified"] is False
    assert payload["adjudication"]["sign_promoted_as_rigorous_action_theorem"] is False
