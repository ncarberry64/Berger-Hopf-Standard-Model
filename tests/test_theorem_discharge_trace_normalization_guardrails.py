import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_trace_normalization as trace  # noqa: E402


def test_trace_normalization_guardrail_booleans():
    assert trace.rg_running_derived() is False
    assert trace.measured_couplings_predicted() is False
    assert trace.replacement_claim_ready() is False


def test_main_doc_contains_mission_and_conclusion_without_overclaiming():
    trace.export_outputs(ROOT)
    text = (ROOT / "theory" / "theorem_discharge_boundary_trace_normalization.md").read_text(
        encoding="utf-8"
    )
    assert trace.MISSION_LANGUAGE in text
    assert trace.CONCLUSION_LANGUAGE in text
    forbidden = [
        "full Standard Model derivation is complete",
        "BHSM replaces the Standard Model",
        "replacement claim is ready",
        "RG running is derived",
        "measured couplings are predicted",
    ]
    for phrase in forbidden:
        assert phrase not in text


def test_payload_keeps_downstream_work_open():
    payload = trace.build_results_payload()
    assert payload["standard_model_fully_derived"] is False
    assert payload["bhsm_replacement_claim_ready"] is False
    assert payload["rg_running_derived"] is False
    assert payload["measured_couplings_predicted"] is False
    assert "RG running theorem" in payload["still_open_downstream"]
    assert "measured gauge coupling theorem" in payload["still_open_downstream"]
