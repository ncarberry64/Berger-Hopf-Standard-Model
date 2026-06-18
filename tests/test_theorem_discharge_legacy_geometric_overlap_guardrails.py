import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_legacy_geometric_overlap as lg  # noqa: E402


def test_legacy_geometric_overlap_main_doc_contains_mission_conclusion_and_guardrails():
    lg.export_outputs(ROOT)
    text = (ROOT / "theory" / "theorem_discharge_legacy_geometric_overlap_bridge.md").read_text()
    payload = lg.build_results_payload()

    assert lg.MISSION_LANGUAGE in text
    assert lg.CONCLUSION_LANGUAGE in text
    assert "PO-BH-22" in payload["discharged_obligations"]
    assert payload["strict_point_sampling_rank_three_derived"] is False
    assert payload["numerical_eigenfunction_amplitudes_computed"] is False
    assert payload["numerical_yukawa_values_derived"] is False
    assert payload["fermion_mass_ratios_derived"] is False
    assert payload["ckm_values_derived"] is False
    assert payload["pmns_values_derived"] is False
    assert payload["bhsm_replacement_claim_ready"] is False
    assert payload["source_ingestion_complete"] is False
