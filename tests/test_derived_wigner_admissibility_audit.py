import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_m_weight_assignment as mw  # noqa: E402


def test_wigner_allowed_weight_and_convention_a_failures_are_reported():
    mw.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_wigner_admissibility_audit.md").read_text()
    failures = {(mode.sector, mode.index, mode.k, mode.j) for mode in mw.convention_A_failures()}

    assert mw.allowed_weight(Fraction(3, 2), Fraction(1, 2)) is True
    assert mw.allowed_weight(Fraction(3, 2), Fraction(1, 1)) is False
    assert ("reference_charged", 1, 5, 2) in failures
    assert ("reference_charged", 2, 9, 3) in failures
    assert ("reference_neutral", 1, 3, 0) in failures
    assert ("reference_neutral", 2, 3, 1) in failures
    assert "Convention A failures" in text
    assert "FAILED_GUARDRAIL" in text
