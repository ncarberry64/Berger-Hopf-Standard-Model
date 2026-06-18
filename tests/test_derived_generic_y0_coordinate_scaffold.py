import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_generic_y0_wigner_feature_rank as gy0  # noqa: E402


def test_y0_coordinates_are_symbolic_not_derived():
    payload = gy0.build_results_payload()
    assert "alpha0,beta0,gamma0" in payload["still_open_downstream"][0]
    assert gy0.y0_coordinates_derived() is False
    assert payload["y0_coordinates_derived"] is False
