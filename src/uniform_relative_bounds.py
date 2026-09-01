"""BHSM v1.3D uniform-in-k_max relative-bound audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

from ht_operator import alpha_scaled_a, default_level2_config
from operator_norm_bounds import row_sum_norm, spectral_norm
from positivity import restrict_to_complement
from sector_coupling_bounds import (
    config_without_sector_coupling,
    default_sector_coupling_perturbations,
    level2_sector_coupling_dirac_block,
    level2_sector_coupling_squared_perturbation,
)
from spectral_gap import natural_lambda2
from structured_sector_bounds import block_norm_table, structured_relative_bound_certificate
from twisted_dirac import DiracMode, DiracOperatorConfig, build_dirac_basis, build_level2_dirac_matrix, zero_mode_subspace


UNIFORM_BOUND_STATUSES = (
    "UNIFORM_BOUND_SUPPORTED",
    "UNIFORM_BOUND_CANDIDATE",
    "FINITE_BASIS_ONLY",
    "FAILS_UNIFORM_SCAN",
    "OPEN",
)

DEFAULT_K_MAX_VALUES = (4, 6, 8, 10, 12, 16, 20, 24, 32)
_DEFAULT_REPORT_CACHE: "UniformRelativeBoundReport | None" = None


@dataclass(frozen=True)
class UniformBoundRow:
    """One row in a uniform-in-k_max relative-bound scan."""

    k_max: int
    a: float
    perturbation_label: str
    basis_size: int
    sector_coupling_sparsity: float
    band_width: int
    spectral_norm: float
    row_sum_norm: float
    max_block_norm: float
    a_k: float
    b_k: float
    structured_lower_bound: float
    finite_basis_lower_bound: float
    required_dirac_lower_bound: float
    passes_required_bound: bool
    classification: str
    theorem_complete: bool


@dataclass(frozen=True)
class UniformBoundTrend:
    """Trend summary for one scanned quantity."""

    quantity: str
    status: str
    first_value: float
    last_value: float
    min_value: float
    max_value: float
    slope_per_k: float
    notes: tuple[str, ...]


@dataclass(frozen=True)
class UniformRelativeBoundReport:
    """Complete v1.3D uniform relative-bound report."""

    title: str
    rows: tuple[UniformBoundRow, ...]
    trends: tuple[UniformBoundTrend, ...]
    classification: str
    theorem_complete: bool
    all_rows_pass: bool
    all_b_k_zero: bool
    max_a_k: float
    min_structured_lower_bound: float
    min_finite_basis_lower_bound: float
    max_band_width: int
    sparsity_trend: str
    blockers_to_infinite_basis_upgrade: tuple[str, ...]
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def _perturbed_config(config: DiracOperatorConfig, perturbation: Mapping[str, float]) -> DiracOperatorConfig:
    boundary = dict(config.boundary_params)
    boundary.update({key: float(value) for key, value in perturbation.items()})
    return DiracOperatorConfig(
        a=config.a,
        k_max=config.k_max,
        sectors=config.sectors,
        twist_params=dict(config.twist_params),
        boundary_params=boundary,
        include_chirality=config.include_chirality,
        operator_level=config.operator_level,
    )


def perturbation_label(perturbation: Mapping[str, float]) -> str:
    """Return a stable label for a sector-coupling perturbation."""

    if not perturbation:
        return "baseline"
    return ",".join(f"{key}={value}" for key, value in sorted(perturbation.items()))


def _mode_block_order(basis: list[DiracMode]) -> dict[int, int]:
    order = sorted(
        range(len(basis)),
        key=lambda idx: (
            basis[idx].k,
            basis[idx].j,
            basis[idx].chirality,
            basis[idx].sector,
            basis[idx].degeneracy,
        ),
    )
    return {old: new for new, old in enumerate(order)}


def mode_block_band_width(config: DiracOperatorConfig) -> int:
    """Return bandwidth after reordering by (k,j,chirality,sector)."""

    basis = build_dirac_basis(config.k_max, sectors=config.sectors, include_chirality=config.include_chirality)
    reorder = _mode_block_order(basis)
    block = level2_sector_coupling_dirac_block(config)
    nonzero = np.argwhere(np.abs(block) > 1e-14)
    if nonzero.size == 0:
        return 0
    return int(max(abs(reorder[int(i)] - reorder[int(j)]) for i, j in nonzero))


def sector_coupling_sparsity(config: DiracOperatorConfig) -> float:
    """Return finite-basis sparsity fraction for the Dirac-level sector block."""

    block = level2_sector_coupling_dirac_block(config)
    total = int(block.size)
    if total == 0:
        return 1.0
    nonzero = int(np.count_nonzero(np.abs(block) > 1e-14))
    return float(1.0 - nonzero / total)


def _zero_modes_for_config(config: DiracOperatorConfig) -> np.ndarray:
    basis = build_dirac_basis(config.k_max, sectors=config.sectors, include_chirality=config.include_chirality)
    return zero_mode_subspace(basis, index_count=int(config.boundary_params.get("zero_mode_count", 3)))


def _restricted_sector_perturbation(config: DiracOperatorConfig) -> np.ndarray:
    zero_modes = _zero_modes_for_config(config)
    perturbation = level2_sector_coupling_squared_perturbation(config)
    return restrict_to_complement(perturbation, zero_modes)


def uniform_bound_row(
    config: DiracOperatorConfig,
    perturbation: Mapping[str, float] | None = None,
    lambda2: float | None = None,
) -> UniformBoundRow:
    """Return one uniform-bound scan row."""

    perturbed = _perturbed_config(config, perturbation or {})
    certificate = structured_relative_bound_certificate(perturbed, lambda2=lambda2)
    restricted_k = _restricted_sector_perturbation(perturbed)
    blocks = block_norm_table(perturbed)
    max_block = max(float(row["spectral_norm"]) for row in blocks)
    return UniformBoundRow(
        k_max=int(perturbed.k_max),
        a=float(perturbed.a),
        perturbation_label=perturbation_label(perturbation or {}),
        basis_size=len(build_dirac_basis(perturbed.k_max, sectors=perturbed.sectors, include_chirality=perturbed.include_chirality)),
        sector_coupling_sparsity=sector_coupling_sparsity(perturbed),
        band_width=mode_block_band_width(perturbed),
        spectral_norm=spectral_norm(restricted_k),
        row_sum_norm=row_sum_norm(restricted_k),
        max_block_norm=max_block,
        a_k=certificate.a_k,
        b_k=certificate.b_k,
        structured_lower_bound=certificate.structured_lower_bound,
        finite_basis_lower_bound=certificate.full_lower_bound,
        required_dirac_lower_bound=certificate.required_dirac_lower_bound,
        passes_required_bound=bool(certificate.structured_lower_bound >= certificate.required_dirac_lower_bound),
        classification=certificate.classification,
        theorem_complete=False,
    )


def scan_uniform_relative_bounds(
    k_max_values: Iterable[int] = DEFAULT_K_MAX_VALUES,
    a_values: Iterable[float] = (),
    perturbations: Iterable[Mapping[str, float]] | None = None,
    lambda2: float | None = None,
) -> list[UniformBoundRow]:
    """Run the v1.3D uniform-in-k_max scan."""

    anisotropies = tuple(a_values) if tuple(a_values) else (alpha_scaled_a(), 1.0, 0.573)
    rows: list[UniformBoundRow] = []
    for k_max in k_max_values:
        for a in anisotropies:
            base = default_level2_config(k_max=int(k_max), a=float(a))
            for perturbation in tuple(perturbations or default_sector_coupling_perturbations()):
                rows.append(uniform_bound_row(base, perturbation, lambda2=lambda2 or natural_lambda2()))
    return rows


def _linear_slope(x_values: list[float], y_values: list[float]) -> float:
    if len(x_values) < 2:
        return 0.0
    slope, _ = np.polyfit(np.asarray(x_values), np.asarray(y_values), deg=1)
    return float(slope)


def _trend_status(first: float, last: float, slope: float, *, tol: float = 1e-10) -> str:
    if abs(last - first) <= tol and abs(slope) <= tol:
        return "stable"
    if last > first and slope > tol:
        return "increasing"
    if last < first and slope < -tol:
        return "decreasing"
    return "mixed"


def _trend(quantity: str, rows: list[UniformBoundRow], attr: str) -> UniformBoundTrend:
    ordered = sorted(rows, key=lambda row: row.k_max)
    x_values = [float(row.k_max) for row in ordered]
    y_values = [float(getattr(row, attr)) for row in ordered]
    slope = _linear_slope(x_values, y_values)
    first = y_values[0]
    last = y_values[-1]
    status = _trend_status(first, last, slope)
    return UniformBoundTrend(
        quantity=quantity,
        status=status,
        first_value=float(first),
        last_value=float(last),
        min_value=float(min(y_values)),
        max_value=float(max(y_values)),
        slope_per_k=slope,
        notes=(f"Trend computed over {len(ordered)} finite k_max rows.",),
    )


def analyze_uniform_trends(rows: Iterable[UniformBoundRow]) -> tuple[UniformBoundTrend, ...]:
    """Return trend summaries for the baseline canonical scan rows."""

    row_list = list(rows)
    canonical_a = alpha_scaled_a()
    baseline = [
        row
        for row in row_list
        if abs(row.a - canonical_a) < 1e-12 and row.perturbation_label == "baseline"
    ]
    if not baseline:
        baseline = row_list
    return (
        _trend("a_K", baseline, "a_k"),
        _trend("b_K", baseline, "b_k"),
        _trend("sparsity", baseline, "sector_coupling_sparsity"),
        _trend("band_width", baseline, "band_width"),
        _trend("structured_lower_bound", baseline, "structured_lower_bound"),
        _trend("finite_basis_lower_bound", baseline, "finite_basis_lower_bound"),
    )


def classify_uniform_scan(rows: Iterable[UniformBoundRow]) -> str:
    """Classify finite uniform-scan evidence without upgrading to theorem."""

    row_list = list(rows)
    if not row_list:
        return "OPEN"
    if any(not row.passes_required_bound for row in row_list):
        return "FAILS_UNIFORM_SCAN"
    if any(row.classification == "FINITE_BASIS_ONLY" for row in row_list):
        return "FINITE_BASIS_ONLY"
    return "UNIFORM_BOUND_CANDIDATE"


def build_uniform_relative_bound_report(
    k_max_values: Iterable[int] = DEFAULT_K_MAX_VALUES,
    a_values: Iterable[float] = (),
    perturbations: Iterable[Mapping[str, float]] | None = None,
) -> UniformRelativeBoundReport:
    """Build the v1.3D uniform-in-k_max relative-bound report."""

    global _DEFAULT_REPORT_CACHE
    k_tuple = tuple(k_max_values)
    a_tuple = tuple(a_values)
    is_default = k_tuple == DEFAULT_K_MAX_VALUES and not a_tuple and perturbations is None
    if is_default and _DEFAULT_REPORT_CACHE is not None:
        return _DEFAULT_REPORT_CACHE

    rows = tuple(scan_uniform_relative_bounds(k_tuple, a_tuple, perturbations, lambda2=natural_lambda2()))
    trends = analyze_uniform_trends(rows)
    all_pass = all(row.passes_required_bound for row in rows)
    all_b_zero = all(abs(row.b_k) <= 1e-15 for row in rows)
    report = UniformRelativeBoundReport(
        title="BHSM v1.3D Uniform Relative-Bound Audit",
        rows=rows,
        trends=trends,
        classification=classify_uniform_scan(rows),
        theorem_complete=False,
        all_rows_pass=all_pass,
        all_b_k_zero=all_b_zero,
        max_a_k=max(float(row.a_k) for row in rows),
        min_structured_lower_bound=min(float(row.structured_lower_bound) for row in rows),
        min_finite_basis_lower_bound=min(float(row.finite_basis_lower_bound) for row in rows),
        max_band_width=max(int(row.band_width) for row in rows),
        sparsity_trend=next(trend.status for trend in trends if trend.quantity == "sparsity"),
        blockers_to_infinite_basis_upgrade=(
            "Finite scan does not prove a k_max-uniform analytic estimate.",
            "Zero-mode/complement separation remains finite-basis inserted/projected.",
            "Sector-coupling rank grows with k_max, so compactness is not certified.",
            "Mode-block bandwidth remains bounded in this scaffold but still needs an action-level infinite-basis proof.",
        ),
        assumptions=(
            "The Level 2 sector-coupling selection rules are fixed before the scan.",
            "The natural cutoff Lambda^2 = 1/(4*pi) is used.",
            "No empirical mass, CKM, PMNS, prediction-ledger, or residual data enter the audit.",
        ),
        limitations=(
            "UNIFORM_BOUND_CANDIDATE is finite truncation evidence, not a proof of the infinite-basis theorem.",
            "The full H_T theorem remains open until zero-mode/complement and infinite-basis limits are certified.",
        ),
    )
    if is_default:
        _DEFAULT_REPORT_CACHE = report
    return report


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


def export_uniform_relative_bound_json(path: str | Path) -> None:
    """Export the v1.3D uniform relative-bound report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_uniform_relative_bound_report()), indent=2, sort_keys=True) + "\n")


