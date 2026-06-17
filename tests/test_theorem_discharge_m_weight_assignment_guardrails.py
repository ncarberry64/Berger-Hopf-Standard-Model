import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_m_weight_assignment as mw  # noqa: E402


def test_m_weight_assignment_main_doc_has_required_sections_and_guardrails():
    mw.export_outputs(ROOT)
    text = (ROOT / "theory" / "theorem_discharge_m_weight_assignment.md").read_text()
    payload = mw.build_results_payload()

    for heading in [
        "Mission: Full BHSM Derivation Of Standard Model Structure",
        "PO-BH-25 Raw-Mode Harmonic Map",
        "Why `m` Is The Next Blocker",
        "Wigner/Hopf Harmonic Admissibility Conditions",
        "Audit Of `ell=k/2`, `n=j`",
        "Alternative Harmonic Conventions",
        "Candidate BHSM Sources For `m`",
        "Boundary Orientation Algebra Audit",
        "Candidate `m` Assignment Status",
        "Harmonic Convention Status",
    ]:
        assert heading in text
    assert mw.MISSION_LANGUAGE in text
    assert mw.CONCLUSION_LANGUAGE in text
    assert payload["m_weight_assignment_derived"] is False
    assert payload["selected_harmonic_convention_derived"] is False
    assert payload["explicit_eigenfunctions_derived"] is False
    assert payload["finite_width_rank_three_derived"] is False
    assert payload["numerical_yukawa_values_derived"] is False
    assert payload["bhsm_replacement_claim_ready"] is False
