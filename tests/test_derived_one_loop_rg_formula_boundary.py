import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_one_loop_rg as rg  # noqa: E402


def test_one_loop_formula_documentation_guardrails():
    rg.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_one_loop_rg_formula_boundary.md").read_text(
        encoding="utf-8"
    )
    assert "dg_i/dlnmu = b_i g_i^3/(16 pi^2)" in text
    assert "- (11/3) C2(G_i)" in text
    assert "(2/3) sum_Weyl T_i(R_f)" in text
    assert "(1/3) sum_complex_scalar T_i(R_s)" in text
    assert "not a measured coupling prediction" in text


def test_rg_guardrail_booleans():
    assert rg.measured_couplings_predicted() is False
    assert rg.two_loop_rg_derived() is False
    assert rg.replacement_claim_ready() is False
