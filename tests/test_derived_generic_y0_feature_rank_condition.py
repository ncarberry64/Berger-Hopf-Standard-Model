import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_generic_y0_wigner_feature_rank as gy0  # noqa: E402


def test_feature_rank_independence_remains_open():
    condition = gy0.feature_rank_condition()
    assert condition["feature_rank_independence_derived"] is False
    assert gy0.feature_rank_independence_derived() is False
    assert "three generation-mode feature multiplets" in condition["condition"]
