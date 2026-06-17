import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_legacy_geometric_overlap as lg  # noqa: E402


def test_legacy_geometric_overlap_results_schema_and_status():
    payload = lg.export_outputs(ROOT)
    parsed = json.loads((ROOT / "theory" / "theorem_discharge_legacy_geometric_overlap_results.json").read_text())

    assert parsed == payload
    assert parsed["status"] == "theorem_discharge_candidate"
    assert parsed["branch"] == "bhsm-theorem-discharge-legacy-geometric-overlap-bridge-v1"
    assert parsed["official_predictions_changed"] is False
    assert parsed["frozen_predictions_changed"] is False
    assert parsed["standard_model_fully_derived"] is False
    assert parsed["bhsm_replacement_claim_ready"] is False
    assert parsed["legacy_geometric_overlap_bridge_discharged_conditionally"] is True
    assert parsed["source_ingestion_complete"] is False
    assert parsed["strict_point_sampling_rank_three_derived"] is False
    assert parsed["numerical_eigenfunction_amplitudes_computed"] is False
    assert parsed["numerical_yukawa_values_derived"] is False
    assert parsed["fermion_mass_ratios_derived"] is False
    assert parsed["ckm_values_derived"] is False
    assert parsed["pmns_values_derived"] is False
    assert "PO-BH-22" in parsed["discharged_obligations"]
    assert "PO_BH_22_LEGACY_GEOMETRIC_OVERLAP_KERNEL_BRIDGED_CONDITIONAL" in parsed["verdict_labels"]


def test_legacy_geometric_overlap_required_files_exist():
    lg.export_outputs(ROOT)
    for name in [
        "theorem_discharge_legacy_geometric_overlap_bridge.md",
        "derived_legacy_yukawa_overlap_integral.md",
        "derived_bhsm_geometric_overlap_kernel.md",
        "derived_universal_higgs_topographic_profile.md",
        "derived_sharp_peak_sampling_approximation.md",
        "derived_sharp_peak_rank_guardrail.md",
        "derived_internal_mode_amplitude_hierarchy_bridge.md",
        "derived_overlap_kernel_vs_distance_law_reconciliation.md",
        "derived_geometric_overlap_numerical_open_problem.md",
        "legacy_geometric_overlap_non_tautology_audit.md",
        "theorem_discharge_legacy_geometric_overlap_results.json",
    ]:
        assert (ROOT / "theory" / name).exists()
