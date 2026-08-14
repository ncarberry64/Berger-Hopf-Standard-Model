from pathlib import Path

from bhsm.interface.aether_n3_congruent_proposal_child_reconstruction_v18_32 import completion_payload
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json


def test_v18_32_congruent_proposal_child_reconstruction() -> None:
    payload = completion_payload()
    result = payload["congruent_proposal_child_reconstruction"]
    assert payload["validation_passed"]
    assert payload["status"] == "VALIDATED"
    assert result["source_solver_model"] == "INVALIDATED_NOT_REASSERTED"
    assert result["chart"]["full_chart_rank"] == 14
    assert result["additional_global_KKT_rows"] == 0
    assert result["nonzero_motion_retained"]
    assert Path(
        "artifacts/BHSM_aether_n3_congruent_proposal_child_reconstruction_v18_32.json"
    ).read_text(encoding="utf-8") == deterministic_json(payload)
