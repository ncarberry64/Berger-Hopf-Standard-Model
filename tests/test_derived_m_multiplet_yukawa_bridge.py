import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_m_multiplet_harmonic_features as mm  # noqa: E402


def test_yukawa_bridge_does_not_promote_numerical_values_or_mixing():
    status = mm.yukawa_bridge_status()
    assert status["multiplet_features_available"] is True
    assert status["numerical_yukawa_values_derived"] is False
    assert status["ckm_values_derived"] is False
    assert status["pmns_values_derived"] is False
