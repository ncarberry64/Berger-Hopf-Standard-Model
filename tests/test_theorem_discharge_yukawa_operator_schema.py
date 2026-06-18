import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_operator as y  # noqa: E402


def test_yukawa_operator_results_schema_and_labels():
    payload = y.export_outputs(ROOT)
    parsed = json.loads((ROOT / "theory" / "theorem_discharge_yukawa_operator_results.json").read_text())
    assert parsed == payload
    assert parsed["status"] == "theorem_discharge_candidate"
    assert parsed["branch"] == "bhsm-theorem-discharge-yukawa-operator-closure-v1"
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["standard_model_fully_derived"] is False
    assert parsed["bhsm_replacement_claim_ready"] is False
    assert parsed["yukawa_operator_layer_discharged_conditionally"] is True
    assert parsed["numerical_yukawa_values_derived"] is False
    assert parsed["mass_ratios_derived"] is False
    assert parsed["ckm_pmns_derived"] is False
    assert parsed["allowed_operator_classes"] == {
        "cyclic_upper_closure": {"fields": ["A_cyc", "H", "S_cyc_upper"], "hypercharge_sum": "0"},
        "cyclic_lower_closure": {"fields": ["A_cyc", "H_tilde", "S_cyc_lower"], "hypercharge_sum": "0"},
        "reference_charged_closure": {
            "fields": ["A_ref", "H_tilde", "S_ref_charged"],
            "hypercharge_sum": "0",
        },
        "reference_neutral_closure": {"fields": ["A_ref", "H", "S_ref_neutral"], "hypercharge_sum": "0"},
    }
    labels = set(parsed["verdict_labels"])
    for label in [
        "THEOREM_DISCHARGE_YUKAWA_OPERATOR_CLOSURE_COMPLETE",
        "PO_BH_18_YUKAWA_OPERATOR_CLOSURE_DERIVED_CONDITIONAL",
        "YUKAWA_ALLOWED_OPERATOR_CLASSES_DERIVED_CONDITIONAL",
        "YUKAWA_FORBIDDEN_OPERATOR_CLASSES_DERIVED_CONDITIONAL",
        "NUMERICAL_YUKAWA_VALUES_REMAIN_OPEN",
        "FERMION_MASS_RATIOS_REMAIN_OPEN",
        "CKM_PMNS_MIXING_REMAINS_OPEN",
        "BHSM_REPLACEMENT_CLAIM_NOT_READY",
    ]:
        assert label in labels


def test_yukawa_operator_required_files_exist():
    y.export_outputs(ROOT)
    for name in [
        "theorem_discharge_yukawa_operator_closure.md",
        "derived_boundary_yukawa_field_inventory.md",
        "derived_yukawa_hypercharge_closure.md",
        "derived_yukawa_orientation_contractions.md",
        "derived_yukawa_cyclic_reference_contractions.md",
        "derived_yukawa_allowed_operator_classes.md",
        "derived_yukawa_forbidden_operator_classes.md",
        "derived_boundary_neutral_singlet_mass_operator.md",
        "yukawa_operator_non_tautology_audit.md",
        "theorem_discharge_yukawa_operator_results.json",
    ]:
        assert (ROOT / "theory" / name).exists()
