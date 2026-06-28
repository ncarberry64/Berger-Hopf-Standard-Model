from bhsm.interface.common_16 import search_common_16_sources


def test_common_16_source_search_is_complete_and_offline() -> None:
    result = search_common_16_sources()
    assert result.status == "COMMON_16_SOURCE_SET_LOCATED"
    assert not result.source_paths_missing
    assert result.omega_values == {"lepton": 3, "up": 6, "down": 12}
    assert result.historical_candidate_selected_by_residual is True
    assert result.empirical_residual_used_as_theorem_input is False
