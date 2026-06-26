import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import residual_yukawa_transport_decomposition as residual
import rg_transport_interface as rg


DATA = ROOT / "data" / "residual_yukawa_transport_decomposition_v1.json"
FROZEN_MD = ROOT / "docs" / "frozen_predictions.md"
FROZEN_JSON = ROOT / "docs" / "frozen_predictions.json"

EXPECTED_FROZEN_HASHES = {
    FROZEN_MD: "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4",
    FROZEN_JSON: "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7",
}


def sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_same_sector_ratios_cancel_sector_universal_residual_identity():
    records = {record.ratio_id: record for record in residual.charged_same_sector_records()}
    expected = {
        "mu_over_tau": "charged_lepton",
        "e_over_tau": "charged_lepton",
        "c_over_t": "up",
        "u_over_t": "up",
        "s_over_b": "down",
        "d_over_b": "down",
    }
    assert set(records) == set(expected)
    for ratio_id, sector in expected.items():
        record = records[ratio_id]
        assert record.sector == sector
        assert record.same_sector is True
        assert record.gauge_component == "CANCELED_BY_SAME_SECTOR_THEOREM"
        assert record.sector_universal_residual_component == (
            "CANCELED_BY_SAME_SECTOR_BRANCH_SPACE"
        )
        assert record.branch_differential_residual_component == "OPEN_LOCALIZABLE"
        assert record.transport_stage == "RG_TRANSPORT_RESIDUAL_LOCALIZED"
        assert record.comparison_ready is False


def test_cross_sector_residual_identity_cancellation_not_applicable():
    records = {record.ratio_id: record for record in residual.cross_sector_records()}
    assert set(records) == {"tau_over_t", "b_over_t", "nu_over_l"}
    for record in records.values():
        assert record.same_sector is False
        assert record.same_sector_identity_cancellation == "NOT_APPLICABLE"
        assert record.comparison_ready is False


def test_kf_aligned_residual_transport_is_candidate_only():
    candidate = residual.kf_aligned_residual_candidate()
    assert candidate.status == "STRUCTURALLY_MOTIVATED_CANDIDATE"
    assert candidate.coefficient_status == "OPEN_LOCALIZABLE"
    assert candidate.uses_empirical_inputs is False
    assert "proportional_to" in candidate.formula


def test_residual_verdict_is_conditional_and_not_numerical_closure():
    verdict = residual.theorem_verdict()
    assert verdict.same_sector_residual_identity_cancellation == (
        "DERIVED_CONDITIONAL_ON_SHARED_SECTOR_BRANCH_SPACE"
    )
    assert verdict.residual_Yukawa_transport_decomposition == "PARTIALLY_LOCALIZED"
    assert verdict.charged_branch_differential_residual_transport == "OPEN_LOCALIZABLE"
    assert verdict.Kf_residual_transport_coefficient == "OPEN_LOCALIZABLE"
    assert verdict.theorem_complete is False
    assert verdict.public_status == residual.PUBLIC_STATUS


def test_rg_interface_reaches_residual_localized_without_scheme_or_comparison_ready():
    readiness = {record.sector: record for record in rg.comparison_readiness_records()}
    for sector in ("charged_lepton", "up", "down"):
        record = readiness[sector]
        assert record.current_readiness == "RG_TRANSPORT_RESIDUAL_LOCALIZED"
        assert record.gauge_component == "CANCELED_BY_SAME_SECTOR_THEOREM"
        assert record.sector_universal_residual_component == (
            "CANCELED_BY_SAME_SECTOR_BRANCH_SPACE"
        )
        assert record.branch_differential_residual_component == "OPEN_LOCALIZABLE"
        assert record.comparison_readiness == "NOT_READY"
    assert rg.STATUS_TABLE["scheme_alignment"] == "OPEN"
    assert rg.STATUS_TABLE["comparison_ready_predictions"] == "OPEN"
    assert rg.STATUS_TABLE["numerical_closure"] == "OPEN"


def test_data_artifact_matches_guardrails_and_public_status():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    assert data["public_status"] == residual.PUBLIC_STATUS
    assert data["status_verdict"]["residual_Yukawa_transport_decomposition"] == (
        "PARTIALLY_LOCALIZED"
    )
    assert data["Kf_aligned_residual_candidate"]["status"] == (
        "STRUCTURALLY_MOTIVATED_CANDIDATE"
    )
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    assert data["uses_empirical_derivation_inputs"] is False
    assert data["status_verdict"]["theorem_complete"] is False


def test_no_empirical_imports_in_residual_transport_modules():
    combined = "\n".join(
        Path(module.__file__).read_text(encoding="utf-8")
        for module in (residual, rg)
    )
    blocked = (
        "prediction_ledger",
        "residual_audit",
        "mass_scheme",
        "quark_running",
        "ckm",
        "pmns",
        "gauge_couplings",
        "reference_common_scale",
        "neutrino_mass",
        "measured_yukawa",
    )
    for item in blocked:
        assert item not in combined


def test_frozen_prediction_files_remain_unchanged():
    for path, expected in EXPECTED_FROZEN_HASHES.items():
        assert sha256(path) == expected
