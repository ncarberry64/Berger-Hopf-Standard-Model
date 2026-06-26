import cmath
import hashlib
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import boundary_no_fit_package_completion as package


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


def assert_close(actual: float, expected: float, tol: float = 1e-12) -> None:
    assert math.isclose(actual, expected, rel_tol=0.0, abs_tol=tol)


def complex_from_entry(entry: dict) -> complex:
    return complex(entry["real"], entry["imag"])


def test_profile_scale_values_and_identities():
    values = load_artifact("profile_scale_closure_values_v1.json")
    assert_close(values["r_squared"], 0.07957747154594767)
    assert_close(values["r_internal_profile"], 0.28209479177387814)
    assert values["Z_H"] == 1.0
    assert_close(values["kappa_H"], 19585.25982625801)
    assert_close(values["sigma"], 69.97367331049945)
    assert_close(values["tau"], 0.04489678053129164)
    assert_close(values["identity_checks"]["sigma_times_tau"], math.pi)
    assert_close(values["identity_checks"]["kappa_H_minus_4_sigma_squared"], 0.0, tol=1e-10)
    assert_close(values["identity_checks"]["tau_minus_pi_over_sigma"], 0.0, tol=1e-16)


def test_canonical_hessian_theorem_closes_kappa_H_from_mu_H():
    theorem = load_artifact("canonical_profile_hessian_theorem_v1.json")
    kappa = load_artifact("kappa_H_profile_hessian_value_or_obstruction_v2.json")
    assert theorem["canonical_profile_hessian_theorem"] == package.AUTHOR_HESSIAN_STATUS
    assert theorem["kappa_H_formula"] == "kappa_H = mu_H = 64*pi^5"
    assert kappa["status"] == package.DERIVED_CONDITIONAL
    assert kappa["derived"] is True
    assert kappa["mu_H_identified_with_kappa_H"] is True
    assert_close(kappa["value"], 64.0 * math.pi**5)


def test_charged_boundary_values_match_exact_formulas_and_ratios():
    charged = load_artifact("charged_boundary_bridge_values_v1.json")
    sectors = charged["sectors"]
    assert_close(sectors["lepton"]["beta_tau"], 0.0005429693790632398)
    assert_close(sectors["lepton"]["kappa_tau"], 0.0005429693790632398)
    assert_close(sectors["up"]["beta_tau"], 0.0010859387581264796)
    assert_close(sectors["up"]["kappa_tau"], 0.0005429693790632398)
    assert_close(sectors["down"]["beta_tau"], 0.0021718775162529592)
    assert_close(sectors["down"]["kappa_tau"], 0.0002000413501811936)
    assert sectors["lepton"]["beta_over_kappa"] == "1/1"
    assert sectors["up"]["beta_over_kappa"] == "2/1"
    assert sectors["down"]["beta_over_kappa"] == "76/7"


def test_common_boundary_transport_identity_and_external_layer_open():
    transport = load_artifact("common_scale_boundary_transport_v1.json")
    assert transport["common_scale_boundary_transport"] == package.DERIVED_FIXED_IDENTITY
    assert transport["T_total(mu_BH_boundary -> mu_BH_boundary)"] == 1.0
    assert transport["external_empirical_RG_transport"] == package.EXTERNAL_LAYER


def test_neutral_operator_seed_values():
    neutral = load_artifact("neutral_operator_no_fit_output_v1.json")
    assert neutral["neutral_boundary_operator"] == "CLOSED_AS_BOUNDARY_SEED"
    assert neutral["H_nu"] == [[1, 1], [1, 2]]
    assert neutral["eta_nu"] == 1 / 3
    assert neutral["g_nu"] == 1 / 3
    assert neutral["beta_nu"] == 1 / 3
    assert neutral["kappa_nu"] == 1 / 6
    assert neutral["K_nu"] == [[0.0, 1 / 3, 0.0], [1 / 3, 3.0, 1 / 6], [0.0, 1 / 6, 5 / 3]]


def test_PMNS_matrix_and_jarlskog_match_test_vector():
    pmns = load_artifact("PMNS_no_fit_operator_output_v1.json")
    expected = [
        [0.993772161423 + 0.0j, 0.110875783974 + 0.0j, 0.005555441244 - 0.009622306494j],
        [-0.110705837445 - 0.001192260813j, 0.986002488911 - 0.000133021287j, 0.124667037493 + 0.0j],
        [0.008346156595 - 0.009488357144j, -0.124517123382 - 0.001058621964j, 0.992136421090 + 0.0j],
    ]
    for row_actual, row_expected in zip(pmns["matrix"], expected):
        for entry, expected_value in zip(row_actual, row_expected):
            assert abs(complex_from_entry(entry) - expected_value) < 1e-12
    assert_close(pmns["J_PMNS_BH"], 0.0001311533433935098)
    assert_close(pmns["magnitude_matrix"][0][2], 0.011110882489)


