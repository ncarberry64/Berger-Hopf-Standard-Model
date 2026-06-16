import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_distance_overlap as d  # noqa: E402


def test_boundary_action_search_findings_report_no_derived_numerical_map():
    findings = d.boundary_action_search_findings()
    assert findings
    assert all(finding.maps_distance_to_overlap is False for finding in findings)
    assert any("topographic_attractor_boundary_action_bridge" in finding.file for finding in findings)
    assert any("Yukawa mode-distance" in finding.finding or "distance diagnostics" in finding.finding for finding in findings)


def test_boundary_action_overlap_audit_document_states_no_law_found():
    d.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_boundary_action_overlap_audit.md").read_text()
    assert "No existing theorem-derived boundary action/Hessian formula was found" in text
    assert "maps mode distance to overlap value" in text
