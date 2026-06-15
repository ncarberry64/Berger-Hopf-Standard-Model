"""Alpha-over-pi stochastic strength audit for BHSM.

This module checks the proposed rationalized-U(1) normalization

    alpha = e^2/(4*pi),  D_U1 = (e/(2*pi))^2 = alpha/pi

and propagates it to the already partial charged-lepton channel factor 8/9.
It does not alter frozen predictions or promote any official output.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from math import exp, isclose, pi, sqrt
from pathlib import Path
from typing import Any

from bhsm_config import canonical_geometry_config
from bhsm_completion_manual_theory_delta import frozen_sanity_payload
from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import ALPHA_INV_LOW_ENERGY, S_OVERLAP


ALPHA_OVER_PI_STOCHASTIC_STRENGTH_DERIVED = "ALPHA_OVER_PI_STOCHASTIC_STRENGTH_DERIVED"
ALPHA_OVER_PI_STOCHASTIC_STRENGTH_PARTIAL = "ALPHA_OVER_PI_STOCHASTIC_STRENGTH_PARTIAL"
ALPHA_OVER_PI_STOCHASTIC_STRENGTH_CONDITIONAL = (
    "ALPHA_OVER_PI_STOCHASTIC_STRENGTH_CONDITIONAL"
)
ALPHA_OVER_PI_STOCHASTIC_STRENGTH_STRUCTURAL_CANDIDATE = (
    "ALPHA_OVER_PI_STOCHASTIC_STRENGTH_STRUCTURAL_CANDIDATE"
)
ALPHA_OVER_PI_STOCHASTIC_STRENGTH_OPEN = "ALPHA_OVER_PI_STOCHASTIC_STRENGTH_OPEN"
ALPHA_OVER_PI_STOCHASTIC_STRENGTH_REJECTED = "ALPHA_OVER_PI_STOCHASTIC_STRENGTH_REJECTED"

U1_PHASE_NORMALIZATION_PARTIAL = "U1_PHASE_NORMALIZATION_PARTIAL"
HOPF_CONTACT_NORMALIZATION_COMPATIBLE = "HOPF_CONTACT_NORMALIZATION_COMPATIBLE"
BROWNIAN_FACTOR_TWO_HAZARD_RECORDED = "BROWNIAN_FACTOR_TWO_HAZARD_RECORDED"
LEPTON_8_9_CHANNEL_RULE_PARTIAL_DERIVATION_STRENGTHENED = (
    "LEPTON_8_9_CHANNEL_RULE_PARTIAL_DERIVATION_STRENGTHENED"
)


@dataclass(frozen=True)
class AlphaPiStatus:
    """Status of one alpha/pi normalization route."""

    name: str
    status: str
    follows: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def e_squared_from_alpha(alpha: float) -> float:
    """Return e^2=4*pi*alpha in rationalized natural units."""

    return 4.0 * pi * float(alpha)


def normalized_u1_phase_coupling(e: float) -> float:
    """Return normalized boundary phase coupling e/(2*pi)."""

    return float(e) / (2.0 * pi)


def stochastic_strength_from_phase_coupling(e: float) -> float:
    """Return D_U1=(e/(2*pi))^2=e^2/(4*pi^2)."""

    coupling = normalized_u1_phase_coupling(e)
    return coupling * coupling


def stochastic_strength_from_alpha(alpha: float) -> float:
    """Return D_U1=alpha/pi."""

    return float(alpha) / pi


def lepton_active_fraction() -> Fraction:
    """Return exact charged-lepton active fraction 8/9."""

    return Fraction(8, 9)


def lepton_eta_from_alpha(alpha: float) -> float:
    """Return eta_l=8*alpha/(9*pi)."""

    return stochastic_strength_from_alpha(alpha) * float(lepton_active_fraction())


def q_from_kj(k: int, j: int) -> int:
    """Return Hopf charge q=k-2j."""

    return int(k) - 2 * int(j)


def mode_norm_N(k: int, j: int) -> int:
    """Return N=q^2+j^2."""

    q = q_from_kj(k, j)
    return q * q + int(j) * int(j)


def lepton_dressing_factor(alpha: float, k: int, j: int) -> float:
    """Return non-official candidate lepton factor exp[-eta_l N(k,j)]."""

    return exp(-lepton_eta_from_alpha(alpha) * mode_norm_N(k, j))


def factor_of_two_hazard_status(cumulant_convention_fixed: bool = False) -> AlphaPiStatus:
    """Return status for Brownian/cumulant factor-of-two normalization."""

    if cumulant_convention_fixed:
        return AlphaPiStatus(
            name="brownian_factor_two_hazard",
            status="BROWNIAN_FACTOR_TWO_HAZARD_RESOLVED_BY_ASSUMPTION",
            follows=True,
            assumptions=("the Brownian generator convention has no extra 1/2 cumulant factor",),
            limitations=("this convention is not derived from the completed stochastic path integral",),
        )
    return AlphaPiStatus(
        name="brownian_factor_two_hazard",
        status=BROWNIAN_FACTOR_TWO_HAZARD_RECORDED,
        follows=False,
        assumptions=("diffusion strength is quadratic in normalized U(1) phase coupling",),
        limitations=(
            "a full Brownian/cumulant normalization could introduce a factor of 1/2 or 2",
            "the completed stochastic path-integral normalization is not implemented",
        ),
    )


def alpha_over_pi_status_object() -> AlphaPiStatus:
    """Return conservative alpha/pi status."""

    return AlphaPiStatus(
        name="alpha_over_pi_stochastic_strength",
        status=ALPHA_OVER_PI_STOCHASTIC_STRENGTH_PARTIAL,
        follows=True,
        assumptions=(
            "rationalized natural units use alpha=e^2/(4*pi)",
            "the boundary U(1) phase cycle is normalized by 2*pi",
            "diffusion strength is quadratic in e/(2*pi)",
        ),
        limitations=(
            "the Brownian cumulant factor convention remains a recorded hazard",
            "the normalized U(1) phase coupling is compatible with A_q=sigma_3/(2*pi) but not a full stochastic derivation",
        ),
    )


def u1_phase_normalization_status_object() -> AlphaPiStatus:
    """Return U(1) phase normalization status."""

    return AlphaPiStatus(
        name="u1_phase_normalization",
        status=U1_PHASE_NORMALIZATION_PARTIAL,
        follows=True,
        assumptions=("boundary phase cycle has circumference 2*pi",),
        limitations=("full boundary U(1) stochastic measure is not derived",),
    )


def hopf_contact_normalization_status_object() -> AlphaPiStatus:
    """Return Hopf/contact normalization compatibility status."""

    return AlphaPiStatus(
        name="hopf_contact_normalization",
        status=HOPF_CONTACT_NORMALIZATION_COMPATIBLE,
        follows=True,
        assumptions=("A_q uses the normalized Hopf/contact form sigma_3/(2*pi)",),
        limitations=("compatibility is not the same as a full stochastic path-integral proof",),
    )


def lepton_eta_status_object() -> AlphaPiStatus:
    """Return lepton eta consequence status."""

    return AlphaPiStatus(
        name="lepton_eta_8alpha_over_9pi",
        status=LEPTON_8_9_CHANNEL_RULE_PARTIAL_DERIVATION_STRENGTHENED,
        follows=True,
        assumptions=("D_U1=alpha/pi", "charged-lepton active fraction is 8/9"),
        limitations=(
            "full lepton 8/9 derivation still depends on primitive monodromy and stochastic generator completion",
            "no frozen lepton output is changed",
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
    """Return alpha-over-pi stochastic strength audit payload."""

    resolved_alpha = 1.0 / ALPHA_INV_LOW_ENERGY if alpha is None else float(alpha)
    e_squared = e_squared_from_alpha(resolved_alpha)
    e = sqrt(e_squared)
    direct_strength = stochastic_strength_from_phase_coupling(e)
    alpha_strength = stochastic_strength_from_alpha(resolved_alpha)
    hazard = factor_of_two_hazard_status(False)
    blockers_remaining = (
        "derive Brownian/cumulant normalization from a completed stochastic path integral",
        "derive the boundary U(1) fluctuation measure rather than only phase-cycle normalization",
        "derive primitive cyclic monodromy and full stochastic generator before promoting full lepton 8/9",
    )
    payload: dict[str, Any] = {
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        "alpha_over_pi_strength_status": alpha_over_pi_status_object().status,
        "u1_phase_normalization_status": u1_phase_normalization_status_object().status,
        "hopf_contact_normalization_status": hopf_contact_normalization_status_object().status,
        "brownian_factor_two_hazard_status": hazard.status,
        "lepton_eta_consequence_status": lepton_eta_status_object().status,
        "does_alpha_over_pi_follow": isclose(direct_strength, alpha_strength, rel_tol=1e-15),
        "does_eta_l_8alpha_9pi_follow": isclose(
            lepton_eta_from_alpha(resolved_alpha),
            8.0 * resolved_alpha / (9.0 * pi),
            rel_tol=1e-15,
        ),
        "does_this_promote_full_lepton_8_9": False,
        "does_this_change_official_predictions": False,
        "alpha": resolved_alpha,
        "e_squared": e_squared,
        "normalized_u1_phase_coupling": normalized_u1_phase_coupling(e),
        "stochastic_strength_from_phase_coupling": direct_strength,
        "stochastic_strength_from_alpha": alpha_strength,
        "lepton_active_fraction": lepton_active_fraction(),
        "lepton_eta": lepton_eta_from_alpha(resolved_alpha),
        "mode_norms": {
            "tau_reference": mode_norm_N(0, 0),
            "muon": mode_norm_N(5, 2),
            "electron": mode_norm_N(9, 3),
        },
        "sample_lepton_dressing_factors": {
            "tau_reference": lepton_dressing_factor(resolved_alpha, 0, 0),
            "muon": lepton_dressing_factor(resolved_alpha, 5, 2),
            "electron": lepton_dressing_factor(resolved_alpha, 9, 3),
        },
        "blockers_closed": (
            "exact_rationalized_U1_algebra_D_U1_equals_alpha_over_pi",
            "Hopf_contact_2pi_normalization_compatibility",
            "eta_l_equals_D_U1_times_8_over_9",
        ),
        "blockers_remaining": blockers_remaining,
        "derived_components": (
            "algebraic_identity_e_squared_over_4pi_squared_equals_alpha_over_pi",
            "eta_l_algebra_given_D_U1_and_active_fraction",
        ),
        "partial_components": (
            "U1_phase_cycle_normalization",
            "Hopf_contact_boundary_normalization_compatibility",
            "alpha_over_pi_stochastic_strength",
        ),
        "conditional_components": (
            "charged_lepton_active_fraction_8_over_9",
            "Brownian_generator_channel_rule",
        ),
        "candidate_components": ("Brownian_cumulant_normalization_without_extra_factor",),
        "missing_assumptions": blockers_remaining,
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "status_objects": {
            "alpha_over_pi": alpha_over_pi_status_object(),
            "u1_phase": u1_phase_normalization_status_object(),
            "hopf_contact": hopf_contact_normalization_status_object(),
            "factor_two_hazard": hazard,
            "lepton_eta": lepton_eta_status_object(),
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


def render_markdown(payload: dict[str, Any] | None = None) -> str:
    """Render alpha-over-pi audit Markdown."""

    p = audit_payload() if payload is None else payload
    lines = [
        "# BHSM Alpha-over-Pi Stochastic Strength Derivation",
        "",
        "This sprint audits the proposed rationalized U(1) normalization for the base stochastic strength.",
        "It verifies the algebra `D_U1=(e/(2*pi))^2=alpha/pi` and records the Brownian factor-of-two hazard.",
        "",
        "## Summary",
        "",
        f"alpha/pi strength status: `{p['alpha_over_pi_strength_status']}`",
        f"U(1) phase normalization status: `{p['u1_phase_normalization_status']}`",
        f"Hopf/contact normalization status: `{p['hopf_contact_normalization_status']}`",
        f"Brownian factor-two hazard: `{p['brownian_factor_two_hazard_status']}`",
        f"Lepton eta consequence: `{p['lepton_eta_consequence_status']}`",
        f"alpha/pi follows: `{p['does_alpha_over_pi_follow']}`",
        f"eta_l=8alpha/(9pi) follows: `{p['does_eta_l_8alpha_9pi_follow']}`",
        f"Promotes full lepton 8/9: `{p['does_this_promote_full_lepton_8_9']}`",
        f"Official predictions changed: `{p['does_this_change_official_predictions']}`",
        "",
        "## Algebra",
        "",
        "```text",
        "alpha = e^2/(4*pi)",
        "g_U1 = e/(2*pi)",
        "D_U1 = g_U1^2 = e^2/(4*pi^2)",
        "e^2 = 4*pi*alpha",
        "D_U1 = alpha/pi",
        "eta_l = D_U1 * 8/9 = 8*alpha/(9*pi)",
        "```",
        "",
        "## Mode Norms",
        "",
        "| Mode | N=q^2+j^2 | Dressing factor |",
        "| --- | ---: | ---: |",
    ]
    labels = {
        "tau_reference": (0, 0),
        "muon": (5, 2),
        "electron": (9, 3),
    }
    for label, mode in labels.items():
        lines.append(
            f"| `{label} {mode}` | `{p['mode_norms'][label]}` | `{p['sample_lepton_dressing_factors'][label]}` |"
        )
    lines.extend(
        [
            "",
            "## Factor-of-Two Hazard",
            "",
            "A completed Brownian/cumulant normalization could introduce an extra conventional factor. This sprint records that hazard rather than hiding it.",
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
            "- No Standard Model replacement claim is made.",
            "",
        ]
    )
    return "\n".join(lines)


def export_alpha_over_pi_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export alpha-over-pi audit artifacts."""

    base = Path(root)
    payload = audit_payload()
    outputs = {
        "theory": base / "theory" / "alpha_over_pi_stochastic_strength_derivation.md",
        "audit_md": base / "audits" / "alpha_over_pi_stochastic_strength_audit.md",
        "audit_json": base / "audits" / "alpha_over_pi_stochastic_strength_audit.json",
    }
    for path in outputs.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    outputs["theory"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["audit_md"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_alpha_over_pi_outputs()
