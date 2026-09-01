"""Fail-closed audit for an unchanged-AE2 localization carrier."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable


AUDIT_VERSION = "BHSM-AE2-LOCALIZATION-CARRIER-AUDIT-1.0.0"


@dataclass(frozen=True)
class LocalizationCandidate:
    """One declared object tested against the physical-carrier type."""

    candidate_id: str
    name: str
    action_owned: bool
    selects_local_domain: bool
    supplies_embedded_interface: bool
    regularity_or_domain_control: bool
    owns_interface_variation: bool
    evidence_status: str
    failure_reason: str

    @property
    def qualifies(self) -> bool:
        """Whether this object supplies every minimum carrier attribute."""

        return all(
            (
                self.action_owned,
                self.selects_local_domain,
                self.supplies_embedded_interface,
                self.regularity_or_domain_control,
                self.owns_interface_variation,
            )
        )


def evaluate_localization_candidates(
    candidates: Iterable[LocalizationCandidate],
) -> dict[str, object]:
    """Evaluate the carrier kill screen without promoting partial objects."""

    rows = []
    qualifying = []
    for candidate in candidates:
        row = asdict(candidate)
        row["qualifies_as_physical_localization_carrier"] = candidate.qualifies
        rows.append(row)
        if candidate.qualifies:
            qualifying.append(candidate.candidate_id)
    return {
        "audit_version": AUDIT_VERSION,
        "minimum_type": {
            "action_owned": True,
            "selects_local_domain": True,
            "supplies_embedded_interface": True,
            "regularity_or_domain_control": True,
            "owns_interface_variation": True,
        },
        "candidates": rows,
        "qualifying_candidate_ids": qualifying,
        "carrier_exists_in_audited_unchanged_ae2": bool(qualifying),
        "classification": (
            "UNCHANGED_AE2_LOCALIZATION_CARRIER_FOUND"
            if qualifying
            else "UNCHANGED_AE2_LOCALIZATION_CARRIER_NOT_FOUND"
        ),
    }


__all__ = [
    "AUDIT_VERSION",
    "LocalizationCandidate",
    "evaluate_localization_candidates",
]
