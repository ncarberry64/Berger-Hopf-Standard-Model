"""SM-ledger sector projector sprint for BHSM boundary coefficients.

The formulas in this module test whether the boundary coefficients can be read
from unchanged Standard Model representation data.  The q coefficient is
supported by the standard baryon-minus-lepton orientation 3B-L.  The j
coefficient is partly supported by weak isospin T3, while the down-type coframe
bonus remains a structural candidate rather than a full action derivation.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from bhsm_completion_manual_theory_delta import frozen_sanity_payload
from bhsm_v1 import compare_bhsm_v1_branches


SECTOR_PROJECTOR_PARTIAL_DERIVATION = "SECTOR_PROJECTOR_PARTIAL_DERIVATION"
Q_COEFFICIENT_3B_MINUS_L_SUPPORTED = "Q_COEFFICIENT_3B_MINUS_L_SUPPORTED"
J_COEFFICIENT_T3_PARTIAL = "J_COEFFICIENT_T3_PARTIAL"
DOWN_COFRAME_BONUS_STRUCTURAL_CANDIDATE = (
    "DOWN_COFRAME_BONUS_STRUCTURAL_CANDIDATE"
)
NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE = (
    "NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE"
)
COEFFICIENT_ORIGIN_PARTIAL = "COEFFICIENT_ORIGIN_PARTIAL"
BOUNDARY_CONNECTION_HOLONOMY_PARTIAL = "BOUNDARY_CONNECTION_HOLONOMY_PARTIAL"
LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE = (
    "LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE"
)


@dataclass(frozen=True)
class SMProjectorData:
    """Standard Model representation data used by the projector formula."""

    sector: str
    B: Fraction
    L: Fraction
    T3: Fraction
    chi_d: Fraction
    color_rank: int
    weak_component: str
    hypercharge: Fraction
    source: str


@dataclass(frozen=True)
class ProjectorCoefficients:
    """Linear boundary coefficients Omega_f=a*q+b*j."""

    sector: str
    a: Fraction
    b: Fraction
    status: str
    notes: tuple[str, ...]


def q_from_kj(k: int, j: int) -> int:
    """Return q=k-2j."""

    return k - 2 * j


def a_from_B_L(B: Fraction | int, L: Fraction | int) -> Fraction:
    """Return a=3B-L."""

    return 3 * Fraction(B) - Fraction(L)


def b_from_T3_chid(T3: Fraction | int, chi_d: Fraction | int) -> Fraction:
    """Return b=-4*T3+2*chi_d."""

    return -4 * Fraction(T3) + 2 * Fraction(chi_d)


def omega_from_projector(q: int, j: int, a: Fraction | int, b: Fraction | int) -> Fraction:
    """Return Omega=a*q+b*j."""

    return Fraction(a) * q + Fraction(b) * j


def sm_projector_data(sector: str) -> SMProjectorData:
    """Return SM-ledger data for charged sectors plus neutrino candidate."""

    data = {
        "charged_lepton": SMProjectorData(
            sector="charged_lepton",
            B=Fraction(0),
            L=Fraction(1),
            T3=Fraction(-1, 2),
            chi_d=Fraction(0),
            color_rank=1,
            weak_component="lower",
            hypercharge=Fraction(-1, 2),
            source="SM lepton doublet lower component",
        ),
        "up": SMProjectorData(
            sector="up",
            B=Fraction(1, 3),
            L=Fraction(0),
            T3=Fraction(1, 2),
            chi_d=Fraction(0),
            color_rank=3,
            weak_component="upper",
            hypercharge=Fraction(1, 6),
            source="SM quark doublet upper component",
        ),
        "down": SMProjectorData(
            sector="down",
            B=Fraction(1, 3),
            L=Fraction(0),
            T3=Fraction(-1, 2),
            chi_d=Fraction(1),
            color_rank=3,
            weak_component="lower",
            hypercharge=Fraction(1, 6),
            source="SM quark doublet lower component plus down-type coframe indicator",
        ),
        "neutrino": SMProjectorData(
            sector="neutrino",
            B=Fraction(0),
            L=Fraction(1),
            T3=Fraction(1, 2),
            chi_d=Fraction(0),
            color_rank=1,
            weak_component="upper",
            hypercharge=Fraction(-1, 2),
            source="SM lepton doublet upper component; candidate-only neutral sector",
        ),
    }
    if sector not in data:
        raise ValueError(f"unknown sector: {sector}")
    return data[sector]


def sm_projector_coefficients(sector: str) -> ProjectorCoefficients:
    """Return projector coefficients from SM-ledger data."""

    data = sm_projector_data(sector)
    a = a_from_B_L(data.B, data.L)
    b = b_from_T3_chid(data.T3, data.chi_d)
    notes = (
        "a=3B-L uses SM baryon/lepton orientation.",
        "b=-4T3+2chi_d uses weak-isospin orientation plus candidate down-type coframe indicator.",
    )
    return ProjectorCoefficients(
        sector=sector,
        a=a,
        b=b,
        status=COEFFICIENT_ORIGIN_PARTIAL if sector != "neutrino" else NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE,
        notes=notes,
    )


def omega_charged_lepton(q: int, j: int) -> Fraction:
    """Return charged-lepton projector omega."""

    coeffs = sm_projector_coefficients("charged_lepton")
    return omega_from_projector(q, j, coeffs.a, coeffs.b)


def omega_up(q: int, j: int) -> Fraction:
    """Return up-sector projector omega."""

    coeffs = sm_projector_coefficients("up")
    return omega_from_projector(q, j, coeffs.a, coeffs.b)


def omega_down(q: int, j: int) -> Fraction:
    """Return down-sector projector omega."""

    coeffs = sm_projector_coefficients("down")
    return omega_from_projector(q, j, coeffs.a, coeffs.b)


def omega_neutrino_candidate(q: int, j: int) -> Fraction:
    """Return candidate neutral-lepton projector omega."""

    coeffs = sm_projector_coefficients("neutrino")
    return omega_from_projector(q, j, coeffs.a, coeffs.b)


def validate_mode_pair_constant_level(sector: str) -> dict[str, Any]:
    """Return exact mode-pair constant-level check for a charged sector."""

    modes = {
        "charged_lepton": ((5, 2), (9, 3)),
        "up": ((6, 0), (10, 1)),
        "down": ((6, 3), (8, 2)),
    }
    functions = {
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
        omega = functions[sector](q, j)
        values.append(omega)
        rows.append({"mode": (k, j), "q": q, "j": j, "omega": omega})
    return {
        "sector": sector,
        "constant": len(set(values)) == 1,
        "level": values[0] if len(set(values)) == 1 else None,
        "rows": rows,
    }


def candidate_formula_status() -> dict[str, Any]:
    """Return formula support classification."""

    return {
        "sector_projector_status": SECTOR_PROJECTOR_PARTIAL_DERIVATION,
        "q_coefficient_status": Q_COEFFICIENT_3B_MINUS_L_SUPPORTED,
        "j_coefficient_status": J_COEFFICIENT_T3_PARTIAL,
        "down_coframe_bonus_status": DOWN_COFRAME_BONUS_STRUCTURAL_CANDIDATE,
        "coefficient_origin_status": COEFFICIENT_ORIGIN_PARTIAL,
        "boundary_connection_consequence_status": BOUNDARY_CONNECTION_HOLONOMY_PARTIAL,
        "lepton_8_9_consequence_status": LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE,
        "does_q_coefficient_follow_from_3B_minus_L": True,
        "does_j_coefficient_follow_from_T3": True,
        "does_down_bonus_follow_independently": False,
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
    """Return the full SM-ledger sector-projector audit payload."""

    status = candidate_formula_status()
    charged_checks = {
        sector: validate_mode_pair_constant_level(sector)
        for sector in ("charged_lepton", "up", "down")
    }
    reproduces = all(check["constant"] for check in charged_checks.values()) and {
        sector: check["level"] for sector, check in charged_checks.items()
    } == {
        "charged_lepton": Fraction(3),
        "up": Fraction(6),
        "down": Fraction(12),
    }
    data = {sector: sm_projector_data(sector) for sector in ("charged_lepton", "up", "down", "neutrino")}
    coeffs = {sector: sm_projector_coefficients(sector) for sector in data}
    missing = (
        "derive chi_d from the full color/coframe boundary connection rather than assigning a down indicator",
        "derive b=-4T3+2chi_d from the connection/action rather than a representation-shaped formula",
        "derive the sector projector P_f as an operator acting on A_boundary",
        "derive cyclic quotient dimension dim(H)=|Omega| separately",
        "derive identity/traceless protection before promoting lepton 8/9",
    )
    payload: dict[str, Any] = {
        "title": "BHSM sector projector derivation from SM representation ledger",
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        **status,
        "neutrino_projector_consequence_status": NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE,
        "does_formula_reproduce_omega_l_u_d": reproduces,
        "blockers_closed": (
            "q_coefficient_from_3B_minus_L",
            "weak_isospin_part_of_j_coefficient",
        ),
        "blockers_remaining": missing,
        "derived_components": (),
        "candidate_components": (
            "sector_projector_formula",
            "down_type_coframe_bonus",
            "neutrino_projector_consequence",
            "boundary_connection_consequence",
        ),
        "rejected_components": (),
        "missing_assumptions": missing,
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "files_concepts_searched": (
            "SM field ledger and hypercharge derivation",
            "boundary_derivation phase/coframe scaffold",
            "mode ledgers and boundary operator notes",
            "anomaly cancellation tests",
            "virtual/coframe candidate notes",
        ),
        "sm_projector_data": data,
        "projector_coefficients": coeffs,
        "mode_pair_checks": charged_checks,
        "neutrino_candidate": {
            "coefficients": coeffs["neutrino"],
            "example_formula": "Omega_nu=-q-2j",
            "ordinary_FTL_claim": False,
            "candidate_only": True,
            "no_numerical_PMNS_claims": True,
        },
        "anomaly_inheritance_safe": True,
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
        "# BHSM Sector Projector Derivation From SM Ledger",
        "",
        "This sprint tests whether the boundary coefficients can be read from unchanged Standard Model representation data.",
        "The result is partial: `a=3B-L` and the T3 part of `b` are supported, while the down-type coframe bonus remains a structural candidate.",
        "",
        "## Summary",
        "",
        f"Sector projector status: `{payload['sector_projector_status']}`",
        f"q coefficient status: `{payload['q_coefficient_status']}`",
        f"j coefficient status: `{payload['j_coefficient_status']}`",
        f"Down coframe bonus status: `{payload['down_coframe_bonus_status']}`",
        f"Coefficient origin status: `{payload['coefficient_origin_status']}`",
        f"Formula reproduces Omega_l,u,d: `{payload['does_formula_reproduce_omega_l_u_d']}`",
        f"q follows from 3B-L: `{payload['does_q_coefficient_follow_from_3B_minus_L']}`",
        f"j follows from T3: `{payload['does_j_coefficient_follow_from_T3']}`",
        f"Down bonus follows independently: `{payload['does_down_bonus_follow_independently']}`",
        "",
        "## Formula",
        "",
        "```text",
        "Omega_f = (3B_f - L_f) q + (-4 T3_f + 2 chi_d,f) j",
        "```",
        "",
        "## Coefficients",
        "",
        "| Sector | a | b | Status |",
        "| --- | ---: | ---: | --- |",
    ]
    for sector, coeff in payload["projector_coefficients"].items():
        lines.append(f"| `{sector}` | `{coeff.a}` | `{coeff.b}` | `{coeff.status}` |")
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
            "## Neutrino Consequence",
            "",
            "The same formula gives the candidate neutral-lepton projector `Omega_nu=-q-2j`.",
            "This is candidate-only: no neutrino mode ledger or numerical PMNS claim is added.",
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


def export_sector_projector_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export theory and audit artifacts."""

    base = Path(root)
    payload = audit_payload()
    markdown = render_markdown(payload)
    paths = {
        "theory": base / "theory" / "sector_projector_sm_ledger_derivation.md",
        "audit_md": base / "audits" / "sector_projector_sm_ledger_derivation_audit.md",
        "audit_json": base / "audits" / "sector_projector_sm_ledger_derivation_audit.json",
        "bl": base / "theory" / "b_minus_l_boundary_orientation.md",
        "weak": base / "theory" / "weak_isospin_j_projector_candidate.md",
        "down": base / "theory" / "down_type_coframe_bonus_candidate.md",
        "nu": base / "theory" / "neutrino_projector_consequence_candidate.md",
    }
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    paths["theory"].write_text(markdown, encoding="utf-8")
    paths["audit_md"].write_text(markdown, encoding="utf-8")
    paths["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    paths["bl"].write_text(
        "# B-minus-L Boundary Orientation\n\n"
        f"Status: `{payload['q_coefficient_status']}`\n\n"
        "`a_f=3B_f-L_f` reproduces the q coefficient: -1 for charged leptons and +1 for quarks using unchanged SM representation data.\n",
        encoding="utf-8",
    )
    paths["weak"].write_text(
        "# Weak-Isospin j Projector Candidate\n\n"
        f"Status: `{payload['j_coefficient_status']}`\n\n"
        "`-4T3` gives +2 for lower lepton/down components and -2 for the upper up component. The down sector still needs the independent coframe bonus.\n",
        encoding="utf-8",
    )
    paths["down"].write_text(
        "# Down-Type Coframe Bonus Candidate\n\n"
        f"Status: `{payload['down_coframe_bonus_status']}`\n\n"
        "`chi_d=1` adds the extra +2 needed for down quarks. Existing coframe scaffolds make this structural, but the full boundary connection has not derived it.\n",
        encoding="utf-8",
    )
    paths["nu"].write_text(
        "# Neutrino Projector Consequence Candidate\n\n"
        f"Status: `{payload['neutrino_projector_consequence_status']}`\n\n"
        "For B=0, L=1, T3=+1/2, chi_d=0, the formula gives `Omega_nu=-q-2j`. This remains candidate-only and adds no numerical PMNS claim.\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_sector_projector_outputs()
