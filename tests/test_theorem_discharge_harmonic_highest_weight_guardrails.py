import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_harmonic_highest_weight as hw  # noqa: E402


def test_guardrails_keep_downstream_claims_open():
    payload = hw.export_outputs(ROOT)
    assert payload["m_weight_assignment_derived"] is False
    assert payload["explicit_eigenfunctions_derived"] is False
    assert payload["finite_width_rank_three_derived"] is False
    assert payload["numerical_yukawa_values_derived"] is False
    assert payload["standard_model_fully_derived"] is False
    assert payload["bhsm_replacement_claim_ready"] is False


def test_negative_results_are_reported():
    hw.export_outputs(ROOT)
    payload = json.loads((ROOT / "theory" / "theorem_discharge_harmonic_highest_weight_results.json").read_text())
    joined = "\n".join(payload["negative_results"])
    assert "m-weight assignment not derived" in joined
    assert "explicit eigenfunction values not derived" in joined
    assert "rank-three Yukawa theorem not derived" in joined
    assert "numerical Yukawa values not derived" in joined
