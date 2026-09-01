"""BHSM v1.3M regression audit for corrected formal-kernel H_T bounds."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

from formal_kernel_operator import (
    DIRAC_PROXY_LEVEL_2_COORDINATE_FIRST,
    DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL,
    FormalKernelOperatorConfig,
    build_formal_kernel_dirac_matrix,
    default_formal_kernel_operator_config,
    formal_kernel_basis_matrix,
    formal_kernel_coordinates,
    formal_kernel_sector_coupling_block,
)
from ht_operator import default_level2_config, level2_ht_gap_report
from operator_norm_bounds import gap_stability_from_norm, operator_norm_bounds
from positivity import min_eigenvalue, restrict_to_complement
from relative_bound_program import rayleigh_relative_bound, structured_relative_certificate
from sector_coupling_bounds import (
    default_sector_coupling_perturbations,
    sector_coupling_bound_report,
)
from spectral_bounds import gershgorin_lower_bound, minmax_bound, required_dirac_lower_bound
from spectral_gap import MU_H, heat_lift, natural_lambda2


@dataclass(frozen=True)
class FormalKernelLowerBoundRow:
    """Lower-bound comparison row for one operator variant."""

    variant: str
    protected_coordinates: tuple[int, ...]
    protected_sectors: tuple[str, ...]
    direct_finite_spectrum_lower_bound: float
    minmax_complement_lower_bound: float
    gershgorin_lower_bound: float
    required_dirac_lower_bound: float
    ht_gap: float
    margin: float
    passes_mu_h: bool
    theorem_complete: bool


@dataclass(frozen=True)
class FormalKernelSectorCouplingRow:
    """Sector-coupling regression row."""

    variant: str
    protected_coordinates: tuple[int, ...]
    sector_coupling: float
    offdiag_boundary_coupling: float
    base_complement_lower_bound: float
    full_complement_lower_bound: float
    spectral_norm: float
    frobenius_norm: float
    row_sum_norm: float
    weyl_lower_bound: float
    relative_a_k: float
    structured_lower_bound: float
    classification: str
    finite_basis_passes: bool
    theorem_complete: bool


@dataclass(frozen=True)
class FormalKernelRegressionReport:
    """Complete v1.3M corrected formal-kernel regression report."""

    title: str
    lower_bound_rows: tuple[FormalKernelLowerBoundRow, ...]
    sector_coupling_rows: tuple[FormalKernelSectorCouplingRow, ...]
    corrected_gap_stable: bool
    previous_conclusions_revised: tuple[str, ...]
    theorem_complete: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def _config_without_sector_coupling(config: FormalKernelOperatorConfig) -> FormalKernelOperatorConfig:
    base = config.base_config
    boundary = dict(base.boundary_params)
    boundary["sector_coupling"] = 0.0
    boundary["offdiag_boundary_coupling"] = 0.0
    return FormalKernelOperatorConfig(
        base_config=type(base)(
            a=base.a,
            k_max=base.k_max,
            sectors=base.sectors,
            twist_params=dict(base.twist_params),
            boundary_params=boundary,
            include_chirality=base.include_chirality,
            operator_level=base.operator_level,
        ),
        protected_coordinates=config.protected_coordinates,
    )


def _formal_restricted_objects(config: FormalKernelOperatorConfig) -> dict[str, np.ndarray]:
    kernel = formal_kernel_basis_matrix(config)
    full_dirac = build_formal_kernel_dirac_matrix(config)
    no_sector = build_formal_kernel_dirac_matrix(_config_without_sector_coupling(config))
    full_sq = full_dirac.T @ full_dirac
    base_sq = no_sector.T @ no_sector
    perturb = full_sq - base_sq
    return {
        "kernel": kernel,
        "full_sq": full_sq,
        "base_sq": base_sq,
        "perturb": perturb,
        "restricted_full": restrict_to_complement(full_sq, kernel),
        "restricted_base": restrict_to_complement(base_sq, kernel),
        "restricted_perturb": restrict_to_complement(perturb, kernel),
    }


def formal_kernel_lower_bound_row(
    config: FormalKernelOperatorConfig | None = None,
    lambda2: float | None = None,
) -> FormalKernelLowerBoundRow:
    """Return corrected formal-kernel lower-bound row."""

    resolved = default_formal_kernel_operator_config() if config is None else config
    resolved_lambda2 = natural_lambda2() if lambda2 is None else float(lambda2)
    objects = _formal_restricted_objects(resolved)
    restricted = objects["restricted_full"]
    direct = min_eigenvalue(restricted)
    kernel = objects["kernel"]
    p_perp = np.eye(kernel.shape[0]) - kernel @ kernel.T
    minmax = minmax_bound(objects["full_sq"], p_perp)
    gersh = gershgorin_lower_bound(restricted)
    ht_gap = heat_lift(max(0.0, direct), resolved_lambda2, mu_h=MU_H)
    return FormalKernelLowerBoundRow(
        variant=DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL,
        protected_coordinates=formal_kernel_coordinates(resolved),
        protected_sectors=("lepton", "up", "down"),
        direct_finite_spectrum_lower_bound=float(direct),
        minmax_complement_lower_bound=float(minmax),
        gershgorin_lower_bound=float(gersh),
        required_dirac_lower_bound=required_dirac_lower_bound(resolved_lambda2, MU_H),
        ht_gap=float(ht_gap),
        margin=float(ht_gap - MU_H),
        passes_mu_h=bool(ht_gap >= MU_H),
        theorem_complete=False,
    )


def old_coordinate_first_lower_bound_row(lambda2: float | None = None) -> FormalKernelLowerBoundRow:
    """Return legacy coordinate-first lower-bound row for comparison."""

    resolved_lambda2 = natural_lambda2() if lambda2 is None else float(lambda2)
    report = level2_ht_gap_report(default_level2_config(), resolved_lambda2)
    return FormalKernelLowerBoundRow(
        variant=DIRAC_PROXY_LEVEL_2_COORDINATE_FIRST,
        protected_coordinates=(0, 1, 2),
        protected_sectors=("lepton", "lepton", "lepton"),
        direct_finite_spectrum_lower_bound=float(report["first_complement_eigenvalue"]),
        minmax_complement_lower_bound=float(report["first_complement_eigenvalue"]),
        gershgorin_lower_bound=1.4366234871740744,
        required_dirac_lower_bound=required_dirac_lower_bound(resolved_lambda2, MU_H),
        ht_gap=float(report["first_ht_complement_gap"]),
        margin=float(report["margin"]),
        passes_mu_h=bool(report["passes"]),
        theorem_complete=False,
    )


def formal_kernel_sector_coupling_row(
    config: FormalKernelOperatorConfig | None = None,
    lambda2: float | None = None,
) -> FormalKernelSectorCouplingRow:
    """Return corrected formal-kernel sector-coupling regression row."""

    resolved = default_formal_kernel_operator_config() if config is None else config
    resolved_lambda2 = natural_lambda2() if lambda2 is None else float(lambda2)
    required = required_dirac_lower_bound(resolved_lambda2, MU_H)
    objects = _formal_restricted_objects(resolved)
    restricted_base = objects["restricted_base"]
    restricted_full = objects["restricted_full"]
    restricted_k = objects["restricted_perturb"]
    base_lower = min_eigenvalue(restricted_base)
    full_lower = min_eigenvalue(restricted_full)
    norms = {bound.name: bound.value for bound in operator_norm_bounds(restricted_k)}
    stability = gap_stability_from_norm(base_lower, norms["spectral_norm"], full_lower, required)
    a_k = rayleigh_relative_bound(restricted_base, restricted_k)
    certificate = structured_relative_certificate(
        a_k=a_k,
        base_lower_bound=base_lower,
        full_lower_bound=full_lower,
        required_dirac_lower_bound=required,
        finite_basis_only=True,
    )
    base = resolved.base_config
    return FormalKernelSectorCouplingRow(
        variant=DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL,
        protected_coordinates=formal_kernel_coordinates(resolved),
        sector_coupling=float(base.boundary_params.get("sector_coupling", 0.0)),
        offdiag_boundary_coupling=float(base.boundary_params.get("offdiag_boundary_coupling", 0.0)),
        base_complement_lower_bound=float(base_lower),
        full_complement_lower_bound=float(full_lower),
        spectral_norm=float(norms["spectral_norm"]),
        frobenius_norm=float(norms["frobenius_norm"]),
        row_sum_norm=float(norms["row_sum_norm"]),
        weyl_lower_bound=float(stability.weyl_lower_bound),
        relative_a_k=float(a_k),
        structured_lower_bound=float(certificate.structured_lower_bound),
        classification=certificate.classification,
        finite_basis_passes=bool(full_lower >= required),
        theorem_complete=False,
    )


def old_coordinate_first_sector_coupling_row() -> FormalKernelSectorCouplingRow:
    """Return legacy coordinate-first sector-coupling row for comparison."""

    report = sector_coupling_bound_report(default_level2_config(), lambda2=natural_lambda2())
    return FormalKernelSectorCouplingRow(
        variant=DIRAC_PROXY_LEVEL_2_COORDINATE_FIRST,
        protected_coordinates=(0, 1, 2),
        sector_coupling=report.sector_coupling,
        offdiag_boundary_coupling=report.offdiag_boundary_coupling,
        base_complement_lower_bound=report.base_complement_lower_bound,
        full_complement_lower_bound=report.full_complement_lower_bound,
        spectral_norm=report.sector_perturbation_spectral_norm,
        frobenius_norm=report.sector_perturbation_frobenius_norm,
        row_sum_norm=report.sector_perturbation_row_sum_norm,
        weyl_lower_bound=report.stability.weyl_lower_bound,
        relative_a_k=report.relative_bound.a_k,
        structured_lower_bound=1.4412292741558648,
        classification=report.stability.classification,
        finite_basis_passes=report.stability.finite_basis_passes,
        theorem_complete=False,
    )


def _perturbed_formal_config(
    config: FormalKernelOperatorConfig,
    perturbation: Mapping[str, float],
) -> FormalKernelOperatorConfig:
    base = config.base_config
    boundary = dict(base.boundary_params)
    boundary.update({key: float(value) for key, value in perturbation.items()})
    new_base = type(base)(
        a=base.a,
        k_max=base.k_max,
        sectors=base.sectors,
        twist_params=dict(base.twist_params),
        boundary_params=boundary,
        include_chirality=base.include_chirality,
        operator_level=base.operator_level,
    )
    return FormalKernelOperatorConfig(
        base_config=new_base,
        protected_coordinates=tuple(
            int(index)
            for index in formal_kernel_coordinates(new_base)
        ),
    )


def scan_formal_kernel_sector_coupling(
    k_max_values: Iterable[int] = (4, 6, 8),
    a_values: Iterable[float] = (1.0,),
    perturbations: Iterable[Mapping[str, float]] | None = None,
) -> tuple[FormalKernelSectorCouplingRow, ...]:
    """Return corrected formal-kernel sector-coupling rows.

    This scan is deliberately smaller than the v1.3D uniform scan; v1.3M keeps
    the full convergence scan in ``formal_kernel_convergence``.
    """

    rows: list[FormalKernelSectorCouplingRow] = []
    for k_max in k_max_values:
        for a in a_values:
            base = default_formal_kernel_operator_config(k_max=int(k_max), a=float(a))
            for perturbation in tuple(perturbations or default_sector_coupling_perturbations()):
                rows.append(formal_kernel_sector_coupling_row(_perturbed_formal_config(base, perturbation)))
    return tuple(rows)


def build_formal_kernel_regression_report() -> FormalKernelRegressionReport:
    """Return the v1.3M corrected formal-kernel regression report."""

    old_lower = old_coordinate_first_lower_bound_row()
    new_lower = formal_kernel_lower_bound_row()
    old_sector = old_coordinate_first_sector_coupling_row()
    new_sector = formal_kernel_sector_coupling_row()
    revised = (
        "Coordinate-first protected block `(0,1,2)` is superseded for formal-kernel H_T audits.",
        "Corrected formal-kernel first complement eigenvalue is larger than the legacy coordinate-first value.",
        "Corrected sector-coupling norms are recomputed on the formal complement and are much smaller in the baseline row.",
        "Theorem status remains incomplete because the full action, index theorem, and infinite-basis split remain open.",
    )
    return FormalKernelRegressionReport(
        title="BHSM v1.3M Formal-Kernel H_T Regression Audit",
        lower_bound_rows=(old_lower, new_lower),
        sector_coupling_rows=(old_sector, new_sector),
        corrected_gap_stable=bool(new_lower.passes_mu_h and new_sector.finite_basis_passes),
        previous_conclusions_revised=revised,
        theorem_complete=False,
        assumptions=(
            "The corrected Level 2 operator protects the formal sector-labeled kernel directly.",
            "The natural cutoff Lambda^2=1/(4*pi) is used.",
            "No empirical flavor, CKM, PMNS, prediction-ledger, or residual-audit data enter the regression.",
        ),
        limitations=(
            "All rows are finite-basis Level 2 scaffold rows.",
            "The full H_T theorem remains open.",
            "Coordinate-first conclusions are superseded only where they depended on the old protected block.",
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


def export_formal_kernel_regression_json(path: str | Path) -> None:
    """Export the v1.3M regression report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_formal_kernel_regression_report()), indent=2, sort_keys=True) + "\n")


