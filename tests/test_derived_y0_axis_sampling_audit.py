import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_leading_axis_m_weight as la  # noqa: E402


def test_y0_axis_sampling_is_not_derived_from_repo():
    assert la.y0_axis_sampling_derived_from_repo() is False
    audit = {row["route"]: row for row in la.y0_axis_sampling_audit()}
    assert audit["group identity"]["repo_support"] is False
    assert audit["north/south Hopf pole"]["repo_support"] is False
    assert audit["squashed-axis focal point"]["repo_support"] is False
    assert audit["generic internal point"]["repo_support"] is True


def test_y0_axis_sampling_audit_file_reports_open_status():
    la.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_y0_axis_sampling_audit.md").read_text()
    assert "Y0_AXIS_SAMPLING_REMAINS_OPEN" in text
    assert "generic internal point" in text
