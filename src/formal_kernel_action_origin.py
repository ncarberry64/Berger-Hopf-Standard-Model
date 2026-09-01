"""BHSM v1.3N action/boundary/basis origin for the formal kernel projector."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from boundary_functional_derivation import build_parent_action_derivation_report
from formal_kernel_operator import (
    DIRAC_PROXY_LEVEL_2_COORDINATE_FIRST,
    DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL,
    default_formal_kernel_operator_config,
    formal_kernel_coordinates,
    formal_kernel_projectors,
)
from sector_labeled_kernel import sector_labeled_zero_modes
from twisted_dirac import build_dirac_basis
from zero_mode_index import protected_family_zero_modes


FORMAL_KERNEL_ACTION_DERIVED = "FORMAL_KERNEL_ACTION_DERIVED"
FORMAL_KERNEL_BOUNDARY_DERIVED = "FORMAL_KERNEL_BOUNDARY_DERIVED"
FORMAL_KERNEL_BASIS_DERIVED = "FORMAL_KERNEL_BASIS_DERIVED"
FORMAL_KERNEL_IMPLEMENTATION_SCAFFOLD = "FORMAL_KERNEL_IMPLEMENTATION_SCAFFOLD"
OPEN = "OPEN"


@dataclass(frozen=True)
class FormalKernelActionRule:
    """One rule contributing to the formal-kernel projector origin."""

    id: str
    statement: str
    source: str
    status: str
    evidence: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class FormalKernelProjectorDerivation:
    """Derivation/construction record for the formal protected projector."""

    protected_coordinates: tuple[int, ...]
    old_coordinate_first_coordinates: tuple[int, ...]
    protected_sectors: tuple[str, ...]
    basis_ordering_formula: str
    modes_per_chirality_sector: int
    projector_rank: int
    projector_idempotent: bool
    projector_orthogonal_to_complement: bool
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class FormalKernelTheoremScaffold:
    """Sufficient scaffold statement for upgrading projector origin."""

    assumptions: tuple[FormalKernelActionRule, ...]
    conclusion: str
    status: str
    theorem_complete: bool
    remaining_obligations: tuple[str, ...]


@dataclass(frozen=True)
class FormalKernelActionOriginReport:
    """Complete v1.3N formal-kernel action-origin report."""

    title: str
    rules: tuple[FormalKernelActionRule, ...]
    projector_derivation: FormalKernelProjectorDerivation
    theorem_scaffold: FormalKernelTheoremScaffold
    parent_action_status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def modes_per_chirality_sector(k_max: int) -> int:
    """Return number of (k,j) modes per chirality in one sector."""

    if k_max < 0:
        raise ValueError("k_max must be nonnegative")
    return sum((k // 2) + 1 for k in range(k_max + 1))


def basis_coordinate_for_sector_zero(sector: str, k_max: int, sectors: tuple[str, ...] = ("lepton", "up", "down")) -> int:
    """Return sector-major coordinate of the protected (0,0,chi=-1) label."""

    if sector not in sectors:
        raise ValueError(f"unknown sector: {sector}")
    modes = modes_per_chirality_sector(k_max)
    return int(sectors.index(sector) * 2 * modes)


def formal_kernel_action_rules() -> tuple[FormalKernelActionRule, ...]:
    """Return action/boundary/basis rules constraining the formal kernel."""

    parent = build_parent_action_derivation_report()
    protected = protected_family_zero_modes()
    return (
        FormalKernelActionRule(
            id="R1_sector_labeled_kernel",
            statement="The protected kernel consists of one heavy (0,0) label in each charged sector.",
            source="zero_mode_index.protected_family_zero_modes",
            status=FORMAL_KERNEL_BOUNDARY_DERIVED,
            evidence=(f"protected sectors = {tuple(mode.sector for mode in protected)}",),
            limitations=("The full topological index theorem is not proven here.",),
        ),
        FormalKernelActionRule(
            id="R2_chiral_projector",
            statement="The protected labels carry the BHSM protected chirality chi=-1.",
            source="weak/chiral projector scaffold",
            status=FORMAL_KERNEL_BOUNDARY_DERIVED,
            evidence=(f"chiralities = {tuple(mode.chirality for mode in protected)}",),
            limitations=("Full chiral kernel proof remains open.",),
        ),
        FormalKernelActionRule(
            id="R3_boundary_functional",
            statement="The v1.2 sector boundary functional supplies the lepton/up/down sector distinction.",
            source="v1.2 boundary functional and parent-action reduction",
            status=FORMAL_KERNEL_BOUNDARY_DERIVED,
            evidence=(f"parent_action_status = {parent.status.value}",),
            limitations=("The complete internal action has not uniquely generated the full operator.",),
        ),
        FormalKernelActionRule(
            id="R4_basis_ordering",
            statement="The finite Level 2 basis is sector-major, then chirality-major, then (k,j)-ordered.",
            source="twisted_dirac.build_dirac_basis",
            status=FORMAL_KERNEL_BASIS_DERIVED,
            evidence=("coordinate(sector,0,0,-1)=sector_index*2*M(k_max)",),
            limitations=("Coordinates are implementation details; the sector-labeled subspace is the invariant object.",),
        ),
        FormalKernelActionRule(
            id="R5_higgs_u1_phase",
            statement="The Higgs-selected U(1) boundary phase participates in selecting the protected chiral boundary channel.",
            source="parent internal-action scaffold",
            status=FORMAL_KERNEL_IMPLEMENTATION_SCAFFOLD,
            evidence=("I_U1 is necessary in the v1.2 parent-action reduction.",),
            limitations=("This is action-linked/scaffolded, not a full spectral proof.",),
        ),
    )


def derive_formal_kernel_projector(k_max: int = 4) -> FormalKernelProjectorDerivation:
    """Derive the finite coordinates for the formal sector-labeled kernel."""

    config = default_formal_kernel_operator_config(k_max=k_max)
    labels = sector_labeled_zero_modes(config.base_config)
    coordinates = tuple(basis_coordinate_for_sector_zero(label.sector, k_max, config.base_config.sectors) for label in labels)
    actual = formal_kernel_coordinates(config)
    if coordinates != actual:
        status = OPEN
    else:
        status = FORMAL_KERNEL_BASIS_DERIVED
    p0, p_perp = formal_kernel_projectors(config)
    return FormalKernelProjectorDerivation(
        protected_coordinates=actual,
        old_coordinate_first_coordinates=(0, 1, 2),
        protected_sectors=tuple(label.sector for label in labels),
        basis_ordering_formula="coordinate = sector_index * 2*M(k_max), M(k_max)=sum_{k=0}^{k_max}(floor(k/2)+1)",
        modes_per_chirality_sector=modes_per_chirality_sector(k_max),
        projector_rank=int(np.linalg.matrix_rank(p0)),
        projector_idempotent=bool(np.allclose(p0 @ p0, p0, atol=1e-10)),
        projector_orthogonal_to_complement=bool(np.allclose(p0 @ p_perp, np.zeros_like(p0), atol=1e-10)),
        status=status,
        theorem_complete=False,
        limitations=(
            "The coordinate tuple is basis-ordering-derived from sector labels.",
            "The sector-labeled protected kernel is boundary/action-linked, not fully action-derived.",
            "The full H_T theorem remains open.",
        ),
    )


def build_formal_kernel_action_origin_report(k_max: int = 4) -> FormalKernelActionOriginReport:
    """Build the v1.3N formal-kernel action-origin report."""

    rules = formal_kernel_action_rules()
    derivation = derive_formal_kernel_projector(k_max)
    parent = build_parent_action_derivation_report()
    scaffold = FormalKernelTheoremScaffold(
        assumptions=rules,
        conclusion=(
            "If the protected sector labels, chiral boundary channel, v1.2 boundary functional, "
            "and Level 2 sector-major basis ordering are admitted, the finite formal-kernel "
            f"coordinates are {derivation.protected_coordinates}."
        ),
        status=FORMAL_KERNEL_BASIS_DERIVED,
        theorem_complete=False,
        remaining_obligations=(
            "derive the full protected kernel from the complete twisted Dirac operator",
            "derive the Higgs-selected U(1) kernel channel spectrally",
            "prove the infinite-basis complement projector",
            "prove the full H_T lower bound",
        ),
    )
    return FormalKernelActionOriginReport(
        title="BHSM v1.3N Formal-Kernel Action-Origin Scaffold",
        rules=rules,
        projector_derivation=derivation,
        theorem_scaffold=scaffold,
        parent_action_status=parent.status.value,
        theorem_complete=False,
        limitations=(
            "The formal kernel is boundary/basis-derived in this scaffold, not fully action-derived.",
            "Coordinates are finite-basis implementation labels for sector-labeled states.",
            "No frozen predictions are changed.",
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


def export_formal_kernel_action_origin_json(path: str | Path) -> None:
    """Export the v1.3N formal-kernel action-origin report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_formal_kernel_action_origin_report()), indent=2, sort_keys=True) + "\n")


