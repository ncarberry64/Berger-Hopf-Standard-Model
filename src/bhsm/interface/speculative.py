"""Disabled-by-default sandbox for non-production candidate templates."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

SPECULATIVE_STATUS = "SPECULATIVE_CANDIDATE_UNVALIDATED"


@dataclass(frozen=True)
class SpeculativeCandidate:
    candidate_key: str
    display_name: str
    proposed_sector: str
    geometry_template: dict[str, Any]
    proposed_quantity: str
    unit: str
    status: str
    enabled_by_default: bool
    requires_author_theorem: bool
    requires_empirical_comparison: bool
    source_note: str
    claim_boundary: str
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["notes"] = list(self.notes)
        return payload


@dataclass
class SpeculativeCandidateRegistry:
    candidates: dict[str, SpeculativeCandidate]

    def enabled(self) -> list[SpeculativeCandidate]:
        return [candidate for candidate in self.candidates.values() if candidate.enabled_by_default]

    def to_dict(self) -> dict[str, Any]:
        return {
            "registry_name": "BHSM Speculative Candidate Sandbox",
            "version": "0.2",
            "status": SPECULATIVE_STATUS,
            "candidates": [self.candidates[key].to_dict() for key in sorted(self.candidates)],
            "enabled_by_default_count": len(self.enabled()),
            "official_predictions_changed": False,
        }


@dataclass
class SpeculativeCandidateReport:
    included: list[dict[str, Any]]
    include_templates: bool
    claim_boundary: str = "Speculative candidates are disabled by default and are not production predictions."

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def default_speculative_registry() -> SpeculativeCandidateRegistry:
    candidate = SpeculativeCandidate(
        candidate_key="template_speculative_mode",
        display_name="Template speculative BHSM mode",
        proposed_sector="author_supplied",
        geometry_template={"curvature_indices": [], "hopf_coefficients": []},
        proposed_quantity="unspecified",
        unit="unspecified",
        status=SPECULATIVE_STATUS,
        enabled_by_default=False,
        requires_author_theorem=True,
        requires_empirical_comparison=True,
        source_note="Template only; no particle or numerical value is asserted.",
        claim_boundary="Template only. Not a production prediction and not an empirical claim.",
        notes=("not_frozen_prediction", "requires_theorem_closure"),
    )
    return SpeculativeCandidateRegistry({candidate.candidate_key: candidate})


def build_speculative_report(include_templates: bool = False) -> SpeculativeCandidateReport:
    registry = default_speculative_registry()
    included = [candidate.to_dict() for candidate in registry.candidates.values()] if include_templates else []
    return SpeculativeCandidateReport(included, include_templates)
