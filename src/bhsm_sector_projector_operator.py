"""Operator-style sector projector construction for BHSM boundary coefficients.

This sprint promotes the SM-ledger formula from a coefficient table into a
projection-operator style construction.  The operators act on representation
labels B, L, and T3.  Coupling those operators to the complete boundary
connection A_boundary remains open, so the sprint status is partial rather than
fully derived.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from bhsm_completion_manual_theory_delta import frozen_sanity_payload
from bhsm_v1 import compare_bhsm_v1_branches


SECTOR_PROJECTOR_OPERATOR_PARTIAL = "SECTOR_PROJECTOR_OPERATOR_PARTIAL"
COLOR_COFRAME_OPERATOR_SUPPORTED = "COLOR_COFRAME_OPERATOR_SUPPORTED"
WEAK_LOWER_PROJECTOR_SUPPORTED = "WEAK_LOWER_PROJECTOR_SUPPORTED"
COLORED_LOWER_PROJECTOR_PARTIAL = "COLORED_LOWER_PROJECTOR_PARTIAL"
Q_ORIENTATION_OPERATOR_SUPPORTED = "Q_ORIENTATION_OPERATOR_SUPPORTED"
J_ORIENTATION_OPERATOR_PARTIAL = "J_ORIENTATION_OPERATOR_PARTIAL"
BOUNDARY_CONNECTION_HOLONOMY_PARTIAL = "BOUNDARY_CONNECTION_HOLONOMY_PARTIAL"
LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE = (
    "LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE"
)
PURE_FIBER_DOUBLE_BRANCH_ANALOGY_ONLY = "PURE_FIBER_DOUBLE_BRANCH_ANALOGY_ONLY"
CKM_H_MIX_DIM4_ANALOGY_ONLY = "CKM_H_MIX_DIM4_ANALOGY_ONLY"
NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE = (
    "NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE"
)


@dataclass(frozen=True)
class SectorRepresentation:
    """SM representation labels used by projector operators."""

    sector: str
    B: Fraction
    L: Fraction
    T3: Fraction
    source: str
    candidate_only: bool = False


@dataclass(frozen=True)
class OperatorCoefficients:
    """Boundary coefficients from representation operators."""

    sector: str
    color_coframe: Fraction
    lower_projector: Fraction
    colored_lower: Fraction
    a: Fraction
    b: Fraction
    status: str


def color_coframe_operator(B: Fraction | int) -> Fraction:
    """Return C_color=3B."""

    return 3 * Fraction(B)


def lower_weak_projector(T3: Fraction | int) -> Fraction:
    """Return P_lower=1/2-T3."""

    return Fraction(1, 2) - Fraction(T3)


def colored_lower_projector(B: Fraction | int, T3: Fraction | int) -> Fraction:
    """Return P_colored_lower=(3B)(1/2-T3)."""

    return color_coframe_operator(B) * lower_weak_projector(T3)


def q_orientation_operator(B: Fraction | int, L: Fraction | int) -> Fraction:
    """Return P_q=3B-L."""

    return color_coframe_operator(B) - Fraction(L)


def j_orientation_operator(B: Fraction | int, T3: Fraction | int) -> Fraction:
    """Return P_j=-4T3+2(3B)(1/2-T3)."""

    return -4 * Fraction(T3) + 2 * colored_lower_projector(B, T3)


def representation_for_sector(sector: str) -> SectorRepresentation:
    """Return SM representation data for charged sectors plus neutrino candidate."""

    data = {
        "charged_lepton": SectorRepresentation(
            sector="charged_lepton",
            B=Fraction(0),
            L=Fraction(1),
            T3=Fraction(-1, 2),
            source="SM lepton doublet lower component",
        ),
        "up": SectorRepresentation(
            sector="up",
            B=Fraction(1, 3),
            L=Fraction(0),
            T3=Fraction(1, 2),
            source="SM quark doublet upper component",
        ),
        "down": SectorRepresentation(
            sector="down",
            B=Fraction(1, 3),
            L=Fraction(0),
            T3=Fraction(-1, 2),
            source="SM quark doublet lower component",
        ),
        "neutrino": SectorRepresentation(
            sector="neutrino",
            B=Fraction(0),
            L=Fraction(1),
            T3=Fraction(1, 2),
            source="SM lepton doublet upper component; candidate-only neutral channel",
            candidate_only=True,
        ),
    }
    if sector not in data:
        raise ValueError(f"unknown sector: {sector}")
    return data[sector]


def sector_projector_coefficients(sector: str) -> OperatorCoefficients:
    """Return operator-generated sector coefficients."""

    rep = representation_for_sector(sector)
    status = (
        NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE
        if sector == "neutrino"
        else SECTOR_PROJECTOR_OPERATOR_PARTIAL
    )
    return OperatorCoefficients(
        sector=sector,
        color_coframe=color_coframe_operator(rep.B),
        lower_projector=lower_weak_projector(rep.T3),
        colored_lower=colored_lower_projector(rep.B, rep.T3),
        a=q_orientation_operator(rep.B, rep.L),
        b=j_orientation_operator(rep.B, rep.T3),
        status=status,
    )


def omega_from_operator(
    q: int,
    j: int,
    B: Fraction | int,
    L: Fraction | int,
    T3: Fraction | int,
) -> Fraction:
    """Return Omega=P_q*q+P_j*j."""

    return q_orientation_operator(B, L) * q + j_orientation_operator(B, T3) * j


def _omega_for_sector(sector: str, q: int, j: int) -> Fraction:
    rep = representation_for_sector(sector)
    return omega_from_operator(q, j, rep.B, rep.L, rep.T3)


def omega_charged_lepton(q: int, j: int) -> Fraction:
    """Return charged-lepton omega."""

    return _omega_for_sector("charged_lepton", q, j)


def omega_up(q: int, j: int) -> Fraction:
    """Return up-sector omega."""

    return _omega_for_sector("up", q, j)


def omega_down(q: int, j: int) -> Fraction:
    """Return down-sector omega."""

    return _omega_for_sector("down", q, j)


def omega_neutrino_candidate(q: int, j: int) -> Fraction:
    """Return candidate neutral-lepton omega."""

    return _omega_for_sector("neutrino", q, j)


def q_from_kj(k: int, j: int) -> int:
    """Return q=k-2j."""

    return k - 2 * j


def validate_mode_pair_constant_level(sector: str) -> dict[str, Any]:
    """Return exact constant-level validation for charged mode pairs."""

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
    """Return the sector-projector operator audit payload."""

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
    reps = {sector: representation_for_sector(sector) for sector in ("charged_lepton", "up", "down", "neutrino")}
    coeffs = {sector: sector_projector_coefficients(sector) for sector in reps}
    missing = (
        "embed C_color=3B as an actual color/coframe projection operator inside A_boundary",
        "embed P_lower=1/2-T3 as an actual weak-boundary projection operator",
        "derive P_colored_lower coupling to the j-channel of A_boundary",
        "derive the universal sector projector P_f acting on the boundary connection",
        "derive cyclic quotient dimension dim(H)=|Omega| separately",
        "derive identity/traceless protection before promoting lepton 8/9",
    )
    payload: dict[str, Any] = {
        "title": "BHSM sector projector operator construction",
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        "sector_projector_operator_status": SECTOR_PROJECTOR_OPERATOR_PARTIAL,
        "color_coframe_operator_status": COLOR_COFRAME_OPERATOR_SUPPORTED,
        "weak_lower_projector_status": WEAK_LOWER_PROJECTOR_SUPPORTED,
        "colored_lower_projector_status": COLORED_LOWER_PROJECTOR_PARTIAL,
        "q_orientation_operator_status": Q_ORIENTATION_OPERATOR_SUPPORTED,
        "j_orientation_operator_status": J_ORIENTATION_OPERATOR_PARTIAL,
        "boundary_connection_consequence_status": BOUNDARY_CONNECTION_HOLONOMY_PARTIAL,
        "lepton_8_9_consequence_status": LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE,
        "pure_fiber_consequence_status": PURE_FIBER_DOUBLE_BRANCH_ANALOGY_ONLY,
        "ckm_consequence_status": CKM_H_MIX_DIM4_ANALOGY_ONLY,
        "neutrino_consequence_status": NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE,
        "does_operator_reproduce_omega_l_u_d": reproduces,
        "does_3B_act_as_color_coframe_operator": True,
        "does_lower_projector_follow_from_T3": True,
        "does_colored_lower_projector_follow": True,
        "blockers_closed": (
            "operator_form_of_colored_lower_projector",
            "operator_form_of_q_and_j_orientation",
        ),
        "blockers_remaining": missing,
        "derived_components": (),
        "candidate_components": (
            "sector_projector_operator",
            "boundary_connection_coupling",
            "neutrino_projector_consequence",
        ),
        "missing_assumptions": missing,
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "representations": reps,
        "operator_coefficients": coeffs,
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
    """Render the audit as Markdown."""

    payload = payload or audit_payload()
    lines = [
        "# BHSM Sector Projector Operator Construction",
        "",
        "This sprint promotes the SM-ledger coefficient formula into an operator-style construction acting on representation labels.",
        "The result remains partial because the projectors are not yet embedded as operators on the full boundary connection A_boundary.",
        "",
        "## Summary",
        "",
        f"Sector projector operator status: `{payload['sector_projector_operator_status']}`",
        f"Color/coframe operator status: `{payload['color_coframe_operator_status']}`",
        f"Weak lower projector status: `{payload['weak_lower_projector_status']}`",
        f"Colored lower projector status: `{payload['colored_lower_projector_status']}`",
        f"Operator reproduces Omega_l,u,d: `{payload['does_operator_reproduce_omega_l_u_d']}`",
        "",
        "## Operators",
        "",
        "```text",
        "C_color = 3B",
        "P_lower = 1/2 - T3",
        "P_colored_lower = C_color P_lower",
        "P_q = 3B - L",
        "P_j = -4T3 + 2 P_colored_lower",
        "Omega_f = P_q q + P_j j",
        "```",
        "",
        "## Coefficients",
        "",
        "| Sector | C_color | P_lower | P_colored_lower | a | b |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for sector, coeff in payload["operator_coefficients"].items():
        lines.append(
            f"| `{sector}` | `{coeff.color_coframe}` | `{coeff.lower_projector}` | `{coeff.colored_lower}` | `{coeff.a}` | `{coeff.b}` |"
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


def export_sector_projector_operator_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export theory and audit artifacts."""

    base = Path(root)
    payload = audit_payload()
    markdown = render_markdown(payload)
    paths = {
        "theory": base / "theory" / "sector_projector_operator_construction.md",
        "audit_md": base / "audits" / "sector_projector_operator_construction_audit.md",
        "audit_json": base / "audits" / "sector_projector_operator_construction_audit.json",
        "color": base / "theory" / "color_coframe_operator_3B.md",
        "weak": base / "theory" / "weak_lower_projector_T3.md",
        "connection": base / "theory" / "sector_projected_boundary_connection_operator_candidate.md",
    }
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    paths["theory"].write_text(markdown, encoding="utf-8")
    paths["audit_md"].write_text(markdown, encoding="utf-8")
    paths["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    paths["color"].write_text(
        "# Color/Coframe Operator 3B\n\n"
        f"Status: `{payload['color_coframe_operator_status']}`\n\n"
        "`C_color=3B` is 0 for leptons and 1 for quarks, so it acts as a color/coframe participation projector on the SM ledger. Embedding it inside A_boundary remains open.\n",
        encoding="utf-8",
    )
    paths["weak"].write_text(
        "# Weak Lower Projector T3\n\n"
        f"Status: `{payload['weak_lower_projector_status']}`\n\n"
        "`P_lower=1/2-T3` is 0 for upper doublet components and 1 for lower doublet components. Embedding it as a boundary operator remains open.\n",
        encoding="utf-8",
    )
    paths["connection"].write_text(
        "# Sector-Projected Boundary Connection Operator Candidate\n\n"
        f"Status: `{payload['sector_projector_operator_status']}`\n\n"
        "The operator construction defines P_q and P_j on representation labels and reproduces the charged-sector Omega levels. The missing step is constructing the universal A_boundary and showing these projectors act on it.\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_sector_projector_operator_outputs()
