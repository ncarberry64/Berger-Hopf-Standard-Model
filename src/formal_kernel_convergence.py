"""BHSM v1.3M convergence audit for corrected formal-kernel H_T scaffold."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from formal_kernel_operator import DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL, default_formal_kernel_operator_config
from formal_kernel_regression import (
    formal_kernel_lower_bound_row,
    formal_kernel_sector_coupling_row,
    _perturbed_formal_config,
)
from ht_operator import alpha_scaled_a
from sector_coupling_bounds import default_sector_coupling_perturbations


DEFAULT_FORMAL_KERNEL_K_MAX_VALUES = (4, 6, 8, 10, 12, 16, 20, 24, 32)
DEFAULT_FORMAL_KERNEL_A_VALUES = ()
_DEFAULT_FORMAL_KERNEL_CONVERGENCE_CACHE: "FormalKernelConvergenceReport | None" = None


@dataclass(frozen=True)
class FormalKernelConvergenceRow:
    """One corrected formal-kernel convergence row."""

    k_max: int
    a: float
    basis_size: int
    protected_coordinates: tuple[int, ...]
    protected_sectors: tuple[str, ...]
    first_complement_eigenvalue: float
    ht_gap: float
    direct_margin: float
    gershgorin_lower_bound: float
    gershgorin_margin_vs_required: float
    minmax_lower_bound: float
    sector_coupling_spectral_norm: float
    structured_lower_bound: float
    passes: bool
    monotonicity_notes: str
    theorem_complete: bool


@dataclass(frozen=True)
class FormalKernelConvergenceReport:
    """Complete corrected formal-kernel convergence report."""

    title: str
    rows: tuple[FormalKernelConvergenceRow, ...]
    perturbation_rows: tuple[dict[str, object], ...]
    all_rows_pass: bool
    worst_direct_margin: float
    worst_gershgorin_margin: float
    min_first_complement_eigenvalue: float
    max_sector_coupling_norm: float
    nonmonotonic_notes: tuple[str, ...]
    classification: str
    theorem_complete: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def _a_values(a_values: Iterable[float] = ()) -> tuple[float, ...]:
    selected = tuple(float(value) for value in a_values)
    return selected if selected else (alpha_scaled_a(), 1.0, 0.573)


def _basis_size(k_max: int) -> int:
    return 3 * 2 * sum((k // 2) + 1 for k in range(k_max + 1))


def scan_formal_kernel_convergence(
    k_max_values: Iterable[int] = DEFAULT_FORMAL_KERNEL_K_MAX_VALUES,
    a_values: Iterable[float] = DEFAULT_FORMAL_KERNEL_A_VALUES,
) -> tuple[FormalKernelConvergenceRow, ...]:
    """Run the corrected formal-kernel basis-convergence scan."""

    rows: list[FormalKernelConvergenceRow] = []
    for a in _a_values(a_values):
        previous: float | None = None
        for k_max in tuple(int(value) for value in k_max_values):
            config = default_formal_kernel_operator_config(k_max=k_max, a=a)
            lower = formal_kernel_lower_bound_row(config)
            sector = formal_kernel_sector_coupling_row(config)
            first = lower.direct_finite_spectrum_lower_bound
            if previous is None:
                note = "baseline basis for this anisotropy"
            elif first < previous - 1e-10:
                note = f"nonmonotonic decrease from {previous} to {first}"
            elif first > previous + 1e-10:
                note = f"nonmonotonic increase from {previous} to {first}"
            else:
                note = "first complement eigenvalue unchanged within tolerance"
            previous = first
            rows.append(
                FormalKernelConvergenceRow(
                    k_max=k_max,
                    a=a,
                    basis_size=_basis_size(k_max),
                    protected_coordinates=lower.protected_coordinates,
                    protected_sectors=lower.protected_sectors,
                    first_complement_eigenvalue=first,
                    ht_gap=lower.ht_gap,
                    direct_margin=lower.margin,
                    gershgorin_lower_bound=lower.gershgorin_lower_bound,
                    gershgorin_margin_vs_required=lower.gershgorin_lower_bound - lower.required_dirac_lower_bound,
                    minmax_lower_bound=lower.minmax_complement_lower_bound,
                    sector_coupling_spectral_norm=sector.spectral_norm,
                    structured_lower_bound=sector.structured_lower_bound,
                    passes=bool(lower.passes_mu_h and sector.finite_basis_passes),
                    monotonicity_notes=note,
                    theorem_complete=False,
                )
            )
    return tuple(rows)


def _small_perturbation_rows() -> tuple[dict[str, object], ...]:
    """Return a feasible perturbation stress table for the corrected variant."""

    rows: list[dict[str, object]] = []
    for k_max in (4, 8, 16):
        base = default_formal_kernel_operator_config(k_max=k_max, a=alpha_scaled_a())
        for perturbation in default_sector_coupling_perturbations():
            row = formal_kernel_sector_coupling_row(_perturbed_formal_config(base, perturbation))
            rows.append(
                {
                    "k_max": k_max,
                    "protected_coordinates": row.protected_coordinates,
                    "sector_coupling": row.sector_coupling,
                    "offdiag_boundary_coupling": row.offdiag_boundary_coupling,
                    "spectral_norm": row.spectral_norm,
                    "structured_lower_bound": row.structured_lower_bound,
                    "classification": row.classification,
                    "finite_basis_passes": row.finite_basis_passes,
                    "theorem_complete": False,
                }
            )
    return tuple(rows)


def build_formal_kernel_convergence_report() -> FormalKernelConvergenceReport:
    """Build the v1.3M corrected formal-kernel convergence report."""

    global _DEFAULT_FORMAL_KERNEL_CONVERGENCE_CACHE
    if _DEFAULT_FORMAL_KERNEL_CONVERGENCE_CACHE is not None:
        return _DEFAULT_FORMAL_KERNEL_CONVERGENCE_CACHE

    rows = scan_formal_kernel_convergence()
    perturbation_rows = _small_perturbation_rows()
    nonmonotonic = tuple(
        f"k_max={row.k_max}, a={row.a}: {row.monotonicity_notes}"
        for row in rows
        if row.monotonicity_notes.startswith("nonmonotonic")
    )
    all_pass = all(row.passes for row in rows)
    classification = "FORMAL_KERNEL_CONVERGENCE_SUPPORTED" if all_pass else "FORMAL_KERNEL_CONVERGENCE_FAILURE_REPORTED"
    report = FormalKernelConvergenceReport(
        title="BHSM v1.3M Corrected Formal-Kernel Convergence Audit",
        rows=rows,
        perturbation_rows=perturbation_rows,
        all_rows_pass=all_pass,
        worst_direct_margin=min(row.direct_margin for row in rows),
        worst_gershgorin_margin=min(row.gershgorin_margin_vs_required for row in rows),
        min_first_complement_eigenvalue=min(row.first_complement_eigenvalue for row in rows),
        max_sector_coupling_norm=max(row.sector_coupling_spectral_norm for row in rows),
        nonmonotonic_notes=nonmonotonic,
        classification=classification,
        theorem_complete=False,
        assumptions=(
            "The corrected formal-kernel operator is used in every convergence row.",
            "The formal protected coordinates move with sector-major basis size but always represent one lepton, one up, and one down state.",
            "No empirical prediction/residual machinery enters the scan.",
        ),
        limitations=(
            "The scan is finite-basis convergence evidence, not an infinite-basis theorem.",
            "The full twisted Dirac spectrum remains open.",
            "Perturbation rows are a feasible stress table, not a full exhaustive scan through k_max=32.",
        ),
    )
    _DEFAULT_FORMAL_KERNEL_CONVERGENCE_CACHE = report
    return report


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


def export_formal_kernel_convergence_json(path: str | Path) -> None:
    """Export the corrected formal-kernel convergence report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_formal_kernel_convergence_report()), indent=2, sort_keys=True) + "\n")


