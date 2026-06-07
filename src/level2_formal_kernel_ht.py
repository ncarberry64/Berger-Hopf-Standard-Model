"""BHSM v1.3L H_T audit for the corrected formal-kernel Level 2 variant."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from formal_kernel_operator import (
    DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL,
    FormalKernelOperatorConfig,
    build_formal_kernel_dirac_matrix,
    default_formal_kernel_operator_config,
    formal_kernel_basis_matrix,
    formal_kernel_coordinates,
    formal_kernel_projectors,
    formal_kernel_sector_coupling_block,
    operator_variant_summary,
)
from ht_operator import alpha_scaled_a, default_level2_config, level2_ht_gap_report
from operator_norm_bounds import operator_norm_bounds
from positivity import min_eigenvalue, restrict_to_complement
from sector_labeled_kernel import coordinate_first_projector
from spectral_bounds import required_dirac_lower_bound
from spectral_gap import MU_H, heat_lift, natural_lambda2


FORMAL_KERNEL_GAP_RESTORED = "FORMAL_KERNEL_GAP_RESTORED"
FORMAL_KERNEL_GAP_FAILS = "FORMAL_KERNEL_GAP_FAILS"
FORMAL_KERNEL_OPERATOR_INCONSISTENT = "FORMAL_KERNEL_OPERATOR_INCONSISTENT"
REQUIRES_NEW_ACTION_TERM = "REQUIRES_NEW_ACTION_TERM"


@dataclass(frozen=True)
class FormalKernelHTReport:
    """Corrected formal-kernel H_T gap report."""

    model_level: str
    basis_size: int
    protected_coordinates: tuple[int, ...]
    protected_sectors: tuple[str, ...]
    first_complement_eigenvalue: float
    first_ht_complement_gap: float
    margin: float
    required_dirac_lower_bound: float
    passes_mu_h: bool
    sector_coupling_spectral_norm: float
    sector_coupling_frobenius_norm: float
    sector_coupling_row_sum_norm: float
    sector_coupling_vanishes_on_formal_kernel: bool
    structured_relative_bound_candidate: str
    basis_convergence_candidate: str
    theorem_complete: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class FormalKernelCorrectionAudit:
    """Complete v1.3L corrected-operator audit."""

    title: str
    old_variant: str
    new_variant: str
    old_protected_coordinates: tuple[int, ...]
    formal_protected_coordinates: tuple[int, ...]
    formal_kernel_protected: bool
    projector_rank: int
    projector_idempotent: bool
    projector_orthogonal_to_complement: bool
    matrix_symmetric: bool
    heat_lift_preserves_formal_kernel: bool
    sector_coupling_vanishes_on_formal_kernel: bool
    ht_report: FormalKernelHTReport
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def _restricted_formal_d2(config: FormalKernelOperatorConfig) -> np.ndarray:
    matrix = build_formal_kernel_dirac_matrix(config)
    d2 = matrix.T @ matrix
    kernel = formal_kernel_basis_matrix(config)
    return restrict_to_complement(d2, kernel)


def _sector_coupling_vanishes(config: FormalKernelOperatorConfig, tol: float = 1e-12) -> bool:
    block = formal_kernel_sector_coupling_block(config)
    for index in formal_kernel_coordinates(config):
        if not (
            np.allclose(block[index, :], 0.0, atol=tol)
            and np.allclose(block[:, index], 0.0, atol=tol)
        ):
            return False
    return True


def _formal_kernel_is_protected(config: FormalKernelOperatorConfig, tol: float = 1e-12) -> bool:
    matrix = build_formal_kernel_dirac_matrix(config)
    d2 = matrix.T @ matrix
    return all(
        np.allclose(matrix[index, :], 0.0, atol=tol)
        and np.allclose(matrix[:, index], 0.0, atol=tol)
        and abs(float(d2[index, index])) <= tol
        for index in formal_kernel_coordinates(config)
    )


def build_formal_kernel_ht_report(
    config: FormalKernelOperatorConfig | None = None,
    lambda2: float | None = None,
    mu_h: float = MU_H,
) -> FormalKernelHTReport:
    """Return the corrected formal-kernel H_T gap report."""

    resolved = default_formal_kernel_operator_config() if config is None else config
    resolved_lambda2 = natural_lambda2() if lambda2 is None else float(lambda2)
    restricted = _restricted_formal_d2(resolved)
    first = min_eigenvalue(restricted)
    ht_gap = heat_lift(max(0.0, first), resolved_lambda2, mu_h=mu_h)
    sector_block = formal_kernel_sector_coupling_block(resolved)
    sector_restricted = restrict_to_complement(sector_block, formal_kernel_basis_matrix(resolved))
    norms = {bound.name: bound.value for bound in operator_norm_bounds(sector_restricted)}
    labels = operator_variant_summary(resolved)["protected_sectors"]
    return FormalKernelHTReport(
        model_level=DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL,
        basis_size=int(build_formal_kernel_dirac_matrix(resolved).shape[0]),
        protected_coordinates=formal_kernel_coordinates(resolved),
        protected_sectors=tuple(labels),  # type: ignore[arg-type]
        first_complement_eigenvalue=float(first),
        first_ht_complement_gap=float(ht_gap),
        margin=float(ht_gap - mu_h),
        required_dirac_lower_bound=float(required_dirac_lower_bound(resolved_lambda2, mu_h)),
        passes_mu_h=bool(ht_gap >= mu_h),
        sector_coupling_spectral_norm=float(norms["spectral_norm"]),
        sector_coupling_frobenius_norm=float(norms["frobenius_norm"]),
        sector_coupling_row_sum_norm=float(norms["row_sum_norm"]),
        sector_coupling_vanishes_on_formal_kernel=_sector_coupling_vanishes(resolved),
        structured_relative_bound_candidate="FORMAL_KERNEL_RECOMPUTED_FINITE_BASIS",
        basis_convergence_candidate="PENDING_RERUN_UNDER_FORMAL_KERNEL_VARIANT",
        theorem_complete=False,
        assumptions=(
            "The formal protected kernel is the sector-labeled coordinate block (0,18,36) for the default k_max=4 basis.",
            "The corrected Level 2 variant zeros rows and columns for the formal protected block.",
            "Natural Lambda^2 = 1/(4*pi) is used when lambda2 is omitted.",
        ),
        limitations=(
            "This is a corrected finite-basis Level 2 scaffold.",
            "Structured, uniform, and basis-convergence audits must be rerun under this formal-kernel variant before stronger H_T claims.",
            "The full H_T theorem remains open.",
        ),
    )


def build_formal_kernel_correction_audit(
    config: FormalKernelOperatorConfig | None = None,
    lambda2: float | None = None,
) -> FormalKernelCorrectionAudit:
    """Return the complete corrected-operator v1.3L audit."""

    resolved = default_formal_kernel_operator_config() if config is None else config
    summary = operator_variant_summary(resolved)
    p0, p_perp = formal_kernel_projectors(resolved)
    matrix = build_formal_kernel_dirac_matrix(resolved)
    ht_report = build_formal_kernel_ht_report(resolved, lambda2=lambda2)
    protected = _formal_kernel_is_protected(resolved)
    consistent = (
        protected
        and bool(summary["matrix_symmetric"])
        and bool(summary["projector_idempotent"])
        and bool(summary["p0_pperp_zero"])
    )
    if not consistent:
        status = FORMAL_KERNEL_OPERATOR_INCONSISTENT
    elif ht_report.passes_mu_h and ht_report.sector_coupling_vanishes_on_formal_kernel:
        status = FORMAL_KERNEL_GAP_RESTORED
    elif not ht_report.passes_mu_h:
        status = FORMAL_KERNEL_GAP_FAILS
    else:
        status = REQUIRES_NEW_ACTION_TERM
    return FormalKernelCorrectionAudit(
        title="BHSM v1.3L Corrected Formal-Kernel H_T Operator Audit",
        old_variant=str(summary["old_variant"]),
        new_variant=str(summary["new_variant"]),
        old_protected_coordinates=coordinate_first_projector(resolved.base_config).coordinate_indices,
        formal_protected_coordinates=formal_kernel_coordinates(resolved),
        formal_kernel_protected=protected,
        projector_rank=int(np.linalg.matrix_rank(p0)),
        projector_idempotent=bool(np.allclose(p0 @ p0, p0, atol=1e-10)),
        projector_orthogonal_to_complement=bool(np.allclose(p0 @ p_perp, np.zeros_like(p0), atol=1e-10)),
        matrix_symmetric=bool(np.allclose(matrix, matrix.T, atol=1e-12)),
        heat_lift_preserves_formal_kernel=bool(summary["heat_lift_preserves_formal_kernel"]),
        sector_coupling_vanishes_on_formal_kernel=ht_report.sector_coupling_vanishes_on_formal_kernel,
        ht_report=ht_report,
        status=status,
        theorem_complete=False,
        limitations=(
            "The corrected formal-kernel operator is a finite-basis scaffold variant.",
            "It does not change frozen BHSM v1.0/v1.1 predictions.",
            "It does not prove the full H_T no-extra-light-state theorem.",
        ),
    )


def legacy_vs_formal_gap_table() -> tuple[dict[str, object], ...]:
    """Return old coordinate-first and corrected formal-kernel gap rows."""

    old = level2_ht_gap_report(default_level2_config(), natural_lambda2())
    formal = build_formal_kernel_ht_report()
    return (
        {
            "variant": "DIRAC_PROXY_LEVEL_2_COORDINATE_FIRST",
            "protected_coordinates": coordinate_first_projector().coordinate_indices,
            "first_complement_eigenvalue": old["first_complement_eigenvalue"],
            "ht_gap": old["first_ht_complement_gap"],
            "margin": old["margin"],
            "passes": old["passes"],
        },
        {
            "variant": formal.model_level,
            "protected_coordinates": formal.protected_coordinates,
            "first_complement_eigenvalue": formal.first_complement_eigenvalue,
            "ht_gap": formal.first_ht_complement_gap,
            "margin": formal.margin,
            "passes": formal.passes_mu_h,
        },
    )


def scan_formal_kernel_ht_gap(
    k_max_values: Iterable[int] = (4, 6, 8),
    a_values: Iterable[float] | None = None,
    lambda2: float | None = None,
) -> tuple[dict[str, object], ...]:
    """Return a small corrected-operator robustness scan.

    Coordinates move with basis size because the basis is sector-major. The
    protected sector content remains one lepton, one up, and one down state.
    """

    resolved_a_values = tuple(a_values or (alpha_scaled_a(), 1.0, 0.573))
    rows: list[dict[str, object]] = []
    for k_max in k_max_values:
        for a in resolved_a_values:
            config = default_formal_kernel_operator_config(k_max=int(k_max), a=float(a))
            audit = build_formal_kernel_correction_audit(config, lambda2=lambda2)
            report = audit.ht_report
            rows.append(
                {
                    "k_max": int(k_max),
                    "a": float(a),
                    "basis_size": report.basis_size,
                    "protected_coordinates": report.protected_coordinates,
                    "protected_sectors": report.protected_sectors,
                    "first_complement_eigenvalue": report.first_complement_eigenvalue,
                    "ht_gap": report.first_ht_complement_gap,
                    "margin": report.margin,
                    "passes": report.passes_mu_h,
                    "status": audit.status,
                    "theorem_complete": False,
                }
            )
    return tuple(rows)


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


def export_formal_kernel_ht_gap_json(path: str | Path) -> None:
    """Export v1.3L corrected formal-kernel H_T audit as JSON."""

    payload = {
        "audit": build_formal_kernel_correction_audit(),
        "legacy_vs_formal_gap_table": legacy_vs_formal_gap_table(),
        "formal_kernel_scan": scan_formal_kernel_ht_gap(),
        "theorem_complete": False,
        "correct_claim": (
            "BHSM v1.3L corrects the Level 2 H_T scaffold to protect the formal "
            "sector-labeled kernel. The corrected formal-kernel gap is recomputed "
            "before any Level 2 H_T claim can rely on it."
        ),
    }
    Path(path).write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n")


def export_formal_kernel_ht_gap_markdown(path: str | Path) -> None:
    """Export v1.3L corrected formal-kernel H_T audit as Markdown."""

    audit = build_formal_kernel_correction_audit()
    report = audit.ht_report
    lines = [
        "# BHSM v1.3L Corrected Formal-Kernel H_T Gap Report",
        "",
        f"Theorem complete: `{audit.theorem_complete}`",
        f"Status: `{audit.status}`",
        "",
        "## Old vs New Protected Coordinates",
        "",
        "| Variant | Coordinates |",
        "| --- | --- |",
        f"| `{audit.old_variant}` | `{audit.old_protected_coordinates}` |",
        f"| `{audit.new_variant}` | `{audit.formal_protected_coordinates}` |",
        "",
        "## Corrected Formal-Kernel Gap",
        "",
        "| Quantity | Value |",
        "| --- | --- |",
        f"| Protected sectors | `{report.protected_sectors}` |",
        f"| Formal kernel protected | `{audit.formal_kernel_protected}` |",
        f"| Sector coupling vanishes on formal kernel | `{audit.sector_coupling_vanishes_on_formal_kernel}` |",
        f"| First complement eigenvalue | `{report.first_complement_eigenvalue}` |",
        f"| Required Dirac lower bound | `{report.required_dirac_lower_bound}` |",
        f"| H_T gap | `{report.first_ht_complement_gap}` |",
        f"| Margin vs mu_H | `{report.margin}` |",
        f"| Passes mu_H | `{report.passes_mu_h}` |",
        "",
        "## Sector-Coupling Norms on Formal Complement",
        "",
        "| Norm | Value |",
        "| --- | --- |",
        f"| Spectral | `{report.sector_coupling_spectral_norm}` |",
        f"| Frobenius | `{report.sector_coupling_frobenius_norm}` |",
        f"| Row-sum | `{report.sector_coupling_row_sum_norm}` |",
        "",
        "## Legacy vs Formal Gap Table",
        "",
        "| Variant | Coordinates | First complement | H_T gap | Margin | Passes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in legacy_vs_formal_gap_table():
        lines.append(
            f"| `{row['variant']}` | `{row['protected_coordinates']}` | `{row['first_complement_eigenvalue']}` | `{row['ht_gap']}` | `{row['margin']}` | `{row['passes']}` |"
        )
    lines.extend(
        [
            "",
            "## Formal-Kernel Robustness Scan",
            "",
            "| k_max | a | Coordinates | First complement | Margin | Passes | Status |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in scan_formal_kernel_ht_gap():
        lines.append(
            f"| `{row['k_max']}` | `{row['a']}` | `{row['protected_coordinates']}` | `{row['first_complement_eigenvalue']}` | `{row['margin']}` | `{row['passes']}` | `{row['status']}` |"
        )
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in audit.limitations],
            *[f"- {item}" for item in report.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))
