"""BHSM v1.3O symbolic formal-kernel operator scaffold.

The objects here give a coordinate-free statement of the corrected
DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL decomposition, while retaining finite-basis
checks as evidence rather than theorem completion.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from coordinate_free_subspace import (
    BASIS_REALIZED,
    COORDINATE_FREE_SCAFFOLD,
    FINITE_BASIS_VERIFIED,
    FULL_OPERATOR_PROVEN,
    SEMI_ANALYTIC_BOUND,
    BasisRealizationMap,
    CoordinateFreeProjector,
    FormalKernelSubspace,
    basis_realization_map,
    coordinate_free_projector,
    formal_kernel_subspace,
)
from formal_kernel_operator import DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL
from semi_analytic_complement_bound import SemiAnalyticComplementBound, build_semi_analytic_complement_bound
from spectral_bounds import BoundResult, complement_gap_bound, heat_lift_lower_bound
from spectral_gap import MU_H, natural_lambda2


@dataclass(frozen=True)
class SymbolicOperatorTerm:
    """One symbolic term in the formal-kernel Level 2 H_T scaffold."""

    id: str
    expression: str
    classification: str
    vanishes_on_k_formal: bool
    preserves_k_formal: bool
    acts_only_on_h_perp: bool
    can_lower_complement_gap: bool
    lower_bound_method: str
    status: str
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class SymbolicComplementBound:
    """Coordinate-free sufficient lower-bound statement with finite realization evidence."""

    model_level: str
    protected_subspace: str
    complement_subspace: str
    diagonal_complement_lower_bound: float
    structured_relative_lower_bound: float
    exact_finite_lower_bound: float
    required_dirac_lower_bound: float
    lambda2: float
    mu_h: float
    heat_lift_lower_bound: float
    heat_gap_margin: float
    clears_required_dirac_bound: bool
    clears_mu_h_after_heat_lift: bool
    psd_profile_assumption: str
    implication: str
    status: str
    theorem_complete: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class SymbolicFormalKernelReport:
    """Complete v1.3O symbolic formal-kernel operator report."""

    title: str
    model_level: str
    formal_kernel: FormalKernelSubspace
    coordinate_free_projector: CoordinateFreeProjector
    basis_realization: BasisRealizationMap
    operator_expression: str
    terms: tuple[SymbolicOperatorTerm, ...]
    complement_bound: SymbolicComplementBound
    theorem_complete: bool
    correct_claim: str
    limitations: tuple[str, ...]


def symbolic_operator_terms() -> tuple[SymbolicOperatorTerm, ...]:
    """Return the symbolic Level 2 formal-kernel operator decomposition."""

    common_limit = (
        "Term classification is for DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL, not the full analytic twisted Dirac operator.",
    )
    return (
        SymbolicOperatorTerm(
            id="D_diag_squared",
            expression="D_diag^2",
            classification="DIAGONAL_EXACT",
            vanishes_on_k_formal=True,
            preserves_k_formal=True,
            acts_only_on_h_perp=False,
            can_lower_complement_gap=False,
            lower_bound_method="exact diagonal complement minimum after removing K_formal",
            status=SEMI_ANALYTIC_BOUND,
            assumptions=("The formal kernel rows/columns are zero-protected in the corrected Level 2 realization.",),
            limitations=common_limit,
        ),
        SymbolicOperatorTerm(
            id="V_Hopf",
            expression="V_Hopf(q)",
            classification="SIGN_INDEFINITE_BOUNDED",
            vanishes_on_k_formal=True,
            preserves_k_formal=True,
            acts_only_on_h_perp=False,
            can_lower_complement_gap=True,
            lower_bound_method="included in semi-analytic diagonal and Gershgorin rows",
            status=SEMI_ANALYTIC_BOUND,
            assumptions=("Protected states have q=0 and are projected into K_formal.",),
            limitations=common_limit,
        ),
        SymbolicOperatorTerm(
            id="V_boundary",
            expression="V_boundary(Omega_f)",
            classification="SIGN_INDEFINITE_BOUNDED",
            vanishes_on_k_formal=True,
            preserves_k_formal=True,
            acts_only_on_h_perp=False,
            can_lower_complement_gap=True,
            lower_bound_method="included in semi-analytic diagonal and Gershgorin rows",
            status=SEMI_ANALYTIC_BOUND,
            assumptions=("The v1.2 boundary functional is supplied and acts compatibly with K_formal.",),
            limitations=common_limit,
        ),
        SymbolicOperatorTerm(
            id="V_chi",
            expression="V_chi(chi)",
            classification="SIGN_INDEFINITE_BOUNDED",
            vanishes_on_k_formal=True,
            preserves_k_formal=True,
            acts_only_on_h_perp=False,
            can_lower_complement_gap=True,
            lower_bound_method="included in semi-analytic diagonal and Gershgorin rows",
            status=SEMI_ANALYTIC_BOUND,
            assumptions=("The protected chiral channel is chi=-1 and is zero-protected by P_formal.",),
            limitations=common_limit,
        ),
        SymbolicOperatorTerm(
            id="K_sector",
            expression="K_sector",
            classification="OFF_DIAGONAL_BOUNDED",
            vanishes_on_k_formal=True,
            preserves_k_formal=True,
            acts_only_on_h_perp=True,
            can_lower_complement_gap=True,
            lower_bound_method="structured relative-bound candidate and finite-basis norm checks",
            status=SEMI_ANALYTIC_BOUND,
            assumptions=("The corrected formal-kernel sector-coupling block vanishes on K_formal.",),
            limitations=(
                "Uniform/infinite-basis sector-coupling control remains a scaffold-level result.",
            ),
        ),
        SymbolicOperatorTerm(
            id="P_lift_perp",
            expression="P_lift^perp = mu_H(1-exp(-D_FK^2/Lambda^2)) P_perp",
            classification="PSD_EXACT",
            vanishes_on_k_formal=True,
            preserves_k_formal=True,
            acts_only_on_h_perp=True,
            can_lower_complement_gap=False,
            lower_bound_method="monotone heat-lift lower bound",
            status=SEMI_ANALYTIC_BOUND,
            assumptions=("Natural Lambda^2=1/(4*pi) is fixed and not tuned.",),
            limitations=("PSD heat lift is exact inside the scaffold once D_FK^2 lower bound is supplied.",),
        ),
        SymbolicOperatorTerm(
            id="PSD_profile",
            expression="V_profile|H_perp >= 0",
            classification="PSD_EXACT",
            vanishes_on_k_formal=True,
            preserves_k_formal=True,
            acts_only_on_h_perp=True,
            can_lower_complement_gap=False,
            lower_bound_method="PSD nonnegative Weyl contribution",
            status=COORDINATE_FREE_SCAFFOLD,
            assumptions=("Curvature/profile contribution is positive semidefinite on H_perp.",),
            limitations=("The PSD profile condition remains a sufficient assumption, not a full scalar/topographic proof.",),
        ),
    )


def symbolic_complement_bound() -> SymbolicComplementBound:
    """Return the v1.3O symbolic complement-bound statement."""

    bound: SemiAnalyticComplementBound = build_semi_analytic_complement_bound()
    lambda2 = natural_lambda2()
    heat_lower = heat_lift_lower_bound(bound.structured_relative_lower_bound, lambda2, MU_H)
    gap: BoundResult = complement_gap_bound(bound.structured_relative_lower_bound, lambda2, mu_h=MU_H)
    return SymbolicComplementBound(
        model_level=DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL,
        protected_subspace="K_formal",
        complement_subspace="H_perp = K_formal^perp",
        diagonal_complement_lower_bound=bound.diagonal_lower_bound,
        structured_relative_lower_bound=bound.structured_relative_lower_bound,
        exact_finite_lower_bound=bound.exact_finite_lower_bound,
        required_dirac_lower_bound=bound.required_dirac_lower_bound,
        lambda2=lambda2,
        mu_h=MU_H,
        heat_lift_lower_bound=heat_lower,
        heat_gap_margin=gap.margin,
        clears_required_dirac_bound=bool(bound.structured_relative_lower_bound >= bound.required_dirac_lower_bound),
        clears_mu_h_after_heat_lift=bool(gap.passes),
        psd_profile_assumption="V_profile|H_perp >= 0",
        implication=(
            "If the coordinate-free K_formal split, semi-analytic complement lower bound, "
            "sector-coupling relative bound, and PSD profile condition hold in the full operator, "
            "then H_T|H_perp >= mu_H."
        ),
        status=SEMI_ANALYTIC_BOUND,
        theorem_complete=False,
        assumptions=(
            "K_formal is removed before complement bounds are evaluated.",
            "The structured relative lower bound is used conservatively.",
            "Natural Lambda^2=1/(4*pi) is fixed.",
            "PSD profile terms cannot lower the complement gap.",
        ),
        limitations=(
            "This implication is conditional and scaffold-level.",
            "The full coordinate-free infinite-basis operator proof remains open.",
        ),
    )


def build_symbolic_formal_kernel_report(k_max: int = 4) -> SymbolicFormalKernelReport:
    """Build the complete v1.3O symbolic formal-kernel operator report."""

    return SymbolicFormalKernelReport(
        title="BHSM v1.3O Symbolic Formal-Kernel H_T Operator Scaffold",
        model_level=DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL,
        formal_kernel=formal_kernel_subspace(),
        coordinate_free_projector=coordinate_free_projector(),
        basis_realization=basis_realization_map(k_max),
        operator_expression="D_FK^2 = D_diag^2 + V_Hopf + V_boundary + V_chi + K_sector + P_lift^perp",
        terms=symbolic_operator_terms(),
        complement_bound=symbolic_complement_bound(),
        theorem_complete=False,
        correct_claim=(
            "BHSM v1.3O gives a closed symbolic formal-kernel scaffold and finite basis realization. "
            "It does not prove the full no-extra-light-state theorem."
        ),
        limitations=(
            "The full operator, index theorem, and infinite-basis complement split remain open.",
            "Finite-basis evidence is not labeled FULL_OPERATOR_PROVEN.",
            "Frozen BHSM v1.0/v1.1 predictions are not changed.",
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


def export_symbolic_formal_kernel_json(path: str | Path) -> None:
    """Export the symbolic formal-kernel operator report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_symbolic_formal_kernel_report()), indent=2, sort_keys=True) + "\n")


