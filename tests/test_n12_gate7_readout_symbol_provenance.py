from scripts.audit_n12_gate7_readout_symbol_provenance import build_payload


def test_p2_is_classified_exactly_as_retired_periodic_fourier_artifact() -> None:
    payload = build_payload()
    classification = payload["p2_classification"]
    assert payload["validation_passed"] is True
    assert classification["selected"] == "D_RETIRED_PERIODIC_FOURIER_ARTIFACT"
    assert classification["D_RETIRED_PERIODIC_FOURIER_ARTIFACT"]["selected"]
    assert not classification["A_ACTION_NATIVE"]["selected"]
    assert not classification["B_PHYSICAL_ASYMPTOTIC_READOUT"]["selected"]
    assert not classification["C_SPECTRAL_PARAMETERIZATION"]["selected"]


def test_native_spectral_parameter_is_not_called_momentum_squared() -> None:
    payload = build_payload()
    native = payload["native_replacement"]
    assert native["spectral_parameter"] == "z_IN_rho(K_C)"
    assert native["forbidden_identification"] == "DO_NOT_CALL_z_MOMENTUM_SQUARED"
    assert "p2" in native["future_physical_map"]


def test_v1569_formula_has_no_executable_parameter_family() -> None:
    payload = build_payload()
    execution = payload["formula_execution_audit"]
    assert execution["formula_string_present"] is True
    assert execution["functions_accepting_p_or_p2"] == []
    assert execution["test_only_checks_formula_prefix"] is True
    assert execution["test_evaluates_p_family_or_derivative"] is False


def test_residue_and_pole_meanings_are_not_conflated() -> None:
    payload = build_payload()
    symbols = payload["symbol_ledger"]
    assert "NOT_A_PROVED_PROPAGATOR_POLE_RESIDUE" in symbols["residue"][
        "gauge_meaning"
    ]
    assert symbols["pole"]["physical_gauge_propagator_pole_derived"] is False
    assert symbols["pole"]["Gate7_native_dependency"] is False


def test_downstream_and_frozen_boundaries_remain_fail_closed() -> None:
    payload = build_payload()
    downstream = payload["downstream"]
    frozen = downstream["frozen_predictions"]
    assert downstream["Gate7_current"] == "ACTIVE_NOT_CLOSED"
    assert downstream["Gate8"] == "LOCKED_BY_GATE7"
    assert downstream["chord_03"] == "UNAUTHORIZED"
    assert frozen["changed"] is False
    assert frozen["exact_readout_dependency_tokens_found"] == []
    assert payload["new_physics_added"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
