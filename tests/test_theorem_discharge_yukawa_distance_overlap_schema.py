import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_distance_overlap as d  # noqa: E402


def test_yukawa_distance_overlap_results_schema_partial_status():
    payload = d.export_outputs(ROOT)
    parsed = json.loads((ROOT / "theory" / "theorem_discharge_yukawa_distance_overlap_results.json").read_text())
    assert parsed == payload
    assert parsed["status"] == "partial_theorem_scaffold"
    assert parsed["branch"] == "bhsm-theorem-discharge-yukawa-distance-overlap-law-v1"
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["standard_model_fully_derived"] is False
    assert parsed["bhsm_replacement_claim_ready"] is False
    assert parsed["distance_overlap_law_discharged_conditionally"] is False
    assert parsed["distance_diagnostics_preserved"] is True
    assert parsed["candidate_laws_audited"] is True
    assert parsed["numerical_overlap_values_derived"] is False
    assert parsed["fermion_mass_ratios_derived"] is False
    assert parsed["ckm_values_derived"] is False
    assert parsed["pmns_values_derived"] is False
    assert parsed["candidate_law_status"]["selection_only"] == "DERIVED_CONDITIONAL"
    assert parsed["candidate_law_status"]["boundary_action_hessian"] == "REMAINS_OPEN"
    assert "PO_BH_21_YUKAWA_DISTANCE_OVERLAP_LAW_PARTIAL" in parsed["verdict_labels"]
    assert "NUMERICAL_OVERLAP_LAW_REMAINS_OPEN" in parsed["verdict_labels"]


def test_yukawa_distance_overlap_required_files_exist():
    d.export_outputs(ROOT)
    for name in [
        "theorem_discharge_yukawa_distance_overlap_law.md",
        "derived_yukawa_distance_overlap_candidates.md",
        "derived_yukawa_boundary_action_overlap_audit.md",
        "derived_yukawa_distance_kernel_status.md",
        "derived_yukawa_overlap_value_guardrails.md",
        "derived_yukawa_numerical_kernel_open_problem.md",
        "yukawa_distance_overlap_non_tautology_audit.md",
        "theorem_discharge_yukawa_distance_overlap_results.json",
    ]:
        assert (ROOT / "theory" / name).exists()
