import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_generic_y0_wigner_feature_rank as gy0  # noqa: E402


def test_phase_structure_statement_exists():
    statement = gy0.phase_structure_statement()
    assert "alpha0" in statement
    assert "gamma0" in statement
    assert "phase factors" in statement