def export_uniform_relative_bound_markdown(path: str | Path) -> None:
    """Export the v1.3D uniform relative-bound report as Markdown."""

    report = build_uniform_relative_bound_report()
    lines = [
        "# BHSM v1.3D Uniform Relative-Bound Audit",
        "",
        f"Classification: `{report.classification}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "BHSM v1.3D tests whether the structured sector-coupling relative bound is uniform across increasing finite-basis truncations. It does not prove the full H_T theorem unless the zero-mode/complement split and infinite-basis limit are certified.",
        "",
        "## Uniform Scan Table",
        "",
        "| k_max | a | perturbation | basis | sparsity | band width | spectral norm | row-sum norm | max block norm | a_K | b_K | structured lower | finite lower | passes |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.rows:
        lines.append(
            f"| `{row.k_max}` | `{row.a}` | `{row.perturbation_label}` | `{row.basis_size}` | `{row.sector_coupling_sparsity}` | `{row.band_width}` | `{row.spectral_norm}` | `{row.row_sum_norm}` | `{row.max_block_norm}` | `{row.a_k}` | `{row.b_k}` | `{row.structured_lower_bound}` | `{row.finite_basis_lower_bound}` | `{row.passes_required_bound}` |"
        )
    lines.extend(
        [
            "",
            "## Trend Summary",
            "",
            "| Quantity | Status | First | Last | Min | Max | Slope per k |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for trend in report.trends:
        lines.append(
            f"| `{trend.quantity}` | `{trend.status}` | `{trend.first_value}` | `{trend.last_value}` | `{trend.min_value}` | `{trend.max_value}` | `{trend.slope_per_k}` |"
        )
    lines.extend(
        [
            "",
            "## Classification",
            "",
            f"- Uniform scan classification: `{report.classification}`",
            f"- All rows pass required bound: `{report.all_rows_pass}`",
            f"- All b_K values remain zero: `{report.all_b_k_zero}`",
            f"- Max a_K: `{report.max_a_k}`",
            f"- Min structured lower bound: `{report.min_structured_lower_bound}`",
            f"- Min finite-basis lower bound: `{report.min_finite_basis_lower_bound}`",
            f"- Max mode-block bandwidth: `{report.max_band_width}`",
            "",
            "## Blockers To Infinite-Basis Upgrade",
            "",
            *[f"- {item}" for item in report.blockers_to_infinite_basis_upgrade],
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in report.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))
