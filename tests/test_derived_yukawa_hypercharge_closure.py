from fractions import Fraction
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_operator as y  # noqa: E402


def test_allowed_yukawa_hypercharge_sums_close_exactly():
    assert y.hypercharge_sum("A_cyc", "H", "S_cyc_upper") == Fraction(0)
    assert y.hypercharge_sum("A_cyc", "H_tilde", "S_cyc_lower") == Fraction(0)
    assert y.hypercharge_sum("A_ref", "H_tilde", "S_ref_charged") == Fraction(0)
    assert y.hypercharge_sum("A_ref", "H", "S_ref_neutral") == Fraction(0)


def test_hypercharge_closure_document_records_all_exact_equations():
    y.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_hypercharge_closure.md").read_text()
    for equation in [
        "1/3 + 1 - 4/3 = 0",
        "1/3 - 1 + 2/3 = 0",
        "-1 - 1 + 2 = 0",
        "-1 + 1 + 0 = 0",
    ]:
        assert equation in text
    assert "YUKAWA_HYPERCHARGE_CLOSURE_DERIVED_CONDITIONAL" in text
