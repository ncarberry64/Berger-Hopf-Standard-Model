import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_generic_y0_wigner_feature_rank as gy0  # noqa: E402


def test_open_downstream_obligations_are_explicit():
    payload = gy0.build_results_payload()
    assert "derive or constrain y0 coordinates alpha0,beta0,gamma0" in payload["still_open_downstream"]
    assert "rank-three Yukawa matrix theorem" in payload["still_open_downstream"]
    assert "CKM mixing theorem" in payload["still_open_downstream"]
    assert "PMNS mixing theorem" in payload["still_open_downstream"]
    assert "full replacement-level SM derivation" in payload["still_open_downstream"]
