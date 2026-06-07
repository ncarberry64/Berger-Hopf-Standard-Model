"""BHSM v1.2 omega action-origin derivation scaffold."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from berger_spectrum import berger_lambda
from bundle_boundary_conditions import (
    CoefficientDerivationStatus,
    SectorBoundaryFunctional,
    derived_coefficients,
    default_sector_boundary_functionals,
)
from internal_action import default_internal_action_terms
from mode_selection import EXPECTED_LEDGER, HEAVY_MODE, hopf_charge


@dataclass(frozen=True)
class OmegaDerivationStep:
    """One symbolic step in the omega derivation scaffold."""

    id: str
    sector: str
    statement: str
    expression: str
    value: int | str
    status: CoefficientDerivationStatus
    dependencies: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class OmegaDerivationReport:
    """Complete report for the v1.2 omega action-origin scaffold."""

    title: str
    model_version: str
    theorem_complete: bool
    action_terms: tuple[Any, ...]
    steps: tuple[OmegaDerivationStep, ...]
    coefficient_status_table: tuple[dict[str, Any], ...]
    dependency_graph: dict[str, Any]
    recovered_mode_ledger: dict[str, Any]
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def omega_equation_from_functional(functional: SectorBoundaryFunctional) -> str:
    """Return a readable omega equation from a boundary functional."""

    label = {"lepton": "ell", "up": "u", "down": "d"}[functional.sector]
    fiber = functional.fiber_coefficient
    base = functional.base_coefficient
    fiber_text = "-q" if fiber == -1 else "q" if fiber == 1 else f"{fiber}q"
    if base == 0:
        base_text = ""
    elif base > 0:
        base_text = f"+{base}j"
    else:
        base_text = f"{base}j"
    return f"Omega_{label} = {fiber_text}{base_text} = {functional.target}"


def omega_value_from_functional(k: int, j: int, functional: SectorBoundaryFunctional) -> int:
    """Evaluate omega = fiber*q + base*j from the action-origin functional."""

    return functional.fiber_coefficient * hopf_charge(k, j) + functional.base_coefficient * j


def coefficient_rows(functionals: dict[str, SectorBoundaryFunctional] | None = None) -> tuple[dict[str, Any], ...]:
    """Return the coefficient status table for all sectors."""

    functionals = default_sector_boundary_functionals() if functionals is None else functionals
    rows = []
    for sector, functional in functionals.items():
        for coefficient in derived_coefficients(functional):
            rows.append(
                {
                    "sector": sector,
                    "coefficient": coefficient.name,
                    "value": coefficient.value,
                    "status": coefficient.status.value,
                    "source": coefficient.source,
                    "dependencies": coefficient.dependencies,
                    "open_reason": coefficient.open_reason,
                }
            )
    return tuple(rows)


def dependency_graph(functionals: dict[str, SectorBoundaryFunctional] | None = None) -> dict[str, Any]:
    """Return coefficient dependencies and remaining open action obligations."""

    functionals = default_sector_boundary_functionals() if functionals is None else functionals
    graph: dict[str, Any] = {
        "nodes": {
            "I_D": "internal Dirac kinetic scaffold",
            "I_HOPF": "Hopf-fiber covariant derivative",
            "I_BASE": "base S^2 angular derivative",
            "I_U1": "Higgs-selected U(1) boundary phase",
            "I_WEAK": "weak-doublet chirality projector",
            "I_COF": "quark coframe triplet projector",
            "I_BDY": "sector boundary functional",
        },
        "coefficients": {},
        "open_parts": (
            "derive the sector boundary functional from variation of the full internal action",
            "derive coframe triplet participation from the complete bundle action",
            "derive the Higgs-selected U(1) boundary phase from the full topological sector",
            "compute the full twisted Dirac/bundle spectrum",
        ),
    }
    for sector, functional in functionals.items():
        graph["coefficients"][sector] = {
            coefficient.name: {
                "value": coefficient.value,
                "status": coefficient.status.value,
                "source": coefficient.source,
                "dependencies": coefficient.dependencies,
                "open_reason": coefficient.open_reason,
            }
            for coefficient in derived_coefficients(functional)
        }
    return graph


def derivation_steps_for_sector(functional: SectorBoundaryFunctional) -> tuple[OmegaDerivationStep, ...]:
    """Return symbolic derivation steps for one sector."""

    sector = functional.sector
    return (
        OmegaDerivationStep(
            id=f"{sector}.fiber",
            sector=sector,
            statement="Boundary variation of the Hopf-fiber phase fixes the q coefficient.",
            expression="c_q = hopf_fiber_orientation * hypercharge_higgs_boundary",
            value=functional.fiber_coefficient,
            status=functional.fiber_status,
            dependencies=("I_HOPF", "I_U1"),
            limitations=("This is a finite symbolic boundary functional, not the full action variation.",),
        ),
        OmegaDerivationStep(
            id=f"{sector}.base",
            sector=sector,
            statement="Base node phase, chirality, weak component, and coframe participation fix the j coefficient.",
            expression="c_j = base_node_phase * chirality_sign * weak_component_sign * coframe_participation",
            value=functional.base_coefficient,
            status=functional.base_status,
            dependencies=("I_BASE", "I_WEAK", "I_COF"),
            limitations=("Coframe participation remains action-linked pending the full bundle derivation.",),
        ),
        OmegaDerivationStep(
            id=f"{sector}.target",
            sector=sector,
            statement="Generation index and sector winding fix the boundary target.",
            expression="target = family_index * sector_winding_multiplier",
            value=functional.target,
            status=functional.target_status,
            dependencies=("I_BDY",),
            limitations=("The winding multiplier remains part of the symbolic boundary functional.",),
        ),
        OmegaDerivationStep(
            id=f"{sector}.equation",
            sector=sector,
            statement="The sector boundary equation follows from the functional coefficients.",
            expression=omega_equation_from_functional(functional),
            value=omega_equation_from_functional(functional),
            status=CoefficientDerivationStatus.DERIVED_FROM_BOUNDARY_FUNCTIONAL,
            dependencies=(f"{sector}.fiber", f"{sector}.base", f"{sector}.target"),
            limitations=("This does not upgrade Omega_f to a completed first-principles action derivation.",),
        ),
    )


def _in_berger_domain(k: int, j: int) -> bool:
    return k >= 0 and 0 <= j <= k // 2


def is_admissible_from_functional(k: int, j: int, functional: SectorBoundaryFunctional) -> bool:
    """Return whether a nonzero mode satisfies the derived boundary functional."""

    if (k, j) == HEAVY_MODE or not _in_berger_domain(k, j):
        return False
    q = hopf_charge(k, j)
    if omega_value_from_functional(k, j, functional) != functional.target:
        return False
    if functional.sector == "lepton":
        return q % 2 == 1
    if functional.sector == "up":
        return q % 2 == 0 and q >= 6
    return q % 4 == 0


def selected_modes_from_functional(
    functional: SectorBoundaryFunctional,
    k_max: int = 12,
    n_modes: int = 2,
) -> list[tuple[int, int]]:
    """Return the first admissible modes from the action-origin functional."""

    modes = [
        (k, j)
        for k in range(k_max + 1)
        for j in range(k // 2 + 1)
        if is_admissible_from_functional(k, j, functional)
    ]
    return sorted(modes, key=lambda mode: (berger_lambda(*mode), mode[0], mode[1]))[:n_modes]


def recovered_mode_ledger(k_max: int = 12) -> dict[str, Any]:
    """Return mode selection recovered from the action-origin functionals."""

    functionals = default_sector_boundary_functionals()
    sectors: dict[str, Any] = {}
    recovered_all = True
    for sector, functional in functionals.items():
        selected = selected_modes_from_functional(functional, k_max=k_max)
        expected = EXPECTED_LEDGER[sector]
        recovered = selected == expected
        recovered_all = recovered_all and recovered
        sectors[sector] = {
            "heavy": HEAVY_MODE,
            "selected": selected,
            "expected": expected,
            "recovered_expected": recovered,
            "equation": omega_equation_from_functional(functional),
        }
    return {"k_max": k_max, "recovered_all": recovered_all, "sectors": sectors}


def build_omega_action_origin_report(k_max: int = 12) -> OmegaDerivationReport:
    """Build the v1.2 omega action-origin report."""

    functionals = default_sector_boundary_functionals()
    steps = tuple(
        step
        for functional in functionals.values()
        for step in derivation_steps_for_sector(functional)
    )
    return OmegaDerivationReport(
        title="BHSM v1.2 Omega Action-Origin Scaffold",
        model_version="BHSM_V1_2_ACTION_ORIGIN_DEVELOPMENT",
        theorem_complete=False,
        action_terms=default_internal_action_terms(),
        steps=steps,
        coefficient_status_table=coefficient_rows(functionals),
        dependency_graph=dependency_graph(functionals),
        recovered_mode_ledger=recovered_mode_ledger(k_max),
        assumptions=(
            "The sector boundary functional is supplied as a symbolic action-origin scaffold.",
            "No empirical masses, residuals, or CKM values are used to select coefficients.",
            "Canonical a and S remain fixed by the v1.0/v1.1 frozen model package.",
        ),
        limitations=(
            "DERIVED_FROM_BOUNDARY_FUNCTIONAL means derived inside the explicit symbolic boundary functional only.",
            "Omega_f is not yet derived from a completed variation/spectrum of the full Berger-Hopf internal action.",
            "The v1.0/v1.1 frozen prediction packages are not modified by this report.",
        ),
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, CoefficientDerivationStatus):
        return value.value
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def export_omega_action_origin_json(path: str | Path, k_max: int = 12) -> None:
    """Export the omega action-origin report as JSON."""

    report = build_omega_action_origin_report(k_max)
    Path(path).write_text(json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n")


def export_omega_action_origin_markdown(path: str | Path, k_max: int = 12) -> None:
    """Export the omega action-origin report as Markdown."""

    report = build_omega_action_origin_report(k_max)
    lines = [
        "# BHSM v1.2 Omega Action-Origin Scaffold",
        "",
        "This development report attacks the boundary-operator proof gap without changing the frozen v1.0/v1.1 prediction packages.",
        "",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "## Action Terms",
        "",
        "| ID | Term | Source factor | Status |",
        "| --- | --- | --- | --- |",
    ]
    for term in report.action_terms:
        lines.append(f"| `{term.id}` | {term.name} | `{term.source_factor}` | `{term.status}` |")
    lines.extend(
        [
            "",
            "## Coefficient Status Table",
            "",
            "| Sector | Coefficient | Value | Status | Source |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )
    for row in report.coefficient_status_table:
        lines.append(
            f"| `{row['sector']}` | `{row['coefficient']}` | `{row['value']}` | `{row['status']}` | {row['source']} |"
        )
    lines.extend(["", "## Recovered Boundary Equations", ""])
    for sector, data in report.recovered_mode_ledger["sectors"].items():
        lines.append(f"- `{sector}`: `{data['equation']}`, selected `{data['selected']}`, recovered `{data['recovered_expected']}`")
    lines.extend(["", "## Dependency Graph Summary", ""])
    for sector, coefficients in report.dependency_graph["coefficients"].items():
        lines.append(f"### {sector}")
        for name, data in coefficients.items():
            deps = ", ".join(data["dependencies"])
            lines.append(
                f"- `{name}` = `{data['value']}` from `{data['source']}` using `{deps}`; status `{data['status']}`."
            )
    lines.extend(
        [
            "",
            "Open parts:",
            *[f"- {item}" for item in report.dependency_graph["open_parts"]],
            "",
            "## What v1.2 Proves and Does Not Prove",
            "",
            "- Proves within the scaffold: the charged-sector omega coefficients follow from the explicit symbolic sector boundary functional.",
            "- Does not prove: the full twisted Dirac/bundle action uniquely generates that functional.",
        ]
    )
    lines.extend(
        [
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
    )
    Path(path).write_text("\n".join(lines))
