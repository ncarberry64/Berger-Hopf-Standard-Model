import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rg_transport_interface as rg
import same_sector_rg_gauge_cancellation as theorem


DATA = ROOT / "data" / "same_sector_rg_gauge_cancellation_v1.json"
FROZEN_MD = ROOT / "docs" / "frozen_predictions.md"
FROZEN_JSON = ROOT / "docs" / "frozen_predictions.json"

EXPECTED_FROZEN_HASHES = {
    FROZEN_MD: "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4",
    FROZEN_JSON: "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7",
}


def sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_same_sector_charged_ratios_are_partially_localized():
    records = {record.ratio_id: record for record in theorem.charged_same_sector_records()}
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
        assert record.same_sector is True
        assert record.numerator_sector == sector
        assert record.denominator_sector == sector
        assert record.gauge_transport_component == theorem.GAUGE_CANCELED
        assert record.residual_transport == theorem.RESIDUAL_OPEN
        assert record.transport_stage == "RG_TRANSPORT_PARTIALLY_LOCALIZED"
        assert record.comparison_ready is False


def test_cross_sector_examples_are_not_canceled_by_same_sector_theorem():
    records = {record.ratio_id: record for record in theorem.cross_sector_records()}
    assert set(records) == {"tau_over_t", "b_over_t", "nu_over_l"}
    for record in records.values():
        assert record.same_sector is False
        assert record.gauge_transport_component == theorem.GAUGE_NOT_CANCELED
        assert record.transport_stage == "RG_TRANSPORT_PENDING"
        assert record.comparison_ready is False


def test_verdict_is_conditional_and_leaves_residual_blockers_open():
    verdict = theorem.theorem_verdict()
    assert verdict.status == theorem.THEOREM_STATUS
    assert verdict.theorem_complete is False
    assert "Yukawa/self transport" in verdict.residual_blockers
    assert "scheme alignment" in verdict.residual_blockers
    assert verdict.public_status == theorem.PUBLIC_STATUS


def test_rg_interface_represents_partial_localization_without_scheme_alignment():
    readiness = {record.sector: record for record in rg.comparison_readiness_records()}
    for sector in ("charged_lepton", "up", "down"):
        record = readiness[sector]
        assert record.current_readiness == "RG_TRANSPORT_PARTIALLY_LOCALIZED"
        assert record.gauge_component == "CANCELED_BY_SAME_SECTOR_THEOREM"
        assert record.residual_component == "OPEN_LOCALIZABLE"
        assert record.comparison_readiness == "NOT_READY"
        assert record.comparison_readiness != "COMPARISON_READY"
    assert readiness["neutral"].current_readiness == "RG_TRANSPORT_PENDING"
    assert rg.STATUS_TABLE["scheme_alignment"] == "OPEN"
    assert rg.STATUS_TABLE["comparison_ready_predictions"] == "OPEN"
    assert rg.STATUS_TABLE["numerical_closure"] == "OPEN"


def test_data_artifact_matches_guardrails_and_public_status():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    assert data["public_status"] == theorem.PUBLIC_STATUS
    assert data["status_verdict"]["status"] == theorem.THEOREM_STATUS
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    assert data["uses_empirical_derivation_inputs"] is False
    assert data["status_verdict"]["theorem_complete"] is False


def test_no_empirical_imports_in_rg_cancellation_modules():
    combined = "\n".join(
        Path(module.__file__).read_text(encoding="utf-8")
        for module in (theorem, rg)
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
    )
    for item in blocked:
        assert item not in combined


def test_frozen_prediction_files_remain_unchanged():
    for path, expected in EXPECTED_FROZEN_HASHES.items():
        assert sha256(path) == expected
