"""Brownian cumulant normalization and factor-of-two audit.

This module distinguishes three related conventions:

* heat-kernel/exponent coefficient: Z=exp[-D N]
* Gaussian phase cumulant: Z=exp[-variance/2]
* doubled diagnostic: Z=exp[-2 D N]

The existing BHSM repo uses eta as the exponent coefficient in exp[-eta N].
That supports the no-extra-half form as the repo convention, while the full
stochastic path-integral normalization remains open.
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


BROWNIAN_FACTOR_TWO_RESOLVED_NO_EXTRA_HALF = "BROWNIAN_FACTOR_TWO_RESOLVED_NO_EXTRA_HALF"
BROWNIAN_FACTOR_TWO_RESOLVED_HALF_FACTOR = "BROWNIAN_FACTOR_TWO_RESOLVED_HALF_FACTOR"
BROWNIAN_FACTOR_TWO_CONVENTION_DEPENDENT = "BROWNIAN_FACTOR_TWO_CONVENTION_DEPENDENT"
BROWNIAN_FACTOR_TWO_OPEN = "BROWNIAN_FACTOR_TWO_OPEN"
BROWNIAN_FACTOR_TWO_REJECTED = "BROWNIAN_FACTOR_TWO_REJECTED"

HEAT_KERNEL_NORMALIZATION_PARTIAL = "HEAT_KERNEL_NORMALIZATION_PARTIAL"
PHASE_CUMULANT_HALF_FACTOR_CONDITIONAL = "PHASE_CUMULANT_HALF_FACTOR_CONDITIONAL"
ITO_GENERATOR_NORMALIZATION_CONVENTION_DEPENDENT = (
    "ITO_GENERATOR_NORMALIZATION_CONVENTION_DEPENDENT"
)
ETA_EXPONENT_CONVENTION_REPO_SUPPORTED = "ETA_EXPONENT_CONVENTION_REPO_SUPPORTED"
ALPHA_OVER_PI_INTERPRETATION_CONVENTION_DEPENDENT = (
    "ALPHA_OVER_PI_INTERPRETATION_CONVENTION_DEPENDENT"
)
LEPTON_ETA_NORMALIZATION_CONVENTION_DEPENDENT = (
    "LEPTON_ETA_NORMALIZATION_CONVENTION_DEPENDENT"
)


@dataclass(frozen=True)
class FactorTwoStatus:
    """Status for one factor-of-two route."""

    route: str
    status: str
    supports_no_extra_half: bool
    supports_half_factor: bool
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]


def e_squared_from_alpha(alpha: float) -> float:
    """Return e^2=4*pi*alpha."""

    return 4.0 * pi * float(alpha)


def phase_coupling_squared(alpha: float) -> float:
    """Return g_U1^2=alpha/pi."""

    return float(alpha) / pi


def heat_kernel_eta(alpha: float, active_fraction: Fraction | float) -> float:
    """Return eta=(alpha/pi)*active_fraction."""

    return phase_coupling_squared(alpha) * float(active_fraction)


def phase_cumulant_eta(alpha: float, active_fraction: Fraction | float) -> float:
    """Return eta=(alpha/(2*pi))*active_fraction."""

    return 0.5 * phase_coupling_squared(alpha) * float(active_fraction)


def doubled_eta(alpha: float, active_fraction: Fraction | float) -> float:
    """Return eta=(2*alpha/pi)*active_fraction."""

    return 2.0 * phase_coupling_squared(alpha) * float(active_fraction)


def lepton_active_fraction() -> Fraction:
    """Return exact lepton active fraction 8/9."""

    return Fraction(8, 9)


def lepton_eta_no_extra_half(alpha: float) -> float:
    """Return eta_l=8alpha/(9pi)."""

    return heat_kernel_eta(alpha, lepton_active_fraction())


def lepton_eta_half_factor(alpha: float) -> float:
    """Return eta_l=4alpha/(9pi)."""

    return phase_cumulant_eta(alpha, lepton_active_fraction())


def lepton_eta_double_factor(alpha: float) -> float:
    """Return eta_l=16alpha/(9pi)."""

    return doubled_eta(alpha, lepton_active_fraction())


def q_from_kj(k: int, j: int) -> int:
    """Return q=k-2j."""

    return int(k) - 2 * int(j)


def mode_norm_N(k: int, j: int) -> int:
    """Return N=q^2+j^2."""

    q = q_from_kj(k, j)
    return q * q + int(j) * int(j)


def attenuation_heat_kernel(alpha: float, N: int, active_fraction: Fraction | float) -> float:
    """Return exp[-(alpha/pi)*active_fraction*N]."""

    return exp(-heat_kernel_eta(alpha, active_fraction) * int(N))


def attenuation_phase_cumulant(alpha: float, N: int, active_fraction: Fraction | float) -> float:
    """Return exp[-(alpha/(2*pi))*active_fraction*N]."""

    return exp(-phase_cumulant_eta(alpha, active_fraction) * int(N))


def attenuation_doubled(alpha: float, N: int, active_fraction: Fraction | float) -> float:
    """Return exp[-(2*alpha/pi)*active_fraction*N]."""

    return exp(-doubled_eta(alpha, active_fraction) * int(N))


def heat_kernel_status_object() -> FactorTwoStatus:
    """Return heat-kernel normalization status."""

    return FactorTwoStatus(
        route="heat_kernel_generator_convention",
        status=HEAT_KERNEL_NORMALIZATION_PARTIAL,
        supports_no_extra_half=True,
        supports_half_factor=False,
        assumptions=(
            "BHSM eta is the exponent/generator coefficient in Z=exp[-eta N]",
            "boundary-cycle time is normalized to one",
        ),
        limitations=(
            "the completed stochastic path-integral generator is not derived",
            "this supports the repo convention rather than proving uniqueness",
        ),
    )


def phase_cumulant_status_object() -> FactorTwoStatus:
    """Return Gaussian phase-cumulant status."""

    return FactorTwoStatus(
        route="gaussian_phase_cumulant",
        status=PHASE_CUMULANT_HALF_FACTOR_CONDITIONAL,
        supports_no_extra_half=False,
        supports_half_factor=True,
        assumptions=(
            "alpha/pi is interpreted as raw phase variance g_U1^2",
            "Z=E[exp(i theta)] with Gaussian variance",
        ),
        limitations=(
            "this is not the convention used by existing eta-as-exponent BHSM notes",
            "it would define a different candidate eta without changing official predictions",
        ),
    )


def ito_status_object() -> FactorTwoStatus:
    """Return Ito/generator convention status."""

    return FactorTwoStatus(
        route="ito_generator_normalization",
        status=ITO_GENERATOR_NORMALIZATION_CONVENTION_DEPENDENT,
        supports_no_extra_half=True,
        supports_half_factor=True,
        assumptions=(
            "dtheta=g dW gives variance g^2 t",
            "the heat generator convention may absorb the 1/2 into D",
        ),
        limitations=(
            "the repo has not derived whether alpha/pi denotes g^2 or the generator coefficient",
        ),
    )


def eta_exponent_status_object() -> FactorTwoStatus:
    """Return repo eta convention status."""

    return FactorTwoStatus(
        route="repo_eta_exponent_convention",
        status=ETA_EXPONENT_CONVENTION_REPO_SUPPORTED,
        supports_no_extra_half=True,
        supports_half_factor=False,
        assumptions=(
            "existing repo notes write lepton dressing as Z=exp[-eta N]",
            "eta_l is repeatedly compared as 8alpha/(9pi)",
        ),
        limitations=(
            "repo convention is not a full stochastic path-integral derivation",
        ),
    )


def factor_two_status_object() -> FactorTwoStatus:
    """Return aggregate factor-of-two status."""

    return FactorTwoStatus(
        route="brownian_factor_two_aggregate",
        status=BROWNIAN_FACTOR_TWO_CONVENTION_DEPENDENT,
        supports_no_extra_half=True,
        supports_half_factor=True,
        assumptions=(
            "repo eta convention supports the no-extra-half exponent coefficient",
            "Gaussian phase cumulant would require a half factor if alpha/pi were raw variance",
        ),
        limitations=(
            "the complete stochastic normalization has not selected variance versus generator coefficient",
            "therefore the no-extra-half form is preferred by repo convention but not uniquely proven",
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
    """Return Brownian cumulant normalization audit payload."""

    resolved_alpha = 1.0 / ALPHA_INV_LOW_ENERGY if alpha is None else float(alpha)
    active = lepton_active_fraction()
    factor = factor_two_status_object()
    heat = heat_kernel_status_object()
    phase = phase_cumulant_status_object()
    ito = ito_status_object()
    eta_status = eta_exponent_status_object()
    blockers_remaining = (
        "derive from completed stochastic path integral whether alpha/pi is raw variance or generator coefficient",
        "derive Brownian time/cycle normalization rather than setting tau=1 by convention",
        "derive primitive cyclic monodromy and full stochastic generator before any full lepton promotion",
    )
    payload: dict[str, Any] = {
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        "brownian_factor_two_status": factor.status,
        "heat_kernel_normalization_status": heat.status,
        "phase_cumulant_status": phase.status,
        "ito_generator_status": ito.status,
        "eta_exponent_convention_status": eta_status.status,
        "alpha_over_pi_interpretation_status": ALPHA_OVER_PI_INTERPRETATION_CONVENTION_DEPENDENT,
        "lepton_eta_normalization_status": LEPTON_ETA_NORMALIZATION_CONVENTION_DEPENDENT,
        "does_repo_define_eta_as_exponent_coefficient": True,
        "does_heat_kernel_convention_support_no_extra_half": True,
        "does_phase_cumulant_convention_require_half": True,
        "is_alpha_over_pi_raw_variance": True,
        "is_alpha_over_pi_generator_coefficient": True,
        "is_factor_two_resolved": False,
        "does_eta_l_8alpha_9pi_remain_supported": True,
        "does_this_change_official_predictions": False,
        "does_this_promote_full_lepton_8_9": False,
        "factor_two_hazards": (
            "Gaussian phase cumulant gives exp[-variance/2] if alpha/pi is raw variance",
            "heat-kernel convention gives exp[-D lambda] if alpha/pi is generator coefficient",
            "completed stochastic path-integral normalization is still absent",
        ),
        "allowed_eta_forms": {
            "no_extra_half": lepton_eta_no_extra_half(resolved_alpha),
            "half_factor": lepton_eta_half_factor(resolved_alpha),
            "double_factor": lepton_eta_double_factor(resolved_alpha),
        },
        "preferred_eta_form": "no_extra_half_repo_exponent_convention",
        "attenuation_examples_muon": {
            "N": mode_norm_N(5, 2),
            "heat_kernel": attenuation_heat_kernel(resolved_alpha, mode_norm_N(5, 2), active),
            "phase_cumulant": attenuation_phase_cumulant(resolved_alpha, mode_norm_N(5, 2), active),
            "double_factor": attenuation_doubled(resolved_alpha, mode_norm_N(5, 2), active),
        },
        "blockers_closed": (
            "repo_eta_as_exponent_coefficient_audited",
            "heat_kernel_no_extra_half_convention_formalized",
            "phase_cumulant_half_factor_hazard_formalized",
            "all_three_eta_forms_reported_without_prediction_changes",
        ),
        "blockers_remaining": blockers_remaining,
        "derived_components": (
            "exact_eta_form_algebra",
            "phase_cumulant_half_factor_formula",
            "heat_kernel_attenuation_formula",
        ),
        "partial_components": (
            "repo_no_extra_half_eta_convention",
            "heat_kernel_generator_interpretation",
        ),
        "conditional_components": (
            "half_factor_if_alpha_over_pi_is_raw_variance",
            "no_extra_half_if_alpha_over_pi_is_generator_coefficient",
        ),
        "candidate_components": ("doubled_eta_sensitivity_form",),
        "missing_assumptions": blockers_remaining,
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "status_objects": {
            "factor_two": factor,
            "heat_kernel": heat,
            "phase_cumulant": phase,
            "ito": ito,
            "eta_exponent": eta_status,
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
    """Render factor-of-two audit Markdown."""

    p = audit_payload() if payload is None else payload
    lines = [
        "# BHSM Brownian Cumulant Normalization and Factor-of-Two Audit",
        "",
        "This sprint audits whether the BHSM lepton exponent uses a heat-kernel coefficient or a Gaussian phase-cumulant variance convention.",
        "The repo consistently treats `eta` as the exponent coefficient in `Z=exp[-eta N]`, but the completed stochastic path-integral normalization is not yet derived.",
        "",
        "## Summary",
        "",
        f"Brownian factor-two status: `{p['brownian_factor_two_status']}`",
        f"Heat-kernel normalization: `{p['heat_kernel_normalization_status']}`",
        f"Phase-cumulant status: `{p['phase_cumulant_status']}`",
        f"Ito/generator status: `{p['ito_generator_status']}`",
        f"Eta exponent convention: `{p['eta_exponent_convention_status']}`",
        f"Lepton eta normalization: `{p['lepton_eta_normalization_status']}`",
        f"Preferred eta form: `{p['preferred_eta_form']}`",
        f"eta_l=8alpha/(9pi) remains supported: `{p['does_eta_l_8alpha_9pi_remain_supported']}`",
        f"Factor two resolved: `{p['is_factor_two_resolved']}`",
        f"Official predictions changed: `{p['does_this_change_official_predictions']}`",
        "",
        "## Eta Forms",
        "",
        "| Form | eta_l | Meaning |",
        "| --- | ---: | --- |",
        f"| `no_extra_half` | `{p['allowed_eta_forms']['no_extra_half']}` | repo heat-kernel/exponent convention |",
        f"| `half_factor` | `{p['allowed_eta_forms']['half_factor']}` | Gaussian phase-cumulant if alpha/pi is raw variance |",
        f"| `double_factor` | `{p['allowed_eta_forms']['double_factor']}` | sensitivity diagnostic |",
        "",
        "## Convention Distinction",
        "",
        "```text",
        "Heat kernel:       dK/dt = D Delta K  -> exp[-D lambda t]",
        "Phase cumulant:    E[exp(i theta)] with Var(theta)=sigma^2 -> exp[-sigma^2/2]",
        "Ito:               dtheta=g dW, generator coefficient may be g^2/2",
        "Repo eta:          Z=exp[-eta N]",
        "```",
        "",
        "## Hazards",
        "",
    ]
    lines.extend(f"- {item}" for item in p["factor_two_hazards"])
    lines.extend(["", "## Blockers Closed", ""])
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


def export_brownian_cumulant_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export factor-of-two audit artifacts."""

    base = Path(root)
    payload = audit_payload()
    outputs = {
        "main": base / "theory" / "brownian_cumulant_normalization_factor_two.md",
        "conventions": base / "theory" / "heat_kernel_vs_phase_cumulant_conventions.md",
        "eta": base / "theory" / "eta_as_exponent_coefficient_repo_convention.md",
        "lepton": base / "theory" / "lepton_eta_factor_two_consequence.md",
        "ito": base / "theory" / "ito_generator_normalization_note.md",
        "no_update": base / "theory" / "no_official_prediction_update_factor_two_note.md",
        "audit_md": base / "audits" / "brownian_cumulant_normalization_factor_two_audit.md",
        "audit_json": base / "audits" / "brownian_cumulant_normalization_factor_two_audit.json",
    }
    for path in outputs.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    outputs["main"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["audit_md"].write_text(render_markdown(payload), encoding="utf-8")
    outputs["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    outputs["conventions"].write_text(
        "# Heat-Kernel vs Phase-Cumulant Conventions\n\n"
        f"Heat-kernel status: `{payload['heat_kernel_normalization_status']}`\n\n"
        f"Phase-cumulant status: `{payload['phase_cumulant_status']}`\n\n"
        "Both conventions are mathematically valid. The repo eta convention supports the heat-kernel/exponent form, while a raw variance interpretation would require a half factor.\n",
        encoding="utf-8",
    )
    outputs["eta"].write_text(
        "# Eta as Exponent Coefficient Repo Convention\n\n"
        f"Status: `{payload['eta_exponent_convention_status']}`\n\n"
        "Existing BHSM notes consistently use `Z=exp[-eta N]`; therefore `eta_l=8alpha/(9pi)` remains the repo-preferred candidate form.\n",
        encoding="utf-8",
    )
    outputs["lepton"].write_text(
        "# Lepton Eta Factor-Two Consequence\n\n"
        f"Status: `{payload['lepton_eta_normalization_status']}`\n\n"
        f"Preferred form: `{payload['preferred_eta_form']}`\n\n"
        "No official lepton prediction is changed. Half and doubled forms are recorded as diagnostics only.\n",
        encoding="utf-8",
    )
    outputs["ito"].write_text(
        "# Ito Generator Normalization Note\n\n"
        f"Status: `{payload['ito_generator_status']}`\n\n"
        "If `alpha/pi` is interpreted as `g^2`, Ito heat-generator notation can introduce a `1/2`. If it is already the generator coefficient, no extra half appears.\n",
        encoding="utf-8",
    )
    outputs["no_update"].write_text(
        "# No Official Prediction Update Factor-Two Note\n\n"
        "This audit changes no frozen outputs and creates no official v2 prediction. It only records normalization conventions and diagnostics.\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_brownian_cumulant_outputs()
