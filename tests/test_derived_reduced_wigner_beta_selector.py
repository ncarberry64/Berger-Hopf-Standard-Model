import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_generic_y0_wigner_feature_rank as gy0  # noqa: E402


def test_beta_selector_statement_exists():
    statement = gy0.beta_selector_statement()
    assert "beta0 controls" in statement
    assert "d^ell_{m,n}(beta0)" in statement