def test_CKM_angles_matrix_and_jarlskog_match_test_vector():
    ckm = load_artifact("CKM_no_fit_operator_output_v1.json")
    angles = ckm["angles"]
    tau = load_artifact("profile_scale_closure_values_v1.json")["tau"]
    assert_close(angles["theta12_CKM"], 0.007979877956825006)
    assert_close(angles["theta23_CKM"], tau * angles["theta12_CKM"])
    assert_close(angles["theta13_CKM"], tau * tau * angles["theta12_CKM"])
    expected = [
        [0.999968160814 + 0.0j, 0.007979793265 + 0.0j, 0.000008042603 - 0.000013930198j],
        [-0.007979795635 - 0.000000004991j, 0.999968096743 - 0.000000000040j, 0.000358270822 + 0.0j],
        [-0.000005183420 - 0.000013929753j, -0.000358323593 - 0.000000111160j, 0.999999935692 + 0.0j],
    ]
    for row_actual, row_expected in zip(ckm["matrix"], expected):
        for entry, expected_value in zip(row_actual, row_expected):
            assert abs(complex_from_entry(entry) - expected_value) < 1e-12
    assert_close(ckm["J_CKM_BH"], 3.982414902386615e-11, tol=1e-22)


def test_CP_holonomy_Z6_phase():
    cp = load_artifact("CP_no_fit_holonomy_output_v1.json")
    phase = complex(cp["Z6_boundary_phase"]["real"], cp["Z6_boundary_phase"]["imag"])
    assert cp["CP_boundary_holonomy"] == "CLOSED"
    assert_close(cp["delta_BH"], math.pi / 3.0)
    assert abs(phase - cmath.exp(1j * math.pi / 3.0)) < 1e-15


def test_boundary_package_status_split_and_artifact_metadata():
    payload = load_artifact("BHSM_boundary_no_fit_prediction_package_v1.json")
    assert payload["BHSM_boundary_no_fit_prediction_package"] == package.COMPLETE_EXPORTED
    assert payload["BHSM_internal_boundary_package"] == package.COMPLETE
    assert payload["external_empirical_comparison_package"] == package.EXTERNAL_LAYER
    for name in (
        "canonical_profile_hessian_theorem_v1.json",
        "tau_sigma_boundary_values_v1.json",
        "profile_scale_closure_values_v1.json",
        "charged_boundary_bridge_values_v1.json",
        "charged_outputs_at_boundary_tau_A_local_v1.json",
        "charged_outputs_at_boundary_tau_A_background_identity_v1.json",
        "common_scale_boundary_transport_v1.json",
        "neutral_operator_no_fit_output_v1.json",
        "PMNS_no_fit_operator_output_v1.json",
        "CKM_no_fit_operator_output_v1.json",
        "CP_no_fit_holonomy_output_v1.json",
        "BHSM_boundary_no_fit_prediction_package_v1.json",
    ):
        artifact = load_artifact(name)
        assert artifact["public_status_before_gate"] == package.PUBLIC_STATUS
        assert artifact["official_predictions_changed"] is False
        assert artifact["empirical_derivation_inputs_used"] is False
        assert artifact["observed_masses_used"] is False
        assert artifact["observed_Higgs_used"] is False
        assert artifact["observed_gauge_values_used"] is False
        assert artifact["observed_CKM_used"] is False
        assert artifact["observed_PMNS_used"] is False
        assert artifact["observed_CP_used"] is False
        assert artifact["external_empirical_comparison_layer"] == package.EXTERNAL_LAYER


def test_status_ledgers_export_internal_package_without_external_validation_claim():
    open_gate = load_artifact("full_BHSM_open_gate_ledger_v2.json")["statuses"]
    central = load_artifact("BHSM_numerical_gate_closure_assault_v1.json")
    assert open_gate["BHSM_boundary_no_fit_prediction_package"] == package.COMPLETE_EXPORTED
    assert open_gate["BHSM_internal_boundary_package"] == package.COMPLETE
    assert open_gate["external_empirical_comparison_package"] == package.EXTERNAL_LAYER
    assert central["BHSM_boundary_no_fit_prediction_package"] == package.COMPLETE_EXPORTED
    assert central["external_empirical_comparison_package"] == package.EXTERNAL_LAYER
    assert central["official_predictions_changed"] is False
    assert central["empirical_derivation_inputs_used"] is False


def test_forbidden_claims_absent_from_status_section_and_source():
    status = (ROOT / "docs" / "current_status.md").read_text(encoding="utf-8")
    marker = "## BHSM Boundary No-Fit Package Completion"
    assert marker in status
    section = status.split(marker, 1)[1]
    source = (ROOT / "src" / "boundary_no_fit_package_completion.py").read_text(encoding="utf-8")
    combined = section + "\n" + source
    for phrase in (
        "BHSM is proven",
        "BHSM replaces the Standard Model",
        "experimentally confirmed",
        "external empirical validation",
        "observed masses used",
    ):
        assert phrase not in combined


def test_frozen_prediction_files_unchanged():
    for path, expected in FROZEN_HASHES.items():
        assert sha256(path) == expected
