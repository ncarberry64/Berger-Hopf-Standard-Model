"""BHSM v1.3I mirror-exclusion derivation audit.

The audit combines three internal channels: weak chiral projector,
Higgs-selected U(1) boundary phase, and the v1.2 sector boundary functional.
It does not use empirical masses or flavor residuals and does not complete the
full H_T theorem.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from boundary_derivation import default_boundaries, omega_from_boundary
from chiral_projector import (
    ChiralProjectionRule,
    EXCLUDED_BY_CHIRAL_PROJECTOR,
    evaluate_chiral_projection,
)
from higgs_u1_boundary_phase import HiggsU1PhaseRule, evaluate_higgs_u1_phase
from mirror_mode_exclusion import OPEN_MIRROR_RISK, generate_mirror_mode_candidates
from zero_mode_index import protected_family_zero_modes


EXCLUDED_BY_BOUNDARY_FUNCTIONAL = "EXCLUDED_BY_BOUNDARY_FUNCTIONAL"
BOUNDARY_COMPATIBLE = "BOUNDARY_COMPATIBLE"
OPEN = "OPEN"
EXCLUDED = "EXCLUDED"
LIFTED = "LIFTED"
INCONSISTENT_STATE = "INCONSISTENT_STATE"
NOT_PRESENT_IN_DOMAIN = "NOT_PRESENT_IN_DOMAIN"


@dataclass(frozen=True)
class MirrorBoundaryCondition:
    """Boundary-functional channel for one mirror candidate."""

    sector: str
    k: int
    j: int
    q: int
    omega_value: int
    target: int
    residual: int
    status: str
    derived_from_internal_structure: bool
    rationale: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class MirrorExclusionDerivation:
    """Per-candidate mirror-exclusion derivation record."""

    mirror_id: str
    protected_mode_id: str
    sector: str
    k: int
    j: int
    q: int
    mirror_chirality: int
    omega_value: int
    chiral_projector_result: ChiralProjectionRule
    higgs_u1_phase_result: HiggsU1PhaseRule
    boundary_functional_result: MirrorBoundaryCondition
    final_classification: str
    exclusion_channels: tuple[str, ...]
    theorem_complete: bool
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class MirrorExclusionReport:
    """Complete v1.3I mirror-exclusion derivation report."""

    title: str
    derivations: tuple[MirrorExclusionDerivation, ...]
    excluded_count: int
    lifted_count: int
    open_mirror_risk_count: int
    scaffold_index: int
    theorem_complete: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def evaluate_boundary_functional(sector: str, k: int, j: int, q: int) -> MirrorBoundaryCondition:
    """Evaluate the v1.2 boundary-functional channel for a mirror candidate."""

    boundary = default_boundaries()[sector]
    omega = omega_from_boundary(k, j, boundary)
    residual = omega - boundary.target
    return MirrorBoundaryCondition(
        sector=sector,
        k=int(k),
        j=int(j),
        q=int(q),
        omega_value=int(omega),
        target=int(boundary.target),
        residual=int(residual),
        status=OPEN,
        derived_from_internal_structure=False,
        rationale=(
            "The v1.2 boundary functional supplies Omega_f and the sector target.",
            "The heavy/protected zero-mode branch is treated separately from nonzero operational mode selection.",
            "Therefore a nonzero residual at (0,0) is not used by itself as a mirror-exclusion proof.",
        ),
        limitations=(
            "Boundary-functional mirror exclusion remains open until the full kernel boundary problem is solved.",
            "This channel is reported, not used to force exclusion.",
        ),
    )


def _final_classification(
    chiral: ChiralProjectionRule,
    higgs: HiggsU1PhaseRule,
    boundary: MirrorBoundaryCondition,
) -> tuple[str, tuple[str, ...]]:
    channels = []
    if chiral.status == EXCLUDED_BY_CHIRAL_PROJECTOR and chiral.derived_from_internal_structure:
        channels.append(chiral.status)
    if higgs.status == "EXCLUDED_BY_HIGGS_U1_PHASE" and higgs.derived_from_internal_structure:
        channels.append(higgs.status)
    if boundary.status == EXCLUDED_BY_BOUNDARY_FUNCTIONAL and boundary.derived_from_internal_structure:
        channels.append(boundary.status)
    if channels:
        return EXCLUDED, tuple(channels)
    return OPEN_MIRROR_RISK, tuple()


def derive_mirror_exclusion() -> tuple[MirrorExclusionDerivation, ...]:
    """Derive mirror-channel classifications for all protected candidates."""

    protected_by_id = {candidate.id: candidate for candidate in protected_family_zero_modes()}
    rows = []
    for mirror in generate_mirror_mode_candidates():
        protected = protected_by_id[mirror.protected_partner_id]
        chiral = evaluate_chiral_projection(mirror.sector, mirror.chirality)
        higgs = evaluate_higgs_u1_phase(mirror.sector, mirror.chirality)
        boundary = evaluate_boundary_functional(mirror.sector, mirror.k, mirror.j, mirror.q)
        final, channels = _final_classification(chiral, higgs, boundary)
        rows.append(
            MirrorExclusionDerivation(
                mirror_id=mirror.id,
                protected_mode_id=protected.id,
                sector=mirror.sector,
                k=mirror.k,
                j=mirror.j,
                q=mirror.q,
                mirror_chirality=mirror.chirality,
                omega_value=boundary.omega_value,
                chiral_projector_result=chiral,
                higgs_u1_phase_result=higgs,
                boundary_functional_result=boundary,
                final_classification=final,
                exclusion_channels=channels,
                theorem_complete=False,
                limitations=(
                    "Final mirror classification is channel-local and does not complete the H_T theorem.",
                    "Topological index and infinite-basis complement assumptions remain open.",
                ),
            )
        )
    return tuple(rows)


def build_mirror_exclusion_report() -> MirrorExclusionReport:
    """Return the v1.3I mirror-exclusion derivation report."""

    derivations = derive_mirror_exclusion()
    excluded = sum(item.final_classification == EXCLUDED for item in derivations)
    lifted = sum(item.final_classification == LIFTED for item in derivations)
    open_count = sum(item.final_classification == OPEN_MIRROR_RISK for item in derivations)
    return MirrorExclusionReport(
        title="BHSM v1.3I Mirror Exclusion Derivation Report",
        derivations=derivations,
        excluded_count=excluded,
        lifted_count=lifted,
        open_mirror_risk_count=open_count,
        scaffold_index=3,
        theorem_complete=False,
        assumptions=(
            "The protected kernel chirality is the BHSM scaffold chirality chi=-1.",
            "The weak chiral projector is model-internal structure from the v1.2 action scaffold.",
            "Higgs-U(1) and boundary-functional channels are reported conservatively when not chirality-resolved.",
        ),
        limitations=(
            "Mirror exclusion by the chiral channel does not prove the full topological index theorem.",
            "Formal/coordinate zero-mode alignment remains a separate open obligation.",
            "The infinite-basis complement bound remains open.",
        ),
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def export_mirror_exclusion_report_json(path: str | Path) -> None:
    """Export the v1.3I mirror-exclusion derivation report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_mirror_exclusion_report()), indent=2, sort_keys=True) + "\n")


def export_mirror_exclusion_report_markdown(path: str | Path) -> None:
    """Export the v1.3I mirror-exclusion derivation report as Markdown."""

    report = build_mirror_exclusion_report()
    lines = [
        "# BHSM v1.3I Mirror Exclusion Derivation Report",
        "",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Scaffold index: `{report.scaffold_index}`",
        f"Excluded count: `{report.excluded_count}`",
        f"Open mirror risk count: `{report.open_mirror_risk_count}`",
        "",
        "## Candidate Channel Table",
        "",
        "| Mirror | Sector | k | j | q | chi | Omega | Chiral | Higgs-U1 | Boundary | Final | Channels |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in report.derivations:
        lines.append(
            f"| `{item.mirror_id}` | `{item.sector}` | `{item.k}` | `{item.j}` | `{item.q}` | `{item.mirror_chirality}` | `{item.omega_value}` | `{item.chiral_projector_result.status}` | `{item.higgs_u1_phase_result.status}` | `{item.boundary_functional_result.status}` | `{item.final_classification}` | `{', '.join(item.exclusion_channels)}` |"
        )
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in report.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))
