from scripts.derive_n12_forward_fixed_channel_transfer import build_payload


def test_fixed_spatial_channel_reduction_is_validated() -> None:
    payload = build_payload()
    theorem = payload["fixed_channel_theorem"]
    assert payload["validation_passed"] is True
    assert "tau_INDEPENDENT" in theorem["spatial_basis"]
    assert "[[-s,1],[-z,s]]" in theorem["rank16_product_Dirac_channel"][
        "transfer"
    ]
    assert "[[0,1],[V_c-z,0]]" in theorem["scalar_and_deRham_channel"][
        "transfer"
    ]


def test_channel_reduction_removes_generic_operator_history() -> None:
    payload = build_payload()
    reduction = payload["dependency_reduction"]
    assert reduction["generic_operator_coefficient_history_required"] is False
    assert reduction["moving_spatial_eigenbasis_transport_required"] is False
    assert reduction["independent_D_tau_or_Delta_tau_oracle_required"] is False
    assert reduction["one_scalar_maximal_history_required"] == (
        "x(tau)=log_R4(tau)"
    )
    assert reduction["full_pointwise_x_history_logically_required"] is False


def test_gate_claims_remain_fail_closed() -> None:
    payload = build_payload()
    boundary = payload["claim_boundary"]
    assert boundary["Gate_7"] == "ACTIVE_NOT_CLOSED"
    assert boundary["Gate_8"] == "LOCKED"
    assert boundary["chord_03"] == "NOT_AUTHORIZED"
    assert boundary["channel_Weyl_values"] == "OPEN"
    assert boundary["FULL_BHSM_COMPLETE"] is False
