import os
from pathlib import Path


def test_v18_55_fifth_direct_residual_scale_audit() -> None:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_fifth_direct_residual_scale_audit_v18_55.json"
    ).read_text(encoding="utf-8"))
    result = payload["fifth_direct_residual_scale_audit"]
    assert payload["validation_passed"]
    assert payload["status"] == "VALIDATED"
    assert result["source_state"].startswith("v18.54")
    assert result["selected_finest_common_stable_pair"] is not None
    assert result["physical_solve_dimension"] == [376, 376]
    assert not result["physical_residual_changed"]
    if os.name == "nt":
        assert Path("artifacts/BHSM_aether_n3_fifth_direct_residual_scale_audit_v18_55.json").read_text(encoding="utf-8") == deterministic_json(payload)
