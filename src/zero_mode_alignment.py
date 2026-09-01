"""BHSM v1.3J zero-mode alignment audit.

This module compares formal sector-labeled protected zero-mode candidates with
the finite Level 2 coordinate-protected block. It does not change the operator
or force an alignment that is not present in the current scaffold.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from boundary_derivation import default_boundaries, omega_from_boundary
from coordinate_protected_block import CoordinateProtectedState, coordinate_protected_states
from ht_operator import default_level2_config
from mirror_exclusion_derivation import EXCLUDED, build_mirror_exclusion_report
from sector_coupling_bounds import level2_sector_coupling_dirac_block
from spectral_gap import heat_lift, natural_lambda2
from twisted_dirac import DiracOperatorConfig, build_dirac_basis, build_level2_dirac_matrix
from zero_mode_index import ZeroModeCandidate, protected_family_zero_modes


ALIGNED = "ALIGNED"
PARTIALLY_ALIGNED = "PARTIALLY_ALIGNED"
OPEN_ALIGNMENT_GAP = "OPEN_ALIGNMENT_GAP"
INCONSISTENT = "INCONSISTENT"
NOT_PRESENT = "NOT_PRESENT"


@dataclass(frozen=True)
class FormalZeroModeLabel:
    """Formal protected zero-mode label from the index scaffold."""

    id: str
    sector: str
    k: int
    j: int
    q: int
    chirality: int
    boundary_condition: str
    omega_rule: str
    omega_value: int
    omega_target: int
    boundary_policy_satisfied: bool
    boundary_policy_status: str
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class ZeroModeAlignmentMap:
    """Alignment row from a formal label to a finite coordinate state."""

    formal_label: FormalZeroModeLabel
    matching_coordinate_index: int | None
    matching_coordinate_sector: str | None
    matching_coordinate_chirality: int | None
    matching_coordinate_protected: bool
    coordinate_block_index: int | None
    heat_lift_preserves_matching_state: bool
    sector_coupling_vanishes_on_matching_state: bool
    sector_matches: bool
    chirality_matches: bool
    status: str
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class AlignmentCriterion:
    """One criterion for formal/coordinate zero-mode alignment."""

    id: str
    statement: str
    passes: bool
    evidence: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class AlignmentAuditReport:
    """Complete v1.3J zero-mode alignment report."""

    title: str
    formal_labels: tuple[FormalZeroModeLabel, ...]
    coordinate_protected_states: tuple[CoordinateProtectedState, ...]
    alignment_maps: tuple[ZeroModeAlignmentMap, ...]
    criteria: tuple[AlignmentCriterion, ...]
    all_three_formal_labels_present: bool
    all_three_coordinate_states_present: bool
    one_to_one_alignment: bool
    open_alignment_gap_remains: bool
    mirror_exclusion_intact: bool
    theorem_complete: bool
    limitations: tuple[str, ...]


def _omega_rule(sector: str) -> str:
    if sector == "lepton":
        return "Omega_l = -q + 2j = 3 for nonzero selected modes; heavy (0,0) is protected separately"
    if sector == "up":
        return "Omega_u = q - 2j = 6 for nonzero selected modes; heavy (0,0) is protected separately"
    if sector == "down":
        return "Omega_d = q + 4j = 12 for nonzero selected modes; heavy (0,0) is protected separately"
    raise ValueError(f"unknown sector: {sector}")


def formal_zero_mode_labels() -> tuple[FormalZeroModeLabel, ...]:
    """Return formal protected labels with boundary-policy diagnostics."""

    boundaries = default_boundaries()
    labels = []
    for candidate in protected_family_zero_modes():
        boundary = boundaries[candidate.sector]
        omega = omega_from_boundary(candidate.k, candidate.j, boundary)
        heavy_mode = candidate.k == 0 and candidate.j == 0
        labels.append(
            FormalZeroModeLabel(
                id=candidate.id,
                sector=candidate.sector,
                k=candidate.k,
                j=candidate.j,
                q=candidate.q,
                chirality=candidate.chirality,
                boundary_condition=candidate.boundary_condition,
                omega_rule=_omega_rule(candidate.sector),
                omega_value=int(omega),
                omega_target=int(boundary.target),
                boundary_policy_satisfied=heavy_mode or omega == boundary.target,
                boundary_policy_status="HEAVY_MODE_PROTECTED_SEPARATELY" if heavy_mode else "OMEGA_TARGET_CHECK",
                limitations=(
                    "The heavy (0,0) mode is included separately from nonzero boundary-operator selection.",
                    "Formal labels remain scaffold labels until the full index theorem is proven.",
                ),
            )
        )
    return tuple(labels)


def _basis_lookup(config: DiracOperatorConfig) -> dict[tuple[str, int, int, int, int], int]:
    basis = build_dirac_basis(config.k_max, sectors=config.sectors, include_chirality=config.include_chirality)
    return {(mode.sector, mode.k, mode.j, mode.q, mode.chirality): index for index, mode in enumerate(basis)}


def _basis_mode_by_index(config: DiracOperatorConfig, index: int):
    basis = build_dirac_basis(config.k_max, sectors=config.sectors, include_chirality=config.include_chirality)
    return basis[index]


def _index_diagnostics(config: DiracOperatorConfig, index: int) -> tuple[bool, bool]:
    dirac = build_level2_dirac_matrix(config)
    d2 = float((dirac.T @ dirac)[index, index])
    heat_ok = bool(abs(d2) <= 1e-12 and abs(heat_lift(d2, natural_lambda2())) <= 1e-12)
    sector_block = level2_sector_coupling_dirac_block(config)
    sector_zero = bool(np.allclose(sector_block[index, :], 0.0) and np.allclose(sector_block[:, index], 0.0))
    return heat_ok, sector_zero


def build_zero_mode_alignment_maps(config: DiracOperatorConfig | None = None) -> tuple[ZeroModeAlignmentMap, ...]:
    """Map formal labels to matching finite coordinates and protection status."""

    resolved = default_level2_config() if config is None else config
    lookup = _basis_lookup(resolved)
    zero_count = int(resolved.boundary_params.get("zero_mode_count", 3))
    rows = []
    for label in formal_zero_mode_labels():
        key = (label.sector, label.k, label.j, label.q, label.chirality)
        index = lookup.get(key)
        if index is None:
            rows.append(
                ZeroModeAlignmentMap(
                    formal_label=label,
                    matching_coordinate_index=None,
                    matching_coordinate_sector=None,
                    matching_coordinate_chirality=None,
                    matching_coordinate_protected=False,
                    coordinate_block_index=None,
                    heat_lift_preserves_matching_state=False,
                    sector_coupling_vanishes_on_matching_state=False,
                    sector_matches=False,
                    chirality_matches=False,
                    status=NOT_PRESENT,
                    limitations=("Formal label is not present in the finite Level 2 basis.",),
                )
            )
            continue
        mode = _basis_mode_by_index(resolved, index)
        protected = index < zero_count
        heat_ok, sector_zero = _index_diagnostics(resolved, index)
        sector_matches = mode.sector == label.sector
        chirality_matches = mode.chirality == label.chirality
        if protected and sector_matches and chirality_matches and heat_ok and sector_zero:
            status = ALIGNED
        elif sector_matches and chirality_matches:
            status = OPEN_ALIGNMENT_GAP
        else:
            status = INCONSISTENT
        rows.append(
            ZeroModeAlignmentMap(
                formal_label=label,
                matching_coordinate_index=index,
                matching_coordinate_sector=mode.sector,
                matching_coordinate_chirality=mode.chirality,
                matching_coordinate_protected=protected,
                coordinate_block_index=index if protected else None,
                heat_lift_preserves_matching_state=heat_ok,
                sector_coupling_vanishes_on_matching_state=sector_zero,
                sector_matches=sector_matches,
                chirality_matches=chirality_matches,
                status=status,
                limitations=(
                    "ALIGNED requires the matching coordinate to be inside the finite protected block.",
                    "OPEN_ALIGNMENT_GAP means the formal label exists in the basis but is not coordinate-protected.",
                ),
            )
        )
    return tuple(rows)


def build_alignment_audit_report(config: DiracOperatorConfig | None = None) -> AlignmentAuditReport:
    """Return the v1.3J zero-mode alignment audit report."""

    resolved = default_level2_config() if config is None else config
    formal = formal_zero_mode_labels()
    coordinate = coordinate_protected_states(resolved)
    maps = build_zero_mode_alignment_maps(resolved)
    one_to_one = len(maps) == 3 and all(item.status == ALIGNED for item in maps)
    mirror_report = build_mirror_exclusion_report()
    criteria = (
        AlignmentCriterion(
            id="A1",
            statement="Exactly three formal protected zero-mode labels are present.",
            passes=len(formal) == 3,
            evidence=(f"formal_label_count={len(formal)}",),
            limitations=("Formal labels are index-scaffold data.",),
        ),
        AlignmentCriterion(
            id="A2",
            statement="Exactly three finite coordinate-protected states are present.",
            passes=len(coordinate) == 3,
            evidence=(f"coordinate_protected_count={len(coordinate)}",),
            limitations=("Coordinate protection is by finite Level 2 construction.",),
        ),
        AlignmentCriterion(
            id="A3",
            statement="Each formal label has a matching sector/chirality coordinate in the finite basis.",
            passes=all(item.matching_coordinate_index is not None and item.sector_matches and item.chirality_matches for item in maps),
            evidence=tuple(f"{item.formal_label.id}->index {item.matching_coordinate_index}" for item in maps),
            limitations=("Presence in the basis is weaker than coordinate protection.",),
        ),
        AlignmentCriterion(
            id="A4",
            statement="Each matching coordinate is in the finite protected block and is preserved by heat lift and sector coupling.",
            passes=one_to_one,
            evidence=tuple(f"{item.formal_label.id}:{item.status}" for item in maps),
            limitations=("This criterion currently fails for up/down formal labels, so the alignment gap remains open.",),
        ),
    )
    return AlignmentAuditReport(
        title="BHSM v1.3J Zero-Mode Alignment Audit",
        formal_labels=formal,
        coordinate_protected_states=coordinate,
        alignment_maps=maps,
        criteria=criteria,
        all_three_formal_labels_present=len(formal) == 3,
        all_three_coordinate_states_present=len(coordinate) == 3,
        one_to_one_alignment=one_to_one,
        open_alignment_gap_remains=not one_to_one,
        mirror_exclusion_intact=bool(
            mirror_report.excluded_count == 3 and mirror_report.open_mirror_risk_count == 0
        ),
        theorem_complete=False,
        limitations=(
            "This audit does not alter the finite Level 2 coordinate ordering or protected block.",
            "The current scaffold has one exact formal/coordinate alignment and two open alignment gaps.",
            "The full H_T theorem remains open until the full operator/index/complement split is certified.",
        ),
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def export_zero_mode_alignment_json(path: str | Path) -> None:
    """Export the zero-mode alignment report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_alignment_audit_report()), indent=2, sort_keys=True) + "\n")


