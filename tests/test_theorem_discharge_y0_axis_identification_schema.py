import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_y0_axis_identification as y0  # noqa: E402


def test_y0_axis_identification_schema_partial_status():
    payload = y0.export_outputs(ROOT)
    parsed = json.loads((ROOT / "theory" / "theorem_discharge_y0_axis_identification_results.json").read_text())

    assert parsed == payload
    assert parsed["status"] == "partial_theorem_scaffold"
    assert parsed["branch"] == "bhsm-theorem-discharge-y0-axis-identification-v1"
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["standard_model_fully_derived"] is False
    assert parsed["bhsm_replacement_claim_ready"] is False
    assert parsed["y0_axis_identification_layer_completed"] is True
    assert parsed["y0_profile_peak_supported"] is True
    assert parsed["y0_axis_sampling_derived"] is False
    assert parsed["m_equals_q_over_2_promotable"] is False
    assert "PO-BH-29" in parsed["discharged_obligations"]
    assert "PO_BH_29_Y0_AXIS_IDENTIFICATION_PARTIAL" in parsed["verdict_labels"]


def test_y0_axis_identification_required_files_exist():
    y0.export_outputs(ROOT)
    for name in [
        "theorem_discharge_y0_axis_identification.md",
        "derived_y0_profile_peak_status.md",
        "derived_y0_squashed_axis_alignment_audit.md",
        "derived_y0_identity_axis_audit.md",
        "derived_y0_hopf_pole_audit.md",
        "derived_y0_axis_sampling_bridge.md",
        "derived_y0_axis_identification_status.md",
        "derived_y0_to_m_weight_bridge.md",
        "derived_y0_axis_open_problem.md",
        "y0_axis_identification_non_tautology_audit.md",
        "theorem_discharge_y0_axis_identification_results.json",
    ]:
        assert (ROOT / "theory" / name).exists()
