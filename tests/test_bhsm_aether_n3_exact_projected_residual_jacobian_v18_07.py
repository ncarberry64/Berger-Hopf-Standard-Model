import json
from pathlib import Path


def test_exact_projected_residual_jacobian_is_invalidated():
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_exact_projected_residual_jacobian_v18_07.json"
    ).read_text(encoding="utf-8"))
    assert not payload["validation_passed"]
    assert payload["status"] == "INVALIDATED"
    result = payload["exact_projected_residual_jacobian"]
    assert result["jacobian"]["projected_multiplier_chain_rule_included_by_construction"]
    assert result["jacobian"]["v17_61_exact_local_jet_covector_differentiated"]
    assert max(row["relative_residual"] for row in result["directional_validation"]) > 2.0e-5
    assert not result["physical_action_changed"]
    assert not result["physical_event_changed"]
    assert not result["global_KKT_row_added"]