def export_formal_kernel_regression_markdown(path: str | Path) -> None:
    """Export the v1.3M regression report as Markdown."""

    report = build_formal_kernel_regression_report()
    lines = [
        "# BHSM v1.3M Formal-Kernel H_T Regression Audit",
        "",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Corrected gap stable: `{report.corrected_gap_stable}`",
        "",
        "BHSM v1.3M reruns the H_T gap and bound audits using the corrected formal sector-labeled kernel. It supersedes coordinate-first Level 2 conclusions where those depended on the old protected block.",
        "",
        "## Old vs Corrected Lower-Bound Table",
        "",
        "| Variant | Coordinates | Sectors | Direct lower | Min-max lower | Gershgorin lower | H_T gap | Margin | Passes |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.lower_bound_rows:
        lines.append(
            f"| `{row.variant}` | `{row.protected_coordinates}` | `{row.protected_sectors}` | `{row.direct_finite_spectrum_lower_bound}` | `{row.minmax_complement_lower_bound}` | `{row.gershgorin_lower_bound}` | `{row.ht_gap}` | `{row.margin}` | `{row.passes_mu_h}` |"
        )
    lines.extend(
        [
            "",
            "## Sector-Coupling Regression Table",
            "",
            "| Variant | Coordinates | Spectral norm | Frobenius norm | Row-sum norm | Weyl lower | a_K | Structured lower | Classification | Finite pass |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.sector_coupling_rows:
        lines.append(
            f"| `{row.variant}` | `{row.protected_coordinates}` | `{row.spectral_norm}` | `{row.frobenius_norm}` | `{row.row_sum_norm}` | `{row.weyl_lower_bound}` | `{row.relative_a_k}` | `{row.structured_lower_bound}` | `{row.classification}` | `{row.finite_basis_passes}` |"
        )
    lines.extend(
        [
            "",
            "## Revised Conclusions",
            "",
            *[f"- {item}" for item in report.previous_conclusions_revised],
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in report.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))
