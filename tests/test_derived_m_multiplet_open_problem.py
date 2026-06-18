import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_m_multiplet_harmonic_features as mm  # noqa: E402


def test_open_downstream_obligations_are_explicit():
    payload = mm.build_results_payload()
    assert "derive numerical Yukawa values" in payload["still_open_downstream"]
    assert "derive CKM mixing values" in payload["still_open_downstream"]
    assert "derive PMNS mixing values" in payload["still_open_downstream"]
    assert "complete replacement-level Standard Model derivation" in payload["still_open_downstream"]
