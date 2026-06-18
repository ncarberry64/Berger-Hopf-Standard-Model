from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_response_layer_decomposition import build_response_payload, export_response_outputs  # noqa: E402


def test_response_factors_are_not_interchangeable_and_ckm_is_not_mass_response() -> None:
    payload = build_response_payload()
    assert "response factors are not interchangeable" in payload["notes"]
    assert "CKM interface response is not a mass response" in payload["notes"]

    export_response_outputs(ROOT)
    text = (ROOT / "theory" / "response_selector_diagnostic_summary.md").read_text(
        encoding="utf-8"
    )
    assert "Response factors are not interchangeable" in text
    assert "CKM interface response is not a mass response" in text


def test_response_selector_status_is_not_upgraded_to_derived() -> None:
    export_response_outputs(ROOT)
    text = (ROOT / "theory" / "response_layer_residual_decomposition.md").read_text(
        encoding="utf-8"
    )
    assert "`RESPONSE_SELECTOR_STRUCTURAL_CANDIDATE` is not upgraded to derived" in text
    assert "No new official response factor is introduced" in text


def test_quark_scheme_sensitivity_is_preserved() -> None:
    payload = build_response_payload()
    for scenario in payload["scenario_results"]:
        quark_rows = [row for row in scenario["rows"] if row["sector"] in {"up", "down"}]
        assert quark_rows
        assert all(row["scheme_sensitive"] is True for row in quark_rows)
