import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_leading_axis_m_weight as la  # noqa: E402


def test_guardrails_keep_partial_claims_partial():
    payload = la.export_outputs(ROOT)
    assert payload["leading_axis_m_assignment_derived"] is False
    assert payload["y0_axis_sampling_derived"] is False
    assert payload["finite_width_rank_three_derived"] is False
    assert payload["numerical_yukawa_values_derived"] is False
    assert payload["ckm_values_derived"] is False
    assert payload["pmns_values_derived"] is False
    assert payload["standard_model_fully_derived"] is False
    assert payload["bhsm_replacement_claim_ready"] is False


def test_negative_results_are_reported():
    la.export_outputs(ROOT)
    payload = json.loads((ROOT / "theory" / "theorem_discharge_leading_axis_m_weight_results.json").read_text())
    joined = "\n".join(payload["negative_results"])
    assert "leading-axis m assignment not promoted" in joined
    assert "finite-width rank-three not derived" in joined
    assert "CKM values not derived" in joined
    assert "PMNS values not derived" in joined
