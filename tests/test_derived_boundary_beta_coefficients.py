import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_one_loop_rg as rg  # noqa: E402


def test_gauge_and_total_beta_coefficients_are_exact():
    assert rg.gauge_self_beta().as_tuple() == (
        Fraction(0),
        Fraction(-22, 3),
        Fraction(-11),
    )
    assert rg.total_one_loop_beta().as_tuple() == (
        Fraction(41, 10),
        Fraction(-19, 6),
        Fraction(-7),
    )
    assert rg.expected_beta_tuple() == rg.total_one_loop_beta().as_tuple()
    assert rg.beta_coefficients_match_expected() is True


def test_beta_discharge_ledger_and_documentation():
    rg.export_outputs(ROOT)
    ledger = rg.proof_discharge_ledger()
    assert ledger["PO-BH-15"].status == rg.DischargeStatus.DERIVED_CONDITIONAL
    text = (ROOT / "theory" / "derived_boundary_beta_coefficients.md").read_text(
        encoding="utf-8"
    )
    assert "b_gauge = (0, -22/3, -11)" in text
    assert "b_fermion = (4,4,4)" in text
    assert "b_scalar = (1/10,1/6,0)" in text
    assert "(41/10, -19/6, -7)" in text
    assert "PO_BH_15_ONE_LOOP_RG_COEFFICIENTS_FROM_BOUNDARY_CONTENT_DERIVED_CONDITIONAL" in text
