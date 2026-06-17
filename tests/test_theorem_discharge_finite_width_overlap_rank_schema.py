import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_finite_width_overlap_rank as fw  # noqa: E402


def test_finite_width_overlap_rank_results_schema_partial_status():
    payload = fw.export_outputs(ROOT)
    parsed = json.loads((ROOT / "theory" / "theorem_discharge_finite_width_overlap_rank_results.json").read_text())

    assert parsed == payload
    assert parsed["status"] == "partial_theorem_scaffold"
    assert parsed["branch"] == "bhsm-theorem-discharge-finite-width-overlap-rank-v1"
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["standard_model_fully_derived"] is False
    assert parsed["bhsm_replacement_claim_ready"] is False
    assert parsed["finite_width_overlap_rank_layer_completed"] is True
    assert parsed["strict_point_sampling_rank_three_derived"] is False
    assert parsed["finite_width_rank_three_derived"] is False
    assert parsed["numerical_yukawa_values_derived"] is False
    assert parsed["fermion_mass_ratios_derived"] is False
    assert parsed["ckm_values_derived"] is False
    assert parsed["pmns_values_derived"] is False
    assert parsed["rank_results"]["rank_three_status"] == "OPEN"
    assert "PO-BH-23" in parsed["discharged_obligations"]
    assert "PO_BH_23_FINITE_WIDTH_OVERLAP_RANK_THEOREM_PARTIAL" in parsed["verdict_labels"]


def test_finite_width_overlap_rank_required_files_exist():
    fw.export_outputs(ROOT)
    for name in [
        "theorem_discharge_finite_width_overlap_rank.md",
        "derived_finite_width_overlap_moment_expansion.md",
        "derived_sharp_peak_outer_product_limit.md",
        "derived_rank_three_overlap_condition.md",
        "derived_internal_eigenfunction_independence_condition.md",
        "derived_universal_profile_width_guardrail.md",
        "derived_finite_width_overlap_rank_status.md",
        "derived_yukawa_rank_three_open_problem.md",
        "finite_width_overlap_rank_non_tautology_audit.md",
        "theorem_discharge_finite_width_overlap_rank_results.json",
    ]:
        assert (ROOT / "theory" / name).exists()
