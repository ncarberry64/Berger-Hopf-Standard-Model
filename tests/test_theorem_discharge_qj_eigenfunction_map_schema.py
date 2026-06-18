import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_qj_eigenfunction_map as qj  # noqa: E402


def test_qj_eigenfunction_map_results_schema_partial_status():
    payload = qj.export_outputs(ROOT)
    parsed = json.loads((ROOT / "theory" / "theorem_discharge_qj_eigenfunction_map_results.json").read_text())

    assert parsed == payload
    assert parsed["status"] == "partial_theorem_scaffold"
    assert parsed["branch"] == "bhsm-theorem-discharge-qj-eigenfunction-map-v1"
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["standard_model_fully_derived"] is False
    assert parsed["bhsm_replacement_claim_ready"] is False
    assert parsed["qj_eigenfunction_map_scaffold_completed"] is True
    assert parsed["explicit_qj_eigenfunction_map_derived"] is False
    assert parsed["internal_feature_independence_derived"] is False
    assert parsed["finite_width_rank_three_derived"] is False
    assert parsed["numerical_yukawa_values_derived"] is False
    assert parsed["fermion_mass_ratios_derived"] is False
    assert parsed["ckm_values_derived"] is False
    assert parsed["pmns_values_derived"] is False
    assert "PO-BH-24" in parsed["discharged_obligations"]
    assert "PO_BH_24_QJ_TO_INTERNAL_EIGENFUNCTION_MAP_PARTIAL" in parsed["verdict_labels"]


def test_qj_eigenfunction_map_required_files_exist():
    qj.export_outputs(ROOT)
    for name in [
        "theorem_discharge_qj_eigenfunction_map.md",
        "derived_qj_to_internal_eigenfunction_map.md",
        "derived_internal_eigenfunction_mode_scaffold.md",
        "derived_internal_local_feature_vectors.md",
        "derived_diagonal_hierarchy_route.md",
        "derived_full_rank_three_route.md",
        "derived_internal_feature_independence_condition.md",
        "derived_finite_width_moment_feature_contractions.md",
        "derived_qj_eigenfunction_map_status.md",
        "derived_internal_eigenfunction_numerical_open_problem.md",
        "qj_eigenfunction_map_non_tautology_audit.md",
        "theorem_discharge_qj_eigenfunction_map_results.json",
    ]:
        assert (ROOT / "theory" / name).exists()
