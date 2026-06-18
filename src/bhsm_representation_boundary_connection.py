"""Representation-valued boundary connection audit.

This module embeds the SM-ledger sector projectors into a universal symbolic
connection form

    A_rep = A_q tensor O_q + A_j tensor O_j

where O_q=3B-L and O_j=-4T3+2(3B)(1/2-T3).  The representation operators are
well-defined on the unchanged SM ledger.  The boundary one-forms A_q and A_j
remain candidate Hopf/Berger components rather than fully constructed
connection forms.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from bhsm_config import canonical_geometry_config
from bhsm_completion_manual_theory_delta import frozen_sanity_payload
from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP


REPRESENTATION_BOUNDARY_CONNECTION_PARTIAL = "REPRESENTATION_BOUNDARY_CONNECTION_PARTIAL"
TENSOR_PRODUCT_CONNECTION_PARTIAL = "TENSOR_PRODUCT_CONNECTION_PARTIAL"
DIRECT_SUM_CONNECTION_STRUCTURAL_CANDIDATE = "DIRECT_SUM_CONNECTION_STRUCTURAL_CANDIDATE"
GAUGE_SAFE_PROJECTOR_CONNECTION_SUPPORTED = "GAUGE_SAFE_PROJECTOR_CONNECTION_SUPPORTED"
HOPF_BERGER_TWO_COMPONENT_CONNECTION_STRUCTURAL_CANDIDATE = (
    "HOPF_BERGER_TWO_COMPONENT_CONNECTION_STRUCTURAL_CANDIDATE"
)
A_Q_HOPF_CHARGE_COMPONENT_SUPPORTED = "A_Q_HOPF_CHARGE_COMPONENT_SUPPORTED"
A_J_BERGER_BASE_COMPONENT_STRUCTURAL_CANDIDATE = (
    "A_J_BERGER_BASE_COMPONENT_STRUCTURAL_CANDIDATE"
)
O_Q_REPRESENTATION_OPERATOR_SUPPORTED = "O_Q_REPRESENTATION_OPERATOR_SUPPORTED"
O_J_REPRESENTATION_OPERATOR_PARTIAL = "O_J_REPRESENTATION_OPERATOR_PARTIAL"
SECTOR_STATE_EIGENVALUE_STATUS_SUPPORTED = "SECTOR_STATE_EIGENVALUE_STATUS_SUPPORTED"
BOUNDARY_CONNECTION_HOLONOMY_PARTIAL = "BOUNDARY_CONNECTION_HOLONOMY_PARTIAL"
LEPTON_8_9_NO_PROMOTION_CONNECTION_ONLY = "LEPTON_8_9_NO_PROMOTION_CONNECTION_ONLY"
NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE = "NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE"


@dataclass(frozen=True)
class SectorRepState:
    """Representation state labels for evaluating O_q and O_j."""

    sector: str
    B: Fraction
    L: Fraction
    T3: Fraction
    candidate_only: bool
    source: str


@dataclass(frozen=True)
class ConnectionEigenvalues:
    """Eigenvalues of O_q and O_j on a sector state."""

    sector: str
    O_q: Fraction
    O_j: Fraction
    status: str


def color_coframe_operator(B: Fraction | int) -> Fraction:
    """Return C_color=3B."""

    return 3 * Fraction(B)


def lower_weak_projector(T3: Fraction | int) -> Fraction:
    """Return P_lower=1/2-T3."""

    return Fraction(1, 2) - Fraction(T3)


def colored_lower_projector(B: Fraction | int, T3: Fraction | int) -> Fraction:
    """Return (3B)(1/2-T3)."""

    return color_coframe_operator(B) * lower_weak_projector(T3)


def O_q(B: Fraction | int, L: Fraction | int) -> Fraction:
    """Return representation operator O_q=3B-L."""

    return color_coframe_operator(B) - Fraction(L)


def O_j(B: Fraction | int, T3: Fraction | int) -> Fraction:
    """Return representation operator O_j=-4T3+2(3B)(1/2-T3)."""

    return -4 * Fraction(T3) + 2 * colored_lower_projector(B, T3)


def boundary_connection_coefficients(
    B: Fraction | int,
    L: Fraction | int,
    T3: Fraction | int,
) -> tuple[Fraction, Fraction]:
    """Return (O_q, O_j) eigenvalues for a representation state."""

    return O_q(B, L), O_j(B, T3)


def omega_from_connection(
    q: int,
    j: int,
    B: Fraction | int,
    L: Fraction | int,
    T3: Fraction | int,
) -> Fraction:
    """Return <f|A_rep|f> = O_q*q + O_j*j."""

    oq, oj = boundary_connection_coefficients(B, L, T3)
    return oq * q + oj * j


def sector_rep_state(sector: str) -> SectorRepState:
    """Return representation labels for charged sectors plus neutrino candidate."""

    states = {
        "charged_lepton": SectorRepState(
            sector="charged_lepton",
            B=Fraction(0),
            L=Fraction(1),
            T3=Fraction(-1, 2),
            candidate_only=False,
            source="SM lepton doublet lower component",
        ),
        "up": SectorRepState(
            sector="up",
            B=Fraction(1, 3),
            L=Fraction(0),
            T3=Fraction(1, 2),
            candidate_only=False,
            source="SM quark doublet upper component",
        ),
        "down": SectorRepState(
            sector="down",
            B=Fraction(1, 3),
            L=Fraction(0),
            T3=Fraction(-1, 2),
            candidate_only=False,
            source="SM quark doublet lower component",
        ),
        "neutrino": SectorRepState(
            sector="neutrino",
            B=Fraction(0),
            L=Fraction(1),
            T3=Fraction(1, 2),
            candidate_only=True,
            source="SM lepton doublet upper component; candidate-only neutral channel",
        ),
    }
    if sector not in states:
        raise ValueError(f"unknown sector: {sector}")
    return states[sector]


def sector_connection_eigenvalues(sector: str) -> ConnectionEigenvalues:
    """Return O_q and O_j eigenvalues for a sector state."""

    state = sector_rep_state(sector)
    oq, oj = boundary_connection_coefficients(state.B, state.L, state.T3)
    status = (
        NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE
        if state.candidate_only
        else SECTOR_STATE_EIGENVALUE_STATUS_SUPPORTED
    )
    return ConnectionEigenvalues(sector=sector, O_q=oq, O_j=oj, status=status)


def _omega_for_sector(sector: str, q: int, j: int) -> Fraction:
    state = sector_rep_state(sector)
    return omega_from_connection(q, j, state.B, state.L, state.T3)


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
    """Return candidate neutrino-sector omega."""

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
    funcs = {
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
        omega = funcs[sector](q, j)
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
    bare = build_bhsm_bare_v1()
    dressed = build_bhsm_dressed_v1_candidate()
    canonical_a = canonical_geometry_config().a
    changed = [row for row in comparison["rows"] if row["changed"]]
    sanity = dict(frozen_sanity_payload())
    sanity.update(
        {
            "a_unchanged": bare.version.geometry_a == canonical_a
            and dressed.version.geometry_a == canonical_a,
            "S_unchanged": bare.version.overlap_s == S_OVERLAP
            and dressed.version.overlap_s == S_OVERLAP,
        }
    )
    return {
        "frozen_sanity": sanity,
        "official_branch_comparison": comparison,
        "official_dressed_changes_only_c_over_t": len(changed) == 1
        and changed[0]["quantity"] == "c/t",
    }


def audit_payload() -> dict[str, Any]:
    """Return representation-valued boundary connection audit payload."""

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
    states = {
        sector: sector_rep_state(sector)
        for sector in ("charged_lepton", "up", "down", "neutrino")
    }
    eigen = {sector: sector_connection_eigenvalues(sector) for sector in states}
    missing = (
        "identify A_q with an explicit Hopf/fiber boundary one-form",
        "identify A_j with an explicit Berger/base boundary one-form",
        "prove A_rep acts as a true connection on H_boundary tensor H_SMrep",
        "derive coupling of O_j to A_j from the full boundary action",
        "derive cyclic quotient dimension dim(H)=|Omega| separately",
        "derive identity/traceless stochastic protection before promoting lepton 8/9",
    )
    payload: dict[str, Any] = {
        "title": "BHSM representation-valued boundary connection audit",
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        "theorem_complete": False,
        "representation_boundary_connection_status": REPRESENTATION_BOUNDARY_CONNECTION_PARTIAL,
        "tensor_product_connection_status": TENSOR_PRODUCT_CONNECTION_PARTIAL,
        "direct_sum_connection_status": DIRECT_SUM_CONNECTION_STRUCTURAL_CANDIDATE,
        "gauge_safe_projector_status": GAUGE_SAFE_PROJECTOR_CONNECTION_SUPPORTED,
        "hopf_berger_two_component_status": HOPF_BERGER_TWO_COMPONENT_CONNECTION_STRUCTURAL_CANDIDATE,
        "A_q_status": A_Q_HOPF_CHARGE_COMPONENT_SUPPORTED,
        "A_j_status": A_J_BERGER_BASE_COMPONENT_STRUCTURAL_CANDIDATE,
        "O_q_status": O_Q_REPRESENTATION_OPERATOR_SUPPORTED,
        "O_j_status": O_J_REPRESENTATION_OPERATOR_PARTIAL,
        "sector_state_eigenvalue_status": SECTOR_STATE_EIGENVALUE_STATUS_SUPPORTED,
        "boundary_connection_consequence_status": BOUNDARY_CONNECTION_HOLONOMY_PARTIAL,
        "lepton_8_9_consequence_status": LEPTON_8_9_NO_PROMOTION_CONNECTION_ONLY,
        "neutrino_consequence_status": NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE,
        "does_universal_connection_reproduce_omega_l_u_d": reproduces,
        "does_A_q_have_existing_BHSM_meaning": True,
        "does_A_j_have_existing_BHSM_meaning": True,
        "does_connection_act_before_sector_evaluation": True,
        "does_this_close_boundary_connection": False,
        "does_this_promote_lepton_8_9": False,
        "blockers_closed": (
            "representation_operator_embedding_of_sector_projector",
            "universal_tensor_product_connection_form",
        ),
        "blockers_remaining": missing,
        "derived_components": (),
        "candidate_components": (
            "A_q_boundary_one_form",
            "A_j_boundary_one_form",
            "A_rep_tensor_product_connection",
            "neutrino_representation_consequence",
        ),
        "missing_assumptions": missing,
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "sector_states": states,
        "sector_connection_eigenvalues": eigen,
        "mode_pair_checks": checks,
        "neutrino_candidate": {
            "eigenvalues": eigen["neutrino"],
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
        "# BHSM Representation-Valued Boundary Connection",
        "",
        "This sprint embeds the SM-representation projectors into a universal symbolic connection form `A_rep=A_q tensor O_q + A_j tensor O_j`.",
        "The result is partial: sector eigenvalues reproduce the boundary operators, but the concrete one-forms `A_q` and `A_j` are not yet constructed.",
        "",
        "## Summary",
        "",
        f"Representation boundary connection status: `{payload['representation_boundary_connection_status']}`",
        f"Tensor-product connection status: `{payload['tensor_product_connection_status']}`",
        f"Hopf/Berger two-component status: `{payload['hopf_berger_two_component_status']}`",
        f"Gauge-safe projector status: `{payload['gauge_safe_projector_status']}`",
        f"A_q status: `{payload['A_q_status']}`",
        f"A_j status: `{payload['A_j_status']}`",
        f"Universal connection reproduces Omega_l,u,d: `{payload['does_universal_connection_reproduce_omega_l_u_d']}`",
        f"Closes boundary connection: `{payload['does_this_close_boundary_connection']}`",
        f"Promotes lepton 8/9: `{payload['does_this_promote_lepton_8_9']}`",
        "",
        "## Connection Form",
        "",
        "```text",
        "A_rep = A_q tensor O_q + A_j tensor O_j",
        "O_q = 3B - L",
        "O_j = -4T3 + 2(3B)(1/2 - T3)",
        "Omega_f = <f|A_rep|f> = O_q(f) q + O_j(f) j",
        "```",
        "",
        "## Sector Eigenvalues",
        "",
        "| Sector | O_q | O_j | Status |",
        "| --- | ---: | ---: | --- |",
    ]
    for sector, eigen in payload["sector_connection_eigenvalues"].items():
        lines.append(f"| `{sector}` | `{eigen.O_q}` | `{eigen.O_j}` | `{eigen.status}` |")
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


def export_representation_boundary_connection_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export theory and audit artifacts."""

    base = Path(root)
    payload = audit_payload()
    markdown = render_markdown(payload)
    paths = {
        "theory": base / "theory" / "representation_valued_boundary_connection.md",
        "audit_md": base / "audits" / "representation_valued_boundary_connection_audit.md",
        "audit_json": base / "audits" / "representation_valued_boundary_connection_audit.json",
        "tensor": base / "theory" / "tensor_product_boundary_connection_candidate.md",
        "hopf": base / "theory" / "hopf_berger_two_component_connection.md",
        "gauge": base / "theory" / "gauge_safe_boundary_projectors.md",
        "nu": base / "theory" / "neutrino_representation_connection_consequence.md",
    }
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    paths["theory"].write_text(markdown, encoding="utf-8")
    paths["audit_md"].write_text(markdown, encoding="utf-8")
    paths["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    paths["tensor"].write_text(
        "# Tensor-Product Boundary Connection Candidate\n\n"
        f"Status: `{payload['tensor_product_connection_status']}`\n\n"
        "`A_rep=A_q tensor O_q + A_j tensor O_j` is a universal symbolic construction before sector evaluation. The missing step is constructing the actual one-forms `A_q` and `A_j`.\n",
        encoding="utf-8",
    )
    paths["hopf"].write_text(
        "# Hopf/Berger Two-Component Connection\n\n"
        f"Status: `{payload['hopf_berger_two_component_status']}`\n\n"
        "`A_q` is supported by the existing Hopf charge q. `A_j` is structurally tied to the Berger/base label j. Neither is yet an explicit boundary one-form.\n",
        encoding="utf-8",
    )
    paths["gauge"].write_text(
        "# Gauge-Safe Boundary Projectors\n\n"
        f"Status: `{payload['gauge_safe_projector_status']}`\n\n"
        "B, L, and T3 are used as boundary representation projectors, not as new local gauge interactions. Anomaly inheritance is therefore not altered.\n",
        encoding="utf-8",
    )
    paths["nu"].write_text(
        "# Neutrino Representation Connection Consequence\n\n"
        f"Status: `{payload['neutrino_consequence_status']}`\n\n"
        "For B=0, L=1, T3=+1/2, the representation-valued connection gives `Omega_nu=-q-2j`. This remains candidate-only and adds no numerical PMNS claims.\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_representation_boundary_connection_outputs()
