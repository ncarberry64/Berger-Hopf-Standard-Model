"""Colored lower-doublet projector audit for the BHSM down-sector bonus.

This sprint replaces the independent ``chi_d`` flag used in the sector
projector audit with the SM-ledger expression ``(3B)(1/2 - T3)``.  The formula
exactly selects colored lower-doublet components, but the full coframe/action
interpretation remains a partial derivation rather than a completed theorem.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from bhsm_completion_manual_theory_delta import frozen_sanity_payload
from bhsm_v1 import compare_bhsm_v1_branches


COLORED_LOWER_PROJECTOR_PARTIAL_DERIVATION = (
    "COLORED_LOWER_PROJECTOR_PARTIAL_DERIVATION"
)
DOWN_COFAME_BONUS_PARTIAL_DERIVATION = "DOWN_COFAME_BONUS_PARTIAL_DERIVATION"
Q_COEFFICIENT_3B_MINUS_L_SUPPORTED = "Q_COEFFICIENT_3B_MINUS_L_SUPPORTED"
J_COEFFICIENT_T3_COLOR_LOWER_PARTIAL = "J_COEFFICIENT_T3_COLOR_LOWER_PARTIAL"
BOUNDARY_CONNECTION_HOLONOMY_PARTIAL = "BOUNDARY_CONNECTION_HOLONOMY_PARTIAL"
LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE = (
    "LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE"
)
NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE = (
    "NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE"
)


@dataclass(frozen=True)
class SectorData:
    """SM-ledger data used by the colored lower-doublet projector."""

    sector: str
    B: Fraction
    L: Fraction
    T3: Fraction
    source: str
    candidate_only: bool = False


@dataclass(frozen=True)
class SectorCoefficients:
    """Exact coefficients for Omega=a*q+b*j."""

    sector: str
    a: Fraction
    b: Fraction
    chi_colored_lower: Fraction
    status: str


def q_from_kj(k: int, j: int) -> int:
    """Return q=k-2j."""

    return k - 2 * j


def a_from_B_L(B: Fraction | int, L: Fraction | int) -> Fraction:
    """Return a=3B-L."""

    return 3 * Fraction(B) - Fraction(L)


def lower_doublet_projector(T3: Fraction | int) -> Fraction:
    """Return the lower weak-doublet projector 1/2-T3."""

    return Fraction(1, 2) - Fraction(T3)


def color_normalized_baryon(B: Fraction | int) -> Fraction:
    """Return 3B as color-normalized baryon participation."""

    return 3 * Fraction(B)


def chi_colored_lower(B: Fraction | int, T3: Fraction | int) -> Fraction:
    """Return (3B)(1/2-T3)."""

    return color_normalized_baryon(B) * lower_doublet_projector(T3)


def b_from_T3_B(T3: Fraction | int, B: Fraction | int) -> Fraction:
    """Return b=-4T3+2(3B)(1/2-T3)."""

    return -4 * Fraction(T3) + 2 * chi_colored_lower(B, T3)


def omega_from_sm_projector(
    q: int,
    j: int,
    B: Fraction | int,
    L: Fraction | int,
    T3: Fraction | int,
) -> Fraction:
    """Return Omega=(3B-L)q+[-4T3+2(3B)(1/2-T3)]j."""

    return a_from_B_L(B, L) * q + b_from_T3_B(T3, B) * j


def sector_data(sector: str) -> SectorData:
    """Return exact SM data for charged sectors plus neutrino candidate."""

    data = {
        "charged_lepton": SectorData(
            sector="charged_lepton",
            B=Fraction(0),
            L=Fraction(1),
            T3=Fraction(-1, 2),
            source="SM lepton doublet lower component",
        ),
        "up": SectorData(
            sector="up",
            B=Fraction(1, 3),
            L=Fraction(0),
            T3=Fraction(1, 2),
            source="SM quark doublet upper component",
        ),
        "down": SectorData(
            sector="down",
            B=Fraction(1, 3),
            L=Fraction(0),
            T3=Fraction(-1, 2),
            source="SM quark doublet lower component",
        ),
        "neutrino": SectorData(
            sector="neutrino",
            B=Fraction(0),
            L=Fraction(1),
            T3=Fraction(1, 2),
            source="SM lepton doublet upper component; candidate-only neutral sector",
            candidate_only=True,
        ),
    }
    if sector not in data:
        raise ValueError(f"unknown sector: {sector}")
    return data[sector]


def sector_coefficients(sector: str) -> SectorCoefficients:
    """Return exact projector coefficients for one sector."""

    data = sector_data(sector)
    status = (
        NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE
        if sector == "neutrino"
        else COLORED_LOWER_PROJECTOR_PARTIAL_DERIVATION
    )
    return SectorCoefficients(
        sector=sector,
        a=a_from_B_L(data.B, data.L),
        b=b_from_T3_B(data.T3, data.B),
        chi_colored_lower=chi_colored_lower(data.B, data.T3),
        status=status,
    )


def omega_charged_lepton(q: int, j: int) -> Fraction:
    """Return charged-lepton omega."""

    data = sector_data("charged_lepton")
    return omega_from_sm_projector(q, j, data.B, data.L, data.T3)


def omega_up(q: int, j: int) -> Fraction:
    """Return up-sector omega."""

    data = sector_data("up")
    return omega_from_sm_projector(q, j, data.B, data.L, data.T3)


def omega_down(q: int, j: int) -> Fraction:
    """Return down-sector omega."""

    data = sector_data("down")
    return omega_from_sm_projector(q, j, data.B, data.L, data.T3)


def omega_neutrino_candidate(q: int, j: int) -> Fraction:
    """Return candidate neutral-lepton omega."""

    data = sector_data("neutrino")
    return omega_from_sm_projector(q, j, data.B, data.L, data.T3)


def validate_mode_pair_constant_level(sector: str) -> dict[str, Any]:
    """Return exact mode-pair constant-level check for a charged sector."""

    modes = {
        "charged_lepton": ((5, 2), (9, 3)),
        "up": ((6, 0), (10, 1)),
        "down": ((6, 3), (8, 2)),
    }
    omega_fns = {
        "charged_lepton": omega_charged_lepton,
        "up": omega_up,
        "down": omega_down,
    }
    if sector not in modes:
        raise ValueError(f"unknown charged sector: {sector}")
    rows = []
    values = []
    for k, j in modes[sector]:
        q = q_from_kj(k, j)
        omega = omega_fns[sector](q, j)
        rows.append({"mode": (k, j), "q": q, "j": j, "omega": omega})
        values.append(omega)
    return {
        "sector": sector,
        "constant": len(set(values)) == 1,
        "level": values[0] if len(set(values)) == 1 else None,
        "rows": rows,
    }


def validate_no_official_outputs_modified() -> dict[str, Any]:
    """Return frozen branch sanity checks."""

    comparison = compare_bhsm_v1_branches()
    changed = [row for row in comparison["rows"] if row["changed"]]
    return {
        "frozen_sanity": frozen_sanity_payload(),
        "official_branch_comparison": comparison,
        "official_dressed_changes_only_c_over_t": len(changed) == 1
        and changed[0]["quantity"] == "c/t",
    }


def audit_payload() -> dict[str, Any]:
    """Return full colored lower-doublet projector audit payload."""

    checks = {
        sector: validate_mode_pair_constant_level(sector)
        for sector in ("charged_lepton", "up", "down")
    }
    levels = {sector: check["level"] for sector, check in checks.items()}
    reproduces = levels == {
        "charged_lepton": Fraction(3),
        "up": Fraction(6),
        "down": Fraction(12),
    }
    coeffs = {
        sector: sector_coefficients(sector)
        for sector in ("charged_lepton", "up", "down", "neutrino")
    }
    data = {sector: sector_data(sector) for sector in coeffs}
    missing = (
        "derive 3B as the actual coframe/color multiplicity operator inside A_boundary",
        "derive lower_doublet_projector(T3)=1/2-T3 as a boundary projector, not only SM bookkeeping",
        "derive the product (3B)(1/2-T3) from the full color/coframe boundary connection",
        "derive cyclic quotient dimension dim(H)=|Omega| separately",
        "derive identity/traceless protection before promoting lepton 8/9",
    )
    payload: dict[str, Any] = {
        "title": "BHSM colored lower-doublet coframe bonus audit",
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        "colored_lower_projector_status": COLORED_LOWER_PROJECTOR_PARTIAL_DERIVATION,
        "down_coframe_bonus_status": DOWN_COFAME_BONUS_PARTIAL_DERIVATION,
        "q_coefficient_status": Q_COEFFICIENT_3B_MINUS_L_SUPPORTED,
        "j_coefficient_status": J_COEFFICIENT_T3_COLOR_LOWER_PARTIAL,
        "does_chi_d_follow_from_B_T3": True,
        "does_formula_reproduce_omega_l_u_d": reproduces,
        "does_this_close_down_bonus": False,
        "boundary_connection_consequence_status": BOUNDARY_CONNECTION_HOLONOMY_PARTIAL,
        "lepton_8_9_consequence_status": LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE,
        "neutrino_projector_consequence_status": NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE,
        "blockers_closed": (
            "independent_chi_d_indicator_replaced_by_B_T3_projector",
        ),
        "blockers_remaining": missing,
        "derived_components": (),
        "candidate_components": (
            "colored_lower_projector",
            "down_coframe_bonus_partial",
            "neutrino_projector_consequence",
        ),
        "missing_assumptions": missing,
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "files_concepts_searched": (
            "SM field ledger and hypercharge records",
            "boundary_derivation coframe factors",
            "sector-projector SM-ledger audit",
            "mode ledgers and anomaly inheritance tests",
        ),
        "sector_data": data,
        "sector_coefficients": coeffs,
        "mode_pair_checks": checks,
        "neutrino_candidate": {
            "coefficients": coeffs["neutrino"],
            "formula": "Omega_nu=-q-2j",
            "ordinary_FTL_claim": False,
            "candidate_only": True,
            "no_numerical_PMNS_claims": True,
        },
    }
    payload.update(validate_no_official_outputs_modified())
    return payload


def _jsonable(value: object) -> object:
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator, "value": float(value)}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def render_markdown(payload: dict[str, Any] | None = None) -> str:
    """Render the audit payload as Markdown."""

    payload = payload or audit_payload()
    lines = [
        "# BHSM Colored Lower-Doublet Coframe Bonus",
        "",
        "This sprint tests whether the independent down-sector `chi_d` flag can be replaced by the SM-ledger projector `(3B)(1/2-T3)`.",
        "The result is partial: the formula exactly selects colored lower-doublet modes, but the full coframe/action operator remains open.",
        "",
        "## Summary",
        "",
        f"Colored lower projector status: `{payload['colored_lower_projector_status']}`",
        f"Down coframe bonus status: `{payload['down_coframe_bonus_status']}`",
        f"q coefficient status: `{payload['q_coefficient_status']}`",
        f"j coefficient status: `{payload['j_coefficient_status']}`",
        f"chi_d follows from B,T3: `{payload['does_chi_d_follow_from_B_T3']}`",
        f"Formula reproduces Omega_l,u,d: `{payload['does_formula_reproduce_omega_l_u_d']}`",
        f"Strictly closes down bonus: `{payload['does_this_close_down_bonus']}`",
        "",
        "## Projector",
        "",
        "```text",
        "chi_colored_lower = (3B)(1/2 - T3)",
        "b_f = -4T3 + 2(3B)(1/2 - T3)",
        "Omega_f = (3B-L)q + b_f j",
        "```",
        "",
        "## Coefficients",
        "",
        "| Sector | a | b | chi colored lower |",
        "| --- | ---: | ---: | ---: |",
    ]
    for sector, coeff in payload["sector_coefficients"].items():
        lines.append(
            f"| `{sector}` | `{coeff.a}` | `{coeff.b}` | `{coeff.chi_colored_lower}` |"
        )
    lines.extend(
        [
            "",
            "## Mode Pair Checks",
            "",
            "| Sector | Constant | Level |",
            "| --- | --- | ---: |",
        ]
    )
    for sector, check in payload["mode_pair_checks"].items():
        lines.append(f"| `{sector}` | `{check['constant']}` | `{check['level']}` |")
    lines.extend(["", "## Missing Assumptions", ""])
    lines.extend(f"- {item}" for item in payload["missing_assumptions"])
    lines.extend(
        [
            "",
            "## Claim Discipline",
            "",
            "- No official frozen outputs are changed.",
            "- No retuning is performed.",
            "- No ordinary superluminal neutrino claim is made.",
            "- No ordinary environmental mass drift claim is made.",
            "- No claim of replacing the Standard Model or proving BHSM is made.",
            "- No claim of a complete first-principles Standard Model derivation is made.",
            "",
        ]
    )
    return "\n".join(lines)


def export_colored_lower_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export theory and audit artifacts."""

    base = Path(root)
    payload = audit_payload()
    markdown = render_markdown(payload)
    paths = {
        "theory": base / "theory" / "colored_lower_doublet_coframe_bonus.md",
        "audit_md": base / "audits" / "colored_lower_doublet_coframe_bonus_audit.md",
        "audit_json": base / "audits" / "colored_lower_doublet_coframe_bonus_audit.json",
    }
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    paths["theory"].write_text(markdown, encoding="utf-8")
    paths["audit_md"].write_text(markdown, encoding="utf-8")
    paths["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_colored_lower_outputs()
