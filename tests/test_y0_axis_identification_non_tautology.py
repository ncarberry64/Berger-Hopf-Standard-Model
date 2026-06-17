import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_y0_axis_identification as y0  # noqa: E402


def test_y0_non_tautology_keeps_peak_and_axis_separate():
    y0.export_outputs(ROOT)
    text = (ROOT / "theory" / "y0_axis_identification_non_tautology_audit.md").read_text()
    assert "profile peak" in text
    assert "identity/Hopf pole" in text
    assert "kept separate" in text


def test_no_downstream_claims_are_promoted():
    assert y0.finite_width_rank_three_derived() is False
    assert y0.numerical_yukawa_values_derived() is False
    assert y0.ckm_values_derived() is False
    assert y0.pmns_values_derived() is False
    assert y0.replacement_claim_ready() is False
