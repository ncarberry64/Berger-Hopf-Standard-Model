import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_raw_mode_berger_harmonic as rh  # noqa: E402


def test_raw_mode_berger_harmonic_schema_partial_status():
    payload = rh.export_outputs(ROOT)
    parsed = json.loads((ROOT / "theory" / "theorem_discharge_raw_mode_berger_harmonic_results.json").read_text())

    assert parsed == payload
    assert parsed["status"] == "partial_theorem_scaffold"
    assert parsed["branch"] == "bhsm-theorem-discharge-raw-mode-berger-harmonic-map-v1"
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["standard_model_fully_derived"] is False
    assert parsed["raw_mode_map_completed"] is True
    assert parsed["raw_mode_map_formula"] == "k=q+2j"
    assert parsed["j_fiber_weight_derived"] is False
    assert parsed["m_weight_assignment_derived"] is False
    assert parsed["explicit_eigenfunctions_derived"] is False
    assert parsed["finite_width_rank_three_derived"] is False
    assert parsed["numerical_yukawa_values_derived"] is False
    assert parsed["bhsm_replacement_claim_ready"] is False
    assert "PO-BH-25" in parsed["discharged_obligations"]
    assert "PO_BH_25_RAW_MODE_BERGER_HARMONIC_MAP_PARTIAL" in parsed["verdict_labels"]


def test_raw_mode_berger_harmonic_required_files_exist():
    rh.export_outputs(ROOT)
    for name in [
        "theorem_discharge_raw_mode_berger_harmonic_map.md",
        "derived_raw_mode_map_k_equals_q_plus_2j.md",
        "derived_generation_raw_mode_ledgers.md",
        "derived_candidate_berger_hopf_harmonic_form.md",
        "derived_j_fiber_weight_audit.md",
        "derived_m_weight_assignment_open_problem.md",
        "derived_raw_mode_to_feature_vector_bridge.md",
        "derived_raw_mode_harmonic_map_status.md",
        "raw_mode_berger_harmonic_non_tautology_audit.md",
        "theorem_discharge_raw_mode_berger_harmonic_results.json",
    ]:
        assert (ROOT / "theory" / name).exists()
