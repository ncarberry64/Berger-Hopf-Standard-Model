import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import charged_kf_generator as kf
import charged_branch_matrix_export as branch_export
import codex_reentry_branch_audit_kcollar as reentry
import bhsm_k_collar_response_audit as collar_audit


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"
FROZEN_HASHES = {
    ROOT / "docs" / "frozen_predictions.md": (
        "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4"
    ),
    ROOT / "docs" / "frozen_predictions.json": (
        "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7"
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def test_recovery_report_preserves_public_status_and_open_stack():
    payload = load_artifact("bhsm_codex_reentry_recovery_report_v1.json")
    assert payload["public_status"] == PUBLIC_STATUS
    assert payload["official_predictions_changed"] is False
    assert payload["charged_generator_classification"] == "B-diagnostic"
    assert payload["A_background_implemented"] is False
    assert payload["Z_virt_leakage_found"] is False
    assert payload["forbidden_fit_found"] is False
    assert any(row["number"] == 39 for row in payload["open_prs_detected"])


def test_charged_generator_inspection_classifies_local_rho3_as_b_diagnostic():
    inspection = reentry.inspect_charged_generator(ROOT)
    assert inspection.classification == "B-diagnostic"
    assert inspection.a_background_implemented is False
    assert "q^2 + rho_ch*j^2" in " ".join(inspection.evidence)


def test_zvirt_threshold_scope_is_only_middle_up_mode():
    assert kf.threshold_insertions() == [
        {
            "sector": "up",
            "slot": 1,
            "mode": [6, 0],
            "value": "ln 2",
            "source": "Z_virt^{u,2}=1/2 weak-double projection bridge",
            "operator_level": True,
        }
    ]


def test_branch_matrix_exports_do_not_guess_a_background():
    a_local = load_artifact("charged_branch_matrices_v2_A_local.json")
    a_bg = load_artifact("charged_branch_matrices_v2_A_background_identity.json")
    b_diag = load_artifact("charged_branch_matrices_v2_B_diagnostic.json")
    assert a_local["matrix_status"] == "EXPORTED"
    assert a_bg["matrix_status"] == "EXPORTED"
    assert a_bg["C_ch"] == 3
    assert a_bg["C_ch_source"] == "Tr_sector(P_ch)"
    assert a_bg["K_collar"] == "identity second-jet collar"
    assert a_bg["dependency_order"] == branch_export.DEPENDENCY_ORDER
    assert a_bg["chi_used"] is False
    assert a_bg["chi_fit_to_masses"] is False
    assert a_bg["direct_projected_Kf_multiplier_by_3"] is False
    assert b_diag["matrix_status"] == "EXPORTED_FROM_REPO_GENERATOR"
    assert b_diag["branch"] == "B-diagnostic"
    assert b_diag["not_A_background"] is True
    assert b_diag["used_target_data"] is False
    assert b_diag["sectors"]["up"]["Z_virt_middle_up"] == "1/2 if dressed branch active"


def test_a_background_identity_is_added_before_projection_not_direct_multiplier():
    a_local = load_artifact("charged_branch_matrices_v2_A_local.json")
    a_bg = load_artifact("charged_branch_matrices_v2_A_background_identity.json")
    for sector in ("lepton", "up", "down"):
        local = a_local["sectors"][sector]["K"]
        background = a_bg["sectors"][sector]["K"]
        differs_from_direct_multiplier = False
        for i in range(3):
            for j in range(3):
                expected = local[i][j] + (3.0 if i == j else 0.0)
                assert abs(background[i][j] - expected) < 1e-12
                if abs(background[i][j] - 3.0 * local[i][j]) > 1e-12:
                    differs_from_direct_multiplier = True
        assert differs_from_direct_multiplier


def test_k_collar_audit_runs_on_valid_matrices_and_open_on_templates():
    a_local = load_artifact("K_collar_response_audit_A_local_v2.json")
    a_bg = load_artifact("K_collar_response_audit_A_background_identity_v2.json")
    for payload in (a_local, a_bg):
        assert payload["public_status"] == PUBLIC_STATUS
        assert payload["official_predictions_changed"] is False
        assert payload["D"] == "3 diag(0,1,2)"
        assert payload["chi_source"] == "chi = lambda_A Tr(A^2)"
        assert payload["chi_fit_to_masses"] is False
        assert payload["stack_verdict"] == "STACK_COLLAR_REJECTED_AS_PRIMARY"
        assert set(payload["sector_responses"]) == {"lepton", "up", "down"}
    template_payload = collar_audit.audit_payload(
        "template",
        {"matrix_status": "OPEN_EXPORT_REQUIRED"},
    )
    assert template_payload["stack_verdict"] == "STACK_COLLAR_OPEN"


def test_frozen_constants_and_status_ledgers_are_guarded():
    constants = load_artifact("frozen_constants_v2.json")
    ledger = load_artifact("full_BHSM_open_gate_ledger_v2.json")
    claims = load_artifact("full_BHSM_claim_status_table_v2.json")
    forbidden = load_artifact("forbidden_claim_audit_v2.json")
    assert constants["public_status"] == PUBLIC_STATUS
    assert constants["Z_virt_u2"] == "1/2"
    assert constants["Z_virt_scope"] == "up sector, middle mode (q,j)=(6,0) only"
    assert ledger["statuses"]["full_BHSM_numerical_closure"] == "OPEN"
    assert ledger["statuses"]["chi_from_mass_fit"] == "FORBIDDEN"
    assert ledger["statuses"]["A_local_branch_matrix_export"] == "EXPORTED"
    assert ledger["statuses"]["A_background_identity_branch"] == "IMPLEMENTED_CONDITIONAL"
    assert ledger["statuses"]["A_background_dependency_order"] == "VERIFIED"
    assert ledger["statuses"]["K_collar_response_audit"] == "RAN"
    assert ledger["statuses"]["B_diagnostic_branch"] == "ALLOWED_ONLY_AS_DIAGNOSTIC"
    assert claims["official_predictions_changed"] is False
    assert forbidden["forbidden_claims_absent"] is True


def test_public_status_appears_in_all_new_artifacts():
    paths = list((ROOT / "artifacts").glob("*_v2.json"))
    paths.append(ROOT / "artifacts" / "a_background_collar_dependency_order_v1.json")
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["public_status"] == PUBLIC_STATUS
        assert payload["official_predictions_changed"] is False
    recovery = load_artifact("bhsm_codex_reentry_recovery_report_v1.json")
    assert recovery["public_status"] == PUBLIC_STATUS


def test_no_forbidden_derivation_imports_in_new_source():
    text = (ROOT / "src" / "codex_reentry_branch_audit_kcollar.py").read_text(encoding="utf-8")
    blocked = (
        "import prediction_ledger",
        "import residual_audit",
        "from prediction_ledger",
        "from residual_audit",
        "observed_mass =",
        "empirical_target =",
        "fit_to_masses = True",
    )
    for token in blocked:
        assert token not in text


def test_frozen_prediction_files_unchanged():
    for path, expected in FROZEN_HASHES.items():
        assert sha256(path) == expected
