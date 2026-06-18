import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_harmonic_highest_weight as hw  # noqa: E402


def test_harmonic_highest_weight_schema_conditional_status():
    payload = hw.export_outputs(ROOT)
    parsed = json.loads((ROOT / "theory" / "theorem_discharge_harmonic_highest_weight_results.json").read_text())

    assert parsed == payload
    assert parsed["status"] == "theorem_discharge_candidate"
    assert parsed["branch"] == "bhsm-theorem-discharge-harmonic-highest-weight-normalization-v1"
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["standard_model_fully_derived"] is False
    assert parsed["bhsm_replacement_claim_ready"] is False
    assert parsed["highest_weight_normalization_derived_conditionally"] is True
    assert parsed["selected_n_weight_convention"] == "ell=k/2, n=q/2, j=ell-n"
    assert parsed["m_weight_assignment_derived"] is False
    assert parsed["explicit_eigenfunctions_derived"] is False
    assert parsed["finite_width_rank_three_derived"] is False
    assert parsed["numerical_yukawa_values_derived"] is False
    assert "PO-BH-27" in parsed["discharged_obligations"]
    assert "PO_BH_27_HARMONIC_HIGHEST_WEIGHT_NORMALIZATION_DERIVED_CONDITIONAL" in parsed["verdict_labels"]


def test_harmonic_highest_weight_required_files_exist():
    hw.export_outputs(ROOT)
    for name in [
        "theorem_discharge_harmonic_highest_weight_normalization.md",
        "derived_highest_weight_relation_q_equals_k_minus_2j.md",
        "derived_wigner_weight_n_equals_q_over_2.md",
        "derived_j_as_lowering_index.md",
        "derived_selected_harmonic_n_convention.md",
        "derived_highest_weight_admissibility_audit.md",
        "derived_remaining_m_weight_open_problem.md",
        "derived_highest_weight_to_feature_vector_bridge.md",
        "harmonic_highest_weight_non_tautology_audit.md",
        "theorem_discharge_harmonic_highest_weight_results.json",
    ]:
        assert (ROOT / "theory" / name).exists()
