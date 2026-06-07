"""BHSM v1.3C structured sector-coupling relative-bound audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

from ht_operator import alpha_scaled_a, default_level2_config
from operator_norm_bounds import operator_norm_bounds, row_sum_norm, spectral_norm
from positivity import min_eigenvalue, restrict_to_complement
from relative_bound_program import (
    RelativeBoundCertificate,
    rayleigh_relative_bound,
    structured_relative_certificate,
)
from sector_coupling_bounds import (
    config_without_sector_coupling,
    default_sector_coupling_perturbations,
    level2_sector_coupling_dirac_block,
    level2_sector_coupling_squared_perturbation,
)
from spectral_bounds import required_dirac_lower_bound
from spectral_gap import MU_H, natural_lambda2
from twisted_dirac import (
    DIRAC_PROXY_LEVEL_2,
    DiracMode,
    DiracOperatorConfig,
    build_dirac_basis,
    build_level2_dirac_matrix,
    zero_mode_subspace,
)


STRUCTURED_BOUND_STATUSES = (
    "STRUCTURED_BOUND_SUFFICIENT",
    "RELATIVE_BOUND_CANDIDATE",
    "FINITE_BASIS_ONLY",
    "FAILS_BOUND",
    "OPEN",
)


@dataclass(frozen=True)
class StructuredCouplingRule:
    """Structural rule satisfied by the Level 2 sector-coupling block."""

    id: str
    statement: str
    value: bool | str | int | float
    evidence: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class SectorSelectionRule:
    """Selection rule for one nonzero sector-coupling entry."""

    source_sector: str
    target_sector: str
    preserves_k: bool
    preserves_j: bool
    preserves_q: bool
    preserves_chirality: bool
    same_sector: bool
    nonzero_count: int
    max_abs_coupling: float


@dataclass(frozen=True)
class StructuredBoundReport:
    """Complete v1.3C structured sector-bound report."""

    model_level: str
    k_max: int
    a: float
    basis_size: int
    zero_mode_count: int
    structural_rules: tuple[StructuredCouplingRule, ...]
    sector_selection_rules: tuple[SectorSelectionRule, ...]
    block_norm_table: tuple[dict[str, object], ...]
    banded_row_sum_bound: float
    schur_two_block_bound: float
    decay_fit: dict[str, float | str]
    relative_certificate: RelativeBoundCertificate
    baseline_classification: str
    robustness_scan: tuple[dict[str, object], ...]
    all_structured_bounds_sufficient: bool
    all_finite_basis_cases_pass: bool
    finite_rank_certificate: str
    banded_support_certificate: str
    compactness_diagnostic: str
    theorem_complete: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def _zero_modes_for_config(config: DiracOperatorConfig) -> np.ndarray:
    basis = build_dirac_basis(config.k_max, sectors=config.sectors, include_chirality=config.include_chirality)
    zero_count = int(config.boundary_params.get("zero_mode_count", 3))
    return zero_mode_subspace(basis, index_count=zero_count)


def _restricted_base_full_perturbation(config: DiracOperatorConfig) -> dict[str, np.ndarray]:
    zero_modes = _zero_modes_for_config(config)
    full = build_level2_dirac_matrix(config)
    base = build_level2_dirac_matrix(config_without_sector_coupling(config))
    full_sq = full.T @ full
    base_sq = base.T @ base
    perturb = full_sq - base_sq
    return {
        "zero_modes": zero_modes,
        "base_sq": base_sq,
        "full_sq": full_sq,
        "perturb": perturb,
        "restricted_base": restrict_to_complement(base_sq, zero_modes),
        "restricted_full": restrict_to_complement(full_sq, zero_modes),
        "restricted_perturb": restrict_to_complement(perturb, zero_modes),
    }


def sector_coupling_selection_rules(config: DiracOperatorConfig | None = None) -> tuple[SectorSelectionRule, ...]:
    """Return structural sector-pair selection rules for Dirac-level coupling."""

    resolved = default_level2_config() if config is None else config
    basis = build_dirac_basis(resolved.k_max, sectors=resolved.sectors, include_chirality=resolved.include_chirality)
    block = level2_sector_coupling_dirac_block(resolved)
    rows: dict[tuple[str, str], list[tuple[DiracMode, DiracMode, float]]] = {}
    for i, mode_i in enumerate(basis):
        for j, mode_j in enumerate(basis):
            value = float(block[i, j])
            if abs(value) <= 1e-14:
                continue
            key = (mode_i.sector, mode_j.sector)
            rows.setdefault(key, []).append((mode_i, mode_j, value))
    results = []
    for (source, target), entries in sorted(rows.items()):
        results.append(
            SectorSelectionRule(
                source_sector=source,
                target_sector=target,
                preserves_k=all(left.k == right.k for left, right, _ in entries),
                preserves_j=all(left.j == right.j for left, right, _ in entries),
                preserves_q=all(left.q == right.q for left, right, _ in entries),
                preserves_chirality=all(left.chirality == right.chirality for left, right, _ in entries),
                same_sector=source == target,
                nonzero_count=len(entries),
                max_abs_coupling=max(abs(value) for _, _, value in entries),
            )
        )
    return tuple(results)


def _block_matrix(matrix: np.ndarray, basis: list[DiracMode], source: str, target: str) -> np.ndarray:
    block = np.zeros_like(matrix, dtype=float)
    source_indices = [idx for idx, mode in enumerate(basis) if mode.sector == source]
    target_indices = [idx for idx, mode in enumerate(basis) if mode.sector == target]
    for i in source_indices:
        for j in target_indices:
            block[i, j] = matrix[i, j]
    return block


def sector_block_decomposition(
    matrix: np.ndarray,
    config: DiracOperatorConfig | None = None,
) -> dict[tuple[str, str], np.ndarray]:
    """Return sector-pair matrix blocks whose sum reconstructs ``matrix``."""

    resolved = default_level2_config() if config is None else config
    basis = build_dirac_basis(resolved.k_max, sectors=resolved.sectors, include_chirality=resolved.include_chirality)
    sectors = tuple(resolved.sectors)
    return {
        (source, target): _block_matrix(np.asarray(matrix, dtype=float), basis, source, target)
        for source in sectors
        for target in sectors
    }


def block_norm_table(config: DiracOperatorConfig | None = None) -> tuple[dict[str, object], ...]:
    """Return sector-pair block norms for the D^dagger D sector perturbation."""

    resolved = default_level2_config() if config is None else config
    perturb = level2_sector_coupling_squared_perturbation(resolved)
    blocks = sector_block_decomposition(perturb, resolved)
    rows = []
    for (source, target), block in sorted(blocks.items()):
        nonzero = int(np.count_nonzero(np.abs(block) > 1e-14))
        rows.append(
            {
                "source_sector": source,
                "target_sector": target,
                "nonzero_count": nonzero,
                "spectral_norm": spectral_norm(block) if nonzero else 0.0,
                "row_sum_norm": row_sum_norm(block) if nonzero else 0.0,
                "same_sector": source == target,
            }
        )
    return tuple(rows)


def structured_coupling_rules(config: DiracOperatorConfig | None = None) -> tuple[StructuredCouplingRule, ...]:
    """Return structural diagnostics for the Level 2 sector-coupling block."""

    resolved = default_level2_config() if config is None else config
    basis = build_dirac_basis(resolved.k_max, sectors=resolved.sectors, include_chirality=resolved.include_chirality)
    dirac_block = level2_sector_coupling_dirac_block(resolved)
    squared_perturb = level2_sector_coupling_squared_perturbation(resolved)
    zero_count = int(resolved.boundary_params.get("zero_mode_count", 3))
    zero_coupling = bool(
        np.allclose(dirac_block[:zero_count, :], 0.0)
        and np.allclose(dirac_block[:, :zero_count], 0.0)
        and np.allclose(squared_perturb[:zero_count, :], 0.0)
        and np.allclose(squared_perturb[:, :zero_count], 0.0)
    )
    nonzero_entries = int(np.count_nonzero(np.abs(dirac_block) > 1e-14))
    total_entries = int(dirac_block.size)
    sparsity_fraction = 1.0 - nonzero_entries / total_entries if total_entries else 1.0
    selection = sector_coupling_selection_rules(resolved)
    preserves_q = all(rule.preserves_q for rule in selection)
    preserves_j = all(rule.preserves_j for rule in selection)
    preserves_chirality = all(rule.preserves_chirality for rule in selection)
    same_sector_dirac = any(rule.same_sector for rule in selection)
    return (
        StructuredCouplingRule(
            id="sector_pairs",
            statement="Dirac-level coupling connects distinct charged sectors only.",
            value=not same_sector_dirac,
            evidence=(f"Nonzero sector-pair rules: {len(selection)}.",),
            limitations=("After squaring, D^dagger D includes same-sector diagonal contributions.",),
        ),
        StructuredCouplingRule(
            id="preserves_mode_labels",
            statement="Dirac-level coupling preserves k, j, q, and chirality.",
            value=bool(preserves_q and preserves_j and preserves_chirality),
            evidence=("Every nonzero Dirac-level sector pair has matching k, j, q, and chirality.",),
            limitations=("This is a Level 2 selection rule, not a full action theorem.",),
        ),
        StructuredCouplingRule(
            id="sparse_support",
            statement="Sector coupling is sparse in the finite Dirac basis.",
            value=round(sparsity_fraction, 12),
            evidence=(f"Dirac-level nonzero entries: {nonzero_entries} of {total_entries}.",),
            limitations=("Sparsity is basis-dependent.",),
        ),
        StructuredCouplingRule(
            id="zero_mode_vanishes",
            statement="Sector coupling vanishes on the protected zero-mode coordinate block.",
            value=zero_coupling,
            evidence=(f"First {zero_count} rows and columns vanish in both Dirac-level and squared perturbation blocks.",),
            limitations=("The protected zero-mode block is finite-basis inserted/projected.",),
        ),
        StructuredCouplingRule(
            id="banded_support",
            statement="Coupling is block-banded after reordering by (k,j,chirality), but not in the raw sector-major basis.",
            value="mode-block-banded",
            evidence=("Nonzero entries preserve k, j, and chirality while changing sector.",),
            limitations=("The current matrix storage order is sector-major.",),
        ),
        StructuredCouplingRule(
            id="finite_rank_status",
            statement="Coupling is finite rank at fixed k_max but rank grows with basis size.",
            value="finite-basis finite-rank; infinite-basis finite-rank not certified",
            evidence=(f"Fixed basis size: {len(basis)}.",),
            limitations=("No k_max-uniform finite-rank certificate is available.",),
        ),
    )


def decay_fit_diagnostic(config: DiracOperatorConfig | None = None) -> dict[str, float | str]:
    """Fit coupling magnitude against diagonal action scale as a diagnostic only."""

    resolved = default_level2_config() if config is None else config
    basis = build_dirac_basis(resolved.k_max, sectors=resolved.sectors, include_chirality=resolved.include_chirality)
    base = build_level2_dirac_matrix(config_without_sector_coupling(resolved))
    base_sq = base.T @ base
    dirac_block = level2_sector_coupling_dirac_block(resolved)
    x_values = []
    y_values = []
    for i, _ in enumerate(basis):
        for j, _ in enumerate(basis):
            value = abs(float(dirac_block[i, j]))
            if value <= 1e-14:
                continue
            scale = max(float(base_sq[i, i]), float(base_sq[j, j]), 1e-12)
            x_values.append(np.log(scale))
            y_values.append(np.log(value))
    if len(x_values) < 2:
        return {"slope": 0.0, "intercept": 0.0, "status": "INSUFFICIENT_DATA"}
    slope, intercept = np.polyfit(np.asarray(x_values), np.asarray(y_values), deg=1)
    status = "DECAY_CANDIDATE" if slope < -0.25 else "NO_STRONG_DECAY"
    return {"slope": float(slope), "intercept": float(intercept), "status": status}


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


def structured_relative_bound_certificate(
    config: DiracOperatorConfig | None = None,
    lambda2: float | None = None,
) -> RelativeBoundCertificate:
    """Return the structured relative-bound certificate for one config."""

    resolved = default_level2_config() if config is None else config
    resolved_lambda2 = natural_lambda2() if lambda2 is None else float(lambda2)
    required = required_dirac_lower_bound(resolved_lambda2, MU_H)
    operators = _restricted_base_full_perturbation(resolved)
    base = operators["restricted_base"]
    full = operators["restricted_full"]
    perturb = operators["restricted_perturb"]
    base_lower = min_eigenvalue(base)
    full_lower = min_eigenvalue(full)
    a_k = rayleigh_relative_bound(base, perturb)
    return structured_relative_certificate(
        a_k=a_k,
        base_lower_bound=base_lower,
        full_lower_bound=full_lower,
        required_dirac_lower_bound=required,
        finite_basis_only=True,
    )


def scan_structured_sector_bounds(
    k_max_values: Iterable[int],
    a_values: Iterable[float],
    perturbations: Iterable[Mapping[str, float]] | None = None,
    lambda2: float | None = None,
) -> list[dict[str, object]]:
    """Scan structured relative-bound certificates across Level 2 controls."""

    rows: list[dict[str, object]] = []
    for k_max in k_max_values:
        for a in a_values:
            base_config = default_level2_config(k_max=int(k_max), a=float(a))
            for perturbation in tuple(perturbations or default_sector_coupling_perturbations()):
                config = _perturbed_config(base_config, perturbation)
                certificate = structured_relative_bound_certificate(config, lambda2=lambda2)
                rows.append(
                    {
                        "k_max": int(k_max),
                        "a": float(a),
                        "basis_size": len(build_dirac_basis(config.k_max, sectors=config.sectors, include_chirality=config.include_chirality)),
                        "zero_mode_count": int(config.boundary_params.get("zero_mode_count", 3)),
                        "sector_coupling": float(config.boundary_params.get("sector_coupling", 0.0)),
                        "offdiag_boundary_coupling": float(config.boundary_params.get("offdiag_boundary_coupling", 0.0)),
                        "a_k": certificate.a_k,
                        "structured_lower_bound": certificate.structured_lower_bound,
                        "full_lower_bound": certificate.full_lower_bound,
                        "required_dirac_lower_bound": certificate.required_dirac_lower_bound,
                        "sufficient": certificate.sufficient,
                        "classification": certificate.classification,
                        "theorem_complete": False,
                    }
                )
    return rows


def default_structured_sector_scan() -> list[dict[str, object]]:
    """Return the required v1.3C structured robustness scan."""

    return scan_structured_sector_bounds(
        k_max_values=(4, 6, 8, 10, 12, 16, 20),
        a_values=(alpha_scaled_a(), 1.0, 0.573),
        perturbations=default_sector_coupling_perturbations(),
        lambda2=natural_lambda2(),
    )


def build_structured_sector_bound_report(config: DiracOperatorConfig | None = None) -> StructuredBoundReport:
    """Build the v1.3C structured sector-bound report."""

    resolved = default_level2_config() if config is None else config
    certificate = structured_relative_bound_certificate(resolved, lambda2=natural_lambda2())
    scan = tuple(default_structured_sector_scan())
    blocks = block_norm_table(resolved)
    banded_row = max(float(row["row_sum_norm"]) for row in blocks)
    offdiag_blocks = [row for row in blocks if not bool(row["same_sector"])]
    schur_bound = max(float(row["spectral_norm"]) for row in offdiag_blocks) if offdiag_blocks else 0.0
    finite_basis_passes = all(float(row["full_lower_bound"]) >= float(row["required_dirac_lower_bound"]) for row in scan)
    return StructuredBoundReport(
        model_level=DIRAC_PROXY_LEVEL_2,
        k_max=int(resolved.k_max),
        a=float(resolved.a),
        basis_size=len(build_dirac_basis(resolved.k_max, sectors=resolved.sectors, include_chirality=resolved.include_chirality)),
        zero_mode_count=int(resolved.boundary_params.get("zero_mode_count", 3)),
        structural_rules=structured_coupling_rules(resolved),
        sector_selection_rules=sector_coupling_selection_rules(resolved),
        block_norm_table=blocks,
        banded_row_sum_bound=float(banded_row),
        schur_two_block_bound=float(schur_bound),
        decay_fit=decay_fit_diagnostic(resolved),
        relative_certificate=certificate,
        baseline_classification=certificate.classification,
        robustness_scan=scan,
        all_structured_bounds_sufficient=all(bool(row["sufficient"]) for row in scan),
        all_finite_basis_cases_pass=finite_basis_passes,
        finite_rank_certificate="finite rank at fixed k_max; not finite-rank certified in the infinite-basis limit",
        banded_support_certificate="banded after mode-block ordering because nonzero Dirac couplings preserve k, j, q, and chirality",
        compactness_diagnostic="relative-bound candidate only; no compactness theorem because baseline coupling does not strongly decay with action",
        theorem_complete=False,
        assumptions=(
            "Structural rules are read from the Level 2 sector-coupling scaffold.",
            "Relative bounds are evaluated on the finite protected complement.",
            "No empirical mass, CKM, PMNS, residual, or prediction-ledger data are used.",
        ),
        limitations=(
            "The structured bound is finite-basis unless made uniform in k_max.",
            "The full zero-mode/complement proof remains open.",
            "This audit does not prove the full H_T theorem.",
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


def export_structured_sector_bound_json(path: str | Path) -> None:
    """Export the structured sector-bound report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_structured_sector_bound_report()), indent=2, sort_keys=True) + "\n")


