import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_finite_width_overlap_rank as fw  # noqa: E402


def test_finite_width_overlap_rank_status_keeps_rank_three_open():
    fw.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_finite_width_overlap_rank_status.md").read_text()
    payload = json.loads((ROOT / "theory" / "theorem_discharge_finite_width_overlap_rank_results.json").read_text())

    assert "| strict point-sampling rank three | `False` |" in text
    assert "| finite-width rank three derived | `False` |" in text
    assert payload["rank_results"]["finite_width_moments"].startswith("can raise rank if")
    assert payload["rank_results"]["rank_three_status"] == "OPEN"
    assert "FINITE_WIDTH_RANK_THREE_REMAINS_OPEN" in payload["verdict_labels"]
