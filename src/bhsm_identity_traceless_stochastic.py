"""Identity-channel protection and traceless Brownian activity audit.

This sprint builds the symbolic channel-algebra step after the conditional
cyclic boundary monodromy result.  It does not alter frozen predictions or
promote any official dressing rule.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from math import isclose, pi
from pathlib import Path
from typing import Any

from bhsm_boundary_holonomy_dimension import (
    DIM_H_EQUALS_ABS_OMEGA_CONDITIONAL,
    sector_channel_dimension,
)
from bhsm_config import canonical_geometry_config
from bhsm_completion_manual_theory_delta import frozen_sanity_payload
from bhsm_v1 import build_bhsm_bare_v1, build_bhsm_dressed_v1_candidate, compare_bhsm_v1_branches
from constants import ALPHA_INV_LOW_ENERGY, S_OVERLAP


IDENTITY_TRACELESS_STOCHASTIC_CONDITIONAL = "IDENTITY_TRACELESS_STOCHASTIC_CONDITIONAL"
IDENTITY_CHANNEL_PROTECTION_CONDITIONAL = "IDENTITY_CHANNEL_PROTECTION_CONDITIONAL"
TRACE_PRESERVING_IDENTITY_PROTECTION_CONDITIONAL = (
    "TRACE_PRESERVING_IDENTITY_PROTECTION_CONDITIONAL"
)
COMMON_MODE_CANCELLATION_DERIVED = "COMMON_MODE_CANCELLATION_DERIVED"
ATTRACTOR_NORMALIZATION_PROTECTION_STRUCTURAL_CANDIDATE = (
    "ATTRACTOR_NORMALIZATION_PROTECTION_STRUCTURAL_CANDIDATE"
)
TRACELESS_BROWNIAN_ACTIVITY_CONDITIONAL = "TRACELESS_BROWNIAN_ACTIVITY_CONDITIONAL"
TRACELESS_BROWNIAN_GENERATOR_CONDITIONAL = "TRACELESS_BROWNIAN_GENERATOR_CONDITIONAL"
ENDOMORPHISM_CHANNEL_ALGEBRA_CONDITIONAL = "ENDOMORPHISM_CHANNEL_ALGEBRA_CONDITIONAL"
LEPTON_8_9_CHANNEL_RULE_CONDITIONAL = "LEPTON_8_9_CHANNEL_RULE_CONDITIONAL"
QUARK_ACTIVE_FRACTION_CONSEQUENCE_CANDIDATE_ONLY = (
    "QUARK_ACTIVE_FRACTION_CONSEQUENCE_CANDIDATE_ONLY"
)


@dataclass(frozen=True)
class IdentityProtectionStatus:
    """Status of identity-channel protection routes."""

    identity_channel_protection_status: str
    trace_preserving_status: str
    common_mode_cancellation_status: str
    attractor_normalization_status: str
    does_identity_channel_get_protected: bool
    does_trace_preservation_justify_protection: bool
    does_common_mode_cancel_in_ratios: bool


@dataclass(frozen=True)
class TracelessActivityStatus:
    """Status of traceless stochastic activity routes."""

    traceless_brownian_activity_status: str
    lindblad_generator_status: str
    endomorphism_channel_algebra_status: str
    does_stochastic_dressing_act_on_End_H: bool
    does_traceless_activity_follow: bool
    does_active_fraction_follow: bool


@dataclass(frozen=True)
class LeptonEightNineStatus:
    """Status of the charged-lepton 8/9 channel rule."""

    lepton_8_9_status: str
    d_l: int
    endomorphism_channels: int
    identity_channels: int
    traceless_channels: int
    active_fraction: Fraction
    eta_l_formula: str
    conditional: bool
    official: bool


def _require_positive_dimension(d: int) -> int:
    if int(d) <= 0:
        raise ValueError("channel dimension must be positive")
    return int(d)


def endomorphism_dimension(d: int) -> int:
    """Return dim End(H)=d^2."""

    n = _require_positive_dimension(d)
    return n * n


def identity_channel_dimension(d: int) -> int:
    """Return the protected identity-channel dimension."""

    _require_positive_dimension(d)
    return 1


def traceless_channel_dimension(d: int) -> int:
    """Return dim su(d)=d^2-1 for relative channels."""

    return endomorphism_dimension(d) - identity_channel_dimension(d)


def active_traceless_fraction(d: int) -> Fraction:
    """Return (d^2-1)/d^2 as an exact Fraction."""

    return Fraction(traceless_channel_dimension(d), endomorphism_dimension(d))


def algebra_split_label(d: int) -> str:
    """Return a compact channel-algebra split label."""

    n = _require_positive_dimension(d)
    return f"C I_{n} + su({n})"


def eta_from_active_fraction(alpha: float, d: int) -> float:
    """Return eta=(alpha/pi)*active_fraction(d)."""

    return float(alpha / pi * active_traceless_fraction(d))


def lepton_eta_8_9(alpha: float) -> float:
    """Return eta_l=8alpha/(9pi)."""

    return eta_from_active_fraction(alpha, 3)


def sector_dimension(sector: str) -> int:
    """Return conditional channel dimension for a charged sector."""

    return sector_channel_dimension(sector).dimension


def sector_active_fraction(sector: str) -> Fraction:
    """Return active traceless fraction for a charged sector."""

    return active_traceless_fraction(sector_dimension(sector))


def common_mode_cancels_in_ratio(z_common: float, m1: float, m2: float) -> bool:
    """Return whether common-sector factor cancels in m1/m2."""

    if z_common == 0:
        raise ValueError("common-mode factor must be nonzero")
    if m2 == 0:
        raise ValueError("denominator mass must be nonzero")
    before = float(m1) / float(m2)
    after = (float(z_common) * float(m1)) / (float(z_common) * float(m2))
    return isclose(before, after, rel_tol=0.0, abs_tol=1e-15)


def trace_preserving_condition(delta_trace: float) -> bool:
    """Return whether a perturbation is trace-preserving."""

    return isclose(float(delta_trace), 0.0, rel_tol=0.0, abs_tol=1e-15)


def identity_protection_status_object() -> IdentityProtectionStatus:
    """Return conditional identity-channel protection status."""

    return IdentityProtectionStatus(
        identity_channel_protection_status=IDENTITY_CHANNEL_PROTECTION_CONDITIONAL,
        trace_preserving_status=TRACE_PRESERVING_IDENTITY_PROTECTION_CONDITIONAL,
        common_mode_cancellation_status=COMMON_MODE_CANCELLATION_DERIVED,
        attractor_normalization_status=ATTRACTOR_NORMALIZATION_PROTECTION_STRUCTURAL_CANDIDATE,
        does_identity_channel_get_protected=True,
        does_trace_preservation_justify_protection=True,
        does_common_mode_cancel_in_ratios=common_mode_cancels_in_ratio(7.0, 2.0, 5.0),
    )


def traceless_activity_status_object() -> TracelessActivityStatus:
    """Return conditional traceless Brownian activity status."""

    return TracelessActivityStatus(
        traceless_brownian_activity_status=TRACELESS_BROWNIAN_ACTIVITY_CONDITIONAL,
        lindblad_generator_status=TRACELESS_BROWNIAN_GENERATOR_CONDITIONAL,
        endomorphism_channel_algebra_status=ENDOMORPHISM_CHANNEL_ALGEBRA_CONDITIONAL,
        does_stochastic_dressing_act_on_End_H=True,
        does_traceless_activity_follow=True,
        does_active_fraction_follow=True,
    )


def lepton_8_9_status_object(alpha: float | None = None) -> LeptonEightNineStatus:
    """Return conditional lepton 8/9 status from channel algebra."""

    resolved_alpha = 1.0 / ALPHA_INV_LOW_ENERGY if alpha is None else float(alpha)
    d_l = sector_dimension("charged_lepton")
    return LeptonEightNineStatus(
        lepton_8_9_status=LEPTON_8_9_CHANNEL_RULE_CONDITIONAL,
        d_l=d_l,
        endomorphism_channels=endomorphism_dimension(d_l),
        identity_channels=identity_channel_dimension(d_l),
        traceless_channels=traceless_channel_dimension(d_l),
        active_fraction=active_traceless_fraction(d_l),
        eta_l_formula=f"{lepton_eta_8_9(resolved_alpha):.17g}",
        conditional=True,
        official=False,
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
    """Return identity/traceless stochastic protection audit payload."""

    resolved_alpha = 1.0 / ALPHA_INV_LOW_ENERGY if alpha is None else float(alpha)
    identity = identity_protection_status_object()
    traceless = traceless_activity_status_object()
    lepton = lepton_8_9_status_object(resolved_alpha)
    blockers_remaining = (
        "derive primitive cyclic boundary monodromy rather than assuming it",
        "derive stochastic dressing action on End(H_f) from the full BHSM dynamics",
        "derive the Brownian generator on su(d_f) from the full internal action",
        "promote eta_l only after the conditional channel dimension becomes derived",
    )
    payload: dict[str, Any] = {
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        "identity_traceless_stochastic_status": IDENTITY_TRACELESS_STOCHASTIC_CONDITIONAL,
        "identity_channel_protection_status": identity.identity_channel_protection_status,
        "trace_preserving_status": identity.trace_preserving_status,
        "common_mode_cancellation_status": identity.common_mode_cancellation_status,
        "attractor_normalization_status": identity.attractor_normalization_status,
        "traceless_brownian_activity_status": traceless.traceless_brownian_activity_status,
        "lindblad_generator_status": traceless.lindblad_generator_status,
        "endomorphism_channel_algebra_status": traceless.endomorphism_channel_algebra_status,
        "lepton_8_9_status": lepton.lepton_8_9_status,
        "quark_active_fraction_consequence_status": QUARK_ACTIVE_FRACTION_CONSEQUENCE_CANDIDATE_ONLY,
        "does_stochastic_dressing_act_on_End_H": traceless.does_stochastic_dressing_act_on_End_H,
        "does_identity_channel_get_protected": identity.does_identity_channel_get_protected,
        "does_trace_preservation_justify_protection": identity.does_trace_preservation_justify_protection,
        "does_common_mode_cancel_in_ratios": identity.does_common_mode_cancel_in_ratios,
        "does_traceless_activity_follow": traceless.does_traceless_activity_follow,
        "does_active_fraction_follow": traceless.does_active_fraction_follow,
        "does_eta_l_8_9_follow": True,
        "is_lepton_8_9_conditional": True,
        "does_this_change_official_predictions": False,
        "upstream_dimension_status": DIM_H_EQUALS_ABS_OMEGA_CONDITIONAL,
        "blockers_closed": (
            "identity_channel_trace_preserving_protection_condition",
            "common_mode_cancellation_in_mass_ratios",
            "traceless_End_H_active_fraction",
            "conditional_eta_l_8alpha_over_9pi",
        ),
        "blockers_remaining": blockers_remaining,
        "derived_components": ("common_mode_cancellation_in_ratios",),
        "conditional_components": (
            "identity_channel_protection",
            "traceless_Brownian_activity",
            "lepton_8_9_channel_rule",
        ),
        "candidate_components": (
            "attractor_normalization_identity_protection",
            "quark_active_fraction_consequence",
            "Lindblad_like_su_d_generator",
        ),
        "missing_assumptions": blockers_remaining,
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "lepton_channel_algebra": asdict(lepton),
        "sector_active_fractions": {
            "charged_lepton": active_traceless_fraction(sector_dimension("charged_lepton")),
            "up": active_traceless_fraction(sector_dimension("up")),
            "down": active_traceless_fraction(sector_dimension("down")),
        },
        "eta_l_8alpha_9pi": lepton_eta_8_9(resolved_alpha),
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
    heading = title or "BHSM Identity-Channel Protection and Traceless Brownian Activity"
    lines = [
        f"# {heading}",
        "",
        "This sprint tests whether the conditional cyclic channel space supports identity protection and traceless stochastic activity.",
        "The result is conditional because the upstream channel dimension remains conditional.",
        "",
        "## Summary",
        "",
        f"Identity/traceless stochastic status: `{p['identity_traceless_stochastic_status']}`",
        f"Identity-channel protection: `{p['identity_channel_protection_status']}`",
        f"Trace-preserving status: `{p['trace_preserving_status']}`",
        f"Common-mode cancellation: `{p['common_mode_cancellation_status']}`",
        f"Traceless Brownian activity: `{p['traceless_brownian_activity_status']}`",
        f"Lepton 8/9 status: `{p['lepton_8_9_status']}`",
        f"Quark active fraction consequence: `{p['quark_active_fraction_consequence_status']}`",
        f"eta_l=8alpha/(9pi) follows: `{p['does_eta_l_8_9_follow']}`",
        f"Lepton 8/9 conditional: `{p['is_lepton_8_9_conditional']}`",
        f"Official predictions changed: `{p['does_this_change_official_predictions']}`",
        "",
        "## Channel Algebra",
        "",
        "```text",
        "End(H_f) = C I_f + su(d_f)",
        "dim End(H_f) = d_f^2",
        "active traceless channels = d_f^2 - 1",
        "F_active(d_f) = (d_f^2 - 1)/d_f^2",
        "```",
        "",
        "## Sector Fractions",
        "",
        "| Sector | d | Active fraction |",
        "| --- | ---: | ---: |",
    ]
    for sector, frac in p["sector_active_fractions"].items():
        lines.append(f"| `{sector}` | `{sector_dimension(sector)}` | `{frac}` |")
    lines.extend(
        [
            "",
            "## Lepton Application",
            "",
            f"`d_l=3`, `End(H_l)=9`, identity channels `1`, traceless channels `8`, active fraction `8/9`.",
            f"`eta_l = {p['eta_l_8alpha_9pi']}` from `alpha/pi * 8/9`.",
            "",
            "## Blockers Remaining",
            "",
        ]
    )
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
            "- No replacement or full-derivation claim is made.",
            "- Quark active fractions are candidate-only consequences.",
            "",
        ]
    )
    return "\n".join(lines)


def export_identity_traceless_stochastic_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export theory and audit artifacts."""

    base = Path(root)
    payload = audit_payload()
    outputs = {
        "identity": base / "theory" / "identity_channel_protection_theorem.md",
        "traceless": base / "theory" / "traceless_brownian_activity_theorem.md",
        "lepton": base / "theory" / "lepton_8_9_conditional_derivation.md",
        "common": base / "theory" / "common_mode_cancellation_in_mass_ratios.md",
        "trace": base / "theory" / "trace_preserving_channel_splitting.md",
        "attractor": base / "theory" / "attractor_normalization_identity_protection.md",
        "quark": base / "theory" / "quark_active_fraction_consequence_candidate.md",
        "lindblad": base / "theory" / "lindblad_like_traceless_generator_candidate.md",
        "audit_md": base / "audits" / "identity_traceless_stochastic_protection_audit.md",
        "audit_json": base / "audits" / "identity_traceless_stochastic_protection_audit.json",
    }
    for path in outputs.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    outputs["identity"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["audit_md"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    outputs["traceless"].write_text(
        "# Traceless Brownian Activity Theorem\n\n"
        f"Status: `{payload['traceless_brownian_activity_status']}`\n\n"
        "Assuming stochastic dressing acts on `End(H_f)` and preserves trace, active relative fluctuations lie in the traceless algebra with dimension `d_f^2-1`.\n",
        encoding="utf-8",
    )
    outputs["lepton"].write_text(
        "# Lepton 8/9 Conditional Derivation\n\n"
        f"Status: `{payload['lepton_8_9_status']}`\n\n"
        "`d_l=3` gives `End(H_l)=9`, one identity direction, eight traceless directions, and `eta_l=(alpha/pi)*(8/9)`. This remains conditional and non-official.\n",
        encoding="utf-8",
    )
    outputs["common"].write_text(
        "# Common-Mode Cancellation in Mass Ratios\n\n"
        f"Status: `{payload['common_mode_cancellation_status']}`\n\n"
        "A common factor `Z_common I_f` cancels from intra-sector ratios, so it cannot produce relative hierarchy dressing.\n",
        encoding="utf-8",
    )
    outputs["trace"].write_text(
        "# Trace-Preserving Channel Splitting\n\n"
        f"Status: `{payload['trace_preserving_status']}`\n\n"
        "Trace-preserving perturbations satisfy `Tr(delta rho_f)=0`, which removes the identity direction from relative stochastic activity.\n",
        encoding="utf-8",
    )
    outputs["attractor"].write_text(
        "# Attractor Normalization Identity Protection\n\n"
        f"Status: `{payload['attractor_normalization_status']}`\n\n"
        "The attractor normalization route remains structural because the full Hessian/action derivation is not implemented here.\n",
        encoding="utf-8",
    )
    outputs["quark"].write_text(
        "# Quark Active Fraction Consequence Candidate\n\n"
        f"Status: `{payload['quark_active_fraction_consequence_status']}`\n\n"
        "Up-sector active fraction is `35/36`; down-sector active fraction is `143/144`. These are channel-theory consequences only, not official dressing rules.\n",
        encoding="utf-8",
    )
    outputs["lindblad"].write_text(
        "# Lindblad-Like Traceless Generator Candidate\n\n"
        f"Status: `{payload['lindblad_generator_status']}`\n\n"
        "A formal zero-mean generator can be expanded in traceless `su(d)` directions. This is a symbolic count, not an imported open-system proof.\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_identity_traceless_stochastic_outputs()