def export_zero_mode_alignment_markdown(path: str | Path) -> None:
    """Export the zero-mode alignment report as Markdown."""

    report = build_alignment_audit_report()
    lines = [
        "# BHSM v1.3J Zero-Mode Alignment Report",
        "",
        f"Theorem complete: `{report.theorem_complete}`",
        f"One-to-one alignment: `{report.one_to_one_alignment}`",
        f"Open alignment gap remains: `{report.open_alignment_gap_remains}`",
        f"Mirror exclusion intact: `{report.mirror_exclusion_intact}`",
        "",
        "## Alignment Table",
        "",
        "| Formal label | Sector | k | j | q | chi | match index | coordinate protected | heat preserved | sector coupling vanishes | status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in report.alignment_maps:
        label = item.formal_label
        lines.append(
            f"| `{label.id}` | `{label.sector}` | `{label.k}` | `{label.j}` | `{label.q}` | `{label.chirality}` | `{item.matching_coordinate_index}` | `{item.matching_coordinate_protected}` | `{item.heat_lift_preserves_matching_state}` | `{item.sector_coupling_vanishes_on_matching_state}` | `{item.status}` |"
        )
    lines.extend(
        [
            "",
            "## Coordinate-Protected Block",
            "",
            "| index | sector | k | j | q | chi | heat preserved | sector coupling vanishes |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in report.coordinate_protected_states:
        lines.append(
            f"| `{item.coordinate_index}` | `{item.sector}` | `{item.k}` | `{item.j}` | `{item.q}` | `{item.chirality}` | `{item.heat_lift_preserves}` | `{item.sector_coupling_vanishes}` |"
        )
    lines.extend(
        [
            "",
            "## Criteria",
            "",
            "| ID | Passes | Statement |",
            "| --- | --- | --- |",
        ]
    )
    for criterion in report.criteria:
        lines.append(f"| `{criterion.id}` | `{criterion.passes}` | {criterion.statement} |")
    lines.extend(["", "## Limitations", "", *[f"- {item}" for item in report.limitations], ""])
    Path(path).write_text("\n".join(lines))
