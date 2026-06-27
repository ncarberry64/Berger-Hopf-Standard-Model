"""Claim-safe gallery assembled from registry and deterministic report data."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .predictions import PredictionStatus, default_prediction_registry
from .report import build_prediction_report
from .speculative import default_speculative_registry


@dataclass
class PredictionGalleryEntry:
    entry_key: str
    display_name: str
    category: str
    status: str
    quantity: str
    unit: str
    value: Any
    value_kind: str
    comparison_kind: str | None
    comparison_value: Any
    delta: Any
    delta_kind: str | None
    source_type: str
    source_artifacts: list[str]
    calibration_anchor: str | None
    independent_prediction: bool
    theorem_status: str
    runtime_status: str
    speculative_status: str
    claim_boundary: str
    show_in_default_gallery: bool
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PredictionGallery:
    entries: list[PredictionGalleryEntry]
    include_speculative: bool
    gallery_name: str = "BHSM Prediction Gallery"
    version: str = "0.2"

    def to_dict(self) -> dict[str, Any]:
        return {
            "gallery_name": self.gallery_name,
            "version": self.version,
            "include_speculative": self.include_speculative,
            "entries": [entry.to_dict() for entry in self.entries],
            "warnings": [
                "Gallery entries are status summaries, not empirical validation claims.",
                "Speculative candidates are disabled by default and are not production predictions.",
            ],
        }

    def status_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for entry in self.entries:
            counts[entry.status] = counts.get(entry.status, 0) + 1
        return dict(sorted(counts.items()))

    def category_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for entry in self.entries:
            counts[entry.category] = counts.get(entry.category, 0) + 1
        return dict(sorted(counts.items()))


def _category(status: PredictionStatus, key: str) -> str:
    if key == "W_boson": return "calibration_anchor"
    if key == "electron_neutrino": return "upper_limit_comparison"
    return {
        PredictionStatus.FROZEN_INTERNAL_PREDICTION: "frozen_internal_prediction",
        PredictionStatus.OPEN_THEOREM_REQUIRED: "open_theorem_blocker",
        PredictionStatus.DISABLED_UNTIL_RUNTIME_VALIDATED: "runtime_disabled_gate",
        PredictionStatus.REFERENCE_COMPARISON_ONLY: "reference_only",
    }.get(status, "model_prediction_given_calibration")


def build_prediction_gallery(include_speculative: bool = False) -> PredictionGallery:
    registry = default_prediction_registry()
    report = build_prediction_report(include_open_theorem_entries=True).to_dict()
    predictions = {row["particle_key"]: row for row in report["predictions"]}
    comparisons = {row["particle_key"]: row for row in report["comparisons"]}
    entries: list[PredictionGalleryEntry] = []
    excluded_default = {"minimal_collider_interface_subset"}
    for item in registry.list_entries():
        if item.particle_key in excluded_default:
            continue
        prediction = predictions.get(item.particle_key, {})
        comparison = comparisons.get(item.particle_key, {})
        status = PredictionStatus(prediction.get("prediction_status", item.default_status.value))
        boundary = item.claim_boundary
        if item.default_status is PredictionStatus.OPEN_THEOREM_REQUIRED:
            boundary += " This is a theorem blocker, not a production prediction."
        if item.default_status is PredictionStatus.DISABLED_UNTIL_RUNTIME_VALIDATED:
            boundary += " This software gate requires live external validation before readiness can be claimed."
        entries.append(PredictionGalleryEntry(
            item.particle_key, item.display_name, _category(item.default_status, item.particle_key),
            status.value, item.quantity, item.unit, prediction.get("mass_gev"),
            "computed_demo" if prediction else "status_only", item.comparison_kind,
            comparison.get("reference", {}).get("value_gev") or comparison.get("reference", {}).get("upper_gev"),
            comparison.get("absolute_delta_gev") or comparison.get("upper_limit_margin_gev"),
            "absolute_delta_or_limit_margin" if comparison else None, item.source_type,
            list(item.source_artifacts), report["anchor_particle"],
            bool(prediction and not prediction.get("is_anchor_particle")), item.theorem_status,
            "requires_live_validation" if item.runtime_required else "not_applicable",
            "not_speculative", boundary, True, list(item.notes)))
    if include_speculative:
        for candidate in default_speculative_registry().candidates.values():
            entries.append(PredictionGalleryEntry(
                candidate.candidate_key, candidate.display_name, "speculative_candidate", candidate.status,
                candidate.proposed_quantity, candidate.unit, None, "template_only", None, None, None, None,
                "speculative sandbox", [], None, False, "requires_author_theorem", "not_applicable",
                candidate.status, candidate.claim_boundary, False, list(candidate.notes)))
    return PredictionGallery(entries, include_speculative)


def gallery_to_markdown(gallery: PredictionGallery) -> str:
    lines = ["# BHSM Prediction Gallery", "", "Gallery entries are status summaries, not empirical validation claims.", "", "| Key | Category | Status | Claim boundary |", "| --- | --- | --- | --- |"]
    lines.extend(f"| `{e.entry_key}` | {e.category} | `{e.status}` | {e.claim_boundary} |" for e in gallery.entries)
    return "\n".join(lines) + "\n"
