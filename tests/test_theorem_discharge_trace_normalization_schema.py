import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_trace_normalization as trace  # noqa: E402


def test_trace_normalization_results_schema_and_labels():
    payload = trace.export_outputs(ROOT)
    parsed = json.loads(
        (ROOT / "theory" / "theorem_discharge_trace_normalization_results.json").read_text(
            encoding="utf-8"
        )
    )
    assert parsed == payload
    assert parsed["status"] == "theorem_discharge_candidate"
    assert parsed["branch"] == "bhsm-theorem-discharge-boundary-trace-normalization-v1"
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["standard_model_fully_derived"] is False
    assert parsed["bhsm_replacement_claim_ready"] is False
    assert parsed["trace_normalization_layer_discharged_conditionally"] is True
    assert parsed["rg_running_derived"] is False
    assert parsed["measured_couplings_predicted"] is False

    labels = set(parsed["verdict_labels"])
    assert "PO_BH_14_BOUNDARY_TRACE_NORMALIZATION_DERIVED_CONDITIONAL" in labels
    assert "HYPERCHARGE_TRACE_FACTOR_3_5_DERIVED_CONDITIONAL" in labels
    assert "GAUGE_COUPLING_CONVENTION_5_3_DERIVED_CONDITIONAL" in labels
    assert "RG_RUNNING_REMAINS_OPEN" in labels
    assert "MEASURED_COUPLINGS_REMAIN_OPEN" in labels


def test_trace_normalization_required_files_exist():
    trace.export_outputs(ROOT)
    required = [
        "theorem_discharge_boundary_trace_normalization.md",
        "derived_boundary_trace_weights.md",
        "derived_hypercharge_normalization_factor.md",
        "derived_normalized_gauge_action_skeleton.md",
        "trace_normalization_non_tautology_audit.md",
        "theorem_discharge_trace_normalization_results.json",
    ]
    for name in required:
        assert (ROOT / "theory" / name).exists()
