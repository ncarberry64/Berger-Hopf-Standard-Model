import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_finite_algebra_charge as discharge  # noqa: E402


def test_exported_results_schema_and_required_labels():
    payload = discharge.export_outputs(ROOT)
    json_path = ROOT / "theory" / "theorem_discharge_finite_algebra_charge_results.json"
    parsed = json.loads(json_path.read_text(encoding="utf-8"))

    assert parsed == payload
    assert parsed["status"] == "theorem_discharge_candidate"
    assert parsed["branch"] == "bhsm-theorem-discharge-finite-algebra-charge-v1"
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["standard_model_fully_derived"] is False
    assert parsed["bhsm_replacement_claim_ready"] is False
    assert parsed["finite_algebra_charge_layer_discharged_conditionally"] is True

    labels = set(parsed["verdict_labels"])
    assert "THEOREM_DISCHARGE_FINITE_ALGEBRA_CHARGE_COMPLETE" in labels
    assert "PO_BH_9_FINITE_ALGEBRA_UNIQUENESS_DERIVED_CONDITIONAL" in labels
    assert "PO_BH_10_CHARGE_HYPERCHARGE_OPERATORS_DERIVED_CONDITIONAL" in labels
    assert "DOWNSTREAM_SM_DERIVATION_REMAINS_OPEN" in labels
    assert "BHSM_REPLACEMENT_CLAIM_NOT_READY" in labels


def test_required_output_files_are_generated():
    discharge.export_outputs(ROOT)
    required = [
        "theorem_discharge_finite_algebra_charge.md",
        "derived_finite_algebra_uniqueness.md",
        "derived_boundary_charge_operator.md",
        "derived_boundary_hypercharge_operator.md",
        "finite_algebra_charge_non_tautology_audit.md",
        "theorem_discharge_finite_algebra_charge_results.json",
    ]
    for name in required:
        assert (ROOT / "theory" / name).exists()
