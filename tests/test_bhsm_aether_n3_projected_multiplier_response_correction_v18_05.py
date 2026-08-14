import json
from pathlib import Path


def test_projected_multiplier_response_correction_is_invalidated():
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_projected_multiplier_response_correction_v18_05.json"
    ).read_text(encoding="utf-8"))
    assert not payload["validation_passed"]
    assert payload["status"] == "INVALIDATED"
    result = payload["projected_multiplier_response_correction"]
    assert result["missing_rank_one_term_norm"] > 0.0
    for row in result["directional_validation"]:
        assert row["corrected_relative_residual"] > 2.0e-5
        assert row["corrected_relative_residual"] < row[
            "fixed_rho_relative_residual"
        ]
    assert not result["derivation"]["physical_action_changed"]
    assert not result["derivation"]["physical_event_changed"]
    assert not result["derivation"]["global_KKT_row_added"]
