import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_legacy_geometric_overlap as lg  # noqa: E402


def test_overlap_kernel_reconciles_without_promoting_distance_law():
    lg.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_overlap_kernel_vs_distance_law_reconciliation.md").read_text()
    payload = json.loads((ROOT / "theory" / "theorem_discharge_legacy_geometric_overlap_results.json").read_text())

    assert "PO-BH-21 found no direct numerical distance-to-overlap law" in text
    assert "Direct `D_f(i,j) -> I_f(i,j)` laws remain unpromoted" in text
    assert any("PO-BH-21 distance-law result remains valid" in note for note in payload["notes"])
    assert "DISTANCE_OVERLAP_RECONCILIATION_DERIVED_CONDITIONAL" in text
