import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_m_weight_assignment as mw  # noqa: E402


def test_m_weight_assignment_schema_partial_status():
    payload = mw.export_outputs(ROOT)
    parsed = json.loads((ROOT / "theory" / "theorem_discharge_m_weight_assignment_results.json").read_text())

    assert parsed == payload
    assert parsed["status"] == "partial_theorem_scaffold"
    assert parsed["branch"] == "bhsm-theorem-discharge-m-weight-assignment-v1"
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["standard_model_fully_derived"] is False
    assert parsed["m_weight_assignment_layer_completed"] is True
    assert parsed["m_weight_assignment_derived"] is False
    assert parsed["selected_harmonic_convention_derived"] is False
    assert parsed["explicit_eigenfunctions_derived"] is False
    assert parsed["finite_width_rank_three_derived"] is False
    assert parsed["numerical_yukawa_values_derived"] is False
    assert parsed["bhsm_replacement_claim_ready"] is False
    assert "PO-BH-26" in parsed["discharged_obligations"]
    assert "PO_BH_26_M_WEIGHT_ASSIGNMENT_FROM_BOUNDARY_ORIENTATION_PARTIAL" in parsed["verdict_labels"]


def test_m_weight_assignment_required_files_exist():
    mw.export_outputs(ROOT)
    for name in [
        "theorem_discharge_m_weight_assignment.md",
        "derived_wigner_admissibility_audit.md",
        "derived_m_weight_candidate_assignments.md",
        "derived_boundary_orientation_sources_for_m.md",
        "derived_m_weight_assignment_status.md",
        "derived_harmonic_convention_status.md",
        "derived_m_weight_to_feature_vector_bridge.md",
        "derived_m_weight_open_problem.md",
        "m_weight_assignment_non_tautology_audit.md",
        "theorem_discharge_m_weight_assignment_results.json",
    ]:
        assert (ROOT / "theory" / name).exists()
