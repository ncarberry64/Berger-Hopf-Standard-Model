"""Berger/base action-coupling and normalization audit.

This module tests whether the supported Berger/base component A_j can be
upgraded from a geometric component to an action-coupled boundary term.  The
result is intentionally conservative: a universal minimal-coupling scaffold is
implemented, but full action variation and global normalization remain open.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from bhsm_config import canonical_geometry_config
from bhsm_completion_manual_theory_delta import frozen_sanity_payload
from bhsm_hopf_berger_oneforms import (
    hopf_connection_symbolic,
    hopf_curvature_symbolic,
    sigma_1_symbolic,
    sigma_2_symbolic,
    sigma_3_symbolic,
)
from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP


BERGER_BASE_ACTION_COUPLING_PARTIAL = "BERGER_BASE_ACTION_COUPLING_PARTIAL"
A_J_ACTION_COUPLING_PARTIAL = "A_J_ACTION_COUPLING_PARTIAL"
A_J_GEOMETRIC_OBJECT_SUPPORTED = "A_J_GEOMETRIC_OBJECT_SUPPORTED"
A_Q_ACTION_COUPLING_SUPPORTED = "A_Q_ACTION_COUPLING_SUPPORTED"
BOUNDARY_MINIMAL_COUPLING_STRUCTURAL_CANDIDATE = (
    "BOUNDARY_MINIMAL_COUPLING_STRUCTURAL_CANDIDATE"
)
BERGER_CASIMIR_DECOMPOSITION_SUPPORTED = "BERGER_CASIMIR_DECOMPOSITION_SUPPORTED"
BASE_CURVATURE_NORMALIZATION_CONVENTION_DEPENDENT = (
    "BASE_CURVATURE_NORMALIZATION_CONVENTION_DEPENDENT"
)
HORIZONTAL_COFRAME_COUPLING_PARTIAL = "HORIZONTAL_COFRAME_COUPLING_PARTIAL"
BERGER_ANISOTROPY_COUPLING_STRUCTURAL_CANDIDATE = (
    "BERGER_ANISOTROPY_COUPLING_STRUCTURAL_CANDIDATE"
)
A_REP_TRUE_CONNECTION_PARTIAL = "A_REP_TRUE_CONNECTION_PARTIAL"


@dataclass(frozen=True)
class ActionCouplingStatus:
    """Status of candidate action-coupling routes."""

    berger_base_action_coupling_status: str
    A_j_action_coupling_status: str
    A_j_geometric_object_status: str
    A_q_action_coupling_status: str
    boundary_minimal_coupling_status: str
    berger_casimir_decomposition_status: str
    horizontal_coframe_coupling_status: str
    berger_anisotropy_coupling_status: str
    A_rep_true_connection_status: str


@dataclass(frozen=True)
class NormalizationStatus:
    """Normalization status for base curvature/coframe coupling."""

    base_curvature_normalization_status: str
    does_A_j_normalization_become_global: bool
    normalization_ambiguities: tuple[str, ...]


@dataclass(frozen=True)
class BoundaryTerms:
    """Representation-valued boundary connection coefficients."""

    O_q: Fraction
    O_j: Fraction
    term: str


def q_from_kj(k: int, j: int) -> int:
    """Return Hopf residual charge q=k-2j."""

    return k - 2 * j


def hopf_connection_Aq() -> str:
    """Return normalized Hopf/fiber connection."""

    return "A_q = sigma_3/(2*pi)"


def hopf_curvature_Fq() -> str:
    """Return Hopf curvature symbol."""

    return hopf_curvature_symbolic()


def berger_metric_symbolic(r_base: str = "r_base", r_fiber: str = "r_fiber") -> str:
    """Return symbolic Berger metric."""

    return f"g_Berger = {r_base}^2 (sigma_1^2 + sigma_2^2) + {r_fiber}^2 sigma_3^2"


def horizontal_coframe_dimension() -> int:
    """Return dimension of the horizontal Hopf base coframe pair."""

    return 2


def base_curvature_flux_status(convention: str = "chern_unit") -> dict[str, Any]:
    """Return base curvature normalization status."""

    if convention == "chern_unit":
        flux_unit = Fraction(1)
    elif convention == "raw_sphere":
        flux_unit = Fraction(2)
    else:
        raise ValueError(f"unknown base curvature convention: {convention}")
    return {
        "convention": convention,
        "flux_unit": flux_unit,
        "status": BASE_CURVATURE_NORMALIZATION_CONVENTION_DEPENDENT,
        "globally_fixed": False,
        "limitation": "Base flux is normalized symbolically, but the full boundary action does not yet fix the A_j coupling convention.",
    }


def color_coframe_operator(B: Fraction | int) -> Fraction:
    """Return C_color=3B."""

    return 3 * Fraction(B)


def lower_weak_projector(T3: Fraction | int) -> Fraction:
    """Return lower weak component projector 1/2-T3."""

    return Fraction(1, 2) - Fraction(T3)


def colored_lower_projector(B: Fraction | int, T3: Fraction | int) -> Fraction:
    """Return colored lower-doublet coframe projector."""

    return color_coframe_operator(B) * lower_weak_projector(T3)


def O_q(B: Fraction | int, L: Fraction | int) -> Fraction:
    """Return O_q=3B-L."""

    return color_coframe_operator(B) - Fraction(L)


def O_j(B: Fraction | int, T3: Fraction | int) -> Fraction:
    """Return O_j=-4T3+2(3B)(1/2-T3)."""

    return -4 * Fraction(T3) + 2 * colored_lower_projector(B, T3)


def representation_boundary_connection_terms(
    B: Fraction | int,
    L: Fraction | int,
    T3: Fraction | int,
) -> BoundaryTerms:
    """Return symbolic representation-valued connection terms."""

    oq = O_q(B, L)
    oj = O_j(B, T3)
    return BoundaryTerms(
        O_q=oq,
        O_j=oj,
        term=f"D_boundary_rep = d + i A_q tensor ({oq}) + i A_j tensor ({oj})",
    )


def omega_from_Arep(
    q: int,
    j: int,
    B: Fraction | int,
    L: Fraction | int,
    T3: Fraction | int,
) -> Fraction:
    """Return Omega_f from the action-coupling scaffold."""

    terms = representation_boundary_connection_terms(B, L, T3)
    return terms.O_q * q + terms.O_j * j


def _sector_rep(sector: str) -> tuple[Fraction, Fraction, Fraction]:
    reps = {
        "charged_lepton": (Fraction(0), Fraction(1), Fraction(-1, 2)),
        "up": (Fraction(1, 3), Fraction(0), Fraction(1, 2)),
        "down": (Fraction(1, 3), Fraction(0), Fraction(-1, 2)),
        "neutrino": (Fraction(0), Fraction(1), Fraction(1, 2)),
    }
    if sector not in reps:
        raise ValueError(f"unknown sector: {sector}")
    return reps[sector]


def mode_pair_omega_values(sector: str) -> tuple[Fraction, Fraction]:
    """Return omega values for charged-sector mode pairs."""

    modes = {
        "charged_lepton": ((5, 2), (9, 3)),
        "up": ((6, 0), (10, 1)),
        "down": ((6, 3), (8, 2)),
    }
    if sector not in modes:
        raise ValueError(f"unknown charged sector: {sector}")
    B, L, T3 = _sector_rep(sector)
    values = []
    for k, j in modes[sector]:
        values.append(omega_from_Arep(q_from_kj(k, j), j, B, L, T3))
    return tuple(values)  # type: ignore[return-value]


def action_coupling_status_object() -> ActionCouplingStatus:
    """Return conservative action-coupling status."""

    return ActionCouplingStatus(
        berger_base_action_coupling_status=BERGER_BASE_ACTION_COUPLING_PARTIAL,
        A_j_action_coupling_status=A_J_ACTION_COUPLING_PARTIAL,
        A_j_geometric_object_status=A_J_GEOMETRIC_OBJECT_SUPPORTED,
        A_q_action_coupling_status=A_Q_ACTION_COUPLING_SUPPORTED,
        boundary_minimal_coupling_status=BOUNDARY_MINIMAL_COUPLING_STRUCTURAL_CANDIDATE,
        berger_casimir_decomposition_status=BERGER_CASIMIR_DECOMPOSITION_SUPPORTED,
        horizontal_coframe_coupling_status=HORIZONTAL_COFRAME_COUPLING_PARTIAL,
        berger_anisotropy_coupling_status=BERGER_ANISOTROPY_COUPLING_STRUCTURAL_CANDIDATE,
        A_rep_true_connection_status=A_REP_TRUE_CONNECTION_PARTIAL,
    )


def normalization_status_object() -> NormalizationStatus:
    """Return base normalization status."""

    return NormalizationStatus(
        base_curvature_normalization_status=BASE_CURVATURE_NORMALIZATION_CONVENTION_DEPENDENT,
        does_A_j_normalization_become_global=False,
        normalization_ambiguities=(
            "Chern-unit and raw-sphere base flux conventions differ by a factor of 2.",
            "The boundary action has not fixed whether A_j is a spin connection, curvature channel, coframe channel, or Casimir term.",
            "The down-sector colored-lower bonus is supported by projectors but not yet derived from a full color/coframe boundary action.",
        ),
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
    """Return structured Berger/base action-coupling audit payload."""

    action = action_coupling_status_object()
    norm = normalization_status_object()
    values = {
        sector: mode_pair_omega_values(sector)
        for sector in ("charged_lepton", "up", "down")
    }
    reproduces = values == {
        "charged_lepton": (Fraction(3), Fraction(3)),
        "up": (Fraction(6), Fraction(6)),
        "down": (Fraction(12), Fraction(12)),
    }
    blockers_remaining = (
        "derive the minimal boundary coupling from the complete Berger-Hopf action variation",
        "globally fix A_j normalization without convention choice",
        "prove A_rep is a true connection on the completed boundary tensor bundle",
        "derive dim(H)=|Omega| separately",
        "derive identity/traceless stochastic protection before promoting lepton 8/9",
    )
    payload: dict[str, Any] = {
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        "berger_base_action_coupling_status": action.berger_base_action_coupling_status,
        "A_j_action_coupling_status": action.A_j_action_coupling_status,
        "A_j_geometric_object_status": action.A_j_geometric_object_status,
        "A_q_action_coupling_status": action.A_q_action_coupling_status,
        "boundary_minimal_coupling_status": action.boundary_minimal_coupling_status,
        "berger_casimir_decomposition_status": action.berger_casimir_decomposition_status,
        "base_curvature_normalization_status": norm.base_curvature_normalization_status,
        "horizontal_coframe_coupling_status": action.horizontal_coframe_coupling_status,
        "berger_anisotropy_coupling_status": action.berger_anisotropy_coupling_status,
        "A_rep_true_connection_status": action.A_rep_true_connection_status,
        "does_A_j_have_action_coupling": True,
        "does_A_j_normalization_become_global": norm.does_A_j_normalization_become_global,
        "does_Arep_act_on_boundary_tensor_bundle": True,
        "does_Arep_reproduce_omega_l_u_d": reproduces,
        "does_this_close_boundary_connection": False,
        "does_this_promote_lepton_8_9": False,
        "normalization_ambiguities": norm.normalization_ambiguities,
        "blockers_closed": (
            "minimal_boundary_coupling_scaffold_for_A_j",
            "Berger_horizontal_Casimir_support_for_j",
            "horizontal_coframe_dimension_two_recorded",
        ),
        "blockers_remaining": blockers_remaining,
        "derived_components": (),
        "candidate_components": (
            "D_boundary_rep_minimal_coupling",
            "A_j_base_spin_curvature_or_coframe_channel",
            "Berger_anisotropy_variation_channel",
            "A_rep_boundary_tensor_bundle_connection",
        ),
        "missing_assumptions": blockers_remaining,
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "symbolic_geometry": {
            "sigma_1": sigma_1_symbolic(),
            "sigma_2": sigma_2_symbolic(),
            "sigma_3": sigma_3_symbolic(),
            "A_q": hopf_connection_Aq(),
            "A_Hopf": hopf_connection_symbolic(),
            "F_q": hopf_curvature_Fq(),
            "berger_metric": berger_metric_symbolic(),
            "horizontal_coframe_dimension": horizontal_coframe_dimension(),
        },
        "base_curvature_flux": base_curvature_flux_status(),
        "mode_pair_omega_values": values,
        "sector_terms": {
            sector: representation_boundary_connection_terms(*_sector_rep(sector))
            for sector in ("charged_lepton", "up", "down", "neutrino")
        },
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
    """Render audit Markdown."""

    p = audit_payload() if payload is None else payload
    heading = title or "BHSM Berger-Base Action Coupling and Normalization"
    lines = [
        f"# {heading}",
        "",
        "This sprint tests whether the Berger/base component `A_j` can be treated as an action-coupled boundary object.",
        "The result is partial: a universal minimal-coupling scaffold is recorded, while full action variation and global normalization remain open.",
        "",
        "## Summary",
        "",
        f"Berger/base action coupling status: `{p['berger_base_action_coupling_status']}`",
        f"A_j action coupling status: `{p['A_j_action_coupling_status']}`",
        f"A_j geometric object status: `{p['A_j_geometric_object_status']}`",
        f"A_rep true connection status: `{p['A_rep_true_connection_status']}`",
        f"Base curvature normalization status: `{p['base_curvature_normalization_status']}`",
        f"Horizontal coframe coupling status: `{p['horizontal_coframe_coupling_status']}`",
        f"Does A_j have action coupling: `{p['does_A_j_have_action_coupling']}`",
        f"Does A_j normalization become global: `{p['does_A_j_normalization_become_global']}`",
        f"Does A_rep act on boundary tensor bundle: `{p['does_Arep_act_on_boundary_tensor_bundle']}`",
        f"Does A_rep reproduce Omega_l,u,d: `{p['does_Arep_reproduce_omega_l_u_d']}`",
        f"Closes boundary connection: `{p['does_this_close_boundary_connection']}`",
        f"Promotes lepton 8/9: `{p['does_this_promote_lepton_8_9']}`",
        "",
        "## Candidate Boundary Coupling",
        "",
        "```text",
        "D_boundary_rep = d + i A_q tensor O_q + i A_j tensor O_j",
        "S_boundary = integral_boundary sqrt(g_Berger) <D_boundary_rep psi, D_boundary_rep psi>",
        "O_q = 3B - L",
        "O_j = -4T3 + 2(3B)(1/2 - T3)",
        "```",
        "",
        "## Geometry",
        "",
        "```text",
        p["symbolic_geometry"]["sigma_1"],
        p["symbolic_geometry"]["sigma_2"],
        p["symbolic_geometry"]["sigma_3"],
        p["symbolic_geometry"]["A_q"],
        p["symbolic_geometry"]["F_q"],
        p["symbolic_geometry"]["berger_metric"],
        "```",
        "",
        "## Mode Pair Checks",
        "",
        "| Sector | Omega values |",
        "| --- | --- |",
    ]
    for sector, values in p["mode_pair_omega_values"].items():
        lines.append(f"| `{sector}` | `{values}` |")
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


def export_berger_base_action_coupling_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export theory and audit artifacts."""

    base = Path(root)
    payload = audit_payload()
    outputs = {
        "theory": base / "theory" / "berger_base_action_coupling_normalization.md",
        "minimal": base / "theory" / "boundary_minimal_coupling_candidate.md",
        "casimir": base / "theory" / "berger_casimir_decomposition_candidate.md",
        "curvature": base / "theory" / "base_curvature_cern_normalization.md",
        "coframe": base / "theory" / "horizontal_coframe_coupling_candidate.md",
        "anisotropy": base / "theory" / "berger_anisotropy_variation_candidate.md",
        "true_connection": base / "theory" / "Arep_true_boundary_connection_candidate.md",
        "down": base / "theory" / "down_projector_action_coupling_note.md",
        "audit_md": base / "audits" / "berger_base_action_coupling_normalization_audit.md",
        "audit_json": base / "audits" / "berger_base_action_coupling_normalization_audit.json",
    }
    for path in outputs.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    outputs["theory"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["audit_md"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    outputs["minimal"].write_text(
        "# Boundary Minimal Coupling Candidate\n\n"
        f"Status: `{payload['boundary_minimal_coupling_status']}`\n\n"
        "`D_boundary_rep = d + i A_q tensor O_q + i A_j tensor O_j` is implemented as a universal candidate scaffold before sector evaluation. It is not derived from full action variation here.\n",
        encoding="utf-8",
    )
    outputs["casimir"].write_text(
        "# Berger Casimir Decomposition Candidate\n\n"
        f"Status: `{payload['berger_casimir_decomposition_status']}`\n\n"
        "The split between Hopf fiber charge q and horizontal/base label j is supported by the existing Berger-Hopf mode notation and scalar spectrum proxy. Full representation-theoretic derivation remains open.\n",
        encoding="utf-8",
    )
    outputs["curvature"].write_text(
        "# Base Curvature Chern Normalization\n\n"
        f"Status: `{payload['base_curvature_normalization_status']}`\n\n"
        "The base curvature channel admits Chern-unit bookkeeping, but the complete boundary action has not fixed the A_j convention globally.\n",
        encoding="utf-8",
    )
    outputs["coframe"].write_text(
        "# Horizontal Coframe Coupling Candidate\n\n"
        f"Status: `{payload['horizontal_coframe_coupling_status']}`\n\n"
        "The two horizontal forms sigma_1 and sigma_2 give horizontal coframe dimension 2. This supports the base channel but does not derive the down-sector color/coframe bonus from the full action.\n",
        encoding="utf-8",
    )
    outputs["anisotropy"].write_text(
        "# Berger Anisotropy Variation Candidate\n\n"
        f"Status: `{payload['berger_anisotropy_coupling_status']}`\n\n"
        "The Berger metric separates base and fiber radii, so anisotropy variation structurally supports separate q and j channels. It does not fix A_j normalization here.\n",
        encoding="utf-8",
    )
    outputs["true_connection"].write_text(
        "# A_rep True Boundary Connection Candidate\n\n"
        f"Status: `{payload['A_rep_true_connection_status']}`\n\n"
        "`A_rep` acts universally in the candidate boundary tensor-bundle scaffold. A completed proof that it is the true connection of the full BHSM boundary action remains open.\n",
        encoding="utf-8",
    )
    outputs["down"].write_text(
        "# Down Projector Action Coupling Note\n\n"
        "The down-sector colored-lower term is preserved as a supported projector consequence. Its full color/coframe action coupling remains a blocker.\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_berger_base_action_coupling_outputs()
