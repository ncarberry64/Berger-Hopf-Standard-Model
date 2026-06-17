import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_m_multiplet_harmonic_features as mm  # noqa: E402


def test_generic_y0_scaffold_is_documented_in_results():
    payload = mm.build_results_payload()
    assert payload["generic_y0_case_documented"] is True
    assert payload["axis_collapse_case_documented"] is True
