import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_raw_mode_berger_harmonic as rh  # noqa: E402


def test_raw_mode_harmonic_map_status_table_keeps_open_items_open():
    rh.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_raw_mode_harmonic_map_status.md").read_text()
    payload = json.loads((ROOT / "theory" / "theorem_discharge_raw_mode_berger_harmonic_results.json").read_text())

    assert "| raw mode map | `DERIVED_CONDITIONAL` |" in text
    assert "| m assignment | `OPEN` |" in text
    assert payload["m_weight_assignment_derived"] is False
    assert payload["explicit_eigenfunctions_derived"] is False
    assert payload["finite_width_rank_three_derived"] is False
