"""Scalar/topographic state ledger for the BHSM completion campaign."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from scalar_decoupling import ScalarMode, build_scalar_proxy_spectrum, classify_scalar_mode, hopf_gap_mass


SM_HIGGS_PROJECTION = "SM_HIGGS_PROJECTION"
HEAVY_LIFTED_SCALAR = "HEAVY_LIFTED_SCALAR"
DERIVATIVE_SCREENED_TOPOGRAPHIC_MODE = "DERIVATIVE_SCREENED_TOPOGRAPHIC_MODE"
CURVATURE_FILTERED_MODE = "CURVATURE_FILTERED_MODE"
SCREENED_TOPOGRAPHIC_MODE = "SCREENED_TOPOGRAPHIC_MODE"
FORBIDDEN_EXTRA_LIGHT_SCALAR = "FORBIDDEN_EXTRA_LIGHT_SCALAR"
OPEN_SCALAR_RISK = "OPEN_SCALAR_RISK"


@dataclass(frozen=True)
class ScalarStateLedgerEntry:
    """One scalar/topographic state classification row."""

    mode_id: str
    category: str
    eigenvalue: float | None
    light: bool | None
    on_shell_particle: bool
    allowed: bool
    conditional: bool
    status: str
    notes: tuple[str, ...]


def category_definitions() -> tuple[ScalarStateLedgerEntry, ...]:
    """Return category-level definitions, including falsifier templates."""

    return (
        ScalarStateLedgerEntry("category_higgs", SM_HIGGS_PROJECTION, None, True, True, True, False, "ALLOWED_UNIQUE_LIGHT_HIGGS", ("Exactly one light Higgs projection is allowed.",)),
        ScalarStateLedgerEntry("category_heavy", HEAVY_LIFTED_SCALAR, None, False, False, True, False, "ALLOWED_HEAVY", ("Orthogonal scalars above the Hopf gap are allowed.",)),
        ScalarStateLedgerEntry("category_derivative", DERIVATIVE_SCREENED_TOPOGRAPHIC_MODE, None, True, False, True, True, "CONDITIONAL_SCREENED", ("Derivative-filtered modes are conditional, not fully proven safe.",)),
        ScalarStateLedgerEntry("category_curvature", CURVATURE_FILTERED_MODE, None, True, False, True, True, "CONDITIONAL_SCREENED", ("Curvature-filtered modes are conditional, not fully proven safe.",)),
        ScalarStateLedgerEntry("category_screened", SCREENED_TOPOGRAPHIC_MODE, None, True, False, True, True, "CONDITIONAL_SCREENED", ("Screened modes are not counted as new on-shell light particles in the scaffold.",)),
        ScalarStateLedgerEntry("category_forbidden", FORBIDDEN_EXTRA_LIGHT_SCALAR, None, True, True, False, False, "FALSIFIER_TEMPLATE", ("An unscreened direct-coupled light scalar is forbidden.",)),
        ScalarStateLedgerEntry("category_open", OPEN_SCALAR_RISK, None, True, None, False, True, "OPEN_RISK_TEMPLATE", ("Any unclassified light scalar remains an open risk.",)),
    )


def _category_for_mode(row: dict[str, object]) -> str:
    coupling = str(row["coupling_type"])
    status = str(row["status"])
    if row["is_higgs_projection"]:
        return SM_HIGGS_PROJECTION
    if status == "heavy_orthogonal":
        return HEAVY_LIFTED_SCALAR
    if coupling == "derivative_filtered":
        return DERIVATIVE_SCREENED_TOPOGRAPHIC_MODE
    if coupling == "curvature_filtered":
        return CURVATURE_FILTERED_MODE
    if coupling == "screened":
        return SCREENED_TOPOGRAPHIC_MODE
    if status == "dangerous_light":
        return FORBIDDEN_EXTRA_LIGHT_SCALAR
    return OPEN_SCALAR_RISK


def scalar_inventory_entries(n_modes: int = 6) -> tuple[ScalarStateLedgerEntry, ...]:
    """Return current finite scalar/topographic proxy inventory entries."""

    modes = build_scalar_proxy_spectrum(n_modes)
    gap = hopf_gap_mass(246.21965)
    rows: list[ScalarStateLedgerEntry] = []
    for mode in modes:
        classification = classify_scalar_mode(mode, gap)
        category = _category_for_mode(classification)
        rows.append(
            ScalarStateLedgerEntry(
                mode_id=mode.mode_id,
                category=category,
                eigenvalue=float(mode.eigenvalue),
                light=bool(classification["is_light"]),
                on_shell_particle=bool(mode.is_higgs_projection),
                allowed=bool(classification["passes"]),
                conditional=bool(classification["conditional"]),
                status=str(classification["status"]),
                notes=(
                    "Current proxy scalar inventory row.",
                    "Conditional rows require action-level screening proof.",
                ),
            )
        )
    return tuple(rows)


def scalar_state_ledger(n_modes: int = 6) -> dict[str, Any]:
    """Return scalar category definitions and current inventory rows."""

    return {
        "category_definitions": [asdict(row) for row in category_definitions()],
        "current_inventory": [asdict(row) for row in scalar_inventory_entries(n_modes)],
        "limitations": (
            "The inventory is finite-basis/proxy scaffold evidence.",
            "Forbidden and open-risk rows are definitions/falsifier templates unless present in current_inventory.",
        ),
    }
