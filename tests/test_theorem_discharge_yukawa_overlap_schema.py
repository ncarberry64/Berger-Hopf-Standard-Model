import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_overlap as yo  # noqa: E402


def test_yukawa_overlap_results_schema_and_labels():
    payload = yo.export_outputs(ROOT)
    parsed = json.loads((ROOT / "theory" / "theorem_discharge_yukawa_overlap_results.json").read_text())
    assert parsed == payload
    assert parsed["status"] == "theorem_discharge_candidate"
    assert parsed["branch"] == "bhsm-theorem-discharge-yukawa-overlap-texture-source-v1"
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["standard_model_fully_derived"] is False
    assert parsed["bhsm_replacement_claim_ready"] is False
    assert parsed["yukawa_overlap_layer_discharged_conditionally"] is True
    assert parsed["numerical_yukawa_values_derived"] is False
    assert parsed["fermion_mass_ratios_derived"] is False
    assert parsed["ckm_values_derived"] is False
    assert parsed["pmns_values_derived"] is False
    assert set(parsed["yukawa_matrices"]) == set(yo.SECTORS)
    for sector, row in parsed["yukawa_matrices"].items():
        assert row["shape"] == "3x3"
        assert row["scalar_insertion"] == yo.SCALAR_INSERTION_BY_SECTOR[sector]
        assert len(row["entry_symbols"]) == 9
    labels = set(parsed["verdict_labels"])
    for label in [
        "THEOREM_DISCHARGE_YUKAWA_OVERLAP_TEXTURE_SOURCE_COMPLETE",
        "PO_BH_19_YUKAWA_OVERLAP_TEXTURE_SOURCE_DERIVED_CONDITIONAL",
        "YUKAWA_OVERLAP_FUNCTIONAL_DERIVED_CONDITIONAL",
        "YUKAWA_MATRIX_SCAFFOLD_DERIVED_CONDITIONAL",
        "NUMERICAL_YUKAWA_VALUES_REMAIN_OPEN",
        "CKM_VALUES_REMAIN_OPEN",
        "PMNS_VALUES_REMAIN_OPEN",
        "BHSM_REPLACEMENT_CLAIM_NOT_READY",
    ]:
        assert label in labels


def test_yukawa_overlap_required_files_exist():
    yo.export_outputs(ROOT)
    for name in [
        "theorem_discharge_yukawa_overlap_texture_source.md",
        "derived_yukawa_overlap_functional.md",
        "derived_yukawa_generation_mode_ledgers.md",
        "derived_yukawa_matrix_scaffold.md",
        "derived_yukawa_mass_matrix_relations.md",
        "derived_yukawa_mixing_scaffold.md",
        "derived_neutral_sector_mass_scaffold.md",
        "yukawa_overlap_non_tautology_audit.md",
        "theorem_discharge_yukawa_overlap_results.json",
    ]:
        assert (ROOT / "theory" / name).exists()
