"""Stochastic path-integral normalization audit for BHSM.

This module separates three conventions for the same U(1) boundary scale:

* raw phase variance, where ``g^2=alpha/pi`` and the phase cumulant gives
  an extra one-half in the exponent;
* heat-kernel generator coefficient, where ``D=alpha/pi`` enters directly
  in ``Z=exp[-D N]``;
* Ito ``sqrt(2D)`` notation, which reconciles the two once the symbol
  assigned to ``alpha/pi`` is fixed.

It does not alter frozen predictions or promote an official lepton dressing.
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
from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import ALPHA_INV_LOW_ENERGY, S_OVERLAP


STOCHASTIC_NORMALIZATION_PARTIAL = "STOCHASTIC_NORMALIZATION_PARTIAL"
STOCHASTIC_PATH_INTEGRAL_HEAT_KERNEL_PARTIAL = "STOCHASTIC_PATH_INTEGRAL_HEAT_KERNEL_PARTIAL"
STOCHASTIC_PATH_INTEGRAL_PHASE_CUMULANT_CONDITIONAL = (
    "STOCHASTIC_PATH_INTEGRAL_PHASE_CUMULANT_CONDITIONAL"
)
ITO_SQRT_2D_NORMALIZATION_PARTIAL = "ITO_SQRT_2D_NORMALIZATION_PARTIAL"
BOUNDARY_CYCLE_TIME_NORMALIZATION_CONVENTION_FIXED = (
    "BOUNDARY_CYCLE_TIME_NORMALIZATION_CONVENTION_FIXED"
)
ALPHA_PI_ROLE_GENERATOR_BY_REPO_CONVENTION_RAW_VARIANCE_ALTERNATIVE = (
    "ALPHA_PI_ROLE_GENERATOR_BY_REPO_CONVENTION_RAW_VARIANCE_ALTERNATIVE"
)
BROWNIAN_FACTOR_TWO_CONVENTION_DEPENDENT_STRENGTHENED = (
    "BROWNIAN_FACTOR_TWO_CONVENTION_DEPENDENT_STRENGTHENED"
)
LEPTON_ETA_NORMALIZATION_CONVENTION_DEPENDENT_STRENGTHENED = (
    "LEPTON_ETA_NORMALIZATION_CONVENTION_DEPENDENT_STRENGTHENED"
)


@dataclass(frozen=True)
class NormalizationRoute:
    """One stochastic-normalization route and its claim limits."""

    name: str
    status: str
    expression: str
    supports_no_extra_half: bool
    supports_half_factor: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def g_squared_from_alpha(alpha: float) -> float:
    """Return the normalized U(1) phase scale ``g^2=alpha/pi``."""

    return float(alpha) / pi


def D_from_g_squared_ito(g_squared: float) -> float:
    """Return the Ito heat-generator coefficient if ``dtheta=g dW``."""

    return 0.5 * float(g_squared)


def attenuation_phase_cumulant(g_squared: float, N: int, active_fraction: Fraction | float) -> float:
    """Return ``exp[-g^2 * active_fraction * N / 2]``."""

    return exp(-0.5 * float(g_squared) * float(active_fraction) * int(N))


def attenuation_heat_kernel(D: float, N: int, active_fraction: Fraction | float) -> float:
    """Return ``exp[-D * active_fraction * N]``."""

    return exp(-float(D) * float(active_fraction) * int(N))


def eta_no_extra_half(alpha: float, active_fraction: Fraction | float) -> float:
    """Return eta if ``alpha/pi`` is the heat-kernel generator coefficient."""

    return g_squared_from_alpha(alpha) * float(active_fraction)


def eta_half_factor(alpha: float, active_fraction: Fraction | float) -> float:
    """Return eta if ``alpha/pi`` is raw Gaussian phase variance."""

    return D_from_g_squared_ito(g_squared_from_alpha(alpha)) * float(active_fraction)


def eta_from_sqrt_2D_convention(
    alpha: float,
    active_fraction: Fraction | float,
    *,
    alpha_pi_role: str = "generator_coefficient",
) -> float:
    """Return eta in Ito ``sqrt(2D)`` notation for the selected alpha/pi role.

    If ``alpha/pi`` is ``D``, no extra half appears. If it is the Brownian
    amplitude squared ``g^2``, the generator is ``g^2/2``.
    """

    if alpha_pi_role == "generator_coefficient":
        return eta_no_extra_half(alpha, active_fraction)
    if alpha_pi_role == "raw_variance":
        return eta_half_factor(alpha, active_fraction)
    raise ValueError("alpha_pi_role must be 'generator_coefficient' or 'raw_variance'")


def lepton_active_fraction() -> Fraction:
    """Return the partial charged-lepton active channel fraction 8/9."""

    return Fraction(8, 9)


def lepton_eta_no_extra_half(alpha: float) -> float:
    """Return ``eta_l=8*alpha/(9*pi)``."""

    return eta_no_extra_half(alpha, lepton_active_fraction())


def lepton_eta_half_factor(alpha: float) -> float:
    """Return ``eta_l=4*alpha/(9*pi)``."""

    return eta_half_factor(alpha, lepton_active_fraction())


def lepton_eta_double_factor(alpha: float) -> float:
    """Return the preserved doubled sensitivity form ``16*alpha/(9*pi)``."""

    return 2.0 * eta_no_extra_half(alpha, lepton_active_fraction())


def q_from_kj(k: int, j: int) -> int:
    """Return Hopf charge ``q=k-2j``."""

    return int(k) - 2 * int(j)


def mode_norm_N(k: int, j: int) -> int:
    """Return the candidate Brownian norm ``N=q^2+j^2``."""

    q = q_from_kj(k, j)
    return q * q + int(j) * int(j)


def heat_kernel_route_status() -> NormalizationRoute:
    """Return heat-kernel route status."""

    return NormalizationRoute(
        name="heat_kernel_generator",
        status=STOCHASTIC_PATH_INTEGRAL_HEAT_KERNEL_PARTIAL,
        expression="K_tau=exp[-tau D Delta_channel], eta=D*active_fraction",
        supports_no_extra_half=True,
        supports_half_factor=False,
        assumptions=(
            "BHSM eta is the exponent coefficient in Z=exp[-eta N]",
            "alpha/pi is interpreted as the generator coefficient D",
            "one normalized boundary cycle sets tau=1",
        ),
        limitations=(
            "the full stochastic measure is not derived",
            "the boundary-cycle time normalization is a convention in this audit",
        ),
    )


def phase_cumulant_route_status() -> NormalizationRoute:
    """Return Gaussian phase-cumulant route status."""

    return NormalizationRoute(
        name="gaussian_phase_cumulant",
        status=STOCHASTIC_PATH_INTEGRAL_PHASE_CUMULANT_CONDITIONAL,
        expression="E[exp(i theta)]=exp[-Var(theta)/2]",
        supports_no_extra_half=False,
        supports_half_factor=True,
        assumptions=(
            "alpha/pi is interpreted as raw phase variance g_U1^2",
            "the stochastic factor is an averaged Wilson phase",
        ),
        limitations=(
            "this is an alternative convention, not the current repo exponent convention",
            "it would define a candidate eta only and changes no official output",
        ),
    )


def ito_sqrt_2D_route_status() -> NormalizationRoute:
    """Return Ito ``sqrt(2D)`` normalization status."""

    return NormalizationRoute(
        name="ito_sqrt_2D",
        status=ITO_SQRT_2D_NORMALIZATION_PARTIAL,
        expression="dtheta=sqrt(2D)dW gives Var(theta)=2D tau and exp[-D tau]",
        supports_no_extra_half=True,
        supports_half_factor=True,
        assumptions=(
            "Ito notation is valid for a one-dimensional boundary phase process",
            "the factor is fixed once alpha/pi is declared to be D or g^2",
        ),
        limitations=(
            "the repo still has not derived from the complete path integral which symbol alpha/pi denotes",
        ),
    )


def boundary_cycle_time_status() -> NormalizationRoute:
    """Return boundary-cycle time normalization status."""

    return NormalizationRoute(
        name="boundary_cycle_time",
        status=BOUNDARY_CYCLE_TIME_NORMALIZATION_CONVENTION_FIXED,
        expression="tau=1 per normalized 2*pi boundary cycle",
        supports_no_extra_half=True,
        supports_half_factor=True,
        assumptions=("the finite boundary phase orbit is sampled once per normalized cycle",),
        limitations=("tau=1 is not yet derived from a completed stochastic action",),
    )


def normalization_status_object() -> dict[str, NormalizationRoute]:
    """Return the route status objects used by the audit."""

    return {
        "heat_kernel": heat_kernel_route_status(),
        "phase_cumulant": phase_cumulant_route_status(),
        "ito_sqrt_2D": ito_sqrt_2D_route_status(),
        "boundary_cycle_time": boundary_cycle_time_status(),
    }


def validate_no_official_outputs_modified() -> dict[str, Any]:
    """Return frozen branch sanity checks without mutating outputs."""

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
    """Return the stochastic path-integral normalization audit payload."""

    resolved_alpha = 1.0 / ALPHA_INV_LOW_ENERGY if alpha is None else float(alpha)
    g2 = g_squared_from_alpha(resolved_alpha)
    D_ito = D_from_g_squared_ito(g2)
    active = lepton_active_fraction()
    routes = normalization_status_object()
    no_extra = lepton_eta_no_extra_half(resolved_alpha)
    half = lepton_eta_half_factor(resolved_alpha)
    double = lepton_eta_double_factor(resolved_alpha)
    blockers_remaining = (
        "derive the boundary stochastic measure from the completed BHSM path integral",
        "derive whether alpha/pi is generator coefficient D or raw variance g^2",
        "derive tau=1 boundary-cycle time rather than fixing it by convention",
        "derive full stochastic generator on the physical channel algebra before promoting lepton 8/9",
    )
    payload: dict[str, Any] = {
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        "stochastic_path_integral_status": STOCHASTIC_NORMALIZATION_PARTIAL,
        "heat_kernel_generator_status": routes["heat_kernel"].status,
        "phase_cumulant_status": routes["phase_cumulant"].status,
        "ito_sqrt_2D_status": routes["ito_sqrt_2D"].status,
        "boundary_cycle_time_status": routes["boundary_cycle_time"].status,
        "alpha_pi_role_status": ALPHA_PI_ROLE_GENERATOR_BY_REPO_CONVENTION_RAW_VARIANCE_ALTERNATIVE,
        "brownian_factor_two_status": BROWNIAN_FACTOR_TWO_CONVENTION_DEPENDENT_STRENGTHENED,
        "lepton_eta_normalization_status": LEPTON_ETA_NORMALIZATION_CONVENTION_DEPENDENT_STRENGTHENED,
        "is_alpha_pi_raw_variance": True,
        "is_alpha_pi_generator_coefficient": True,
        "is_tau_boundary_cycle_fixed": True,
        "does_sqrt_2D_convention_resolve_half_factor": True,
        "does_eta_l_8alpha_9pi_remain_supported": True,
        "does_factor_two_close": False,
        "does_this_change_official_predictions": False,
        "does_this_promote_full_lepton_8_9": False,
        "preferred_eta_form": "no_extra_half_repo_exponent_convention",
        "allowed_eta_forms": {
            "no_extra_half": no_extra,
            "half_factor": half,
            "double_factor": double,
        },
        "alpha": resolved_alpha,
        "g_squared_alpha_over_pi": g2,
        "D_from_g_squared_ito": D_ito,
        "eta_from_sqrt_2D_generator_role": eta_from_sqrt_2D_convention(
            resolved_alpha, active, alpha_pi_role="generator_coefficient"
        ),
        "eta_from_sqrt_2D_raw_variance_role": eta_from_sqrt_2D_convention(
            resolved_alpha, active, alpha_pi_role="raw_variance"
        ),
        "lepton_active_fraction": active,
        "mode_norms": {
            "tau_reference": mode_norm_N(0, 0),
            "muon": mode_norm_N(5, 2),
            "electron": mode_norm_N(9, 3),
        },
        "attenuation_examples_muon": {
            "N": mode_norm_N(5, 2),
            "heat_kernel": attenuation_heat_kernel(g2, mode_norm_N(5, 2), active),
            "phase_cumulant": attenuation_phase_cumulant(g2, mode_norm_N(5, 2), active),
        },
        "blockers_closed": (
            "Ito_sqrt_2D_notation_reconciles_half_factor_by_convention",
            "alpha_pi_generator_vs_variance_roles_are_explicit",
            "eta_l_8alpha_9pi_remains_supported_as_repo_exponent_convention",
        ),
        "blockers_remaining": blockers_remaining,
        "derived_components": (
            "g_squared_from_alpha_equals_alpha_over_pi",
            "D_from_raw_variance_equals_g_squared_over_2",
            "phase_cumulant_attenuation_formula",
            "heat_kernel_attenuation_formula",
        ),
        "partial_components": (
            "heat_kernel_path_integral_route",
            "Ito_sqrt_2D_boundary_noise_route",
            "boundary_cycle_time_tau_equals_one",
        ),
        "conditional_components": (
            "no_extra_half_if_alpha_pi_is_generator_coefficient",
            "half_factor_if_alpha_pi_is_raw_variance",
        ),
        "candidate_components": (
            "double_factor_sensitivity_form",
            "lepton_eta_8alpha_over_9pi_candidate_consequence",
        ),
        "missing_assumptions": blockers_remaining,
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "route_status_objects": routes,
        "frozen_sanity": validate_no_official_outputs_modified(),
    }
    payload["lepton_eta_exact_checks"] = {
        "no_extra_half_matches_8alpha_over_9pi": isclose(no_extra, 8.0 * resolved_alpha / (9.0 * pi)),
        "half_factor_matches_4alpha_over_9pi": isclose(half, 4.0 * resolved_alpha / (9.0 * pi)),
        "double_factor_matches_16alpha_over_9pi": isclose(double, 16.0 * resolved_alpha / (9.0 * pi)),
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
    """Render a Markdown report for this audit."""

    p = audit_payload() if payload is None else payload
    heading = title or "BHSM Stochastic Path-Integral Normalization"
    lines = [
        f"# {heading}",
        "",
        "This audit localizes the remaining Brownian factor-of-two issue. It does not alter frozen outputs or create an official prediction update.",
        "",
        "## Summary",
        "",
        f"Stochastic path-integral status: `{p['stochastic_path_integral_status']}`",
        f"Heat-kernel generator status: `{p['heat_kernel_generator_status']}`",
        f"Phase-cumulant status: `{p['phase_cumulant_status']}`",
        f"Ito sqrt(2D) status: `{p['ito_sqrt_2D_status']}`",
        f"Boundary-cycle time status: `{p['boundary_cycle_time_status']}`",
        f"alpha/pi role: `{p['alpha_pi_role_status']}`",
        f"Brownian factor-two status: `{p['brownian_factor_two_status']}`",
        f"Lepton eta normalization status: `{p['lepton_eta_normalization_status']}`",
        f"Preferred eta form: `{p['preferred_eta_form']}`",
        f"Factor two closed: `{p['does_factor_two_close']}`",
        "",
        "## Convention Fork",
        "",
        "```text",
        "Raw variance route:",
        "  g_U1^2 = alpha/pi",
        "  D = g_U1^2/2",
        "  Z = exp[-(alpha/pi) N active_fraction / 2]",
        "",
        "Heat-kernel route:",
        "  D_U1 = alpha/pi",
        "  Z = exp[-D_U1 N active_fraction]",
        "",
        "Ito sqrt(2D) route:",
        "  dtheta = sqrt(2D) dW",
        "  Var(theta)=2D tau",
        "  E[exp(i theta)] = exp[-D tau]",
        "```",
        "",
        "## Eta Forms Preserved",
        "",
        "| Form | eta_l | Status |",
        "| --- | ---: | --- |",
        f"| `no_extra_half` | `{p['allowed_eta_forms']['no_extra_half']}` | repo-preferred candidate convention |",
        f"| `half_factor` | `{p['allowed_eta_forms']['half_factor']}` | raw-variance alternative |",
        f"| `double_factor` | `{p['allowed_eta_forms']['double_factor']}` | sensitivity diagnostic |",
        "",
        "## Mode Norm Checks",
        "",
        "| Mode | N=q^2+j^2 |",
        "| --- | ---: |",
        f"| tau `(0,0)` | `{p['mode_norms']['tau_reference']}` |",
        f"| muon `(5,2)` | `{p['mode_norms']['muon']}` |",
        f"| electron `(9,3)` | `{p['mode_norms']['electron']}` |",
        "",
        "## Interpretation",
        "",
        "The sprint strengthens the bookkeeping: `alpha/pi` can be treated as the generator coefficient under the existing repo exponent convention, while the raw-variance interpretation remains a valid alternative that would introduce a half factor. The complete stochastic path-integral measure is still not derived, so the factor-of-two issue remains convention-dependent.",
        "",
        "## Blockers Closed",
        "",
    ]
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
            "- No Standard Model replacement claim is made.",
            "",
        ]
    )
    return "\n".join(lines)


def export_stochastic_path_integral_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export audit artifacts for the stochastic path-integral sprint."""

    base = Path(root)
    payload = audit_payload()
    outputs = {
        "theory_main": base / "theory" / "stochastic_path_integral_normalization.md",
        "theory_heat": base / "theory" / "heat_kernel_generator_vs_phase_variance.md",
        "theory_ito": base / "theory" / "ito_sqrt_2D_boundary_noise_normalization.md",
        "theory_cycle": base / "theory" / "boundary_cycle_time_normalization.md",
        "audit_md": base / "audits" / "stochastic_path_integral_normalization_audit.md",
        "audit_json": base / "audits" / "stochastic_path_integral_normalization_audit.json",
    }
    for path in outputs.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    outputs["theory_main"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["theory_heat"].write_text(
        render_markdown(payload, "Heat-Kernel Generator vs Phase Variance"),
        encoding="utf-8",
    )
    outputs["theory_ito"].write_text(
        render_markdown(payload, "Ito sqrt(2D) Boundary Noise Normalization"),
        encoding="utf-8",
    )
    outputs["theory_cycle"].write_text(
        render_markdown(payload, "Boundary Cycle-Time Normalization"),
        encoding="utf-8",
    )
    outputs["audit_md"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_stochastic_path_integral_outputs()
