import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_m_multiplet_harmonic_features as mm  # noqa: E402


def test_m_multiplet_schema_and_payload():
    payload = mm.export_outputs(ROOT)
    parsed = json.loads((ROOT / "theory" / "theorem_discharge_m_multiplet_harmonic_features_results.json").read_text())

    assert parsed == payload
    assert parsed["status"] == "theorem_discharge_candidate"
    assert parsed["branch"] == "bhsm-theorem-discharge-m-multiplet-harmonic-features-v1"
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["standard_model_fully_derived"] is False
    assert parsed["bhsm_replacement_claim_ready"] is False
    assert parsed["m_multiplet_scaffold_derived_conditionally"] is True
    assert parsed["axis_collapse_case_documented"] is True
    assert parsed["generic_y0_case_documented"] is True
    assert parsed["single_m_assignment_forced"] is False
    assert "PO-BH-30" in parsed["discharged_obligations"]
    assert "PO_BH_30_M_MULTIPLET_HARMONIC_FEATURE_SCAFFOLD_DERIVED_CONDITIONAL" in parsed["verdict_labels"]


def test_m_multiplet_required_files_exist():
    mm.export_outputs(ROOT)
    for name in [
        "theorem_discharge_m_multiplet_harmonic_features.md",
        "derived_m_multiplet_admissible_set.md",
        "derived_m_multiplet_harmonic_representatives.md",
        "derived_axis_collapse_vs_generic_y0_sampling.md",
        "derived_generic_y0_wigner_evaluation_scaffold.md",
        "derived_m_multiplet_local_feature_vectors.md",
        "derived_m_multiplet_rank_support_condition.md",
        "derived_m_multiplet_yukawa_bridge.md",
        "derived_m_multiplet_open_problem.md",
        "m_multiplet_harmonic_features_non_tautology_audit.md",
        "theorem_discharge_m_multiplet_harmonic_features_results.json",
    ]:
        assert (ROOT / "theory" / name).exists()
