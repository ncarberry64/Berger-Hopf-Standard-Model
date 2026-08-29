from scripts.derive_n12_gate7_open_family_stop_transversality_reduction import (
    build_payload,
)


def test_one_transverse_witness_promotes_to_open_stop_stratum() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "ONE_TRANSVERSE_CENTER_WITNESS_SUFFICES_FOR_OPEN_72D_STOP_STRATUM"
    )
    theorem = payload["reduction_theorem"]
    assert theorem["launch_rank"] == 73
    assert theorem["universal_reachability_required"] is False
    assert payload["certified_open_core_input"]["dimension"] == 72
    assert payload["certified_open_core_input"][
        "terminal_first_jet_singular_value_lower"
    ] > 0.0


def test_reduction_does_not_overpromote_numerical_center() -> None:
    payload = build_payload()
    target = payload["existing_transverse_center_target"]
    assert target["Ds_V"] < 0.0
    assert target["selected_eigenline_gap"] > 0.0
    assert target["boundary_lapse"] > 0.0
    assert target["boundary_radius"] > 0.0
    assert target["role"] == "KRAWCZYK_CENTER_ONLY_NOT_INTERVAL_HISTORY_AUTHORITY"
    assert payload["adjudication"]["whole_open_family_multiple_shooting_required"] is False
    assert payload["adjudication"]["one_correlated_center_shadowing_certificate_required"] is True
    assert "NOT_YET_INTERVAL_SHADOWED" in payload["claim_boundary"]
    assert payload["FULL_BHSM_COMPLETE"] is False
