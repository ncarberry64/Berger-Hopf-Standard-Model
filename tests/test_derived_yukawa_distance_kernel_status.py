import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_yukawa_distance_overlap as d  # noqa: E402


def test_distance_kernel_status_values_are_partial_and_open():
    assert d.distance_overlap_law_discharged_conditionally() is False
    assert d.theorem_status().startswith("PARTIAL")
    payload = d.build_results_payload()
    assert payload["texture_summary_preserved"] == {
        "leading_diagonal_entries": 12,
        "conditional_off_diagonal_entries": 24,
        "forbidden_entries": 0,
        "total_entries": 36,
    }
    assert set(payload["distance_matrices_preserved"]) == set(d.SECTORS)


def test_distance_kernel_status_document_contains_open_statuses():
    d.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_yukawa_distance_kernel_status.md").read_text()
    assert "mode distances | `DERIVED_CONDITIONAL`" in text
    assert "distance-to-numerical-overlap law | `REMAINS_OPEN`" in text
    assert "numerical overlap values | `REMAIN_OPEN`" in text
