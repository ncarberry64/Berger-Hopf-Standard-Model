import pytest

from bhsm.interface.universal_prediction_freeze import (
    ExperimentalDatum,
    FrozenPrediction,
    compare_frozen_prediction,
    coverage_matrix,
)
from bhsm.interface.universal_spectral_forecast import CertifiedInterval


def prediction(*, promoted: bool = True) -> FrozenPrediction:
    return FrozenPrediction(
        prediction_id="prediction-1",
        mode_id="mode-1",
        observable_id="mass",
        classification="DERIVED_INTERVAL_PREDICTION",
        interval=CertifiedInterval(2.0, 3.0),
        categorical_value=None,
        action_version="BHSM-TEST",
        background_id="background",
        scale_map_id="GF-scale",
        frozen_git_commit="0123456789abcdef",
        provenance=("same-action spectrum",),
        gate7_closed=promoted,
        engine_promotion_passed=promoted,
    )


def test_downstream_comparison_cannot_mutate_or_retune_prediction() -> None:
    result = compare_frozen_prediction(
        prediction(),
        ExperimentalDatum(
            observable_id="mass",
            interval=CertifiedInterval(4.0, 5.0),
            categorical_value=None,
            source_id="comparison-only-dataset",
        ),
    )
    assert result["verdict"] == "DISJOINT_FALSIFICATION"
    assert result["prediction_mutated"] is False
    assert result["scale_retuned"] is False


def test_provisional_prediction_cannot_cross_comparison_firewall() -> None:
    datum = ExperimentalDatum(
        observable_id="mass",
        interval=CertifiedInterval(2.5, 2.6),
        categorical_value=None,
        source_id="comparison-only-dataset",
    )
    with pytest.raises(RuntimeError, match="provisional"):
        compare_frozen_prediction(prediction(promoted=False), datum)


def test_coverage_requires_every_pair_to_have_a_promoted_prediction() -> None:
    result = coverage_matrix(
        (("mode-1", "mass"), ("mode-1", "lifetime")),
        (prediction(),),
    )
    assert result["known_particle_coverage_complete"] is False
    assert result["physically_promoted_pair_count"] == 1
    assert result["rows"][1]["classification"] == "OPEN_INTERNAL_BLOCKER"
