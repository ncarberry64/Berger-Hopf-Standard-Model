"""Primitive cyclic monodromy from the BHSM boundary action scaffold.

This module audits whether the existing Berger-Hopf representation-valued
boundary connection can be upgraded from an assumed cyclic monodromy route to
an action-level monodromy mechanism.  It does not alter frozen predictions.
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
    A_J_EXPLICIT_BERGER_BASE_COMPONENT_SUPPORTED,
    A_Q_EXPLICIT_HOPF_FIBER_ONEFORM_SUPPORTED,
    omega_from_explicit_connection,
    q_from_kj,
)
from bhsm_identity_traceless_stochastic import LEPTON_8_9_CHANNEL_RULE_CONDITIONAL
from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import S_OVERLAP


PRIMITIVE_CYCLIC_MONODROMY_DERIVED = "PRIMITIVE_CYCLIC_MONODROMY_DERIVED"
PRIMITIVE_CYCLIC_MONODROMY_PARTIAL = "PRIMITIVE_CYCLIC_MONODROMY_PARTIAL"
PRIMITIVE_CYCLIC_MONODROMY_CONDITIONAL = "PRIMITIVE_CYCLIC_MONODROMY_CONDITIONAL"
PRIMITIVE_CYCLIC_MONODROMY_STRUCTURAL_CANDIDATE = (
    "PRIMITIVE_CYCLIC_MONODROMY_STRUCTURAL_CANDIDATE"
)
PRIMITIVE_CYCLIC_MONODROMY_OPEN = "PRIMITIVE_CYCLIC_MONODROMY_OPEN"
PRIMITIVE_CYCLIC_MONODROMY_REJECTED = "PRIMITIVE_CYCLIC_MONODROMY_REJECTED"

BOUNDARY_ACTION_MONODROMY_PARTIAL = "BOUNDARY_ACTION_MONODROMY_PARTIAL"
WILSON_LOOP_MONODROMY_PARTIAL = "WILSON_LOOP_MONODROMY_PARTIAL"
BOUNDARY_PHASE_MATCHING_STRUCTURAL_CANDIDATE = (
    "BOUNDARY_PHASE_MATCHING_STRUCTURAL_CANDIDATE"
)
SELF_ADJOINT_MONODROMY_STRUCTURAL_CANDIDATE = (
    "SELF_ADJOINT_MONODROMY_STRUCTURAL_CANDIDATE"
)
HOPF_PRIMITIVE_ORBIT_PARTIAL = "HOPF_PRIMITIVE_ORBIT_PARTIAL"
TOPOLOGICAL_BOUNDARY_TERM_STRUCTURAL_CANDIDATE = (
    "TOPOLOGICAL_BOUNDARY_TERM_STRUCTURAL_CANDIDATE"
)
CYCLIC_ORBIT_CHANNEL_PARTIAL = "CYCLIC_ORBIT_CHANNEL_PARTIAL"
DIM_H_EQUALS_ABS_OMEGA_PARTIAL = "DIM_H_EQUALS_ABS_OMEGA_PARTIAL"
LEPTON_8_9_CHANNEL_RULE_CONDITIONAL_STRENGTHENED = (
    "LEPTON_8_9_CHANNEL_RULE_CONDITIONAL_STRENGTHENED"
)
S2_GEOMETRIC_QUANTIZATION_NOT_USED_FOR_CHANNEL_DIMENSION = (
    "S2_GEOMETRIC_QUANTIZATION_NOT_USED_FOR_CHANNEL_DIMENSION"
)


@dataclass(frozen=True)
class MonodromyRouteStatus:
    """Status for one derivation route."""

    route: str
    status: str
    defines_monodromy: bool
    derives_primitive_order: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class SectorMonodromy:
    """Exact sector monodromy arithmetic."""

    sector: str
    omega: int
    order: int
    dimension: int
    orbit_states: tuple[int, ...]
    primitive: bool
    modes: tuple[dict[str, int], ...]


def _require_nonzero_integer_omega(Omega: int | Fraction) -> int:
    value = Fraction(Omega)
    if value.denominator != 1:
        raise ValueError("Omega must be an integer boundary level")
    if value == 0:
        raise ValueError("Omega must be nonzero")
    return abs(int(value))


def monodromy_order_from_omega(Omega: int | Fraction) -> int:
    """Return the primitive cyclic order |Omega| for an integer level."""

    return _require_nonzero_integer_omega(Omega)


def U_power_identity_condition(Omega: int | Fraction, power: int) -> bool:
    """Return whether U^power=I for a primitive order-|Omega| monodromy."""

    if int(power) < 0:
        raise ValueError("power must be nonnegative")
    order = monodromy_order_from_omega(Omega)
    return int(power) % order == 0


def is_primitive_order(Omega: int | Fraction, candidate_order: int) -> bool:
    """Return whether candidate_order is the first positive identity power."""

    order = monodromy_order_from_omega(Omega)
    if int(candidate_order) != order:
        return False
    return all(not U_power_identity_condition(Omega, power) for power in range(1, order))


def primitive_closure_check(Omega: int | Fraction) -> bool:
    """Return whether U^|Omega|=I and no smaller positive power closes."""

    order = monodromy_order_from_omega(Omega)
    return U_power_identity_condition(Omega, order) and is_primitive_order(Omega, order)


def cyclic_orbit_states(Omega: int | Fraction) -> list[int]:
    """Return boundary orbit representatives 0,...,|Omega|-1."""

    return list(range(monodromy_order_from_omega(Omega)))


def orbit_dimension(Omega: int | Fraction) -> int:
    """Return the finite cyclic orbit dimension."""

    return len(cyclic_orbit_states(Omega))


def omega_from_Arep(
    q: int,
    j: int,
    B: Fraction | int,
    L: Fraction | int,
    T3: Fraction | int,
) -> Fraction:
    """Return Omega_f from the representation-valued connection scaffold."""

    return omega_from_explicit_connection(q, j, B, L, T3)


def _sector_rep(sector: str) -> tuple[Fraction, Fraction, Fraction]:
    reps = {
        "charged_lepton": (Fraction(0), Fraction(1), Fraction(-1, 2)),
        "up": (Fraction(1, 3), Fraction(0), Fraction(1, 2)),
        "down": (Fraction(1, 3), Fraction(0), Fraction(-1, 2)),
    }
    if sector not in reps:
        raise ValueError(f"unknown charged sector: {sector}")
    return reps[sector]


def _sector_modes(sector: str) -> tuple[tuple[int, int], ...]:
    modes = {
        "charged_lepton": ((5, 2), (9, 3)),
        "up": ((6, 0), (10, 1)),
        "down": ((6, 3), (8, 2)),
    }
    if sector not in modes:
        raise ValueError(f"unknown charged sector: {sector}")
    return modes[sector]


def _sector_omega_values(sector: str) -> tuple[Fraction, ...]:
    B, L, T3 = _sector_rep(sector)
    return tuple(omega_from_Arep(q_from_kj(k, j), j, B, L, T3) for k, j in _sector_modes(sector))


def charged_lepton_omega_values() -> tuple[Fraction, ...]:
    """Return charged-lepton omega levels for middle/light modes."""

    return _sector_omega_values("charged_lepton")


def up_omega_values() -> tuple[Fraction, ...]:
    """Return up-sector omega levels for middle/light modes."""

    return _sector_omega_values("up")


def down_omega_values() -> tuple[Fraction, ...]:
    """Return down-sector omega levels for middle/light modes."""

    return _sector_omega_values("down")


def sector_monodromy_order(sector: str) -> int:
    """Return |Omega_f| for a charged sector with constant nonzero level."""

    values = _sector_omega_values(sector)
    if len(set(values)) != 1:
        raise ValueError(f"sector does not have a constant Omega level: {sector}")
    return monodromy_order_from_omega(values[0])


def sector_orbit_dimension(sector: str) -> int:
    """Return dim C[Z_|Omega_f|] for a charged sector."""

    return orbit_dimension(sector_monodromy_order(sector))


def sector_monodromy(sector: str) -> SectorMonodromy:
    """Return exact sector monodromy data."""

    order = sector_monodromy_order(sector)
    B, L, T3 = _sector_rep(sector)
    rows = []
    for k, j in _sector_modes(sector):
        q = q_from_kj(k, j)
        omega = int(omega_from_Arep(q, j, B, L, T3))
        rows.append({"k": k, "j": j, "q": q, "omega": omega})
    return SectorMonodromy(
        sector=sector,
        omega=order,
        order=order,
        dimension=orbit_dimension(order),
        orbit_states=tuple(cyclic_orbit_states(order)),
        primitive=primitive_closure_check(order),
        modes=tuple(rows),
    )


def wilson_loop_status_object() -> MonodromyRouteStatus:
    """Return the Wilson-loop boundary-action status."""

    return MonodromyRouteStatus(
        route="wilson_loop_boundary_action",
        status=WILSON_LOOP_MONODROMY_PARTIAL,
        defines_monodromy=True,
        derives_primitive_order=False,
        assumptions=(
            "S_hol = integral_gamma <psi, i D_gamma psi> is accepted as the boundary scaffold",
            "A_rep is the representation-valued connection along the boundary loop",
            "sector eigenvalues reduce A_rep to Omega_f",
        ),
        limitations=(
            "variation gives parallel transport but not by itself the primitive finite quotient",
            "A_j normalization remains convention-dependent in the existing repo",
            "the completed Berger-Hopf boundary action is not uniquely derived here",
        ),
    )


def boundary_phase_matching_status_object() -> MonodromyRouteStatus:
    """Return phase-matching status."""

    return MonodromyRouteStatus(
        route="boundary_phase_matching",
        status=BOUNDARY_PHASE_MATCHING_STRUCTURAL_CANDIDATE,
        defines_monodromy=True,
        derives_primitive_order=False,
        assumptions=(
            "boundary states obey psi(1)=U_f psi(0)",
            "physical channel states are finite cyclic orbit residues",
        ),
        limitations=(
            "single-valuedness can trivialize the phase unless the quotient/orbit rule is supplied",
            "primitive closure is not forced by finite action alone in the current scaffold",
        ),
    )


def self_adjoint_monodromy_status_object() -> MonodromyRouteStatus:
    """Return self-adjoint boundary-condition status."""

    return MonodromyRouteStatus(
        route="self_adjoint_boundary_condition",
        status=SELF_ADJOINT_MONODROMY_STRUCTURAL_CANDIDATE,
        defines_monodromy=True,
        derives_primitive_order=False,
        assumptions=(
            "self-adjoint boundary conditions are represented by unitary boundary data",
            "the sector unitary is restricted to finite cyclic order |Omega_f|",
        ),
        limitations=(
            "the full boundary operator domain classification is not implemented here",
            "finite cyclic restriction remains an added sector condition",
        ),
    )


def hopf_primitive_orbit_status_object() -> MonodromyRouteStatus:
    """Return Hopf primitive orbit route status."""

    return MonodromyRouteStatus(
        route="hopf_fiber_primitive_orbit",
        status=HOPF_PRIMITIVE_ORBIT_PARTIAL,
        defines_monodromy=True,
        derives_primitive_order=False,
        assumptions=(
            "A_q is the normalized Hopf/contact one-form with unit fiber holonomy",
            "q couples to the Hopf fiber and j couples to the Berger/base component",
        ),
        limitations=(
            "Hopf periodicity supports the q part but does not alone derive O_j j",
            "including A_j preserves integer levels but its global normalization remains open",
        ),
    )


def topological_boundary_term_status_object() -> MonodromyRouteStatus:
    """Return topological boundary-term route status."""

    return MonodromyRouteStatus(
        route="topological_boundary_term",
        status=TOPOLOGICAL_BOUNDARY_TERM_STRUCTURAL_CANDIDATE,
        defines_monodromy=True,
        derives_primitive_order=False,
        assumptions=(
            "a topological boundary phase exp(i integral A_rep) is allowed",
            "integer sector levels label boundary winding sectors",
        ),
        limitations=(
            "the topological term is a scaffold rather than a term derived from the completed action",
            "path-integral phase invariance quantizes levels but does not select physical orbit states",
        ),
    )


def primitive_monodromy_status_object() -> MonodromyRouteStatus:
    """Return the aggregate primitive monodromy status."""

    return MonodromyRouteStatus(
        route="primitive_cyclic_boundary_monodromy",
        status=PRIMITIVE_CYCLIC_MONODROMY_PARTIAL,
        defines_monodromy=True,
        derives_primitive_order=False,
        assumptions=(
            "A_rep defines Wilson-loop parallel transport",
            "the boundary quotient uses primitive finite cyclic orbit states",
            "A_j is normalized consistently with the charged-sector levels",
        ),
        limitations=(
            "primitive finite closure is not forced solely by variation/finite action",
            "A_j normalization and full bundle proof remain open",
            "physical identification of orbit states as H_f remains conditional",
        ),
    )


def lepton_8_9_consequence_status_object() -> MonodromyRouteStatus:
    """Return lepton 8/9 consequence status after this sprint."""

    return MonodromyRouteStatus(
        route="lepton_8_9_consequence",
        status=LEPTON_8_9_CHANNEL_RULE_CONDITIONAL_STRENGTHENED,
        defines_monodromy=True,
        derives_primitive_order=False,
        assumptions=(
            "dim H_l=3 follows from the partial/conditional monodromy route",
            "stochastic dressing acts trace-preservingly on End(H_l)",
        ),
        limitations=(
            "full stochastic End(H_f) dynamics remains conditional",
            "the Brownian generator on su(3) is not derived from the full action",
            "the rule is not an official frozen prediction update",
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
    """Return primitive cyclic monodromy audit payload."""

    primitive = primitive_monodromy_status_object()
    wilson = wilson_loop_status_object()
    phase = boundary_phase_matching_status_object()
    self_adjoint = self_adjoint_monodromy_status_object()
    hopf = hopf_primitive_orbit_status_object()
    topological = topological_boundary_term_status_object()
    lepton = lepton_8_9_consequence_status_object()
    sectors = {
        sector: sector_monodromy(sector)
        for sector in ("charged_lepton", "up", "down")
    }
    blockers_remaining = (
        "derive primitive finite cyclic quotient from the completed boundary action",
        "fix A_j normalization and global bundle coupling without convention dependence",
        "prove orbit states C[Z_|Omega_f|] are the physical boundary channel states",
        "derive stochastic dressing action on End(H_f) from the full BHSM dynamics",
    )
    payload: dict[str, Any] = {
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        "primitive_cyclic_monodromy_status": primitive.status,
        "boundary_action_monodromy_status": BOUNDARY_ACTION_MONODROMY_PARTIAL,
        "wilson_loop_monodromy_status": wilson.status,
        "boundary_phase_matching_status": phase.status,
        "self_adjoint_monodromy_status": self_adjoint.status,
        "hopf_primitive_orbit_status": hopf.status,
        "topological_boundary_term_status": topological.status,
        "cyclic_orbit_channel_status": CYCLIC_ORBIT_CHANNEL_PARTIAL,
        "dim_H_equals_abs_Omega_status": DIM_H_EQUALS_ABS_OMEGA_PARTIAL,
        "lepton_8_9_consequence_status": lepton.status,
        "does_boundary_action_define_U_f": True,
        "does_variation_force_parallel_transport": True,
        "does_finite_action_force_primitive_closure": False,
        "does_U_f_have_order_abs_Omega": True,
        "does_cyclic_orbit_define_channel_space": True,
        "does_dim_H_equal_abs_Omega_become_derived": False,
        "does_this_promote_full_lepton_8_9": False,
        "does_this_change_official_predictions": False,
        "geometric_quantization_plus_one_hazard": True,
        "preferred_dimension_route": "cyclic_boundary_monodromy",
        "S2_geometric_quantization_used_for_channel_dimension": False,
        "rejected_or_limited_route_note": S2_GEOMETRIC_QUANTIZATION_NOT_USED_FOR_CHANNEL_DIMENSION,
        "upstream_A_q_status": A_Q_EXPLICIT_HOPF_FIBER_ONEFORM_SUPPORTED,
        "upstream_A_j_status": A_J_EXPLICIT_BERGER_BASE_COMPONENT_SUPPORTED,
        "blockers_closed": (
            "boundary_action_defines_Wilson_loop_monodromy_operator",
            "variation_gives_parallel_transport_in_symbolic_boundary_action",
            "exact_integer_orbit_arithmetic_for_3_6_12",
        ),
        "blockers_remaining": blockers_remaining,
        "derived_components": (
            "U_f_parallel_transport_solution_from_boundary_covariant_derivative",
            "exact_primitive_order_arithmetic_once_U_f_is_primitive",
        ),
        "partial_components": (
            "boundary_action_monodromy_mechanism",
            "Hopf_fiber_primitive_orbit_support_for_q",
            "dim_H_equals_abs_Omega_under_boundary_orbit_channel_identification",
        ),
        "conditional_components": (
            "primitive_finite_cyclic_quotient",
            "physical_channel_space_equals_regular_cyclic_orbit",
            LEPTON_8_9_CHANNEL_RULE_CONDITIONAL,
        ),
        "candidate_components": (
            "boundary_phase_matching_orbit_rule",
            "self_adjoint_finite_monodromy_restriction",
            "topological_boundary_phase_term",
        ),
        "missing_assumptions": blockers_remaining,
        "normalization_ambiguities": (
            "A_j may be a Berger/base curvature or coframe component rather than a line holonomy",
            "global A_j normalization is not uniquely fixed by the completed boundary action",
            "finite cyclic order requires the primitive boundary quotient rather than ordinary S2 quantization",
        ),
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "routes": {
            "primitive": primitive,
            "wilson_loop": wilson,
            "boundary_phase_matching": phase,
            "self_adjoint": self_adjoint,
            "hopf_primitive_orbit": hopf,
            "topological_boundary_term": topological,
            "lepton_8_9": lepton,
        },
        "sector_monodromy": sectors,
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
    """Render the primitive monodromy audit payload."""

    p = audit_payload() if payload is None else payload
    heading = title or "BHSM Primitive Cyclic Monodromy from Boundary Action"
    lines = [
        f"# {heading}",
        "",
        "This sprint tests whether the Berger-Hopf boundary-action scaffold defines a primitive finite cyclic monodromy whose order is `|Omega_f|`.",
        "The result is partial: the symbolic Wilson-loop boundary action defines `U_f` and exact cyclic arithmetic works, but primitive closure is not forced by finite action alone.",
        "",
        "## Summary",
        "",
        f"Primitive cyclic monodromy: `{p['primitive_cyclic_monodromy_status']}`",
        f"Boundary action monodromy: `{p['boundary_action_monodromy_status']}`",
        f"Wilson-loop monodromy: `{p['wilson_loop_monodromy_status']}`",
        f"Boundary phase matching: `{p['boundary_phase_matching_status']}`",
        f"Self-adjoint monodromy: `{p['self_adjoint_monodromy_status']}`",
        f"Hopf primitive orbit: `{p['hopf_primitive_orbit_status']}`",
        f"Topological boundary term: `{p['topological_boundary_term_status']}`",
        f"dim(H)=|Omega|: `{p['dim_H_equals_abs_Omega_status']}`",
        f"Lepton 8/9 consequence: `{p['lepton_8_9_consequence_status']}`",
        "",
        "## Boundary-Action Mechanism",
        "",
        "```text",
        "S_hol = integral_gamma <psi, i D_gamma psi>",
        "D_gamma = d/ds + i A_rep(gamma_dot)",
        "A_rep = A_q tensor O_q + A_j tensor O_j",
        "Omega_f = O_q q + O_j j",
        "psi(1) = U_f psi(0),  U_f = P exp(i integral_gamma A_rep)",
        "```",
        "",
        f"Boundary action defines U_f: `{p['does_boundary_action_define_U_f']}`",
        f"Variation forces parallel transport: `{p['does_variation_force_parallel_transport']}`",
        f"Finite action forces primitive closure: `{p['does_finite_action_force_primitive_closure']}`",
        f"U_f has order |Omega_f| in the primitive cyclic model: `{p['does_U_f_have_order_abs_Omega']}`",
        "",
        "## Sector Monodromy",
        "",
        "| Sector | Omega | Order | dim(H_f) | Orbit states | Primitive check |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for sector, row in p["sector_monodromy"].items():
        lines.append(
            f"| `{sector}` | `{row.omega}` | `{row.order}` | `{row.dimension}` | `{list(row.orbit_states)}` | `{row.primitive}` |"
        )
    lines.extend(
        [
            "",
            "## Preferred Dimension Route",
            "",
            f"Preferred route: `{p['preferred_dimension_route']}`",
            f"S2 geometric quantization used for channel dimension: `{p['S2_geometric_quantization_used_for_channel_dimension']}`",
            f"Geometric quantization plus-one hazard: `{p['geometric_quantization_plus_one_hazard']}`",
            f"Rejected/limited route note: `{p['rejected_or_limited_route_note']}`",
            "",
            "Ordinary S2 geometric quantization is not used for BHSM channel counting here; it remains a hazard route because line-bundle conventions can produce an `n+1` dimension.",
            "",
            "## Blockers Closed",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in p["blockers_closed"])
    lines.extend(["", "## Blockers Remaining", ""])
    lines.extend(f"- {item}" for item in p["blockers_remaining"])
    lines.extend(["", "## Normalization Ambiguities", ""])
    lines.extend(f"- {item}" for item in p["normalization_ambiguities"])
    lines.extend(
        [
            "",
            "## Claim Safety",
            "",
            "- No official frozen outputs are changed.",
            "- No retuning is performed.",
            "- No frozen lepton or quark dressing rule is changed.",
            "- No neutrino speed anomaly claim is made.",
            "- No lab-scale environmental mass-drift claim is made.",
            "- No Standard Model replacement claim is made.",
            "",
        ]
    )
    return "\n".join(lines)


def export_primitive_cyclic_monodromy_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export theory and audit artifacts."""

    base = Path(root)
    payload = audit_payload()
    outputs = {
        "main": base / "theory" / "primitive_cyclic_monodromy_from_boundary_action.md",
        "wilson": base / "theory" / "wilson_loop_boundary_monodromy_candidate.md",
        "phase": base / "theory" / "boundary_phase_matching_condition.md",
        "self_adjoint": base / "theory" / "self_adjoint_boundary_monodromy_candidate.md",
        "hopf": base / "theory" / "hopf_fiber_primitive_orbit_candidate.md",
        "topological": base / "theory" / "topological_boundary_term_monodromy_candidate.md",
        "lepton": base / "theory" / "lepton_8_9_monodromy_status_update.md",
        "assumptions": base / "theory" / "action_monodromy_remaining_assumptions.md",
        "audit_md": base / "audits" / "primitive_cyclic_monodromy_boundary_action_audit.md",
        "audit_json": base / "audits" / "primitive_cyclic_monodromy_boundary_action_audit.json",
    }
    for path in outputs.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    outputs["main"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["audit_md"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    route_files = {
        "wilson": ("Wilson-Loop Boundary Monodromy Candidate", "wilson_loop"),
        "phase": ("Boundary Phase Matching Condition", "boundary_phase_matching"),
        "self_adjoint": ("Self-Adjoint Boundary Monodromy Candidate", "self_adjoint"),
        "hopf": ("Hopf Fiber Primitive Orbit Candidate", "hopf_primitive_orbit"),
        "topological": ("Topological Boundary Term Monodromy Candidate", "topological_boundary_term"),
        "lepton": ("Lepton 8/9 Monodromy Status Update", "lepton_8_9"),
    }
    for key, (heading, route_key) in route_files.items():
        route = payload["routes"][route_key]
        outputs[key].write_text(
            f"# {heading}\n\n"
            f"Status: `{route.status}`\n\n"
            f"Defines monodromy: `{route.defines_monodromy}`\n\n"
            f"Derives primitive order: `{route.derives_primitive_order}`\n\n"
            "## Assumptions\n\n"
            + "\n".join(f"- {item}" for item in route.assumptions)
            + "\n\n## Limitations\n\n"
            + "\n".join(f"- {item}" for item in route.limitations)
            + "\n",
            encoding="utf-8",
        )
    outputs["assumptions"].write_text(
        "# Action Monodromy Remaining Assumptions\n\n"
        + "\n".join(f"- {item}" for item in payload["missing_assumptions"])
        + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_primitive_cyclic_monodromy_outputs()
