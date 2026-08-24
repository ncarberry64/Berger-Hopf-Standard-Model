from scripts.derive_n12_forward_proper_time_form_ownership import build_payload


def test_proper_time_temporal_form_is_action_owned_not_independent() -> None:
    payload = build_payload()
    provenance = payload["provenance_classification"]
    assert payload["validation_passed"] is True
    assert provenance["positive_boundary_lapse"][
        "independent_bulk_source_coefficient_after_pullback"
    ] is False
    assert provenance["D_tau"]["separate_coefficient_oracle_required"] is False
    assert provenance["Delta_tau"]["independently_selectable"] is False
    assert provenance["log_R4_of_tau"][
        "maximal_history_value_and_Jacobi_envelope"
    ] == "OPEN"


def test_temporal_form_witnesses_do_not_restore_periodicity() -> None:
    payload = build_payload()
    witnesses = payload["finite_witnesses"]
    periodic = witnesses["historical_periodic_equivalence_only"]
    nonperiodic = witnesses["nonperiodic_endpoint_form"]
    assert periodic["relative_DstarD_residual"] < 1.0e-14
    assert periodic["physical_periodicity_selected"] is False
    assert nonperiodic["form_pair_residual"] == 0.0
    assert nonperiodic["minimum_eigenvalue"] >= -1.0e-13


def test_dependency_is_reduced_to_radius_history_or_direct_oracle() -> None:
    payload = build_payload()
    reduction = payload["dependency_reduction"]
    assert "NOT_INDEPENDENT_HISTORY_COEFFICIENTS" in reduction[
        "reclassification"
    ]
    assert "log_R4" in reduction["remaining_owner"]
    assert payload["claim_boundary"]["chord_03"] == "NOT_AUTHORIZED"
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
