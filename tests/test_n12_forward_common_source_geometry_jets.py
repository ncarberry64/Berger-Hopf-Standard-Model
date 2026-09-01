from scripts.derive_n12_forward_common_source_geometry_jets import build_payload


def test_all_retained_source_classes_have_validated_radius_jets() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["implemented_classes"] == [
        "RANK16_WEYL_COEXACT_GAUGE_AND_UNIT_EC_HS",
        "COMPLEX_HS_DOUBLET",
        "NONABELIAN_ONEFORM_MINUS_TWO_COMPLEX_GHOST",
    ]
    assert payload["validation"][
        "contact_radius_jets_are_zero_by_exact_local_homogeneity"
    ] is True


def test_geometry_jet_scope_does_not_fabricate_maximal_history() -> None:
    payload = build_payload()
    scope = payload["scope"]
    assert scope["local_log_R4_first_and_mixed_second_variations"] == "DERIVED"
    assert scope["supplied_temporal_D_tau_and_Delta_tau"] == "STILL_PARAMETERS"
    assert scope["maximal_forward_log_R4_history_and_variation_tube"] == "OPEN"
    assert scope["exterior_Weyl_oracle_bundle"] == "OPEN"
    assert payload["claim_boundary"]["chord_03"] == "NOT_AUTHORIZED"
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
