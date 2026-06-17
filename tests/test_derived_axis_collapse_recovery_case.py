import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_generic_y0_wigner_feature_rank as gy0  # noqa: E402


def test_axis_collapse_recovery_case_documented():
    statement = gy0.axis_collapse_recovery_statement()
    assert "beta0=0" in statement
    assert "delta_mn" in statement
