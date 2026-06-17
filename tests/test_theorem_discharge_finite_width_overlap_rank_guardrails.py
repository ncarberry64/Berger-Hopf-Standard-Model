import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_finite_width_overlap_rank as fw  # noqa: E402


def test_finite_width_overlap_rank_main_doc_contains_required_sections_and_guardrails():
    fw.export_outputs(ROOT)
    text = (ROOT / "theory" / "theorem_discharge_finite_width_overlap_rank.md").read_text()
    payload = fw.build_results_payload()

    for heading in [
        "Mission: Full BHSM Derivation Of Standard Model Structure",
        "PO-BH-22 Geometric Kernel Bridge",
        "Why Strict Point Sampling Is Rank-Limited",
        "Finite-Width Profile And Local Coordinate Expansion",
        "Moment Tensors Of The Universal Profile",
        "Finite-Width Overlap Expansion",
        "Rank-Three Condition",
        "Internal Eigenfunction Independence Condition",
        "Universal Profile Width Guardrail",
        "Status Of Rank-Three Derivation",
    ]:
        assert heading in text
    assert fw.MISSION_LANGUAGE in text
    assert fw.CONCLUSION_LANGUAGE in text
    assert payload["strict_point_sampling_rank_three_derived"] is False
    assert payload["finite_width_rank_three_derived"] is False
    assert payload["numerical_yukawa_values_derived"] is False
    assert payload["fermion_mass_ratios_derived"] is False
    assert payload["ckm_values_derived"] is False
    assert payload["pmns_values_derived"] is False
    assert payload["bhsm_replacement_claim_ready"] is False
