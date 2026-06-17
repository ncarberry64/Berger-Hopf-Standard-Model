import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_qj_eigenfunction_map as qj  # noqa: E402


def test_qj_eigenfunction_map_main_doc_contains_required_sections_and_guardrails():
    qj.export_outputs(ROOT)
    text = (ROOT / "theory" / "theorem_discharge_qj_eigenfunction_map.md").read_text()
    payload = qj.build_results_payload()

    for heading in [
        "Mission: Full BHSM Derivation Of Standard Model Structure",
        "PO-BH-23 Rank Condition",
        "Why `(q,j) -> psi_qj(y)` Is The Next Blocker",
        "BHSM Generation Mode Ledgers",
        "Candidate/Internal Eigenfunction Map",
        "Local Value/Gradient/Hessian Data At `y0`",
        "Finite-Width Feature Vectors",
        "Diagonal Hierarchy Route",
        "Full Rank-Three Matrix Route",
        "Internal Feature Independence Condition",
    ]:
        assert heading in text
    assert qj.MISSION_LANGUAGE in text
    assert qj.CONCLUSION_LANGUAGE in text
    assert payload["explicit_qj_eigenfunction_map_derived"] is False
    assert payload["internal_feature_independence_derived"] is False
    assert payload["finite_width_rank_three_derived"] is False
    assert payload["fermion_mass_ratios_derived"] is False
    assert payload["ckm_values_derived"] is False
    assert payload["pmns_values_derived"] is False
    assert payload["bhsm_replacement_claim_ready"] is False
