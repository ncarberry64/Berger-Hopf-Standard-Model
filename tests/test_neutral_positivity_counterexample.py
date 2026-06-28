from __future__ import annotations

from bhsm.interface.neutrino_spectral import search_admissible_positivity_counterexample


def test_raw_counterexample_is_not_silently_promoted_to_admissible_cone() -> None:
    result = search_admissible_positivity_counterexample()
    assert result.counterexample_found is False
    assert result.counterexample is None
    assert result.negative_eigendirection is not None
    assert min(result.negative_eigendirection) < 0 < max(result.negative_eigendirection)
    assert result.positivity_proven_without_thresholding is True
    assert "rational-grid" in result.search_method

