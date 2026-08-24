from scripts.audit_n12_forward_exterior_gap_oracle_route import build_payload


def test_gap_and_friedrichs_define_but_do_not_determine_weyl_value() -> None:
    payload = build_payload()
    theorem = payload["theorem"]
    rows = theorem["sample_rows"]
    assert payload["validation_passed"] is True
    assert theorem["coercive_probe"] == "z=-1"
    assert all(row["form_gap_lower"] >= 1.0 for row in rows)
    assert all(
        left["Weyl_value"] < right["Weyl_value"]
        for left, right in zip(rows, rows[1:])
    )
    assert "SUP_Q>=1_M_Q(-1)=INFINITY" in theorem["conclusion"]


def test_two_chord_core_does_not_supply_operator_variation_bundle() -> None:
    payload = build_payload()
    core = payload["certified_core_effect"]
    assert core["two_chord_time_end"] == 2.0e-8
    assert core["best_case_scalar_endpoint_uncertainty_lower"] > 4.4e7
    assert core["uncertainty_over_target_magnitude"] > 5.0e7
    assert "D_Phi_M_C(z)_ON_THE_MAXIMAL_EXTERIOR" in core["what_is_not_owned"]
    assert core["promotion_authorized"] is False


def test_route_adjudication_preserves_native_gate_and_forbids_chord_three() -> None:
    payload = build_payload()
    route = payload["route_adjudication"]
    boundary = payload["claim_boundary"]
    assert route["positive_gap_plus_Friedrichs_only"] == (
        "RIGOROUS_NO_GO_FOR_ORACLE_VALUE"
    )
    assert route["terminal_event_required"] is False
    assert route["third_chord_authorized"] is False
    assert route["action_obstruction_proved"] is False
    assert "INVALIDATED_AS_A_STRUCTURAL_IDENTITY" in route[
        "Ward_BRST_zero_force_shortcut"
    ]
    assert route["historical_nonzero_force_witness"][
        "N12_forward_force_evaluated"
    ] is False
    assert boundary["Gate_7"] == "ACTIVE_NOT_CLOSED"
    assert boundary["Gate_8"] == "LOCKED"
    assert boundary["FULL_BHSM_COMPLETE"] is False
