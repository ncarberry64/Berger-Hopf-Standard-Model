import hashlib
import json
import sys
from math import isclose
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import oriented_jet_heat_response_audit as jet
import universal_tau_sigma_response_scaffold as tau_sigma


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"
FROZEN_HASHES = {
    ROOT / "docs" / "frozen_predictions.md": (
        "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4"
    ),
    ROOT / "docs" / "frozen_predictions.json": (
        "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7"
    ),
}


def load_artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_tau_sigma_inverse_formula():
    sigma = 7.0
    r = 3.0
    tau = tau_sigma.tau_from_sigma_r(sigma, r)
    assert isclose(tau, 1.0 / (4.0 * sigma * r**2), rel_tol=0, abs_tol=1e-15)
    assert isclose(tau_sigma.sigma_from_tau_r(tau, r), sigma, rel_tol=0, abs_tol=1e-12)


def test_sector_specific_width_configs_are_rejected():
    validation = tau_sigma.validate_universal_tau_config(
        {
            "tau_l": 0.01,
            "sigma_u": 10.0,
            "tau_by_generation": [0.0, 0.01, 0.02],
            "observed_masses_used": True,
            "target_ratios_used": True,
        }
    )
    assert validation.valid is False
    assert "tau_l" in validation.forbidden_keys_found
    assert "sigma_u" in validation.forbidden_keys_found
    assert "tau_by_generation" in validation.forbidden_keys_found
    assert validation.observed_masses_used is True
    assert validation.target_ratios_used is True


def test_berger_lambdas_match_prior_formulas():
    a = jet.berger_a()
    lambdas = tau_sigma.berger_lambdas(a)
    assert lambdas["Lambda_0"] == 0.0
    assert isclose(lambdas["Lambda_1"], 1.0 + a**-2, rel_tol=0, abs_tol=1e-15)
    assert isclose(lambdas["Lambda_2"], 2.0 + 4.0 * a**-2, rel_tol=0, abs_tol=1e-15)


def test_response_curve_artifacts_preserve_no_fit_guardrails():
    for name in (
        "universal_tau_sigma_response_scaffold_v1.json",
        "tau_response_curves_A_local_v1.json",
        "tau_response_curves_A_background_identity_v1.json",
    ):
        payload = load_artifact(name)
        assert payload["public_status"] == PUBLIC_STATUS
        assert payload["official_predictions_changed"] is False
        assert payload["tau_grid_fit_to_masses"] is False
        assert payload["tau_fit_to_masses"] is False
        assert payload["sigma_fit_to_masses"] is False
        assert payload["observed_masses_used"] is False
        assert payload["target_ratios_used"] is False
        assert payload["charged_precision_closure"] == "OPEN"


def test_response_curves_are_exported_for_both_branches_and_all_sectors():
    for name in ("tau_response_curves_A_local_v1.json", "tau_response_curves_A_background_identity_v1.json"):
        payload = load_artifact(name)
        assert payload["tau_grid"] == [0.0, 0.01, 0.02, 0.05, 0.1]
        assert payload["stack_verdict"] == jet.STACK_JET_HEAT_SUPPORTED
        assert payload["oriented_jet_heat_response"] == "STRUCTURALLY_SUPPORTED_CANDIDATE"
        for sector in ("lepton", "up", "down"):
            row = payload["sector_curves"][sector]
            assert row["sector_verdict"] == jet.JET_HEAT_STRENGTHENS_HIERARCHY
            assert row["first_order_q_values"]["q_e"] < row["first_order_q_values"]["q_mu"]
            assert row["first_order_q_values"]["q_mu"] < row["first_order_q_values"]["q_tau"]
            assert len(row["curve"]) == 5
            assert row["curve"][0]["tau"] == 0.0
            assert row["curve"][0]["ln_Y_tau_over_Y_e"] is not None


def test_open_gate_and_claim_status_are_updated_without_closure():
    open_gate = load_artifact("full_BHSM_open_gate_ledger_v2.json")
    statuses = open_gate["statuses"]
    assert statuses["universal_tau_sigma_scaffold"] == "IMPLEMENTED_CONDITIONAL"
    assert statuses["tau_response_curves"] == "EXPORTED_NO_FIT_DIAGNOSTIC"
    assert statuses["oriented_jet_heat_response"] == "STRUCTURALLY_SUPPORTED_CANDIDATE"
    if (ROOT / "artifacts" / "BHSM_boundary_no_fit_prediction_package_v1.json").exists():
        assert statuses["tau_from_boundary_geometry"] == "DERIVED_CONDITIONAL"
        assert statuses["sigma_from_boundary_geometry"] == "DERIVED_CONDITIONAL"
    elif (ROOT / "artifacts" / "profile_normalization_hessian_closure_v1.json").exists():
        assert statuses["tau_from_boundary_geometry"] == "OPEN_LOCALIZABLE_BLOCKED_BY_KAPPA_H"
        assert statuses["sigma_from_boundary_geometry"] == "OPEN_LOCALIZABLE_BLOCKED_BY_KAPPA_H"
    else:
        assert statuses["tau_from_boundary_geometry"] == "OPEN_LOCALIZABLE"
        assert statuses["sigma_from_boundary_geometry"] == "OPEN_LOCALIZABLE"
    assert statuses["tau_from_mass_fit"] == "FORBIDDEN"
    assert statuses["sigma_from_mass_fit"] == "FORBIDDEN"
    assert statuses["charged_precision_closure"] == "OPEN"
    assert statuses["minimal_diagonal_K_collar_route"] == "REJECTED_AS_PRIMARY_BY_RESPONSE_AUDIT"
    claims = load_artifact("full_BHSM_claim_status_table_v2.json")
    rows = {row["claim"]: row["status"] for row in claims["claim_statuses"]}
    assert rows["Universal tau/sigma finite-width scaffold"] == "IMPLEMENTED_CONDITIONAL"
    assert rows["Tau response curves"] == "EXPORTED_NO_FIT_DIAGNOSTIC"


def test_source_does_not_import_empirical_closure_modules():
    text = (ROOT / "src" / "universal_tau_sigma_response_scaffold.py").read_text(encoding="utf-8")
    blocked = (
        "prediction_ledger",
        "residual_audit",
        "EMPIRICAL_MASS_RATIOS",
        "target_ratio_fixture",
        "observed_mass_fixture",
    )
    for token in blocked:
        assert token not in text


def test_frozen_prediction_files_unchanged():
    for path, expected in FROZEN_HASHES.items():
        assert sha256(path) == expected
