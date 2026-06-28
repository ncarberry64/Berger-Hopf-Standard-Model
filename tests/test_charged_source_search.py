from __future__ import annotations

from pathlib import Path

from bhsm.interface.charged_closure import search_charged_closure_sources


ROOT = Path(__file__).resolve().parents[1]


def test_charged_source_search_is_complete_and_offline() -> None:
    result = search_charged_closure_sources(ROOT)
    assert result.status == "CHARGED_SOURCE_INVENTORY_COMPLETE"
    assert not result.sources_missing
    assert all((ROOT / path).is_file() for path in result.sources_found)
    assert result.empirical_inputs_used is False
    assert result.frozen_predictions_changed is False
    assert result.official_prediction_logic_changed is False
    assert "complete charged action normalization" in result.open_sources
