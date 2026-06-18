import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_leading_axis_m_weight as la  # noqa: E402


def test_non_tautology_audit_blocks_mass_and_mixing_input():
    la.export_outputs(ROOT)
    text = (ROOT / "theory" / "leading_axis_m_weight_non_tautology_audit.md").read_text()
    assert "masses, CKM, PMNS" in text
    assert "No leading-axis m assignment is promoted unless y0 axis sampling is derived" in text


def test_no_downstream_claims_are_promoted():
    assert la.finite_width_rank_three_derived() is False
    assert la.numerical_yukawa_values_derived() is False
    assert la.ckm_values_derived() is False
    assert la.pmns_values_derived() is False
    assert la.replacement_claim_ready() is False
