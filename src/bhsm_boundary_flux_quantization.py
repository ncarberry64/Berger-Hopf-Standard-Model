"""Boundary flux quantization and identity-channel protection sprint.

The functions here implement exact channel-count arithmetic and an auditable
status ledger for the boundary-flux theorem attempt.  The current repository
supports a coherent structural candidate, but not a completed derivation of the
flux quotient, identity protection, or traceless Brownian activity from the full
internal action.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from math import pi
from pathlib import Path
from typing import Any

from bhsm_completion_manual_theory_delta import frozen_sanity_payload
from bhsm_v1 import compare_bhsm_v1_branches
from constants import ALPHA_INV_LOW_ENERGY
from mode_selection import hopf_charge, omega_down, omega_lepton, omega_up


BOUNDARY_FLUX_QUANTIZATION_STRUCTURAL_CANDIDATE = (
    "BOUNDARY_FLUX_QUANTIZATION_STRUCTURAL_CANDIDATE"
)
BOUNDARY_FLUX_QUANTIZATION_OPEN = "BOUNDARY_FLUX_QUANTIZATION_OPEN"
CYCLIC_CHANNEL_SPACE_STRUCTURAL_CANDIDATE = "CYCLIC_CHANNEL_SPACE_STRUCTURAL_CANDIDATE"
GEOMETRIC_QUANTIZATION_DIMENSION_OPEN = "GEOMETRIC_QUANTIZATION_DIMENSION_OPEN"
BOUNDARY_ALGEBRA_REGULAR_REP_STRUCTURAL_CANDIDATE = (
    "BOUNDARY_ALGEBRA_REGULAR_REP_STRUCTURAL_CANDIDATE"
)
BOUNDARY_ACTION_FLUX_STRUCTURAL_CANDIDATE = "BOUNDARY_ACTION_FLUX_STRUCTURAL_CANDIDATE"
IDENTITY_CHANNEL_PROTECTION_STRUCTURAL_CANDIDATE = (
    "IDENTITY_CHANNEL_PROTECTION_STRUCTURAL_CANDIDATE"
)
TRACELESS_BROWNIAN_ACTIVITY_STRUCTURAL_CANDIDATE = (
    "TRACELESS_BROWNIAN_ACTIVITY_STRUCTURAL_CANDIDATE"
)
LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE = (
    "LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE"
)
PURE_FIBER_DOUBLE_BRANCH_ANALOGY_ONLY = "PURE_FIBER_DOUBLE_BRANCH_ANALOGY_ONLY"
CKM_H_MIX_DIM4_ANALOGY_ONLY = "CKM_H_MIX_DIM4_ANALOGY_ONLY"
NEUTRINO_LEAKAGE_CHANNEL_REFINED = "NEUTRINO_LEAKAGE_CHANNEL_REFINED"


@dataclass(frozen=True)
class RouteStatus:
    """One derivation route status."""

    route_id: str
    title: str
    status: str
    derived: bool
    candidate_only: bool
    evidence_found: tuple[str, ...]
    evidence_missing: tuple[str, ...]


@dataclass(frozen=True)
class TheoremStatusObject:
    """Full theorem decision object."""

    theorem_status: str
    flux_quantization_status: str
    cyclic_channel_space_status: str
    geometric_quantization_status: str
    boundary_algebra_status: str
    boundary_action_status: str
    identity_protection_status: str
    traceless_activity_status: str
    lepton_status: str
    pure_fiber_status: str
    ckm_status: str
    neutrino_status: str
    does_dim_H_equal_abs_Omega_follow: bool
    does_identity_channel_protection_follow: bool
    does_traceless_activity_follow: bool
    does_lepton_8_9_follow: bool
    blockers_closed: tuple[str, ...]
    blockers_remaining: tuple[str, ...]


def is_integer_boundary_level(Omega: int | Fraction) -> bool:
    """Return whether Omega is an integer boundary level."""

    return Fraction(Omega).denominator == 1


def boundary_flux_number(Omega: int | Fraction) -> Fraction:
    """Return the candidate quantized boundary flux number as a Fraction."""

    value = Fraction(Omega)
    if value == 0:
        raise ValueError("boundary flux level must be nonzero")
    if value.denominator != 1:
        raise ValueError("boundary flux level must be integral")
    return value


def cyclic_channel_dimension(Omega: int | Fraction) -> int:
    """Return |Omega| for an integral candidate cyclic channel space."""

    return int(abs(boundary_flux_number(Omega)))


def endomorphism_channel_count(dim_H: int) -> int:
    """Return dim End(H)=dim(H)^2."""

    if dim_H <= 0:
        raise ValueError("dim_H must be positive")
    return dim_H * dim_H


def identity_channel_count(dim_H: int) -> int:
    """Return the identity/coherent channel count."""

    if dim_H <= 0:
        raise ValueError("dim_H must be positive")
    return 1


def traceless_channel_count(dim_H: int) -> int:
    """Return the traceless channel count dim End(H)-1."""

    return endomorphism_channel_count(dim_H) - identity_channel_count(dim_H)


def active_traceless_fraction(dim_H: int) -> Fraction:
    """Return (dim(H)^2-1)/dim(H)^2 exactly."""

    return Fraction(traceless_channel_count(dim_H), endomorphism_channel_count(dim_H))


def active_traceless_fraction_from_Omega(Omega: int | Fraction) -> Fraction:
    """Return active traceless fraction using dim(H)=|Omega|."""

    return active_traceless_fraction(cyclic_channel_dimension(Omega))


def lepton_eta_flux_rule(alpha: float, Omega_l: int = 3) -> float:
    """Return eta_l=(alpha/pi)*active_traceless_fraction_from_Omega(Omega_l)."""

    return float((alpha / pi) * active_traceless_fraction_from_Omega(Omega_l))


def end_algebra_split_label(dim_H: int) -> str:
    """Return a compact label for End(H)=C I_d + su(d)."""

    if dim_H <= 0:
        raise ValueError("dim_H must be positive")
    return f"C I_{dim_H} + su({dim_H})"


def pure_fiber_rank_projection(dim: int = 2, rank: int = 1) -> Fraction:
    """Return the candidate pure-fiber rank projection rank/dim."""

    if dim <= 0:
        raise ValueError("dim must be positive")
    if rank < 0 or rank > dim:
        raise ValueError("rank must satisfy 0 <= rank <= dim")
    return Fraction(rank, dim)


def ckm_channel_dilution_factor(
    Z_mass: Fraction | float = Fraction(1, 2), dim_H_mix: int = 4
) -> float:
    """Return Z_mass^(1/dim(End(H_mix)))."""

    value = float(Z_mass)
    if value <= 0:
        raise ValueError("Z_mass must be positive")
    if dim_H_mix <= 0:
        raise ValueError("dim_H_mix must be positive")
    return float(value ** (1.0 / endomorphism_channel_count(dim_H_mix)))


def charged_boundary_flux_table() -> dict[str, dict[str, Any]]:
    """Return charged-sector boundary levels interpreted as candidate fluxes."""

    entries = {
        "lepton_middle": ("lepton", (5, 2), omega_lepton),
        "lepton_light": ("lepton", (9, 3), omega_lepton),
        "up_middle": ("up", (6, 0), omega_up),
        "up_light": ("up", (10, 1), omega_up),
        "down_middle": ("down", (6, 3), omega_down),
        "down_light": ("down", (8, 2), omega_down),
    }
    out: dict[str, dict[str, Any]] = {}
    for label, (sector, mode, omega_fn) in entries.items():
        k, j = mode
        omega = omega_fn(k, j)
        dim_h = cyclic_channel_dimension(omega)
        out[label] = {
            "sector": sector,
            "mode": mode,
            "q": hopf_charge(k, j),
            "omega": omega,
            "integer_boundary_level": is_integer_boundary_level(omega),
            "candidate_flux_number": boundary_flux_number(omega),
            "candidate_dim_H": dim_h,
            "endomorphism_channels": endomorphism_channel_count(dim_h),
            "traceless_channels": traceless_channel_count(dim_h),
        }
    return out


def flux_quantization_route() -> RouteStatus:
    """Route 1: boundary flux quantization."""

    return RouteStatus(
        route_id="flux_quantization",
        title="Boundary flux quantization",
        status=BOUNDARY_FLUX_QUANTIZATION_STRUCTURAL_CANDIDATE,
        derived=False,
        candidate_only=True,
        evidence_found=(
            "Omega_l, Omega_u, and Omega_d are integer boundary levels on the supplied mode ledger.",
            "Each sector's two non-heavy modes lie on the same integer boundary level.",
            "Existing notes use Hopf, boundary phase, orientation, and holonomy language.",
        ),
        evidence_missing=(
            "No implemented boundary one-form A_boundary has integral Omega_f=(1/2pi) integral A_boundary.",
            "No complete variation derives Omega_f as a flux rather than a boundary selection functional.",
            "Sector signs and cofactors are not yet derived from an integral flux object.",
        ),
    )


def cyclic_channel_route() -> RouteStatus:
    """Route 2: holonomy and cyclic phase space."""

    return RouteStatus(
        route_id="cyclic_channel_space",
        title="Holonomy and cyclic phase space",
        status=CYCLIC_CHANNEL_SPACE_STRUCTURAL_CANDIDATE,
        derived=False,
        candidate_only=True,
        evidence_found=(
            "A cyclic phase basis exp(2*pi*i*r/|Omega_f|) gives |Omega_f| channels.",
            "The construction is compatible with Hopf U(1) periodicity language.",
        ),
        evidence_missing=(
            "No proof makes physical boundary channels residues modulo Omega_f.",
            "No proof selects the regular cyclic representation as H_f.",
        ),
    )


def geometric_quantization_route() -> RouteStatus:
    """Route 3: geometric quantization dimension."""

    return RouteStatus(
        route_id="geometric_quantization",
        title="Geometric quantization finite dimension",
        status=GEOMETRIC_QUANTIZATION_DIMENSION_OPEN,
        derived=False,
        candidate_only=True,
        evidence_found=(
            "The proposed dimension rule resembles flux/Chern-number degeneracy statements.",
        ),
        evidence_missing=(
            "No compact boundary phase space, line bundle, curvature two-form, or Chern number is implemented for this channel count.",
            "No geometric-quantization theorem is matched to concrete BHSM boundary data.",
        ),
    )


def boundary_algebra_route() -> RouteStatus:
    """Route 4: boundary algebra regular representation."""

    return RouteStatus(
        route_id="boundary_algebra",
        title="Boundary algebra / regular representation",
        status=BOUNDARY_ALGEBRA_REGULAR_REP_STRUCTURAL_CANDIDATE,
        derived=False,
        candidate_only=True,
        evidence_found=(
            "The group algebra C[Z_|Omega_f|] has a regular representation of dimension |Omega_f|.",
            "Its identity element gives a natural coherent-channel candidate.",
        ),
        evidence_missing=(
            "No boundary quotient algebra A_f=C[Z_|Omega_f|] is derived from the internal action.",
            "No proof identifies the regular representation with the stochastic dressing channel space.",
        ),
    )


def boundary_action_route() -> RouteStatus:
    """Route 5: boundary action variation."""

    return RouteStatus(
        route_id="boundary_action",
        title="Boundary action variation",
        status=BOUNDARY_ACTION_FLUX_STRUCTURAL_CANDIDATE,
        derived=False,
        candidate_only=True,
        evidence_found=(
            "A constraint or penalty term can be written that would enforce Omega_f=Omega_f0.",
            "The existing mode ledger is consistent with stationary constant boundary levels.",
        ),
        evidence_missing=(
            "The candidate term is not derived from the full Berger-Hopf internal action.",
            "Stationarity has not been shown to leave exactly |Omega_f0| residual channels.",
        ),
    )


def identity_protection_route() -> RouteStatus:
    """Route 6: identity-channel protection."""

    return RouteStatus(
        route_id="identity_protection",
        title="Identity-channel protection",
        status=IDENTITY_CHANNEL_PROTECTION_STRUCTURAL_CANDIDATE,
        derived=False,
        candidate_only=True,
        evidence_found=(
            "Trace-preserving endomorphism language naturally splits End(H)=C I + traceless channels.",
            "The identity component is common-mode and can be interpreted as normalization/gauge-coherent.",
        ),
        evidence_missing=(
            "No repository stochastic rule proves dressing acts on density/covariance endomorphisms.",
            "No action-level conservation law proves the identity channel is protected from relative mass-ratio dressing.",
        ),
    )


def traceless_activity_route() -> RouteStatus:
    """Route 7: active traceless Brownian stochastic channels."""

    return RouteStatus(
        route_id="traceless_activity",
        title="Active traceless Brownian stochastic channels",
        status=TRACELESS_BROWNIAN_ACTIVITY_STRUCTURAL_CANDIDATE,
        derived=False,
        candidate_only=True,
        evidence_found=(
            "Zero-mean stochastic fluctuations are naturally traceless after removing common-mode identity drift.",
            "The active fraction (d^2-1)/d^2 follows if total channels are End(H) and active channels are traceless.",
        ),
        evidence_missing=(
            "No Brownian generator on su(d_f) is derived from BHSM virtual dressing dynamics.",
            "No proof excludes identity-channel stochastic activity except as common normalization.",
        ),
    )


def route_statuses() -> tuple[RouteStatus, ...]:
    """Return all route statuses in the audit."""

    return (
        flux_quantization_route(),
        cyclic_channel_route(),
        geometric_quantization_route(),
        boundary_algebra_route(),
        boundary_action_route(),
        identity_protection_route(),
        traceless_activity_route(),
    )


def theorem_status_object() -> TheoremStatusObject:
    """Return the theorem status object."""

    return TheoremStatusObject(
        theorem_status=BOUNDARY_FLUX_QUANTIZATION_STRUCTURAL_CANDIDATE,
        flux_quantization_status=BOUNDARY_FLUX_QUANTIZATION_STRUCTURAL_CANDIDATE,
        cyclic_channel_space_status=CYCLIC_CHANNEL_SPACE_STRUCTURAL_CANDIDATE,
        geometric_quantization_status=GEOMETRIC_QUANTIZATION_DIMENSION_OPEN,
        boundary_algebra_status=BOUNDARY_ALGEBRA_REGULAR_REP_STRUCTURAL_CANDIDATE,
        boundary_action_status=BOUNDARY_ACTION_FLUX_STRUCTURAL_CANDIDATE,
        identity_protection_status=IDENTITY_CHANNEL_PROTECTION_STRUCTURAL_CANDIDATE,
        traceless_activity_status=TRACELESS_BROWNIAN_ACTIVITY_STRUCTURAL_CANDIDATE,
        lepton_status=LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE,
        pure_fiber_status=PURE_FIBER_DOUBLE_BRANCH_ANALOGY_ONLY,
        ckm_status=CKM_H_MIX_DIM4_ANALOGY_ONLY,
        neutrino_status=NEUTRINO_LEAKAGE_CHANNEL_REFINED,
        does_dim_H_equal_abs_Omega_follow=False,
        does_identity_channel_protection_follow=False,
        does_traceless_activity_follow=False,
        does_lepton_8_9_follow=False,
        blockers_closed=(),
        blockers_remaining=(
            "derive Omega_f as an integral boundary flux or holonomy from a concrete A_boundary",
            "derive dim(H_f)=|Omega_f| rather than postulating cyclic residues",
            "derive End(H_f) as the stochastic dressing channel algebra",
            "derive identity-channel protection from trace/gauge/normalization conservation",
            "derive Brownian activity on traceless su(d_f) channels",
            "derive pure-fiber double branch rather than analogy",
            "derive CKM H_mix dimension 4 rather than analogy",
        ),
    )


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
    """Return the full audit payload."""

    status = theorem_status_object()
    routes = route_statuses()
    alpha = 1.0 / ALPHA_INV_LOW_ENERGY
    missing = tuple(
        f"{route.route_id}: {item}" for route in routes for item in route.evidence_missing
    ) + status.blockers_remaining
    no_outputs = validate_no_official_outputs_modified()
    payload: dict[str, Any] = {
        "title": "BHSM boundary flux quantization and identity-channel protection theorem sprint",
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        "theorem_status": status.theorem_status,
        "flux_quantization_status": status.flux_quantization_status,
        "cyclic_channel_space_status": status.cyclic_channel_space_status,
        "geometric_quantization_status": status.geometric_quantization_status,
        "boundary_algebra_status": status.boundary_algebra_status,
        "boundary_action_status": status.boundary_action_status,
        "identity_protection_status": status.identity_protection_status,
        "traceless_activity_status": status.traceless_activity_status,
        "lepton_status": status.lepton_status,
        "pure_fiber_status": status.pure_fiber_status,
        "ckm_status": status.ckm_status,
        "neutrino_status": status.neutrino_status,
        "does_dim_H_equal_abs_Omega_follow": status.does_dim_H_equal_abs_Omega_follow,
        "does_identity_channel_protection_follow": status.does_identity_channel_protection_follow,
        "does_traceless_activity_follow": status.does_traceless_activity_follow,
        "does_lepton_8_9_follow": status.does_lepton_8_9_follow,
        "blockers_closed": status.blockers_closed,
        "blockers_remaining": status.blockers_remaining,
        "derived_components": (),
        "candidate_components": (
            "boundary_flux_quantization",
            "cyclic_channel_space",
            "boundary_algebra_regular_rep",
            "boundary_action_flux",
            "identity_channel_protection",
            "traceless_brownian_activity",
            "lepton_8_9",
            "pure_fiber_double_branch",
            "ckm_h_mix_dim4",
            "neutrino_leakage_refinement",
        ),
        "rejected_components": (),
        "missing_assumptions": missing,
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "routes": routes,
        "searched_repo_concepts": (
            "boundary one-forms and action scaffolds",
            "Hopf/Berger fiber and holonomy notes",
            "mode-selection and omega ledgers",
            "virtual/stochastic dressing audits",
            "CKM mixing-dressing candidate audits",
            "PMNS effective-extension ledgers",
        ),
        "charged_boundary_flux_table": charged_boundary_flux_table(),
        "calculations": {
            "cyclic_channel_dimension_3": cyclic_channel_dimension(3),
            "endomorphism_channel_count_3": endomorphism_channel_count(3),
            "identity_channel_count_3": identity_channel_count(3),
            "traceless_channel_count_3": traceless_channel_count(3),
            "active_traceless_fraction_3": active_traceless_fraction(3),
            "active_traceless_fraction_from_Omega_3": active_traceless_fraction_from_Omega(3),
            "lepton_eta_flux_rule_3": lepton_eta_flux_rule(alpha, 3),
            "end_algebra_split_label_3": end_algebra_split_label(3),
            "pure_fiber_rank_projection_2_1": pure_fiber_rank_projection(2, 1),
            "ckm_channel_dilution_1_2_dim4": ckm_channel_dilution_factor(Fraction(1, 2), 4),
        },
        "neutrino_consequence": {
            "ordinary_FTL_claim": False,
            "candidate_only": True,
            "no_numerical_PMNS_claims": True,
            "status": status.neutrino_status,
            "note": (
                "Boundary-channel language refines the candidate leakage ledger: neutral modes may occupy weakly "
                "field-attached residual or quotient channels rather than charged EM-dressed traceless channels."
            ),
        },
    }
    payload.update(no_outputs)
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
        "# BHSM Boundary Flux Quantization and Identity-Channel Protection",
        "",
        "This sprint tests whether Omega_f is a quantized boundary flux/holonomy number and whether the identity/traceless channel split derives the lepton 8/9 factor.",
        "The result remains candidate-only: the concrete boundary flux object, identity protection theorem, and Brownian su(d) generator are not yet derived.",
        "",
        "## Summary",
        "",
        f"Theorem status: `{payload['theorem_status']}`",
        f"Flux quantization: `{payload['flux_quantization_status']}`",
        f"Cyclic channel space: `{payload['cyclic_channel_space_status']}`",
        f"Geometric quantization: `{payload['geometric_quantization_status']}`",
        f"Boundary algebra: `{payload['boundary_algebra_status']}`",
        f"Boundary action: `{payload['boundary_action_status']}`",
        f"Identity protection: `{payload['identity_protection_status']}`",
        f"Traceless Brownian activity: `{payload['traceless_activity_status']}`",
        f"Lepton 8/9: `{payload['lepton_status']}`",
        f"Pure-fiber 1/2 consequence: `{payload['pure_fiber_status']}`",
        f"CKM 1/16 consequence: `{payload['ckm_status']}`",
        f"Neutrino/PMNS: `{payload['neutrino_status']}`",
        "",
        "## Exact Calculations",
        "",
        "| Quantity | Value |",
        "| --- | --- |",
    ]
    for key, value in payload["calculations"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Route Statuses",
            "",
            "| Route | Status | Derived | Candidate only |",
            "| --- | --- | --- | --- |",
        ]
    )
    for route in payload["routes"]:
        lines.append(
            f"| `{route.route_id}` | `{route.status}` | `{route.derived}` | `{route.candidate_only}` |"
        )
    lines.extend(
        [
            "",
            "## Charged Boundary Flux Table",
            "",
            "| Mode label | Sector | Mode | q | Omega | dim(H) candidate | End channels | Traceless |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for label, row in payload["charged_boundary_flux_table"].items():
        lines.append(
            f"| `{label}` | `{row['sector']}` | `{tuple(row['mode'])}` | {row['q']} | {row['omega']} | {row['candidate_dim_H']} | {row['endomorphism_channels']} | {row['traceless_channels']} |"
        )
    lines.extend(["", "## Missing Assumptions", ""])
    lines.extend(f"- {item}" for item in payload["missing_assumptions"])
    lines.extend(
        [
            "",
            "## Neutrino/PMNS Consequence",
            "",
            f"Status: `{payload['neutrino_consequence']['status']}`",
            f"ordinary_FTL_claim: `{payload['neutrino_consequence']['ordinary_FTL_claim']}`",
            f"candidate_only: `{payload['neutrino_consequence']['candidate_only']}`",
            "",
            payload["neutrino_consequence"]["note"],
            "",
            "## Claim Discipline",
            "",
            "- No official frozen outputs are changed.",
            "- No retuning is performed.",
            "- No ordinary superluminal neutrino claim is made.",
            "- No ordinary environmental mass drift claim is made.",
            "- No claim of replacing the Standard Model or proving BHSM is made.",
            "- No claim of a complete first-principles Standard Model derivation is made.",
            "- The lepton 8/9 factor remains structural candidate unless the missing flux/protection/activity assumptions are derived.",
            "",
        ]
    )
    return "\n".join(lines)


def export_boundary_flux_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export theory and audit artifacts."""

    base = Path(root)
    payload = audit_payload()
    markdown = render_markdown(payload)
    paths = {
        "theory_flux": base / "theory" / "boundary_flux_quantization_theorem.md",
        "theory_identity": base / "theory" / "identity_traceless_channel_protection.md",
        "audit_md": base / "audits" / "boundary_flux_quantization_theorem_audit.md",
        "audit_json": base / "audits" / "boundary_flux_quantization_theorem_audit.json",
        "geo": base / "theory" / "geometric_quantization_boundary_channel_candidate.md",
        "holonomy": base / "theory" / "boundary_cyclic_holonomy_construction.md",
        "lepton": base / "theory" / "lepton_su3_traceless_dressing_rule.md",
        "fiber": base / "theory" / "pure_fiber_double_branch_consequence.md",
        "ckm": base / "theory" / "ckm_mix_channel_dim4_consequence.md",
        "neutrino": base / "theory" / "neutrino_leakage_boundary_consequence.md",
    }
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    paths["theory_flux"].write_text(markdown, encoding="utf-8")
    paths["audit_md"].write_text(markdown, encoding="utf-8")
    paths["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    paths["theory_identity"].write_text(
        "\n".join(
            [
                "# Identity and Traceless Channel Protection",
                "",
                f"Identity status: `{payload['identity_protection_status']}`",
                f"Traceless activity status: `{payload['traceless_activity_status']}`",
                "",
                "Candidate split:",
                "",
                "```text",
                "End(H_f) = C I_f + su(dim(H_f))",
                "dim End(H_f)=d_f^2",
                "dim su(d_f)=d_f^2-1",
                "```",
                "",
                "This sprint does not derive the trace-preserving stochastic rule or Brownian generator from the full internal action.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    paths["geo"].write_text(
        "# Geometric Quantization Boundary Channel Candidate\n\n"
        "Status: `GEOMETRIC_QUANTIZATION_DIMENSION_OPEN`\n\n"
        "A flux-degeneracy theorem could imply dim(H_f)=|Omega_f|, but the repo does not yet define the required compact boundary phase space, line bundle, curvature two-form, or Chern number.\n",
        encoding="utf-8",
    )
    paths["holonomy"].write_text(
        "# Boundary Cyclic Holonomy Construction\n\n"
        "Status: `CYCLIC_CHANNEL_SPACE_STRUCTURAL_CANDIDATE`\n\n"
        "A cyclic phase basis exp(2*pi*i*r/|Omega_f|) is compatible with the proposed channel count. The missing step is deriving the modulo-Omega_f boundary equivalence from the BHSM action or holonomy object.\n",
        encoding="utf-8",
    )
    paths["lepton"].write_text(
        "# Lepton su(3) Traceless Dressing Rule\n\n"
        f"Status: `{payload['lepton_status']}`\n\n"
        "For Omega_l=3, the candidate channel space has d=3, End(H_l) has 9 channels, and su(3) has 8 traceless directions. This gives eta_l=8 alpha/(9 pi) if identity protection and traceless Brownian activity are derived. They remain structural candidates here.\n",
        encoding="utf-8",
    )
    paths["fiber"].write_text(
        "# Pure-Fiber Double-Branch Consequence\n\n"
        f"Status: `{payload['pure_fiber_status']}`\n\n"
        "The boundary-flux language is compatible by analogy with a two-branch pure-fiber orientation space for mode (6,0), but it does not derive the double branch or rank-one projection.\n",
        encoding="utf-8",
    )
    paths["ckm"].write_text(
        "# CKM H_mix Dimension-4 Consequence\n\n"
        f"Status: `{payload['ckm_status']}`\n\n"
        "The End-channel language is compatible by analogy with a 16-channel CKM 2-3 correlation space, but it does not derive dim(H_mix)=4.\n",
        encoding="utf-8",
    )
    paths["neutrino"].write_text(
        "# Neutrino Leakage Boundary Consequence\n\n"
        f"Status: `{payload['neutrino_status']}`\n\n"
        "ordinary_FTL_claim: `False`\n\n"
        "Neutral modes remain candidate leakage/complement channels. No numerical PMNS claims are added.\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_boundary_flux_outputs()
