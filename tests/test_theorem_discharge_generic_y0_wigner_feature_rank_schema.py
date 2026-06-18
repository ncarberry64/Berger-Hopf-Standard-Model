import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_generic_y0_wigner_feature_rank as gy0  # noqa: E402


def test_generic_y0_schema_and_payload():
    payload = gy0.export_outputs(ROOT)
    parsed = json.loads((ROOT / "theory" / "theorem_discharge_generic_y0_wigner_feature_rank_results.json").read_text())

    assert parsed == payload
    assert parsed["status"] == "theorem_discharge_candidate"
    assert parsed["branch"] == "bhsm-theorem-discharge-generic-y0-wigner-feature-rank-v1"
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["standard_model_fully_derived"] is False
    assert parsed["bhsm_replacement_claim_ready"] is False
    assert parsed["generic_y0_wigner_scaffold_derived_conditionally"] is True
    assert "PO-BH-31" in parsed["discharged_obligations"]
    assert "PO_BH_31_GENERIC_Y0_WIGNER_FEATURE_RANK_SCAFFOLD_DERIVED_CONDITIONAL" in parsed["verdict_labels"]


def test_generic_y0_required_files_exist():
    gy0.export_outputs(ROOT)
    for name in [
        "theorem_discharge_generic_y0_wigner_feature_rank.md",
        "derived_generic_y0_coordinate_scaffold.md",
        "derived_generic_y0_wigner_evaluation_formula.md",
        "derived_reduced_wigner_beta_selector.md",
        "derived_generic_y0_phase_structure.md",
        "derived_generic_y0_local_feature_vectors.md",
        "derived_generic_y0_feature_rank_condition.md",
        "derived_axis_collapse_recovery_case.md",
        "derived_generic_y0_yukawa_bridge.md",
        "derived_generic_y0_open_problem.md",
        "generic_y0_wigner_feature_rank_non_tautology_audit.md",
        "theorem_discharge_generic_y0_wigner_feature_rank_results.json",
    ]:
        assert (ROOT / "theory" / name).exists()
