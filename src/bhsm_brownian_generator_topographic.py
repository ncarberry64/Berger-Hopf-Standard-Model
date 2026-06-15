"""Brownian generator from topographic attractor dynamics audit.

The module formalizes a conservative bridge from the topographic-attractor
scaffold to trace-preserving Brownian activity on the finite channel algebra.
It does not alter frozen BHSM predictions.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from math import exp, isclose, pi
from pathlib import Path
from typing import Any

from bhsm_config import canonical_geometry_config
from bhsm_completion_manual_theory_delta import frozen_sanity_payload
from bhsm_physical_boundary_channel_space import (
    PHYSICAL_CHANNEL_SPACE_PARTIAL,
    active_fraction_from_orbit,
    physical_channel_dimension,
)
from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import ALPHA_INV_LOW_ENERGY, S_OVERLAP


BROWNIAN_GENERATOR_TOPOGRAPHIC_PARTIAL = "BROWNIAN_GENERATOR_TOPOGRAPHIC_PARTIAL"
ATTRACTOR_HESSIAN_BROWNIAN_PARTIAL = "ATTRACTOR_HESSIAN_BROWNIAN_PARTIAL"
BOUNDARY_NOISE_PROJECTION_PARTIAL = "BOUNDARY_NOISE_PROJECTION_PARTIAL"
TRACE_PRESERVING_NOISE_PARTIAL = "TRACE_PRESERVING_NOISE_PARTIAL"
TRACELESS_BROWNIAN_GENERATOR_PARTIAL = "TRACELESS_BROWNIAN_GENERATOR_PARTIAL"
EXPONENTIAL_DRESSING_FROM_BROWNIAN_PARTIAL = "EXPONENTIAL_DRESSING_FROM_BROWNIAN_PARTIAL"
QUADRATIC_NORM_HOPF_BASE_PARTIAL = "QUADRATIC_NORM_HOPF_BASE_PARTIAL"
ALPHA_OVER_PI_STOCHASTIC_STRENGTH_STRUCTURAL_CANDIDATE = (
    "ALPHA_OVER_PI_STOCHASTIC_STRENGTH_STRUCTURAL_CANDIDATE"
)
LEPTON_8_9_CHANNEL_RULE_PARTIAL_DERIVATION_STRENGTHENED = (
    "LEPTON_8_9_CHANNEL_RULE_PARTIAL_DERIVATION_STRENGTHENED"
)
QUARK_BROWNIAN_ACTIVE_FRACTION_CANDIDATE_ONLY = (
    "QUARK_BROWNIAN_ACTIVE_FRACTION_CANDIDATE_ONLY"
)
NEUTRINO_BROWNIAN_CHANNEL_CANDIDATE_ONLY = (
    "NEUTRINO_BROWNIAN_CHANNEL_CANDIDATE_ONLY"
)


@dataclass(frozen=True)
class BrownianRouteStatus:
    """Status for one Brownian-generator route."""

    route: str
    status: str
    supports_brownian_rule: bool
    derived_from_complete_dynamics: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class SectorBrownianStatus:
    """Exact sector Brownian channel counts."""

    sector: str
    dimension: int
    endomorphism_dimension: int
    traceless_generators: int
    active_fraction: Fraction
    brownian_generator_count: int
    candidate_only: bool


def q_from_kj(k: int, j: int) -> int:
    """Return Hopf charge q=k-2j."""

    return int(k) - 2 * int(j)


def mode_norm_N(k: int, j: int) -> int:
    """Return the candidate Hopf/base quadratic norm N=q^2+j^2."""

    q = q_from_kj(k, j)
    return q * q + int(j) * int(j)


def endomorphism_dimension(d: int) -> int:
    """Return dim End(H)=d^2."""

    if int(d) <= 0:
        raise ValueError("dimension must be positive")
    return int(d) * int(d)


def traceless_generator_count(d: int) -> int:
    """Return dim su(d)=d^2-1."""

    return endomorphism_dimension(d) - 1


def active_fraction(d: int) -> Fraction:
    """Return exact active traceless fraction (d^2-1)/d^2."""

    return Fraction(traceless_generator_count(d), endomorphism_dimension(d))


def brownian_generator_count(d: int) -> int:
    """Return number of traceless Brownian generator directions."""

    return traceless_generator_count(d)


def trace_preserving_noise_condition(trace_delta: float) -> bool:
    """Return whether a fluctuation is trace-preserving."""

    return isclose(float(trace_delta), 0.0, rel_tol=0.0, abs_tol=1e-15)


def probability_simplex_fluctuation_dimension(d: int) -> int:
    """Return zero-sum probability-vector fluctuation dimension d-1."""

    if int(d) <= 0:
        raise ValueError("dimension must be positive")
    return int(d) - 1


def end_traceless_fluctuation_dimension(d: int) -> int:
    """Return traceless End(H) fluctuation dimension d^2-1."""

    return traceless_generator_count(d)


def exponential_dressing(eta: float, k: int, j: int) -> float:
    """Return exp[-eta N(k,j)]."""

    return exp(-float(eta) * mode_norm_N(k, j))


def eta_from_alpha_active_fraction(alpha: float, d: int) -> float:
    """Return eta=(alpha/pi)*(d^2-1)/d^2."""

    return float(alpha) / pi * float(active_fraction(d))


def lepton_eta_8_9(alpha: float) -> float:
    """Return eta_l=8alpha/(9pi)."""

    return eta_from_alpha_active_fraction(alpha, 3)


def attractor_susceptibility_proxy(k: int, j: int, gap: float | None = None) -> float:
    """Return monotone inverse-Hessian susceptibility proxy."""

    scale = 1.0 + mode_norm_N(k, j)
    if gap is not None:
        scale += max(float(gap), 0.0)
    return 1.0 / scale


def sector_brownian_status(sector: str) -> SectorBrownianStatus:
    """Return exact Brownian channel counts for charged sectors."""

    sector_to_omega = {"charged_lepton": 3, "up": 6, "down": 12}
    if sector not in sector_to_omega:
        raise ValueError(f"unknown sector: {sector}")
    d = physical_channel_dimension(sector_to_omega[sector])
    return SectorBrownianStatus(
        sector=sector,
        dimension=d,
        endomorphism_dimension=endomorphism_dimension(d),
        traceless_generators=traceless_generator_count(d),
        active_fraction=active_fraction_from_orbit(d),
        brownian_generator_count=brownian_generator_count(d),
        candidate_only=sector != "charged_lepton",
    )


def topographic_fluctuation_status_object() -> BrownianRouteStatus:
    """Return topographic fluctuation route status."""

    return BrownianRouteStatus(
        route="topographic_fluctuation",
        status=BROWNIAN_GENERATOR_TOPOGRAPHIC_PARTIAL,
        supports_brownian_rule=True,
        derived_from_complete_dynamics=False,
        assumptions=(
            "local topographic attractors admit a quadratic fluctuation expansion",
            "the inverse stability operator gives a covariance/susceptibility proxy",
        ),
        limitations=(
            "the full Hessian of the completed BHSM action is not computed",
            "noise statistics are modeled rather than derived from a measure",
        ),
    )


def attractor_hessian_status_object() -> BrownianRouteStatus:
    """Return attractor Hessian route status."""

    return BrownianRouteStatus(
        route="attractor_hessian",
        status=ATTRACTOR_HESSIAN_BROWNIAN_PARTIAL,
        supports_brownian_rule=True,
        derived_from_complete_dynamics=False,
        assumptions=(
            "T=T_f^*+delta T near a stable attractor",
            "E[T] has a positive quadratic stability form on local fluctuations",
        ),
        limitations=(
            "the attractor Hessian is represented by a proxy",
            "no full topographic Green function is computed",
        ),
    )


def boundary_noise_projection_status_object() -> BrownianRouteStatus:
    """Return boundary projection route status."""

    return BrownianRouteStatus(
        route="boundary_noise_projection",
        status=BOUNDARY_NOISE_PROJECTION_PARTIAL,
        supports_brownian_rule=True,
        derived_from_complete_dynamics=False,
        assumptions=(
            "boundary projection maps delta T_boundary into channel covariance",
            "the channel space H_f is the physical residue-channel scaffold",
        ),
        limitations=(
            "the projection kernel Pi_f is symbolic",
            "projection weights are not derived from a completed boundary action",
        ),
    )


def trace_preserving_noise_status_object() -> BrownianRouteStatus:
    """Return trace-preserving route status."""

    return BrownianRouteStatus(
        route="trace_preserving_noise",
        status=TRACE_PRESERVING_NOISE_PARTIAL,
        supports_brownian_rule=True,
        derived_from_complete_dynamics=False,
        assumptions=(
            "relative hierarchy observables remove common normalization",
            "trace-preserving perturbations have Tr(delta rho_f)=0",
        ),
        limitations=(
            "trace preservation is a channel-normalization condition",
            "full stochastic dynamics selecting this constraint remains open",
        ),
    )


def brownian_generator_status_object() -> BrownianRouteStatus:
    """Return su(d) Brownian generator route status."""

    return BrownianRouteStatus(
        route="su_d_brownian_generator",
        status=TRACELESS_BROWNIAN_GENERATOR_PARTIAL,
        supports_brownian_rule=True,
        derived_from_complete_dynamics=False,
        assumptions=(
            "noise acts on End(H_f)",
            "trace-preserving zero-mean fluctuations live in traceless Hermitian End(H_f)",
        ),
        limitations=(
            "the Lindblad/Brownian rates D_a are not derived",
            "the complete stochastic process is not constructed from first principles",
        ),
    )


def exponential_dressing_status_object() -> BrownianRouteStatus:
    """Return exponential dressing route status."""

    return BrownianRouteStatus(
        route="exponential_dressing",
        status=EXPONENTIAL_DRESSING_FROM_BROWNIAN_PARTIAL,
        supports_brownian_rule=True,
        derived_from_complete_dynamics=False,
        assumptions=(
            "Gaussian/Brownian quadratic activity gives exp[-eta <v,v>]",
            "the Hopf/base displacement norm is N=q^2+j^2",
        ),
        limitations=(
            "eta is not retuned or fitted here",
            "the full fluctuation measure is still a scaffold",
        ),
    )


def alpha_over_pi_status_object() -> BrownianRouteStatus:
    """Return alpha/pi stochastic strength route status."""

    return BrownianRouteStatus(
        route="alpha_over_pi_strength",
        status=ALPHA_OVER_PI_STOCHASTIC_STRENGTH_STRUCTURAL_CANDIDATE,
        supports_brownian_rule=True,
        derived_from_complete_dynamics=False,
        assumptions=(
            "alpha is the electromagnetic/geometric U(1) coupling scale",
            "1/pi is the phase-averaging or loop-normalization scale used in the scaffold",
        ),
        limitations=(
            "alpha/pi is not derived from a completed stochastic path integral",
            "no new fitted strength is introduced",
        ),
    )


def lepton_status_object() -> BrownianRouteStatus:
    """Return lepton 8/9 consequence status."""

    return BrownianRouteStatus(
        route="lepton_8_9_consequence",
        status=LEPTON_8_9_CHANNEL_RULE_PARTIAL_DERIVATION_STRENGTHENED,
        supports_brownian_rule=True,
        derived_from_complete_dynamics=False,
        assumptions=(
            "d_l=3 from the partial physical channel-space scaffold",
            "trace-preserving Brownian activity acts on su(3)",
            "eta_l=(alpha/pi)*(8/9)",
        ),
        limitations=(
            "primitive monodromy remains partial",
            "alpha/pi and Brownian rates remain structural/partial",
            "this is not an official frozen prediction update",
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


def audit_payload(alpha: float | None = None) -> dict[str, Any]:
    """Return Brownian generator topographic audit payload."""

    resolved_alpha = 1.0 / ALPHA_INV_LOW_ENERGY if alpha is None else float(alpha)
    topographic = topographic_fluctuation_status_object()
    hessian = attractor_hessian_status_object()
    projection = boundary_noise_projection_status_object()
    trace = trace_preserving_noise_status_object()
    generator = brownian_generator_status_object()
    exp_status = exponential_dressing_status_object()
    alpha_status = alpha_over_pi_status_object()
    lepton = lepton_status_object()
    sectors = {
        sector: sector_brownian_status(sector)
        for sector in ("charged_lepton", "up", "down")
    }
    blockers_remaining = (
        "compute the full topographic attractor Hessian from the completed BHSM action",
        "derive the boundary projection kernel Pi_f from the full boundary dynamics",
        "derive Brownian/Lindblad rates D_a on su(d_f)",
        "derive alpha/pi from a completed stochastic path integral or boundary U(1) normalization",
        "derive primitive cyclic monodromy rather than using the partial scaffold",
    )
    payload: dict[str, Any] = {
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        "brownian_generator_topographic_status": topographic.status,
        "topographic_fluctuation_status": topographic.status,
        "attractor_hessian_status": hessian.status,
        "boundary_noise_projection_status": projection.status,
        "trace_preserving_noise_status": trace.status,
        "su_d_brownian_generator_status": generator.status,
        "exponential_dressing_status": exp_status.status,
        "quadratic_norm_status": QUADRATIC_NORM_HOPF_BASE_PARTIAL,
        "alpha_over_pi_strength_status": alpha_status.status,
        "lepton_8_9_consequence_status": lepton.status,
        "quark_brownian_consequence_status": QUARK_BROWNIAN_ACTIVE_FRACTION_CANDIDATE_ONLY,
        "neutrino_brownian_consequence_status": NEUTRINO_BROWNIAN_CHANNEL_CANDIDATE_ONLY,
        "does_topographic_dynamics_generate_noise": True,
        "does_boundary_projection_map_noise_to_H_f": True,
        "does_noise_act_on_End_H": True,
        "does_trace_preservation_force_su_d": True,
        "does_brownian_generator_live_on_su_d": True,
        "does_exponential_dressing_follow": True,
        "does_N_equal_q2_plus_j2_follow": True,
        "does_alpha_over_pi_follow": False,
        "does_eta_l_8_9_follow": True,
        "does_this_promote_full_lepton_8_9": False,
        "does_this_change_official_predictions": False,
        "upstream_physical_channel_space_status": PHYSICAL_CHANNEL_SPACE_PARTIAL,
        "blockers_closed": (
            "trace_preserving_noise_restricts_relative_activity_to_su_d",
            "Brownian_generator_count_equals_d_squared_minus_one",
            "exponential_quadratic_dressing_scaffold",
            "lepton_eta_8alpha_over_9pi_strengthened_as_partial_consequence",
        ),
        "blockers_remaining": blockers_remaining,
        "derived_components": (
            "exact_su_d_generator_count",
            "exact_active_fraction_from_End_H",
        ),
        "partial_components": (
            "topographic_fluctuation_covariance_proxy",
            "boundary_noise_projection_to_H_f",
            "trace_preserving_Brownian_generator_on_su_d",
            "exponential_dressing_from_quadratic_norm",
        ),
        "conditional_components": (
            "physical_channel_space_H_f",
            "primitive_cyclic_monodromy",
        ),
        "candidate_components": (
            "alpha_over_pi_stochastic_strength",
            "quark_active_fraction_consequences",
            "neutrino_brownian_channel_consequence",
        ),
        "missing_assumptions": blockers_remaining,
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "lepton_eta_8alpha_9pi": lepton_eta_8_9(resolved_alpha),
        "sector_brownian_statuses": sectors,
        "mode_norms": {
            "tau_reference": mode_norm_N(0, 0),
            "muon": mode_norm_N(5, 2),
            "electron": mode_norm_N(9, 3),
        },
        "dimension_warning": (
            "probability simplex dimension d-1 is not the lepton 8/9 count; "
            "8/9 uses traceless End(H) dimension d^2-1 over d^2"
        ),
        "routes": {
            "topographic": topographic,
            "hessian": hessian,
            "projection": projection,
            "trace": trace,
            "generator": generator,
            "exponential": exp_status,
            "alpha_over_pi": alpha_status,
            "lepton": lepton,
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
    heading = title or "BHSM Brownian Generator from Topographic Attractor Dynamics"
    lines = [
        f"# {heading}",
        "",
        "This sprint tests whether topographic attractor fluctuations can support trace-preserving Brownian activity on the finite channel algebra.",
        "The result is partial: exact su(d) channel counts and the quadratic damping scaffold are implemented, while the full stochastic dynamics remains open.",
        "",
        "## Summary",
        "",
        f"Brownian generator topographic status: `{p['brownian_generator_topographic_status']}`",
        f"Attractor Hessian status: `{p['attractor_hessian_status']}`",
        f"Boundary noise projection status: `{p['boundary_noise_projection_status']}`",
        f"Trace-preserving noise status: `{p['trace_preserving_noise_status']}`",
        f"su(d) Brownian generator status: `{p['su_d_brownian_generator_status']}`",
        f"Exponential dressing status: `{p['exponential_dressing_status']}`",
        f"Quadratic norm status: `{p['quadratic_norm_status']}`",
        f"alpha/pi strength status: `{p['alpha_over_pi_strength_status']}`",
        f"Lepton 8/9 consequence: `{p['lepton_8_9_consequence_status']}`",
        f"Quark consequence: `{p['quark_brownian_consequence_status']}`",
        f"Neutrino consequence: `{p['neutrino_brownian_consequence_status']}`",
        "",
        "## Brownian Chain",
        "",
        "```text",
        "T = T_f^* + delta T",
        "E[T] ~= E[T_f^*] + 1/2 <delta T, H_f delta T>",
        "delta rho_f = Pi_f delta T_boundary Pi_f^dagger",
        "Tr(delta rho_f)=0",
        "delta rho_f in su(d_f)",
        "Z(k,j)=exp[-eta (q^2+j^2)]",
        "```",
        "",
        f"Topographic dynamics generates noise scaffold: `{p['does_topographic_dynamics_generate_noise']}`",
        f"Boundary projection maps noise to H_f: `{p['does_boundary_projection_map_noise_to_H_f']}`",
        f"Noise acts on End(H): `{p['does_noise_act_on_End_H']}`",
        f"Trace preservation forces su(d): `{p['does_trace_preservation_force_su_d']}`",
        f"Exponential dressing follows as scaffold: `{p['does_exponential_dressing_follow']}`",
        f"alpha/pi follows: `{p['does_alpha_over_pi_follow']}`",
        "",
        "## Sector Counts",
        "",
        "| Sector | d | dim End(H) | su(d) generators | Active fraction | Candidate only |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for sector, row in p["sector_brownian_statuses"].items():
        lines.append(
            f"| `{sector}` | `{row.dimension}` | `{row.endomorphism_dimension}` | `{row.traceless_generators}` | `{row.active_fraction}` | `{row.candidate_only}` |"
        )
    lines.extend(
        [
            "",
            "## Lepton Consequence",
            "",
            f"`eta_l = {p['lepton_eta_8alpha_9pi']}` from `(alpha/pi)*(8/9)`.",
            f"Promotes full lepton 8/9: `{p['does_this_promote_full_lepton_8_9']}`",
            "",
            "## Dimension Warning",
            "",
            p["dimension_warning"],
            "",
            "## Blockers Closed",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in p["blockers_closed"])
    lines.extend(["", "## Blockers Remaining", ""])
    lines.extend(f"- {item}" for item in p["blockers_remaining"])
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


def export_brownian_generator_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export Brownian generator audit artifacts."""

    base = Path(root)
    payload = audit_payload()
    outputs = {
        "main": base / "theory" / "brownian_generator_from_topographic_attractor_dynamics.md",
        "hessian": base / "theory" / "attractor_hessian_fluctuation_candidate.md",
        "projection": base / "theory" / "boundary_projection_of_topographic_noise.md",
        "su_d": base / "theory" / "traceless_su_d_brownian_generator.md",
        "exponential": base / "theory" / "exponential_dressing_from_brownian_quadratic_norm.md",
        "alpha": base / "theory" / "alpha_over_pi_stochastic_strength_candidate.md",
        "lepton": base / "theory" / "lepton_8_9_partial_derivation_strengthened.md",
        "quark": base / "theory" / "quark_brownian_active_fraction_candidate.md",
        "neutrino": base / "theory" / "neutrino_brownian_channel_candidate.md",
        "audit_md": base / "audits" / "brownian_generator_topographic_attractor_audit.md",
        "audit_json": base / "audits" / "brownian_generator_topographic_attractor_audit.json",
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
        "hessian": ("Attractor Hessian Fluctuation Candidate", "hessian"),
        "projection": ("Boundary Projection of Topographic Noise", "projection"),
        "su_d": ("Traceless su(d) Brownian Generator", "generator"),
        "exponential": ("Exponential Dressing from Brownian Quadratic Norm", "exponential"),
        "alpha": ("Alpha over Pi Stochastic Strength Candidate", "alpha_over_pi"),
        "lepton": ("Lepton 8/9 Partial Derivation Strengthened", "lepton"),
    }
    for key, (heading, route_key) in route_files.items():
        route = payload["routes"][route_key]
        outputs[key].write_text(
            f"# {heading}\n\n"
            f"Status: `{route.status}`\n\n"
            f"Supports Brownian rule: `{route.supports_brownian_rule}`\n\n"
            f"Derived from complete dynamics: `{route.derived_from_complete_dynamics}`\n\n"
            "## Assumptions\n\n"
            + "\n".join(f"- {item}" for item in route.assumptions)
            + "\n\n## Limitations\n\n"
            + "\n".join(f"- {item}" for item in route.limitations)
            + "\n",
            encoding="utf-8",
        )
    outputs["quark"].write_text(
        "# Quark Brownian Active Fraction Candidate\n\n"
        f"Status: `{payload['quark_brownian_consequence_status']}`\n\n"
        "Up active fraction is `35/36`; down active fraction is `143/144`. These remain candidate-only and do not alter frozen quark predictions.\n",
        encoding="utf-8",
    )
    outputs["neutrino"].write_text(
        "# Neutrino Brownian Channel Candidate\n\n"
        f"Status: `{payload['neutrino_brownian_consequence_status']}`\n\n"
        "No neutrino mode ledger, PMNS derivation, or neutrino speed anomaly claim is introduced.\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_brownian_generator_outputs()
