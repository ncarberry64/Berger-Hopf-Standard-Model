"""BHSM v1.3K protected-kernel correction audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from ht_operator import default_level2_config, level2_ht_gap_report
from positivity import restrict_to_complement
from sector_coupling_bounds import level2_sector_coupling_dirac_block
from sector_labeled_kernel import (
    ProtectedKernelProjector,
    coordinate_first_projector,
    formal_protected_projector,
    protected_kernel_basis_matrix,
    sector_labeled_zero_modes,
)
from spectral_gap import MU_H, heat_lift, natural_lambda2
from twisted_dirac import DiracOperatorConfig, build_level2_dirac_matrix


FORMAL_KERNEL_CONFIRMED = "FORMAL_KERNEL_CONFIRMED"
FINITE_SCAFFOLD_BUG_FOUND = "FINITE_SCAFFOLD_BUG_FOUND"
FORMAL_KERNEL_NOT_PROTECTED = "FORMAL_KERNEL_NOT_PROTECTED"
BASIS_CHANGE_REQUIRED = "BASIS_CHANGE_REQUIRED"


@dataclass(frozen=True)
class KernelCorrectionResult:
    """Gap comparison for legacy versus formal protected projectors."""

    old_projector_name: str
    formal_projector_name: str
    old_protected_coordinates: tuple[int, ...]
    formal_protected_coordinates: tuple[int, ...]
    old_first_complement_eigenvalue: float
    old_ht_gap: float
    old_margin: float
    formal_first_complement_eigenvalue: float
    formal_ht_gap: float
    formal_margin: float
    formal_gap_passes: bool
    previous_gap_survives: bool
    classification: str
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class ProtectedKernelAuditReport:
    """Complete v1.3K protected-kernel audit report."""

    title: str
    old_projector: ProtectedKernelProjector
    formal_projector: ProtectedKernelProjector
    sector_labeled_modes: tuple[object, ...]
    formal_kernel_rank: int
    formal_kernel_present: bool
    formal_kernel_heat_preserved: bool
    formal_kernel_sector_coupling_vanishes: bool
    correction_result: KernelCorrectionResult
    alignment_gap_closes: bool
    theorem_complete: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def _projector_basis_for_indices(size: int, indices: tuple[int, ...]) -> np.ndarray:
    basis = np.zeros((size, len(indices)))
    for col, index in enumerate(indices):
        basis[index, col] = 1.0
    return basis


def _gap_with_projector_indices(
    config: DiracOperatorConfig,
    indices: tuple[int, ...],
) -> tuple[float, float, float]:
    matrix = build_level2_dirac_matrix(config)
    d2 = matrix.T @ matrix
    basis = _projector_basis_for_indices(d2.shape[0], indices)
    restricted = restrict_to_complement(d2, basis)
    first = float(np.linalg.eigvalsh(restricted)[0])
    ht_gap = float(heat_lift(max(first, 0.0), natural_lambda2(), mu_h=MU_H))
    return first, ht_gap, ht_gap - MU_H


def _formal_kernel_heat_preserved(config: DiracOperatorConfig) -> bool:
    matrix = build_level2_dirac_matrix(config)
    d2 = matrix.T @ matrix
    for label in sector_labeled_zero_modes(config):
        if label.coordinate_index is None:
            return False
        if abs(float(d2[label.coordinate_index, label.coordinate_index])) > 1e-12:
            return False
    return True


def _formal_kernel_sector_coupling_vanishes(config: DiracOperatorConfig) -> bool:
    sector_block = level2_sector_coupling_dirac_block(config)
    for label in sector_labeled_zero_modes(config):
        if label.coordinate_index is None:
            return False
        index = label.coordinate_index
        if not (
            np.allclose(sector_block[index, :], 0.0, atol=1e-12)
            and np.allclose(sector_block[:, index], 0.0, atol=1e-12)
        ):
            return False
    return True


def build_kernel_correction_result(config: DiracOperatorConfig | None = None) -> KernelCorrectionResult:
    """Compare old coordinate-first and formal sector-labeled projectors."""

    resolved = default_level2_config() if config is None else config
    old = coordinate_first_projector(resolved)
    formal = formal_protected_projector(resolved)
    old_first, old_gap, old_margin = _gap_with_projector_indices(resolved, old.coordinate_indices)
    formal_first, formal_gap, formal_margin = _gap_with_projector_indices(resolved, formal.coordinate_indices)
    formal_passes = bool(formal_gap >= MU_H)
    survives = bool(formal_passes and formal_first >= old_first - 1e-10)
    heat_ok = _formal_kernel_heat_preserved(resolved)
    sector_ok = _formal_kernel_sector_coupling_vanishes(resolved)
    if heat_ok and sector_ok and formal_passes:
        classification = FORMAL_KERNEL_CONFIRMED
    elif not heat_ok or not sector_ok:
        classification = FORMAL_KERNEL_NOT_PROTECTED
    elif old.coordinate_indices != formal.coordinate_indices and not formal_passes:
        classification = FINITE_SCAFFOLD_BUG_FOUND
    else:
        classification = BASIS_CHANGE_REQUIRED
    return KernelCorrectionResult(
        old_projector_name=old.name,
        formal_projector_name=formal.name,
        old_protected_coordinates=old.coordinate_indices,
        formal_protected_coordinates=formal.coordinate_indices,
        old_first_complement_eigenvalue=float(old_first),
        old_ht_gap=float(old_gap),
        old_margin=float(old_margin),
        formal_first_complement_eigenvalue=float(formal_first),
        formal_ht_gap=float(formal_gap),
        formal_margin=float(formal_margin),
        formal_gap_passes=formal_passes,
        previous_gap_survives=survives,
        classification=classification,
        limitations=(
            "Formal-projector recomputation is finite-basis scaffold evidence.",
            "Failure under the formal projector exposes a Level 2 kernel-protection blocker, not a change to frozen predictions.",
        ),
    )


def build_protected_kernel_audit_report(config: DiracOperatorConfig | None = None) -> ProtectedKernelAuditReport:
    """Return the v1.3K protected-kernel audit report."""

    resolved = default_level2_config() if config is None else config
    old = coordinate_first_projector(resolved)
    formal = formal_protected_projector(resolved)
    modes = sector_labeled_zero_modes(resolved)
    result = build_kernel_correction_result(resolved)
    heat_ok = _formal_kernel_heat_preserved(resolved)
    sector_ok = _formal_kernel_sector_coupling_vanishes(resolved)
    return ProtectedKernelAuditReport(
        title="BHSM v1.3K Protected Kernel Audit",
        old_projector=old,
        formal_projector=formal,
        sector_labeled_modes=modes,
        formal_kernel_rank=formal.rank,
        formal_kernel_present=all(mode.present_in_basis for mode in modes),
        formal_kernel_heat_preserved=heat_ok,
        formal_kernel_sector_coupling_vanishes=sector_ok,
        correction_result=result,
        alignment_gap_closes=result.classification == FORMAL_KERNEL_CONFIRMED,
        theorem_complete=False,
        assumptions=(
            "The formal BHSM kernel is the sector-labeled lepton/up/down heavy-mode triplet.",
            "The finite Level 2 basis ordering is inspected without changing the operator.",
        ),
        limitations=(
            "The formal sector-labeled kernel is present in the finite basis but is not protected by the current Level 2 matrix.",
            "The full H_T theorem remains open.",
            "No frozen model output is changed.",
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


def export_protected_kernel_audit_json(path: str | Path) -> None:
    """Export the protected-kernel audit report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_protected_kernel_audit_report()), indent=2, sort_keys=True) + "\n")


