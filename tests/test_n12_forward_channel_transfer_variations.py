from scripts.derive_n12_forward_channel_transfer_variations import build_payload


def test_triangular_transfer_and_weyl_variations_validate() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    theorem = payload["transfer_variation_theorem"]
    assert theorem["mixed_second"] == (
        "T_hk'=G*T_hk+G_h*T_k+G_k*T_h+G_hk*T"
    )
    assert "x_hk" in theorem["bulk_generator_data"]


def test_variation_owner_remains_action_and_domain_data() -> None:
    payload = build_payload()
    remaining = payload["remaining_action_owned_data"]
    assert remaining["maximal_forward_base_history"] == "x(tau)=log_R4(tau)"
    assert "mu_hk" in remaining["terminal_or_Friedrichs_graph_jets"]
    assert payload["claim_boundary"]["Gate_7"] == "ACTIVE_NOT_CLOSED"
    assert payload["claim_boundary"]["chord_03"] == "NOT_AUTHORIZED"
    assert payload["FULL_BHSM_COMPLETE"] is False
