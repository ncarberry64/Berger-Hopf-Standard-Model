import os
from pathlib import Path

from bhsm.interface.aether_n3_constrained_root_hindsight_record_v18_59 import completion_payload
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json


def test_v18_59_constrained_root_hindsight_record() -> None:
    payload = completion_payload()
    result = payload["constrained_root_hindsight_record"]
    assert payload["validation_passed"]
    assert payload["status"] == "VALIDATED"
    assert result["constrained_root_target"]["additional_KKT_rows"] == 0
    assert result["local_child_chart"]["regular_local_nullity"] == 12
    assert not result["physical_admissibility_is_scalar_residual_ordering"]
    assert result["accepted_corridor"]["none_of_four_boundary_collapses_established"]
    if os.name == "nt":
        assert Path("artifacts/BHSM_aether_n3_constrained_root_hindsight_record_v18_59.json").read_text(encoding="utf-8") == deterministic_json(payload)
