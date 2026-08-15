from pathlib import Path

from bhsm.interface.aether_n3_accepted_secant_geometry_v18_60 import completion_payload
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json


def test_v18_60_accepted_secant_geometry() -> None:
    payload = completion_payload()
    result = payload["accepted_secant_geometry"]
    assert payload["validation_passed"]
    assert payload["status"] == "VALIDATED"
    assert len(result["accepted_secants"]) == 5
    assert len(result["consecutive_alignments"]) == 4
    assert not result["finite_secants_promoted_to_manifold_theorem"]
    assert not result["continuation_restriction_added"]
    assert Path("artifacts/BHSM_aether_n3_accepted_secant_geometry_v18_60.json").read_text(encoding="utf-8") == deterministic_json(payload)
