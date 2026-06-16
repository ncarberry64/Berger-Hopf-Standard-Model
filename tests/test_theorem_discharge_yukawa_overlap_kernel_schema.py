import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_overlap_kernel as k  # noqa: E402


def test_yukawa_overlap_kernel_results_schema_and_labels():
    payload = k.export_outputs(ROOT)
    parsed = json.loads((ROOT / "theory" / "theorem_discharge_yukawa_overlap_kernel_results.json").read_text())
    assert parsed == payload
    assert parsed["status"] == "theorem_discharge_candidate"
    assert parsed["branch"] == "bhsm-theorem-discharge-yukawa-overlap-kernel-selection-v1"
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["standard_model_fully_derived"] is False
    assert parsed["bhsm_replacement_claim_ready"] is False
    assert parsed["yukawa_overlap_kernel_layer_discharged_conditionally"] is True
    assert parsed["numerical_overlap_values_derived"] is False
    assert parsed["fermion_mass_ratios_derived"] is False
    assert parsed["ckm_values_derived"] is False
    assert parsed["pmns_values_derived"] is False
    assert parsed["texture_summary"] == {
        "leading_diagonal_entries": 12,
        "conditional_off_diagonal_entries": 24,
        "forbidden_entries": 0,
        "total_entries": 36,
    }
    labels = set(parsed["verdict_labels"])
    for label in [
        "THEOREM_DISCHARGE_YUKAWA_OVERLAP_KERNEL_SELECTION_COMPLETE",
        "PO_BH_20_YUKAWA_OVERLAP_KERNEL_SELECTION_DERIVED_CONDITIONAL",
        "YUKAWA_MODE_ALIGNMENT_PRINCIPLE_DERIVED_CONDITIONAL",
        "YUKAWA_MODE_DISTANCE_SCAFFOLD_DERIVED_CONDITIONAL",
        "NUMERICAL_OVERLAP_VALUES_REMAIN_OPEN",
        "CKM_VALUES_REMAIN_OPEN",
        "PMNS_VALUES_REMAIN_OPEN",
        "BHSM_REPLACEMENT_CLAIM_NOT_READY",
    ]:
        assert label in labels


def test_yukawa_overlap_kernel_required_files_exist():
    k.export_outputs(ROOT)
    for name in [
        "theorem_discharge_yukawa_overlap_kernel_selection.md",
        "derived_yukawa_overlap_kernel_selection_rules.md",
        "derived_yukawa_mode_alignment_principle.md",
        "derived_yukawa_mode_distance_scaffold.md",
        "derived_yukawa_leading_texture_status.md",
        "derived_yukawa_off_diagonal_overlap_status.md",
        "derived_yukawa_mass_hierarchy_bridge.md",
        "derived_yukawa_mixing_source_bridge.md",
        "yukawa_overlap_kernel_non_tautology_audit.md",
        "theorem_discharge_yukawa_overlap_kernel_results.json",
    ]:
        assert (ROOT / "theory" / name).exists()
