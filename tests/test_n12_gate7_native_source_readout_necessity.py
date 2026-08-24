from scripts.audit_n12_gate7_native_source_readout_necessity import build_payload


def test_terminal_reachability_is_not_a_native_source_domain_requirement() -> None:
    payload = build_payload()
    adjudication = payload["necessity_adjudication"]
    assert payload["validation_passed"] is True
    assert adjudication["B_one_terminal_reaching_history"].startswith(
        "EXISTENCE_ONLY"
    )
    assert adjudication["D_universal_terminal_reachability"].startswith(
        "NOT_REQUIRED"
    )
    assert payload["Gate7_status_changed"] is False


def test_inherited_p2_formula_is_not_yet_an_executable_forward_evaluator() -> None:
    payload = build_payload()
    provenance = payload["provenance"]
    readout = payload["readout_adjudication"]
    assert provenance["inherited_scalar_formula"].startswith("Z_g=partial_(p^2)")
    assert provenance["periodic_cycle_restored"] is False
    assert provenance["dynamic_frequency_response_derived"] is False
    assert readout["current_formula_status"].startswith("INHERITED_FORMAL")
    assert readout["definition_must_precede_value_computation"] is True


def test_compact_source_response_retains_exterior_weyl_dependence() -> None:
    payload = build_payload()
    witness = payload["exact_witnesses"]["exterior_Schur_response"]
    assert witness["exact_response_difference"]["exact"] == "1/72"
    assert witness["rows"][0]["core_response_for_source_(1,0)"]["exact"] == "5/8"
    assert witness["rows"][1]["core_response_for_source_(1,0)"]["exact"] == "11/18"


def test_gate_and_prediction_boundaries_remain_locked() -> None:
    payload = build_payload()
    assert payload["frozen_prediction_audit"][
        "terminal_reachability_is_a_frozen_prediction_dependency"
    ] is False
    assert payload["downstream"]["Gate7"] == "ACTIVE_NOT_CLOSED"
    assert payload["downstream"]["Gate8"] == "LOCKED"
    assert payload["chord_03_authorized"] is False
