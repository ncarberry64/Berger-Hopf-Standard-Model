import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_raw_mode_berger_harmonic as rh  # noqa: E402


def test_raw_mode_berger_harmonic_main_doc_has_required_sections_and_guardrails():
    rh.export_outputs(ROOT)
    text = (ROOT / "theory" / "theorem_discharge_raw_mode_berger_harmonic_map.md").read_text()
    payload = rh.build_results_payload()

    for heading in [
        "Mission: Full BHSM Derivation Of Standard Model Structure",
        "The BHSM Relation `q=k-2j`",
        "Raw-Mode Map `k=q+2j`",
        "Generation Ledgers In `q,j` And Raw `k,j` Form",
        "Candidate Berger/Hopf Harmonic Interpretation",
        "Audit Of `j` As Hopf/Fiber Weight",
        "The Remaining `m` Orientation/Base-Weight Problem",
        "Candidate Sources For `m`",
        "Bridge To Local Feature Vectors At `y0`",
    ]:
        assert heading in text
    assert rh.MISSION_LANGUAGE in text
    assert rh.CONCLUSION_LANGUAGE in text
    assert payload["m_weight_assignment_derived"] is False
    assert payload["explicit_eigenfunctions_derived"] is False
    assert payload["finite_width_rank_three_derived"] is False
    assert payload["numerical_yukawa_values_derived"] is False
    assert payload["bhsm_replacement_claim_ready"] is False
