import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_trace_normalization as trace  # noqa: E402


def test_trace_weight_results_and_discharge_ledger():
    results = trace.all_trace_weight_results()
    names = {row.name for row in results}
    assert {
        "K1_hypercharge_raw",
        "K2_orientation",
        "K3_cyclic",
        "eta_Y",
        "K1_hypercharge_normalized",
    } <= names
    assert trace.proof_discharge_ledger()["PO-BH-14"].status == trace.DischargeStatus.DERIVED_CONDITIONAL


def test_normalized_gauge_action_documentation_guardrails():
    trace.export_outputs(ROOT)
    text = (ROOT / "theory" / "derived_normalized_gauge_action_skeleton.md").read_text(
        encoding="utf-8"
    )
    assert "eta_Y = 3/5" in text
    assert "eta_Y F_Y wedge *F_Y" in text
    assert "NORMALIZED_GAUGE_ACTION_SKELETON_DERIVED_CONDITIONAL" in text
    assert "does not derive RG running or measured values" in text
