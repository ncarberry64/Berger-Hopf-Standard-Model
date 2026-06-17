import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_generic_y0_wigner_feature_rank as gy0  # noqa: E402


def test_yukawa_bridge_keeps_numerical_outputs_open():
    status = gy0.yukawa_bridge_status()
    assert status["generic_y0_features_available"] is True
    assert status["finite_width_rank_three_derived"] is False
    assert status["numerical_yukawa_values_derived"] is False
    assert status["ckm_values_derived"] is False
    assert status["pmns_values_derived"] is False
