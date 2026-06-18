import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_harmonic_highest_weight as hw  # noqa: E402


def test_non_tautology_audit_blocks_fit_and_numerical_overclaim():
    hw.export_outputs(ROOT)
    text = (ROOT / "theory" / "harmonic_highest_weight_non_tautology_audit.md").read_text()
    assert "masses or mixing values" in text
    assert "admissibility-only" not in text
    assert "`m`, explicit eigenfunction values, and numerical Yukawa values remain open" in text


def test_no_downstream_numerical_theorem_is_promoted():
    assert hw.finite_width_rank_three_derived() is False
    assert hw.numerical_yukawa_values_derived() is False
    assert hw.replacement_claim_ready() is False