def export_formal_kernel_action_origin_markdown(path: str | Path) -> None:
    """Export the v1.3N formal-kernel action-origin report as Markdown."""

    report = build_formal_kernel_action_origin_report()
    derivation = report.projector_derivation
    lines = [
        "# BHSM v1.3N Formal-Kernel Action-Origin Scaffold",
        "",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Projector derivation status: `{derivation.status}`",
        f"Parent-action status: `{report.parent_action_status}`",
        "",
        "## Action / Boundary / Basis Rules",
        "",
        "| Rule | Status | Source | Statement |",
        "| --- | --- | --- | --- |",
    ]
    for rule in report.rules:
        lines.append(f"| `{rule.id}` | `{rule.status}` | {rule.source} | {rule.statement} |")
    lines.extend(
        [
            "",
            "## Projector Derivation",
            "",
            "| Quantity | Value |",
            "| --- | --- |",
            f"| Formal protected coordinates | `{derivation.protected_coordinates}` |",
            f"| Old coordinate-first block | `{derivation.old_coordinate_first_coordinates}` |",
            f"| Protected sectors | `{derivation.protected_sectors}` |",
            f"| Modes per chirality/sector | `{derivation.modes_per_chirality_sector}` |",
            f"| Basis formula | `{derivation.basis_ordering_formula}` |",
            f"| Projector rank | `{derivation.projector_rank}` |",
            f"| Idempotent | `{derivation.projector_idempotent}` |",
            "",
            "## Theorem Scaffold",
            "",
            report.theorem_scaffold.conclusion,
            "",
            "Remaining obligations:",
            *[f"- {item}" for item in report.theorem_scaffold.remaining_obligations],
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in report.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))