def export_symbolic_formal_kernel_markdown(path: str | Path) -> None:
    """Export the symbolic formal-kernel operator report as Markdown."""

    report = build_symbolic_formal_kernel_report()
    realization = report.basis_realization
    bound = report.complement_bound
    lines = [
        "# BHSM v1.3O Symbolic Formal-Kernel H_T Operator Scaffold",
        "",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Model level: `{report.model_level}`",
        "",
        "## Coordinate-Free Operator",
        "",
        f"`{report.coordinate_free_projector.protected_subspace}`",
        "",
        f"`{report.coordinate_free_projector.complement_subspace}`",
        "",
        f"`{report.operator_expression}`",
        "",
        "## Term Classification",
        "",
        "| Term | Expression | Classification | vanishes on K_formal | preserves K_formal | acts only on H_perp | lower-bound method | status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for term in report.terms:
        lines.append(
            f"| `{term.id}` | `{term.expression}` | `{term.classification}` | `{term.vanishes_on_k_formal}` | `{term.preserves_k_formal}` | `{term.acts_only_on_h_perp}` | {term.lower_bound_method} | `{term.status}` |"
        )
    lines.extend(
        [
            "",
            "## Basis Realization",
            "",
            f"- Formula: `{realization.formula}`",
            f"- Realized coordinates at k_max={realization.k_max}: `{realization.realized_coordinates}`",
            f"- Old coordinate-first block: `{realization.old_coordinate_first_block}`",
            f"- Matches current corrected operator basis: `{realization.matches_current_basis}`",
            "",
            "## Complement-Bound Statement",
            "",
            "| Quantity | Value |",
            "| --- | --- |",
            f"| Required Dirac lower bound | `{bound.required_dirac_lower_bound}` |",
            f"| Diagonal complement lower bound | `{bound.diagonal_complement_lower_bound}` |",
            f"| Structured relative lower bound | `{bound.structured_relative_lower_bound}` |",
            f"| Exact finite lower bound | `{bound.exact_finite_lower_bound}` |",
            f"| Heat-lift lower bound | `{bound.heat_lift_lower_bound}` |",
            f"| Heat gap margin | `{bound.heat_gap_margin}` |",
            f"| Clears required Dirac bound | `{bound.clears_required_dirac_bound}` |",
            f"| Clears mu_H after heat lift | `{bound.clears_mu_h_after_heat_lift}` |",
            "",
            bound.implication,
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in report.limitations],
            *[f"- {item}" for item in bound.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))
