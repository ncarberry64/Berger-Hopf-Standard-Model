"""Uniqueness audit for nearby BHSM parent-action variants."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, replace
from enum import StrEnum
from pathlib import Path
from typing import Any

from action_minimality import ActionAuditReport, ActionVariant, ReductionOutcome
from action_reduction import reduce_parent_action_to_boundary_functional, reduced_coefficients
from anomalies import anomalies_cancel
from bundle_boundary_conditions import SectorBoundaryFunctional, derive_base_coefficient, derive_fiber_coefficient, derive_target
from hypercharge import derive_hypercharges
from omega_derivation import omega_equation_from_functional, selected_modes_from_functional


class UniquenessStatus(StrEnum):
    """Uniqueness status for the action-variant audit."""

    UNIQUE_UNDER_BHSM_AXIOMS = "UNIQUE_UNDER_BHSM_AXIOMS"
    COMPETING_VARIANT_EXISTS = "COMPETING_VARIANT_EXISTS"
    INDETERMINATE = "INDETERMINATE"
    FAILS_SM_LEDGER = "FAILS_SM_LEDGER"


@dataclass(frozen=True)
class UniquenessCriterion:
    """Criterion for judging a nearby parent-action variant."""

    id: str
    variant_id: str
    status: UniquenessStatus
    recovers_mode_ledger: bool
    equations: dict[str, str]
    selected_modes: dict[str, list[tuple[int, int]]]
    anomaly_compatible: bool
    sm_field_ledger_survives: bool
    frozen_outputs_would_change_if_adopted: bool
    limitations: tuple[str, ...]


def uniqueness_variants() -> tuple[ActionVariant, ...]:
    """Return nearby action-scaffold variants for uniqueness auditing."""

    return (
        ActionVariant(
            id="flip_hopf_orientation",
            description="Flip Hopf fiber orientation in every charged sector.",
            overrides={sector: {"hopf_fiber_orientation": "flip"} for sector in ("lepton", "up", "down")},
        ),
        ActionVariant(
            id="flip_weak_chirality",
            description="Flip weak chirality sign in every charged sector.",
            overrides={sector: {"chirality_sign": "flip"} for sector in ("lepton", "up", "down")},
        ),
        ActionVariant(
            id="remove_coframe_triplet",
            description="Remove coframe triplet participation.",
            overrides={sector: {"coframe_participation": None} for sector in ("lepton", "up", "down")},
        ),
        ActionVariant(
            id="coframe_singlet",
            description="Change coframe factor from triplet/doublet value to singlet.",
            overrides={sector: {"coframe_participation": 1} for sector in ("lepton", "up", "down")},
        ),
        ActionVariant(
            id="shift_boundary_winding",
            description="Change sector boundary winding multiplier by one unit.",
            overrides={
                "lepton": {"sector_winding_multiplier": 2},
                "up": {"sector_winding_multiplier": 3},
                "down": {"sector_winding_multiplier": 5},
            },
        ),
        ActionVariant(
            id="swap_weak_component_sign",
            description="Swap weak-component sign.",
            overrides={sector: {"weak_component_sign": -1} for sector in ("lepton", "up", "down")},
        ),
        ActionVariant(
            id="trace_u1_dynamical",
            description="Allow trace U(1) as dynamical rather than topological.",
            overrides={sector: {"hypercharge_higgs_boundary": None} for sector in ("lepton", "up", "down")},
        ),
        ActionVariant(
            id="disable_higgs_u1",
            description="Disable Higgs-selected U(1) boundary condition.",
            overrides={sector: {"hypercharge_higgs_boundary": None} for sector in ("lepton", "up", "down")},
        ),
    )


def _apply_value(current: int | None, override: int | None | str) -> int | None:
    if override == "flip":
        if current is None:
            return None
        return -current
    if override is None:
        return None
    return int(override)


def apply_variant_to_functional(functional: SectorBoundaryFunctional, variant: ActionVariant) -> SectorBoundaryFunctional:
    """Apply a controlled variant to a sector boundary functional."""

    overrides = (variant.overrides or {}).get(functional.sector, {})
    updated = functional
    for field, override in overrides.items():
        updated = replace(updated, **{field: _apply_value(getattr(updated, field), override)})
    return updated


def baseline_functionals() -> dict[str, SectorBoundaryFunctional]:
    """Return parent-action-reduced baseline boundary functionals."""

    return {
        sector: reduce_parent_action_to_boundary_functional(sector).functional
        for sector in ("lepton", "up", "down")
    }


def _safe_equation(functional: SectorBoundaryFunctional) -> str:
    try:
        return omega_equation_from_functional(functional)
    except ValueError as exc:
        return f"OPEN: {exc}"


def _safe_modes(functional: SectorBoundaryFunctional) -> list[tuple[int, int]]:
    try:
        return selected_modes_from_functional(functional, k_max=12)
    except ValueError:
        return []


def evaluate_uniqueness_variant(variant: ActionVariant) -> UniquenessCriterion:
    """Evaluate one nearby action variant."""

    baseline = baseline_functionals()
    variant_functionals = {
        sector: apply_variant_to_functional(functional, variant)
        for sector, functional in baseline.items()
    }
    expected = {
        "lepton": [(5, 2), (9, 3)],
        "up": [(6, 0), (10, 1)],
        "down": [(6, 3), (8, 2)],
    }
    equations = {sector: _safe_equation(functional) for sector, functional in variant_functionals.items()}
    selected = {sector: _safe_modes(functional) for sector, functional in variant_functionals.items()}
    recovers = selected == expected
    baseline_equations = {sector: _safe_equation(functional) for sector, functional in baseline.items()}
    differs_from_baseline = equations != baseline_equations
    anomaly_compatible = anomalies_cancel(derive_hypercharges())
    sm_field_ledger_survives = anomaly_compatible and not any("OPEN" in equation for equation in equations.values())
    would_change = differs_from_baseline or not recovers
    if recovers and differs_from_baseline:
        status = UniquenessStatus.COMPETING_VARIANT_EXISTS
    elif not sm_field_ledger_survives or not recovers:
        status = UniquenessStatus.FAILS_SM_LEDGER
    else:
        status = UniquenessStatus.INDETERMINATE
    return UniquenessCriterion(
        id=f"criterion_{variant.id}",
        variant_id=variant.id,
        status=status,
        recovers_mode_ledger=recovers,
        equations=equations,
        selected_modes=selected,
        anomaly_compatible=anomaly_compatible,
        sm_field_ledger_survives=sm_field_ledger_survives,
        frozen_outputs_would_change_if_adopted=would_change,
        limitations=(
            "Variant audit is local to controlled symbolic nearby scaffolds.",
            "Anomaly compatibility is checked for the unchanged SM hypercharge ledger only.",
        ),
    )


def build_uniqueness_audit() -> ActionAuditReport:
    """Build the uniqueness audit over controlled nearby variants."""

    variants = uniqueness_variants()
    criteria = tuple(evaluate_uniqueness_variant(variant) for variant in variants)
    competing = [criterion for criterion in criteria if criterion.status == UniquenessStatus.COMPETING_VARIANT_EXISTS]
    status = (
        UniquenessStatus.COMPETING_VARIANT_EXISTS.value
        if competing
        else UniquenessStatus.UNIQUE_UNDER_BHSM_AXIOMS.value
    )
    outcomes = tuple(
        ReductionOutcome(
            variant_id=criterion.variant_id,
            sector=sector,
            parent_status=criterion.status.value,
            fiber_value=None,
            fiber_status="VARIANT",
            base_value=None,
            base_status="VARIANT",
            target_value=None,
            target_status="VARIANT",
            open_reasons=(),
            recovered_expected_modes=criterion.recovers_mode_ledger,
        )
        for criterion in criteria
        for sector in ("lepton", "up", "down")
    )
    return ActionAuditReport(
        title="BHSM v1.2C Parent-Action Uniqueness Audit",
        status=status,
        theorem_complete=False,
        variants=variants,
        outcomes=outcomes,
        criteria=criteria,
        limitations=(
            "Uniqueness is only under the current BHSM axioms and tested nearby variants.",
            "This does not prove global uniqueness of the complete internal action.",
        ),
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, (UniquenessStatus,)):
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


def export_uniqueness_audit_json(path: str | Path) -> None:
    """Export parent-action uniqueness audit as JSON."""

    report = build_uniqueness_audit()
    Path(path).write_text(json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n")


def export_uniqueness_audit_markdown(path: str | Path) -> None:
    """Export parent-action uniqueness audit as Markdown."""

    report = build_uniqueness_audit()
    lines = [
        "# BHSM v1.2C Parent-Action Uniqueness Audit",
        "",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Variant | Status | Recovers ledger | Would change frozen outputs if adopted |",
        "| --- | --- | --- | --- |",
    ]
    for criterion in report.criteria:
        lines.append(
            f"| `{criterion.variant_id}` | `{criterion.status.value}` | `{criterion.recovers_mode_ledger}` | `{criterion.frozen_outputs_would_change_if_adopted}` |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "BHSM v1.2C audits whether the parent-action scaffold is minimal and unique under the current BHSM axioms. It does not claim full uniqueness of the complete internal action unless competing variants are excluded by explicit tests.",
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in report.limitations],
            "",
        ]
    )
    Path(path).write_text("\n".join(lines))
