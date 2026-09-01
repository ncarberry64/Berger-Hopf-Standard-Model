from scripts.derive_n12_finite_history_terminal_coefficient_jet import (
    build_payload,
)


def test_terminal_coefficient_cauchy_jet_is_certified() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    data = payload["terminal_coefficient_data"]
    assert data["root_D_tau_log_R4_interval"][0] > 0.0
    assert data["lapse_interval"][0] > 0.0


def test_duration_remains_parametric_without_selecting_lambda() -> None:
    payload = build_payload()
    duration = payload["desingularized_duration_jet"]
    assert duration["lambda_0_selected"] is False
    assert duration["quadratic_coefficient_interval"][0] > 0.0
    assert payload["claim_boundary"]["full_coefficient_path"] == "OPEN"
