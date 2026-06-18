import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_raw_mode_berger_harmonic as rh  # noqa: E402


def test_raw_mode_map_k_equals_q_plus_2j():
    rh.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_raw_mode_map_k_equals_q_plus_2j.md").read_text()

    assert rh.k_from_qj(0, 0) == 0
    assert rh.k_from_qj(1, 2) == 5
    assert rh.k_from_qj(8, 1) == 10
    assert rh.raw_mode_map_formula() == "raw_mode(q,j)=(k,j)=(q+2j,j)"
    assert "RAW_MODE_MAP_DERIVED_CONDITIONAL" in text
