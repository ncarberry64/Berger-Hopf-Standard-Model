from scripts.derive_n12_forward_common_source_incidence import build_payload


def test_forward_common_source_incidence_is_domain_parametric_and_exact() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert max(payload["periodic_equivalence_residuals"].values()) < 1.0e-12
    assert payload["claim_boundary"][
        "domain_parametric_nonzero_local_incidence"
    ] == "DERIVED"
    assert payload["incidence"]["temporal_graph_selected_by_this_assembly"] is False
    assert payload["incidence"]["source_profile_selected_by_this_assembly"] is False
    assert payload["incidence"]["momentum_or_p2_label_used"] is False
    assert payload["claim_boundary"]["admissible_BRST_source_builder"] == (
        "DERIVED_FOR_SUPPLIED_SECTIONS"
    )
    assert payload["claim_boundary"]["p_indexed_source_family"] == (
        "RETIRED_NOT_REQUIRED"
    )


def test_incidence_derivation_does_not_promote_gate7_value() -> None:
    payload = build_payload()
    assert payload["claim_boundary"]["maximal_history_temporal_realization"] == "OPEN"
    assert payload["claim_boundary"]["zero_source_weak_geometry_force"] == "OPEN"
    assert payload["claim_boundary"]["pair_plus_contact_gauge_Hessian"] == "OPEN"
    assert payload["claim_boundary"]["Gate_7"] == "ACTIVE_NOT_CLOSED"
    assert payload["FLAGSHIP_READY"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