def export_structured_sector_bound_markdown(path: str | Path) -> None:
    """Export the structured sector-bound report as Markdown."""

    report = build_structured_sector_bound_report()
    lines = [
        "# BHSM v1.3C Structured Sector-Coupling Bound Report",
        "",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Baseline classification: `{report.baseline_classification}`",
        "",
        "BHSM v1.3C investigates structured relative bounds for the Level 2 sector-coupling block. It does not prove the full H_T theorem unless the zero-mode/complement and infinite-basis limits are also certified.",
        "",
        "## Structural Table",
        "",
        "| Rule | Value | Evidence |",
        "| --- | --- | --- |",
    ]
    for rule in report.structural_rules:
        lines.append(f"| `{rule.id}` | `{rule.value}` | {' '.join(rule.evidence)} |")
    lines.extend(
        [
            "",
            "## Sector Selection Rules",
            "",
            "| Source | Target | Preserves q | Preserves j | Preserves chirality | Nonzero count | Max coupling |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for rule in report.sector_selection_rules:
        lines.append(
            f"| `{rule.source_sector}` | `{rule.target_sector}` | `{rule.preserves_q}` | `{rule.preserves_j}` | `{rule.preserves_chirality}` | `{rule.nonzero_count}` | `{rule.max_abs_coupling}` |"
        )
    lines.extend(
        [
            "",
            "## Block-Wise Norm Table",
            "",
            "| Source | Target | Nonzero count | Spectral norm | Row-sum norm | Same sector |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.block_norm_table:
        lines.append(
            "| `{source_sector}` | `{target_sector}` | `{nonzero_count}` | `{spectral_norm}` | `{row_sum_norm}` | `{same_sector}` |".format(
                **row
            )
        )
    cert = report.relative_certificate
    lines.extend(
        [
            "",
            "## Relative-Bound Certificate",
            "",
            "| Quantity | Value |",
            "| --- | --- |",
            f"| a_K | `{cert.a_k}` |",
            f"| b_K | `{cert.b_k}` |",
            f"| Structured lower bound | `{cert.structured_lower_bound}` |",
            f"| Required Dirac lower bound | `{cert.required_dirac_lower_bound}` |",
            f"| Full finite-basis lower bound | `{cert.full_lower_bound}` |",
            f"| Sufficient | `{cert.sufficient}` |",
            f"| Classification | `{cert.classification}` |",
            "",
            "## Robustness Summary",
            "",
            f"- Cases: `{len(report.robustness_scan)}`",
            f"- All structured bounds sufficient: `{report.all_structured_bounds_sufficient}`",
            f"- All finite-basis cases pass: `{report.all_finite_basis_cases_pass}`",
            f"- Finite-rank certificate: {report.finite_rank_certificate}",
            f"- Banded-support certificate: {report.banded_support_certificate}",
            f"- Compactness diagnostic: {report.compactness_diagnostic}",
            f"- Decay-fit status: `{report.decay_fit['status']}`",
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in report.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))
