import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

import candidate_theorem_discharge_one_loop_rg as rg  # noqa: E402


def test_main_document_has_required_mission_and_conclusion():
    rg.export_outputs(ROOT)
    text = (ROOT / "theory" / "theorem_discharge_one_loop_rg_boundary_content.md").read_text(
        encoding="utf-8"
    )
    assert rg.MISSION_LANGUAGE in text
    assert rg.CONCLUSION_LANGUAGE in text
    forbidden = [
        "full Standard Model derivation is complete",
        "BHSM replaces the Standard Model",
        "replacement claim is ready",
        "measured coupling values are predicted",
        "two-loop RG is derived",
    ]
    for phrase in forbidden:
        assert phrase not in text


def test_payload_keeps_downstream_work_open():
    payload = rg.build_results_payload()
    assert payload["standard_model_fully_derived"] is False
    assert payload["bhsm_replacement_claim_ready"] is False
    assert payload["measured_couplings_predicted"] is False
    assert payload["two_loop_rg_derived"] is False
    assert "measured gauge coupling matching theorem" in payload["still_open_downstream"]
    assert "two-loop RG and threshold theorem" in payload["still_open_downstream"]
