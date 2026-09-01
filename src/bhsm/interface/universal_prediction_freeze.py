"""Prediction freeze and downstream comparison firewall.

An action-derived prediction is immutable before any experimental datum is
attached.  Comparison records can classify overlap or disagreement, but they
cannot alter the prediction, select a branch, or retune the universal scale.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from bhsm.interface.universal_spectral_forecast import CertifiedInterval


DERIVED_CLASSIFICATIONS = {
    "DERIVED_POINT_PREDICTION",
    "DERIVED_INTERVAL_PREDICTION",
    "DERIVED_SELECTION_RULE",
    "DERIVED_QUALITATIVE_STRUCTURE",
}


@dataclass(frozen=True)
class FrozenPrediction:
    prediction_id: str
    mode_id: str
    observable_id: str
    classification: str
    interval: CertifiedInterval | None
    categorical_value: str | None
    action_version: str
    background_id: str
    scale_map_id: str | None
    frozen_git_commit: str
    provenance: tuple[str, ...]
    gate7_closed: bool
    engine_promotion_passed: bool

    def __post_init__(self) -> None:
        if self.classification not in DERIVED_CLASSIFICATIONS:
            raise ValueError("prediction must use a derived classification")
        if (self.interval is None) == (self.categorical_value is None):
            raise ValueError("prediction needs exactly one interval or categorical value")
        if not self.frozen_git_commit or not self.provenance:
            raise ValueError("prediction freeze commit and provenance are required")

    @property
    def physically_promoted(self) -> bool:
        return bool(self.gate7_closed and self.engine_promotion_passed)


@dataclass(frozen=True)
class ExperimentalDatum:
    observable_id: str
    interval: CertifiedInterval | None
    categorical_value: str | None
    source_id: str

    def __post_init__(self) -> None:
        if (self.interval is None) == (self.categorical_value is None):
            raise ValueError("datum needs exactly one interval or categorical value")
        if not self.source_id:
            raise ValueError("comparison datum source is required")


def compare_frozen_prediction(
    prediction: FrozenPrediction,
    datum: ExperimentalDatum,
) -> dict:
    if prediction.observable_id != datum.observable_id:
        raise ValueError("prediction and comparison observable ids differ")
    if not prediction.physically_promoted:
        raise RuntimeError("provisional prediction cannot enter experimental comparison")
    if prediction.interval is not None and datum.interval is not None:
        overlap_lower = max(prediction.interval.lower, datum.interval.lower)
        overlap_upper = min(prediction.interval.upper, datum.interval.upper)
        verdict = "INTERVALS_OVERLAP" if overlap_lower <= overlap_upper else "DISJOINT_FALSIFICATION"
    elif prediction.categorical_value is not None and datum.categorical_value is not None:
        verdict = (
            "CATEGORICAL_MATCH"
            if prediction.categorical_value == datum.categorical_value
            else "CATEGORICAL_FALSIFICATION"
        )
    else:
        raise ValueError("prediction and datum value types differ")
    return {
        "prediction_id": prediction.prediction_id,
        "observable_id": prediction.observable_id,
        "frozen_git_commit": prediction.frozen_git_commit,
        "datum_source_id": datum.source_id,
        "verdict": verdict,
        "prediction_mutated": False,
        "scale_retuned": False,
        "branch_selected_from_datum": False,
    }


def coverage_matrix(
    required_observables: Iterable[tuple[str, str]],
    predictions: Iterable[FrozenPrediction],
) -> dict:
    """Return one explicit coverage row per ``(mode, observable)`` pair."""

    required = tuple(required_observables)
    if len(required) != len(set(required)):
        raise ValueError("required coverage pairs must be unique")
    entries = tuple(predictions)
    keys = [(entry.mode_id, entry.observable_id) for entry in entries]
    if len(keys) != len(set(keys)):
        raise ValueError("only one frozen prediction is allowed per coverage pair")
    lookup = dict(zip(keys, entries))
    rows = []
    for mode_id, observable_id in required:
        prediction = lookup.get((mode_id, observable_id))
        rows.append({
            "mode_id": mode_id,
            "observable_id": observable_id,
            "prediction_id": None if prediction is None else prediction.prediction_id,
            "classification": (
                "OPEN_INTERNAL_BLOCKER" if prediction is None else prediction.classification
            ),
            "physically_promoted": False if prediction is None else prediction.physically_promoted,
        })
    complete = bool(rows) and all(row["physically_promoted"] for row in rows)
    return {
        "rows": rows,
        "required_pair_count": len(rows),
        "physically_promoted_pair_count": sum(row["physically_promoted"] for row in rows),
        "known_particle_coverage_complete": complete,
        "experimental_data_used_to_build_predictions": False,
    }


__all__ = [
    "DERIVED_CLASSIFICATIONS",
    "ExperimentalDatum",
    "FrozenPrediction",
    "compare_frozen_prediction",
    "coverage_matrix",
]