def export_formal_kernel_convergence_markdown(path: str | Path) -> None:
    """Export the corrected formal-kernel convergence report as Markdown."""

    report = build_formal_kernel_convergence_report()
    lines = [
        "# BHSM v1.3M Corrected Formal-Kernel Convergence Audit",
        "",
        f"Classification: `{report.classification}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"All rows pass: `{report.all_rows_pass}`",
        "",
        "BHSM v1.3M reruns the basis-convergence audit using `DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL`.",
        "",
        "## Corrected Convergence Table",
        "",
        "| k_max | a | basis | protected coordinates | first complement | H_T margin | Gershgorin margin | sector norm | structured lower | passes | notes |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.rows:
        lines.append(
            f"| `{row.k_max}` | `{row.a}` | `{row.basis_size}` | `{row.protected_coordinates}` | `{row.first_complement_eigenvalue}` | `{row.direct_margin}` | `{row.gershgorin_margin_vs_required}` | `{row.sector_coupling_spectral_norm}` | `{row.structured_lower_bound}` | `{row.passes}` | {row.monotonicity_notes} |"
        )
    lines.extend(
        [
            "",
            "## Feasible Perturbation Stress Table",
            "",
            "| protected coordinates | sector coupling | offdiag boundary | spectral norm | structured lower | classification | finite pass |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.perturbation_rows:
        lines.append(
            f"| `{row['protected_coordinates']}` | `{row['sector_coupling']}` | `{row['offdiag_boundary_coupling']}` | `{row['spectral_norm']}` | `{row['structured_lower_bound']}` | `{row['classification']}` | `{row['finite_basis_passes']}` |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Worst direct margin: `{report.worst_direct_margin}`",
            f"- Worst Gershgorin margin: `{report.worst_gershgorin_margin}`",
            f"- Minimum first complement eigenvalue: `{report.min_first_complement_eigenvalue}`",
            f"- Maximum sector-coupling spectral norm: `{report.max_sector_coupling_norm}`",
            f"- Nonmonotonic notes: `{report.nonmonotonic_notes}`",
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in report.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))
