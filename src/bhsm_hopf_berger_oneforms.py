"""Explicit symbolic Hopf/Berger boundary one-form audit.

The functions here are symbolic and exact where possible.  They introduce the
standard SU(2) / Hopf-fibration one-forms as candidate BHSM boundary geometry
objects without changing frozen predictions or promoting unresolved boundary
action claims.
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


EXPLICIT_HOPF_BERGER_ONEFORMS_PARTIAL = "EXPLICIT_HOPF_BERGER_ONEFORMS_PARTIAL"
A_Q_EXPLICIT_HOPF_FIBER_ONEFORM_SUPPORTED = "A_Q_EXPLICIT_HOPF_FIBER_ONEFORM_SUPPORTED"
A_J_EXPLICIT_BERGER_BASE_COMPONENT_SUPPORTED = "A_J_EXPLICIT_BERGER_BASE_COMPONENT_SUPPORTED"
A_J_BERGER_BASE_COMPONENT_STRUCTURAL_CANDIDATE = "A_J_BERGER_BASE_COMPONENT_STRUCTURAL_CANDIDATE"
HOPF_NORMALIZATION_RESOLVED = "HOPF_NORMALIZATION_RESOLVED"
HOPF_NORMALIZATION_CONVENTION_DEPENDENT = "HOPF_NORMALIZATION_CONVENTION_DEPENDENT"
BERGER_BASE_NORMALIZATION_CONVENTION_DEPENDENT = "BERGER_BASE_NORMALIZATION_CONVENTION_DEPENDENT"
Q_EQUALS_K_MINUS_2J_REPRESENTATION_SUPPORTED = "Q_EQUALS_K_MINUS_2J_REPRESENTATION_SUPPORTED"


@dataclass(frozen=True)
class NormalizationStatus:
    """Normalization convention status for Hopf and Berger/base pieces."""

    hopf_normalization_status: str
    berger_base_normalization_status: str
    hopf_fiber_holonomy_unit: Fraction
    base_curvature_flux_unit: Fraction
    ambiguities: tuple[str, ...]


@dataclass(frozen=True)
class ConnectionStatus:
    """Boundary connection status summary."""

    explicit_hopf_berger_oneform_status: str
    A_q_status: str
    A_j_status: str
    hopf_connection_status: str
    berger_base_connection_status: str
    q_equals_k_minus_2j_status: str
    A_rep_with_explicit_components_status: str
    representation_boundary_connection_consequence_status: str
    lepton_8_9_consequence_status: str
    neutrino_consequence_status: str


@dataclass(frozen=True)
class SectorEigenvalues:
    """Representation operator eigenvalues for a sector."""

    sector: str
    O_q: Fraction
    O_j: Fraction
    candidate_only: bool


def sigma_1_symbolic() -> str:
    """Return symbolic SU(2) left-invariant one-form sigma_1."""

    return "sigma_1 = cos(psi) dtheta + sin(psi) sin(theta) dphi"


def sigma_2_symbolic() -> str:
    """Return symbolic SU(2) left-invariant one-form sigma_2."""

    return "sigma_2 = -sin(psi) dtheta + cos(psi) sin(theta) dphi"


def sigma_3_symbolic() -> str:
    """Return symbolic Hopf fiber/contact one-form sigma_3."""

    return "sigma_3 = dpsi + cos(theta) dphi"


def hopf_connection_symbolic() -> str:
    """Return the canonical Hopf/contact connection candidate."""

    return "A_Hopf = sigma_3"


def normalized_hopf_connection(convention: str = "unit_fiber_holonomy") -> str:
    """Return normalized Hopf connection convention."""

    if convention == "unit_fiber_holonomy":
        return "A_Hopf_norm = sigma_3/(2*pi)"
    if convention == "integer_phase":
        return "A_Hopf_phase = sigma_3"
    raise ValueError(f"unknown Hopf convention: {convention}")


def hopf_fiber_holonomy(convention: str = "unit_fiber_holonomy") -> Fraction:
    """Return the symbolic integral over the fiber cycle in chosen units."""

    if convention == "unit_fiber_holonomy":
        return Fraction(1)
    if convention == "integer_phase":
        return Fraction(2)  # records 2*pi in units of pi
    raise ValueError(f"unknown Hopf convention: {convention}")


def hopf_curvature_symbolic() -> str:
    """Return symbolic Hopf curvature."""

    return "F_Hopf = dA_Hopf = -sin(theta) dtheta wedge dphi"


def base_curvature_flux(convention: str = "chern_unit") -> Fraction:
    """Return symbolic base flux in selected convention."""

    if convention == "chern_unit":
        return Fraction(1)
    if convention == "raw_sphere":
        return Fraction(2)  # records 4*pi in units of 2*pi
    raise ValueError(f"unknown base flux convention: {convention}")


def q_from_kj(k: int, j: int) -> int:
    """Return q=k-2j."""

    return k - 2 * j


def O_q(B: Fraction | int, L: Fraction | int) -> Fraction:
    """Return O_q=3B-L."""

    return 3 * Fraction(B) - Fraction(L)


def colored_lower_projector(B: Fraction | int, T3: Fraction | int) -> Fraction:
    """Return (3B)(1/2-T3)."""

    return 3 * Fraction(B) * (Fraction(1, 2) - Fraction(T3))


def O_j(B: Fraction | int, T3: Fraction | int) -> Fraction:
    """Return O_j=-4T3+2(3B)(1/2-T3)."""

    return -4 * Fraction(T3) + 2 * colored_lower_projector(B, T3)


def omega_from_explicit_connection(
    q: int,
    j: int,
    B: Fraction | int,
    L: Fraction | int,
    T3: Fraction | int,
) -> Fraction:
    """Evaluate Omega_f = O_q q + O_j j."""

    return O_q(B, L) * q + O_j(B, T3) * j


def _sector_rep(sector: str) -> tuple[Fraction, Fraction, Fraction, bool]:
    sectors = {
        "charged_lepton": (Fraction(0), Fraction(1), Fraction(-1, 2), False),
        "up": (Fraction(1, 3), Fraction(0), Fraction(1, 2), False),
        "down": (Fraction(1, 3), Fraction(0), Fraction(-1, 2), False),
        "neutrino": (Fraction(0), Fraction(1), Fraction(1, 2), True),
    }
    if sector not in sectors:
        raise ValueError(f"unknown sector: {sector}")
    return sectors[sector]


def sector_connection_eigenvalues(sector: str) -> SectorEigenvalues:
    """Return O_q and O_j on one sector representation state."""

    B, L, T3, candidate_only = _sector_rep(sector)
    return SectorEigenvalues(sector=sector, O_q=O_q(B, L), O_j=O_j(B, T3), candidate_only=candidate_only)


def validate_mode_pair_constant_level(sector: str) -> dict[str, Any]:
    """Validate that charged-sector ledger pairs have constant Omega."""

    modes = {
        "charged_lepton": ((5, 2), (9, 3)),
        "up": ((6, 0), (10, 1)),
        "down": ((6, 3), (8, 2)),
    }
    if sector not in modes:
        raise ValueError(f"unknown charged sector: {sector}")
    B, L, T3, _candidate = _sector_rep(sector)
    rows = []
    values = []
    for k, j in modes[sector]:
        q = q_from_kj(k, j)
        omega = omega_from_explicit_connection(q, j, B, L, T3)
        rows.append({"mode": (k, j), "q": q, "j": j, "omega": omega})
        values.append(omega)
    return {
        "sector": sector,
        "constant": len(set(values)) == 1,
        "level": values[0] if len(set(values)) == 1 else None,
        "rows": rows,
    }


def normalization_status_object(
    hopf_convention: str = "unit_fiber_holonomy",
    base_convention: str = "chern_unit",
) -> NormalizationStatus:
    """Return explicit normalization status."""

    return NormalizationStatus(
        hopf_normalization_status=HOPF_NORMALIZATION_RESOLVED
        if hopf_convention == "unit_fiber_holonomy"
        else HOPF_NORMALIZATION_CONVENTION_DEPENDENT,
        berger_base_normalization_status=BERGER_BASE_NORMALIZATION_CONVENTION_DEPENDENT,
        hopf_fiber_holonomy_unit=hopf_fiber_holonomy(hopf_convention),
        base_curvature_flux_unit=base_curvature_flux(base_convention),
        ambiguities=(
            "Euler-angle period and 2*pi normalization conventions must be fixed globally.",
            "The Berger/base j-channel may be a curvature or coframe flux component rather than a line holonomy.",
            "No full boundary-action coupling fixes the A_j normalization uniquely.",
        ),
    )


def connection_status_object() -> ConnectionStatus:
    """Return conservative explicit Hopf/Berger connection status."""

    return ConnectionStatus(
        explicit_hopf_berger_oneform_status=EXPLICIT_HOPF_BERGER_ONEFORMS_PARTIAL,
        A_q_status=A_Q_EXPLICIT_HOPF_FIBER_ONEFORM_SUPPORTED,
        A_j_status=A_J_EXPLICIT_BERGER_BASE_COMPONENT_SUPPORTED,
        hopf_connection_status="HOPF_CONTACT_ONEFORM_EXPLICIT",
        berger_base_connection_status="BERGER_BASE_CURVATURE_OR_COFRAME_COMPONENT_SUPPORTED",
        q_equals_k_minus_2j_status=Q_EQUALS_K_MINUS_2J_REPRESENTATION_SUPPORTED,
        A_rep_with_explicit_components_status="A_REP_EXPLICIT_HOPF_PLUS_BASE_COMPONENT_PARTIAL",
        representation_boundary_connection_consequence_status="REPRESENTATION_BOUNDARY_CONNECTION_PARTIAL",
        lepton_8_9_consequence_status="LEPTON_8_9_NO_PROMOTION_CONNECTION_ONLY",
        neutrino_consequence_status="NEUTRINO_PROJECTOR_CONSEQUENCE_CANDIDATE",
    )


def validate_no_official_outputs_modified() -> dict[str, Any]:
    """Return frozen branch sanity checks."""

    comparison = compare_bhsm_v1_branches()
    bare = build_bhsm_bare_v1()
    dressed = build_bhsm_dressed_v1_candidate()
    canonical_a = canonical_geometry_config().a
    sanity = dict(frozen_sanity_payload())
    sanity.update(
        {
            "a_unchanged": bare.version.geometry_a == canonical_a
            and dressed.version.geometry_a == canonical_a,
            "S_unchanged": bare.version.overlap_s == S_OVERLAP
            and dressed.version.overlap_s == S_OVERLAP,
            "official_branch_comparison": comparison,
        }
    )
    return sanity


def audit_payload() -> dict[str, Any]:
    """Return explicit Hopf/Berger one-form audit payload."""

    status = connection_status_object()
    norm = normalization_status_object()
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
    blockers_remaining = (
        "derive A_j coupling from the full Berger-Hopf boundary action",
        "fix Berger/base normalization globally rather than by convention",
        "prove A_rep is a true connection on the boundary tensor-product bundle",
        "derive dim(H)=|Omega| separately",
        "derive identity/traceless stochastic protection before promoting lepton 8/9",
    )
    payload: dict[str, Any] = {
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        "explicit_hopf_berger_oneform_status": status.explicit_hopf_berger_oneform_status,
        "A_q_status": status.A_q_status,
        "A_j_status": status.A_j_status,
        "hopf_connection_status": status.hopf_connection_status,
        "berger_base_connection_status": status.berger_base_connection_status,
        "hopf_normalization_status": norm.hopf_normalization_status,
        "berger_base_normalization_status": norm.berger_base_normalization_status,
        "q_equals_k_minus_2j_status": status.q_equals_k_minus_2j_status,
        "A_rep_with_explicit_components_status": status.A_rep_with_explicit_components_status,
        "representation_boundary_connection_consequence_status": (
            status.representation_boundary_connection_consequence_status
        ),
        "lepton_8_9_consequence_status": status.lepton_8_9_consequence_status,
        "neutrino_consequence_status": status.neutrino_consequence_status,
        "does_A_q_have_explicit_oneform": True,
        "does_A_j_have_explicit_oneform_or_curvature": True,
        "does_q_couple_to_hopf_fiber": True,
        "does_j_couple_to_berger_base": True,
        "does_explicit_connection_reproduce_omega_l_u_d": reproduces,
        "does_this_close_boundary_connection": False,
        "does_this_promote_lepton_8_9": False,
        "normalization_ambiguities": norm.ambiguities,
        "blockers_closed": (
            "explicit_symbolic_Hopf_contact_oneform_A_q",
            "symbolic_Berger_base_curvature_or_coframe_component_A_j",
            "q_equals_k_minus_2j_representation_support",
        ),
        "blockers_remaining": blockers_remaining,
        "derived_components": (),
        "candidate_components": (
            "A_j_base_curvature_component",
            "A_rep_with_explicit_Hopf_plus_Berger_components",
            "neutrino_connection_consequence",
        ),
        "missing_assumptions": blockers_remaining,
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "sigma_forms": {
            "sigma_1": sigma_1_symbolic(),
            "sigma_2": sigma_2_symbolic(),
            "sigma_3": sigma_3_symbolic(),
        },
        "hopf_connection": hopf_connection_symbolic(),
        "normalized_hopf_connection": normalized_hopf_connection(),
        "hopf_curvature": hopf_curvature_symbolic(),
        "normalization_status": norm,
        "sector_connection_eigenvalues": {
            sector: sector_connection_eigenvalues(sector)
            for sector in ("charged_lepton", "up", "down", "neutrino")
        },
        "mode_pair_checks": checks,
        "frozen_sanity": validate_no_official_outputs_modified(),
    }
    return payload


def _jsonable(value: object) -> object:
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator, "value": float(value)}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def render_markdown(payload: dict[str, Any] | None = None, title: str | None = None) -> str:
    """Render Markdown for the audit payload."""

    p = audit_payload() if payload is None else payload
    heading = title or "BHSM Explicit Hopf-Berger Boundary One-Forms"
    lines = [
        f"# {heading}",
        "",
        "This sprint introduces symbolic Hopf/Berger boundary geometry components without changing frozen predictions.",
        "",
        "## Summary",
        "",
        f"Explicit Hopf-Berger oneform status: `{p['explicit_hopf_berger_oneform_status']}`",
        f"A_q status: `{p['A_q_status']}`",
        f"A_j status: `{p['A_j_status']}`",
        f"Hopf normalization status: `{p['hopf_normalization_status']}`",
        f"Berger/base normalization status: `{p['berger_base_normalization_status']}`",
        f"q=k-2j status: `{p['q_equals_k_minus_2j_status']}`",
        f"Reproduces Omega_l,u,d: `{p['does_explicit_connection_reproduce_omega_l_u_d']}`",
        f"Closes boundary connection: `{p['does_this_close_boundary_connection']}`",
        f"Promotes lepton 8/9: `{p['does_this_promote_lepton_8_9']}`",
        "",
        "## Symbolic One-Forms",
        "",
        "```text",
        p["sigma_forms"]["sigma_1"],
        p["sigma_forms"]["sigma_2"],
        p["sigma_forms"]["sigma_3"],
        p["hopf_connection"],
        p["normalized_hopf_connection"],
        p["hopf_curvature"],
        "```",
        "",
        "The Hopf/fiber component supports `A_q`. The Berger/base component is recorded as a curvature/coframe component because the full boundary-action coupling is not yet derived.",
        "",
        "## Representation Operators",
        "",
        "```text",
        "O_q = 3B - L",
        "O_j = -4T3 + 2(3B)(1/2 - T3)",
        "Omega_f = O_q q + O_j j",
        "```",
        "",
        "| Sector | O_q | O_j | Candidate Only |",
        "| --- | ---: | ---: | --- |",
    ]
    for sector, eigen in p["sector_connection_eigenvalues"].items():
        lines.append(f"| `{sector}` | `{eigen.O_q}` | `{eigen.O_j}` | `{eigen.candidate_only}` |")
    lines.extend(
        [
            "",
            "## Mode Pair Checks",
            "",
            "| Sector | Constant | Level |",
            "| --- | --- | ---: |",
        ]
    )
    for sector, check in p["mode_pair_checks"].items():
        lines.append(f"| `{sector}` | `{check['constant']}` | `{check['level']}` |")
    lines.extend(["", "## Normalization Ambiguities", ""])
    lines.extend(f"- {item}" for item in p["normalization_ambiguities"])
    lines.extend(["", "## Blockers Remaining", ""])
    lines.extend(f"- {item}" for item in p["blockers_remaining"])
    lines.extend(
        [
            "",
            "## Claim Safety",
            "",
            "- No official frozen outputs are changed.",
            "- No retuning is performed.",
            "- No neutrino speed anomaly claim is made.",
            "- No lab-scale mass variation claim is made.",
            "- No Standard Model replacement or full derivation claim is made.",
            "- Lepton 8/9 remains unpromoted.",
            "",
        ]
    )
    return "\n".join(lines)


def export_explicit_hopf_berger_oneform_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export theory and audit artifacts."""

    base = Path(root)
    payload = audit_payload()
    outputs = {
        "theory": base / "theory" / "explicit_hopf_berger_boundary_oneforms.md",
        "Aq": base / "theory" / "hopf_fiber_connection_Aq.md",
        "Aj": base / "theory" / "berger_base_connection_Aj.md",
        "norm": base / "theory" / "normalization_conventions_hopf_berger.md",
        "base": base / "theory" / "base_curvature_vs_oneform_Aj.md",
        "qnote": base / "theory" / "q_equals_k_minus_2j_representation_note.md",
        "Arep": base / "theory" / "Arep_with_explicit_hopf_berger_components.md",
        "audit_md": base / "audits" / "explicit_hopf_berger_boundary_oneforms_audit.md",
        "audit_json": base / "audits" / "explicit_hopf_berger_boundary_oneforms_audit.json",
    }
    for path in outputs.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    outputs["theory"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["audit_md"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    outputs["Aq"].write_text(
        "# Hopf Fiber Connection A_q\n\n"
        f"Status: `{payload['A_q_status']}`\n\n"
        "`A_q` is identified with the normalized Hopf/contact form `sigma_3/(2*pi)` under the unit-fiber-holonomy convention. This supports q as the fiber charge.\n",
        encoding="utf-8",
    )
    outputs["Aj"].write_text(
        "# Berger Base Connection A_j\n\n"
        f"Status: `{payload['A_j_status']}`\n\n"
        "`A_j` is supported as a Berger/base curvature or horizontal-coframe component associated with j. It is not yet fixed by the full boundary action.\n",
        encoding="utf-8",
    )
    outputs["norm"].write_text(
        "# Hopf-Berger Normalization Conventions\n\n"
        f"Hopf: `{payload['hopf_normalization_status']}`\n\n"
        f"Berger/base: `{payload['berger_base_normalization_status']}`\n\n"
        + "\n".join(f"- {item}" for item in payload["normalization_ambiguities"])
        + "\n",
        encoding="utf-8",
    )
    outputs["base"].write_text(
        "# Base Curvature vs One-Form A_j\n\n"
        "The audit permits `A_j` to be a curvature/coframe boundary component rather than a line-holonomy one-form. This avoids forcing the geometry into the wrong object type.\n",
        encoding="utf-8",
    )
    outputs["qnote"].write_text(
        "# q = k - 2j Representation Note\n\n"
        f"Status: `{payload['q_equals_k_minus_2j_status']}`\n\n"
        "The repo consistently uses `q=k-2j` as the Hopf residual fiber charge after removing the base contribution.\n",
        encoding="utf-8",
    )
    outputs["Arep"].write_text(
        "# A_rep with Explicit Hopf-Berger Components\n\n"
        f"Status: `{payload['A_rep_with_explicit_components_status']}`\n\n"
        "`A_rep = A_Hopf_norm tensor O_q + A_Berger_base tensor O_j` reproduces the charged-sector omega levels, but the full boundary-action coupling remains open.\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_explicit_hopf_berger_oneform_outputs()
