import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_higgs_scalar as hs  # noqa: E402


def test_higgs_scalar_results_schema_and_labels():
    payload = hs.export_outputs(ROOT)
    parsed = json.loads((ROOT / "theory" / "theorem_discharge_higgs_scalar_results.json").read_text())
    assert parsed == payload
    assert parsed["status"] == "theorem_discharge_candidate"
    assert parsed["branch"] == "bhsm-theorem-discharge-higgs-scalar-boundary-mechanism-v1"
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["standard_model_fully_derived"] is False
    assert parsed["bhsm_replacement_claim_ready"] is False
    assert parsed["higgs_scalar_layer_discharged_conditionally"] is True
    assert parsed["higgs_mass_predicted"] is False
    assert parsed["vev_predicted"] is False
    assert parsed["quartic_predicted"] is False
    assert parsed["yukawa_sector_derived"] is False
    assert parsed["scalar_representation"]["C"] == 0
    assert parsed["scalar_representation"]["Y"] == "1"
    labels = set(parsed["verdict_labels"])
    assert "PO_BH_16_HIGGS_SCALAR_ACTIVE_ORIENTATION_DOUBLET_DERIVED_CONDITIONAL" in labels
    assert "SCALAR_BETA_INPUT_NOW_DERIVED_CONDITIONAL" in labels
    assert "HIGGS_MASS_REMAINS_OPEN" in labels
    assert "YUKAWA_MASS_MIXING_REMAINS_OPEN" in labels


def test_higgs_scalar_required_files_exist():
    hs.export_outputs(ROOT)
    for name in [
        "theorem_discharge_higgs_scalar_boundary_mechanism.md",
        "derived_active_scalar_orientation_doublet.md",
        "derived_scalar_charge_table.md",
        "derived_scalar_conjugate_doublet.md",
        "derived_electroweak_breaking_generator.md",
        "derived_scalar_covariant_derivative.md",
        "derived_scalar_potential_skeleton.md",
        "higgs_scalar_non_tautology_audit.md",
        "theorem_discharge_higgs_scalar_results.json",
    ]:
        assert (ROOT / "theory" / name).exists()