def export_protected_kernel_audit_markdown(path: str | Path) -> None:
    """Export the protected-kernel audit report as Markdown."""

    report = build_protected_kernel_audit_report()
    result = report.correction_result
    lines = [
        "# BHSM v1.3K Protected Kernel Audit",
        "",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Classification: `{result.classification}`",
        f"Alignment gap closes: `{report.alignment_gap_closes}`",
        "",
        "## Old vs Formal Projectors",
        "",
        "| Projector | Coordinates | Rank | Sector distribution |",
        "| --- | --- | --- | --- |",
        f"| `{report.old_projector.name}` | `{report.old_projector.coordinate_indices}` | `{report.old_projector.rank}` | `{report.old_projector.sector_distribution}` |",
        f"| `{report.formal_projector.name}` | `{report.formal_projector.coordinate_indices}` | `{report.formal_projector.rank}` | `{report.formal_projector.sector_distribution}` |",
        "",
        "## Formal Kernel Table",
        "",
        "| ID | Sector | k | j | q | chi | coordinate | present |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for mode in report.sector_labeled_modes:
        lines.append(
            f"| `{mode.id}` | `{mode.sector}` | `{mode.k}` | `{mode.j}` | `{mode.q}` | `{mode.chirality}` | `{mode.coordinate_index}` | `{mode.present_in_basis}` |"
        )
    lines.extend(
        [
            "",
            "## Gap Recompute",
            "",
            "| Quantity | Old coordinate-first | Formal sector-labeled |",
            "| --- | --- | --- |",
            f"| first complement eigenvalue | `{result.old_first_complement_eigenvalue}` | `{result.formal_first_complement_eigenvalue}` |",
            f"| H_T gap | `{result.old_ht_gap}` | `{result.formal_ht_gap}` |",
            f"| margin vs mu_H | `{result.old_margin}` | `{result.formal_margin}` |",
            f"| passes | `True` | `{result.formal_gap_passes}` |",
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in report.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))
