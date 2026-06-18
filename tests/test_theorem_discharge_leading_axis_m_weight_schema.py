import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_leading_axis_m_weight as la  # noqa: E402


def test_leading_axis_m_weight_schema_partial_status():
    payload = la.export_outputs(ROOT)
    parsed = json.loads((ROOT / "theory" / "theorem_discharge_leading_axis_m_weight_results.json").read_text())

    assert parsed == payload
    assert parsed["status"] == "partial_theorem_scaffold"
    assert parsed["branch"] == "bhsm-theorem-discharge-leading-axis-m-weight-v1"
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["standard_model_fully_derived"] is False
    assert parsed["bhsm_replacement_claim_ready"] is False
    assert parsed["leading_axis_m_weight_layer_completed"] is True
    assert parsed["y0_axis_sampling_derived"] is False
    assert parsed["leading_axis_m_assignment_derived"] is False
    assert parsed["candidate_assignment"] == "m=n=q/2"
    assert "PO-BH-28" in parsed["discharged_obligations"]
    assert "PO_BH_28_LEADING_AXIS_M_WEIGHT_ASSIGNMENT_PARTIAL" in parsed["verdict_labels"]


def test_leading_axis_required_files_exist():
    la.export_outputs(ROOT)
    for name in [
        "theorem_discharge_leading_axis_m_weight.md",
        "derived_y0_axis_sampling_audit.md",
        "derived_wigner_identity_axis_selection.md",
        "derived_m_equals_n_leading_axis_assignment.md",
        "derived_m_equals_q_over_2_leading_component.md",
        "derived_leading_axis_harmonic_representatives.md",
        "derived_leading_axis_admissibility_audit.md",
        "derived_leading_axis_to_feature_vector_bridge.md",
        "derived_leading_axis_m_weight_status.md",
        "leading_axis_m_weight_non_tautology_audit.md",
        "theorem_discharge_leading_axis_m_weight_results.json",
    ]:
        assert (ROOT / "theory" / name).exists()
