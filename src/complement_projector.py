"""BHSM v1.3G complement-projector scaffold.

The finite projector checks here audit the protected zero-mode coordinate
block used by the Level 2 H_T scaffold. They are compatibility tests, not a
proof of the full infinite-dimensional kernel/complement decomposition.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from ht_operator import default_level2_config
from positivity import complement_projector as orthogonal_complement_projector
from positivity import orthogonal_projector, restrict_to_complement
from sector_coupling_bounds import level2_sector_coupling_dirac_block
from spectral_gap import heat_lift, natural_lambda2
from twisted_dirac import (
    DIRAC_PROXY_LEVEL_2,
    DiracOperatorConfig,
    build_dirac_basis,
    build_level2_dirac_matrix,
    level2_dirac_squared_spectrum,
    zero_mode_subspace,
)


@dataclass(frozen=True)
class ComplementProjectorReport:
    """Finite-basis complement-projector diagnostics."""

    model_level: str
    k_max: int
    a: float
    basis_size: int
    zero_mode_count: int
    p0_idempotent: bool
    p_perp_idempotent: bool
    p0_p_perp_zero: bool
    sector_coupling_vanishes_on_zero_block: bool
    heat_lift_preserves_zero_modes: bool
    complement_excludes_zero_modes: bool
    commutes_with_block_decomposition: bool
    projector_status: str
    theorem_complete: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def protected_zero_mode_basis(config: DiracOperatorConfig | None = None) -> np.ndarray:
    """Return the finite coordinate basis for the protected Level 2 zero block."""

    resolved = default_level2_config() if config is None else config
    basis = build_dirac_basis(
        resolved.k_max,
        sectors=resolved.sectors,
        include_chirality=resolved.include_chirality,
    )
    zero_count = int(resolved.boundary_params.get("zero_mode_count", 3))
    return zero_mode_subspace(basis, index_count=zero_count)


def protected_projector(config: DiracOperatorConfig | None = None) -> np.ndarray:
    """Return P0 for the finite protected coordinate block."""

    return orthogonal_projector(protected_zero_mode_basis(config))


def complement_projector(config: DiracOperatorConfig | None = None) -> np.ndarray:
    """Return P_perp = I - P0 for the finite protected coordinate block."""

    return orthogonal_complement_projector(protected_zero_mode_basis(config))


def restricted_complement_operator(
    operator: np.ndarray,
    config: DiracOperatorConfig | None = None,
) -> np.ndarray:
    """Restrict ``operator`` to the finite protected complement."""

    return restrict_to_complement(operator, protected_zero_mode_basis(config))


def _projector_idempotent(projector: np.ndarray, tol: float = 1e-10) -> bool:
    return bool(np.allclose(projector @ projector, projector, atol=tol))


def _projector_product_zero(left: np.ndarray, right: np.ndarray, tol: float = 1e-10) -> bool:
    return bool(np.allclose(left @ right, np.zeros_like(left), atol=tol))


def _heat_lift_preserves_zero_modes(config: DiracOperatorConfig, tol: float = 1e-12) -> bool:
    spectrum = level2_dirac_squared_spectrum(config)
    zero_count = int(config.boundary_params.get("zero_mode_count", 3))
    zero_values = [float(row["eigenvalue"]) for row in spectrum[:zero_count]]
    lifted = [heat_lift(value, natural_lambda2()) for value in zero_values]
    return bool(all(abs(value) <= tol for value in zero_values) and all(abs(value) <= tol for value in lifted))


def build_complement_projector_report(config: DiracOperatorConfig | None = None) -> ComplementProjectorReport:
    """Return the v1.3G finite complement-projector report."""

    resolved = default_level2_config() if config is None else config
    basis = build_dirac_basis(
        resolved.k_max,
        sectors=resolved.sectors,
        include_chirality=resolved.include_chirality,
    )
    zero_modes = protected_zero_mode_basis(resolved)
    zero_count = int(zero_modes.shape[1])
    p0 = protected_projector(resolved)
    p_perp = complement_projector(resolved)
    sector_block = level2_sector_coupling_dirac_block(resolved)
    dirac = build_level2_dirac_matrix(resolved)
    complement_restricted = restricted_complement_operator(dirac.T @ dirac, resolved)
    sector_zero = bool(
        np.allclose(sector_block[:zero_count, :], 0.0)
        and np.allclose(sector_block[:, :zero_count], 0.0)
    )
    commutator = p0 @ sector_block - sector_block @ p0
    return ComplementProjectorReport(
        model_level=DIRAC_PROXY_LEVEL_2,
        k_max=int(resolved.k_max),
        a=float(resolved.a),
        basis_size=len(basis),
        zero_mode_count=zero_count,
        p0_idempotent=_projector_idempotent(p0),
        p_perp_idempotent=_projector_idempotent(p_perp),
        p0_p_perp_zero=_projector_product_zero(p0, p_perp),
        sector_coupling_vanishes_on_zero_block=sector_zero,
        heat_lift_preserves_zero_modes=_heat_lift_preserves_zero_modes(resolved),
        complement_excludes_zero_modes=bool(complement_restricted.shape[0] == len(basis) - zero_count),
        commutes_with_block_decomposition=bool(np.allclose(commutator, 0.0, atol=1e-10)),
        projector_status="COMPLEMENT_PROJECTOR_SCAFFOLD",
        theorem_complete=False,
        assumptions=(
            "The finite Level 2 protected coordinate block represents the three protected zero modes.",
            "The formal sector-labeled kernel and finite coordinate block must be identified in the complete operator.",
        ),
        limitations=(
            "Finite-basis projector identities do not prove the infinite-dimensional complement split.",
            "The full statement H = ker D_twist plus H_perp remains an index/domain proof obligation.",
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


def export_complement_projector_json(path: str | Path) -> None:
    """Export the finite complement-projector report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_complement_projector_report()), indent=2, sort_keys=True) + "\n")


def export_complement_projector_markdown(path: str | Path) -> None:
    """Export the finite complement-projector report as Markdown."""

    report = build_complement_projector_report()
    lines = [
        "# BHSM v1.3G Complement Projector Report",
        "",
        f"Projector status: `{report.projector_status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "## Finite-Basis Diagnostics",
        "",
        "| Diagnostic | Value |",
        "| --- | --- |",
        f"| Model level | `{report.model_level}` |",
        f"| Basis size | `{report.basis_size}` |",
        f"| Zero-mode count | `{report.zero_mode_count}` |",
        f"| P0 idempotent | `{report.p0_idempotent}` |",
        f"| P_perp idempotent | `{report.p_perp_idempotent}` |",
        f"| P0 P_perp = 0 | `{report.p0_p_perp_zero}` |",
        f"| Sector coupling vanishes on zero block | `{report.sector_coupling_vanishes_on_zero_block}` |",
        f"| Heat lift preserves zero modes | `{report.heat_lift_preserves_zero_modes}` |",
        f"| Complement excludes zero modes | `{report.complement_excludes_zero_modes}` |",
        f"| P0 commutes with sector block | `{report.commutes_with_block_decomposition}` |",
        "",
        "## Assumptions",
        "",
        *[f"- {item}" for item in report.assumptions],
        "",
        "## Limitations",
        "",
        *[f"- {item}" for item in report.limitations],
        "",
    ]
    Path(path).write_text("\n".join(lines))
