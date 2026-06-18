import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_y0_axis_identification as y0  # noqa: E402


def test_y0_axis_open_problem_names_exact_target():
    y0.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_y0_axis_open_problem.md").read_text()
    assert "group identity, Hopf pole, Berger axis, or canonical focal point" in text
    assert "Y0_AXIS_IDENTIFICATION_REMAINS_OPEN" in text
