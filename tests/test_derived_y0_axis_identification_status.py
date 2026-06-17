import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_y0_axis_identification as y0  # noqa: E402


def test_y0_claim_distinctions_are_explicit():
    rows = {row["claim"][0]: row for row in y0.y0_claim_table()}
    assert rows["A"]["supported"] is True
    assert rows["B"]["status"] == "STRUCTURALLY_MOTIVATED_NOT_DERIVED"
    assert rows["C"]["supported"] is False
    y0.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_y0_axis_identification_status.md").read_text()
    assert "Y0_AXIS_IDENTIFICATION_REMAINS_OPEN" in text
    assert "Required before promoting m=n=q/2" in text
