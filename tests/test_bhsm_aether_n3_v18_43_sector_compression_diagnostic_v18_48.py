from pathlib import Path

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_v18_43_sector_compression_diagnostic_v18_48 import completion_payload


def test_v18_48_v18_43_sector_compression_diagnostic() -> None:
    payload = completion_payload()
    result = payload["v18_43_sector_compression_diagnostic"]
    assert payload["validation_passed"]
    assert payload["status"] == "VALIDATED"
    assert len(result["sector_measurements"]) == 9
    assert result["accepted_nonlinear_line_state"] == "v18.47"
    assert result["coordinate_map"]["invertible"]
    assert not result["physical_equations_changed"]
    assert not result["residual_rows_left_scaled"]
    assert Path(
        "artifacts/BHSM_aether_n3_v18_43_sector_compression_diagnostic_v18_48.json"
    ).read_text(encoding="utf-8") == deterministic_json(payload)
