"""Charged-lepton partial derivation consolidation for BHSM.

This module consolidates existing charged-lepton partial, conditional, and
candidate audit results into one claim-safe ledger. It does not modify frozen
predictions or promote a lepton dressing rule to official status.
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


CONSOLIDATION_STATUS = "CHARGED_LEPTON_PARTIAL_DERIVATION_CONSOLIDATED"
LEPTON_CHAIN_OVERALL_STATUS = "LEPTON_DRESSING_PARTIAL_DERIVATION_CANDIDATE_ONLY"
LEPTON_OMEGA_STATUS = "LEPTON_OMEGA_STRUCTURALLY_DERIVED_FROM_BOUNDARY_PROJECTOR"
CHANNEL_DIMENSION_STATUS = "DIM_H_EQUALS_ABS_OMEGA_PARTIAL"
PHYSICAL_CHANNEL_SPACE_STATUS = "PHYSICAL_CHANNEL_SPACE_PARTIAL"
END_H_STOCHASTIC_ALGEBRA_STATUS = "END_H_STOCHASTIC_ALGEBRA_PARTIAL"
IDENTITY_TRACELESS_STATUS = "IDENTITY_TRACELESS_STOCHASTIC_CONDITIONAL"
BROWNIAN_GENERATOR_STATUS = "BROWNIAN_GENERATOR_TOPOGRAPHIC_PARTIAL"
ALPHA_PI_STATUS = "ALPHA_OVER_PI_STOCHASTIC_STRENGTH_PARTIAL"
FACTOR_TWO_STATUS = "BROWNIAN_FACTOR_TWO_CONVENTION_DEPENDENT_STRENGTHENED"
ETA_STATUS = "LEPTON_ETA_NORMALIZATION_CONVENTION_DEPENDENT_STRENGTHENED"
DRESSING_STATUS = "LEPTON_DRESSING_CANDIDATE_NOT_OFFICIAL"
LEPTON_8_9_STATUS = "LEPTON_8_9_CHANNEL_RULE_PARTIAL_DERIVATION_STRENGTHENED"


@dataclass(frozen=True)
class ClaimStatusRow:
    """One link in the consolidated charged-lepton claim chain."""

    link: str
    statement: str
    status: str
    evidence: str
    limitation: str


def q_from_kj(k: int, j: int) -> int:
    """Return Hopf charge q=k-2j."""

    return int(k) - 2 * int(j)


def lepton_omega(q: int, j: int) -> int:
    """Return charged-lepton boundary operator Omega_l=-q+2j."""

    return -int(q) + 2 * int(j)


def mode_norm_N(k: int, j: int) -> int:
    """Return candidate Brownian norm N=q^2+j^2."""

    q = q_from_kj(k, j)
    return q * q + int(j) * int(j)


def lepton_channel_dimension() -> int:
    """Return dim H_l=3 under the partial cyclic monodromy scaffold."""

    return 3


def end_dimension(d: int) -> int:
    """Return dim End(H)=d^2."""

    return int(d) * int(d)


def identity_channel_count(d: int) -> int:
    """Return common identity-channel count."""

    _ = int(d)
    return 1


def traceless_channel_count(d: int) -> int:
    """Return traceless active channel count d^2-1."""

    return end_dimension(d) - identity_channel_count(d)


def active_fraction(d: int) -> Fraction:
    """Return active traceless fraction (d^2-1)/d^2."""

    return Fraction(traceless_channel_count(d), end_dimension(d))


def alpha_over_pi(alpha: float) -> float:
    """Return alpha/pi."""

    return float(alpha) / pi


def eta_no_extra_half(alpha: float) -> float:
    """Return preferred repo-convention eta_l=8alpha/(9pi)."""

    return alpha_over_pi(alpha) * float(active_fraction(lepton_channel_dimension()))


def eta_half_factor(alpha: float) -> float:
    """Return raw-variance alternative eta_l=4alpha/(9pi)."""

    return 0.5 * eta_no_extra_half(alpha)


def eta_double_factor(alpha: float) -> float:
    """Return doubled sensitivity alternative eta_l=16alpha/(9pi)."""

    return 2.0 * eta_no_extra_half(alpha)


def preferred_eta_form() -> str:
    """Return preferred eta-form label."""

    return "no_extra_half_repo_exponent_convention"


def allowed_eta_forms(alpha: float) -> dict[str, float]:
    """Return all eta forms preserved by the factor-of-two audit trail."""

    return {
        "no_extra_half": eta_no_extra_half(alpha),
        "half_factor": eta_half_factor(alpha),
        "double_factor": eta_double_factor(alpha),
    }


def lepton_dressing_factor(alpha: float, k: int, j: int, eta_form: str = "preferred") -> float:
    """Return candidate-only lepton dressing factor for a selected eta form."""

    forms = allowed_eta_forms(alpha)
    form = "no_extra_half" if eta_form == "preferred" else eta_form
    if form not in forms:
        raise ValueError("eta_form must be preferred, no_extra_half, half_factor, or double_factor")
    return exp(-forms[form] * mode_norm_N(k, j))


def lepton_chain_status_object() -> tuple[ClaimStatusRow, ...]:
    """Return the consolidated charged-lepton claim-status table."""

    return (
        ClaimStatusRow(
            "hopf_charge",
            "q=k-2j",
            "DERIVED_LEDGER_FORMULA",
            "Implemented throughout the Berger/Hopf mode ledger.",
            "This is a supplied framework equation, not a new dynamical derivation.",
        ),
        ClaimStatusRow(
            "lepton_omega",
            "For B=0, L=1, T3=-1/2, O_q=-1 and O_j=+2, so Omega_l=-q+2j.",
            LEPTON_OMEGA_STATUS,
            "Boundary projector form A_rep=A_q tensor O_q + A_j tensor O_j.",
            "Global A_j normalization and full action-level uniqueness remain open.",
        ),
        ClaimStatusRow(
            "lepton_level",
            "The nonzero charged-lepton modes (5,2) and (9,3) both satisfy Omega_l=3.",
            "BOUNDARY_LEVEL_LEDGER_RECOVERED",
            "Direct q,j arithmetic recovers the supplied charged-lepton mode pair.",
            "This does not update official frozen predictions.",
        ),
        ClaimStatusRow(
            "cyclic_channel_dimension",
            "H_l=C[Z_3] and dim(H_l)=3 under cyclic boundary monodromy.",
            CHANNEL_DIMENSION_STATUS,
            "Preferred route is finite cyclic boundary monodromy.",
            "Ordinary S2 geometric quantization is not used for channel dimension; plus-one hazard remains.",
        ),
        ClaimStatusRow(
            "physical_channel_space",
            "Orbit residues are interpreted as physical stochastic boundary channels.",
            PHYSICAL_CHANNEL_SPACE_STATUS,
            "Density/covariance channel-space scaffold exists.",
            "Full stochastic dynamics from the completed action remains open.",
        ),
        ClaimStatusRow(
            "endomorphism_algebra",
            "End(H_l) has dimension 9, with one identity/common channel and eight traceless active channels.",
            END_H_STOCHASTIC_ALGEBRA_STATUS,
            "Finite channel algebra gives dim End(H_l)=3^2.",
            "Trace-preserving stochastic generator remains partial/conditional.",
        ),
        ClaimStatusRow(
            "active_fraction",
            "F_l=(3^2-1)/3^2=8/9.",
            LEPTON_8_9_STATUS,
            "Identity/common mode cancellation and traceless channel counting.",
            "Full Brownian/Lindblad rates on su(3) remain open.",
        ),
        ClaimStatusRow(
            "alpha_over_pi",
            "g_U1^2=e^2/(4pi^2)=alpha/pi in rationalized units.",
            ALPHA_PI_STATUS,
            "Algebra from alpha=e^2/(4pi) and normalized boundary phase e/(2pi).",
            "The completed stochastic path-integral role of alpha/pi remains convention-dependent.",
        ),
        ClaimStatusRow(
            "brownian_exponential",
            "Z_l(k,j)=exp[-eta_l N(k,j)] with N=q^2+j^2 is the repo-preferred candidate form.",
            BROWNIAN_GENERATOR_STATUS,
            "Topographic/Brownian and stochastic path-integral audits support this scaffold.",
            "The full stochastic generator is not derived.",
        ),
        ClaimStatusRow(
            "eta_preferred",
            "Under the repo exponent convention, eta_l=(alpha/pi)(8/9)=8alpha/(9pi).",
            ETA_STATUS,
            "Combines alpha/pi with active fraction 8/9.",
            "Half and doubled alternatives remain recorded; this is not official prediction adoption.",
        ),
        ClaimStatusRow(
            "factor_two",
            "The factor-of-two hazard remains convention-dependent.",
            FACTOR_TWO_STATUS,
            "Heat-kernel, phase-cumulant, and Ito routes are explicitly separated.",
            "The completed stochastic measure has not selected D versus g^2.",
        ),
    )


def factor_two_status_object(alpha: float | None = None) -> dict[str, Any]:
    """Return compact factor-two status and eta alternatives."""

    resolved_alpha = 1.0 / ALPHA_INV_LOW_ENERGY if alpha is None else float(alpha)
    return {
        "status": FACTOR_TWO_STATUS,
        "preferred_eta_form": preferred_eta_form(),
        "allowed_eta_forms": allowed_eta_forms(resolved_alpha),
        "does_factor_two_close": False,
        "does_eta_l_8alpha_9pi_remain_supported": True,
        "limitations": (
            "alpha/pi may be generator coefficient under repo convention",
            "alpha/pi may be raw variance under phase-cumulant convention",
            "completed stochastic path-integral normalization remains open",
        ),
    }


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
    """Return consolidated charged-lepton audit payload."""

    resolved_alpha = 1.0 / ALPHA_INV_LOW_ENERGY if alpha is None else float(alpha)
    d = lepton_channel_dimension()
    mu_q = q_from_kj(5, 2)
    e_q = q_from_kj(9, 3)
    open_blockers = (
        "derive primitive finite cyclic quotient from the completed boundary action",
        "prove C[Z_|Omega_f|] orbit states are physical boundary channel states from full dynamics",
        "derive stochastic residue sampling from completed topographic/BHSM dynamics",
        "derive full Brownian/Lindblad generator rates D_a on su(d_f)",
        "derive from completed stochastic path integral whether alpha/pi is generator coefficient D or raw variance g^2",
        "derive Brownian time/cycle normalization beyond repo convention tau=1",
        "fix A_j normalization/global bundle coupling without convention dependence",
        "decide later whether lepton dressing belongs in an official v2 prediction set",
    )
    payload: dict[str, Any] = {
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "prs_opened": False,
        "consolidation_status": CONSOLIDATION_STATUS,
        "lepton_chain_overall_status": LEPTON_CHAIN_OVERALL_STATUS,
        "lepton_omega_status": LEPTON_OMEGA_STATUS,
        "channel_dimension_status": CHANNEL_DIMENSION_STATUS,
        "physical_channel_space_status": PHYSICAL_CHANNEL_SPACE_STATUS,
        "End_H_stochastic_algebra_status": END_H_STOCHASTIC_ALGEBRA_STATUS,
        "identity_traceless_status": IDENTITY_TRACELESS_STATUS,
        "brownian_generator_status": BROWNIAN_GENERATOR_STATUS,
        "alpha_pi_status": ALPHA_PI_STATUS,
        "factor_two_status": FACTOR_TWO_STATUS,
        "eta_status": ETA_STATUS,
        "dressing_status": DRESSING_STATUS,
        "preferred_eta_form": preferred_eta_form(),
        "allowed_eta_forms": allowed_eta_forms(resolved_alpha),
        "does_eta_l_8alpha_9pi_remain_supported": True,
        "does_factor_two_close": False,
        "does_this_promote_full_lepton_8_9": False,
        "does_this_change_official_predictions": False,
        "lepton_modes": {
            "tau_reference": {"k": 0, "j": 0, "q": q_from_kj(0, 0), "N": mode_norm_N(0, 0), "Z": lepton_dressing_factor(resolved_alpha, 0, 0)},
            "muon": {"k": 5, "j": 2, "q": mu_q, "Omega_l": lepton_omega(mu_q, 2), "N": mode_norm_N(5, 2), "Z": lepton_dressing_factor(resolved_alpha, 5, 2)},
            "electron": {"k": 9, "j": 3, "q": e_q, "Omega_l": lepton_omega(e_q, 3), "N": mode_norm_N(9, 3), "Z": lepton_dressing_factor(resolved_alpha, 9, 3)},
        },
        "channel_counts": {
            "dim_H_l": d,
            "dim_End_H_l": end_dimension(d),
            "identity_count": identity_channel_count(d),
            "traceless_count": traceless_channel_count(d),
            "active_fraction": active_fraction(d),
            "geometric_quantization_plus_one_hazard": True,
            "preferred_dimension_route": "cyclic_boundary_monodromy",
        },
        "factor_two": factor_two_status_object(resolved_alpha),
        "claim_status_table": lepton_chain_status_object(),
        "derived_components": (
            "charged_lepton_boundary_projector_coefficients_Oq_minus_1_Oj_plus_2",
            "Omega_l_mode_pair_arithmetic_equals_3",
            "End_H_l_dimension_count_3_squared",
            "common_mode_cancellation_for_identity_channel",
            "alpha_over_pi_algebra_from_rationalized_U1_coupling",
        ),
        "partial_components": (
            "cyclic_boundary_monodromy_channel_dimension",
            "physical_boundary_channel_space_identification",
            "Brownian_generator_topographic_scaffold",
            "exponential_dressing_from_Brownian_scaffold",
            "quadratic_norm_N_equals_q_squared_plus_j_squared",
            "stochastic_path_integral_normalization",
        ),
        "conditional_components": (
            "identity_traceless_stochastic_protection",
            "trace_preserving_noise_on_End_H_l",
            "eta_l_8alpha_over_9pi_under_repo_convention",
        ),
        "candidate_components": (
            "charged_lepton_dressing_factor_Z_l",
            "half_factor_eta_alternative",
            "double_factor_eta_sensitivity",
        ),
        "open_blockers": open_blockers,
        "forbidden_claims_absent": True,
        "safe_to_merge_as_candidate_only": True,
        "frozen_sanity": validate_no_official_outputs_modified(),
    }
    payload["eta_exact_checks"] = {
        "no_extra_half_matches_8alpha_over_9pi": isclose(
            payload["allowed_eta_forms"]["no_extra_half"], 8.0 * resolved_alpha / (9.0 * pi)
        ),
        "half_factor_matches_4alpha_over_9pi": isclose(
            payload["allowed_eta_forms"]["half_factor"], 4.0 * resolved_alpha / (9.0 * pi)
        ),
        "double_factor_matches_16alpha_over_9pi": isclose(
            payload["allowed_eta_forms"]["double_factor"], 16.0 * resolved_alpha / (9.0 * pi)
        ),
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


def render_consolidated_markdown(payload: dict[str, Any] | None = None, title: str | None = None) -> str:
    """Render the consolidated charged-lepton Markdown report."""

    p = audit_payload() if payload is None else payload
    active = p["channel_counts"]["active_fraction"]
    if isinstance(active, Fraction):
        active_label = f"{active.numerator}/{active.denominator}"
    else:
        active_label = f"{active['numerator']}/{active['denominator']}"
    heading = title or "BHSM Charged-Lepton Partial Derivation Consolidated"
    lines = [
        f"# {heading}",
        "",
        "This document consolidates the charged-lepton partial derivation chain. It is a status and audit package only: no frozen output is changed and no lepton dressing is promoted to an official prediction.",
        "",
        "## Summary",
        "",
        f"Consolidation status: `{p['consolidation_status']}`",
        f"Overall status: `{p['lepton_chain_overall_status']}`",
        f"Omega status: `{p['lepton_omega_status']}`",
        f"Channel dimension status: `{p['channel_dimension_status']}`",
        f"Identity/traceless status: `{p['identity_traceless_status']}`",
        f"alpha/pi status: `{p['alpha_pi_status']}`",
        f"Factor-two status: `{p['factor_two_status']}`",
        f"Eta status: `{p['eta_status']}`",
        f"Dressing status: `{p['dressing_status']}`",
        "",
        "## Charged-Lepton Arithmetic",
        "",
        "```text",
        "q = k - 2j",
        "Omega_l = -q + 2j",
        "N(k,j) = q^2 + j^2",
        "```",
        "",
        "| Mode | (k,j) | q | Omega_l | N | Candidate Z under preferred eta |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for label in ("tau_reference", "muon", "electron"):
        row = p["lepton_modes"][label]
        omega = row.get("Omega_l", lepton_omega(row["q"], row["j"]))
        lines.append(
            f"| `{label}` | `({row['k']},{row['j']})` | `{row['q']}` | `{omega}` | `{row['N']}` | `{row['Z']}` |"
        )
    lines.extend(
        [
            "",
            "## Channel Space",
            "",
            f"Preferred dimension route: `{p['channel_counts']['preferred_dimension_route']}`",
            f"Geometric quantization plus-one hazard: `{p['channel_counts']['geometric_quantization_plus_one_hazard']}`",
            "",
            "| Quantity | Value |",
            "| --- | ---: |",
            f"| dim H_l | `{p['channel_counts']['dim_H_l']}` |",
            f"| dim End(H_l) | `{p['channel_counts']['dim_End_H_l']}` |",
            f"| identity/common count | `{p['channel_counts']['identity_count']}` |",
            f"| traceless active count | `{p['channel_counts']['traceless_count']}` |",
            f"| active fraction | `{active_label}` |",
            "",
            "## Eta Forms",
            "",
            "| Form | eta_l | Claim status |",
            "| --- | ---: | --- |",
            f"| no_extra_half | `{p['allowed_eta_forms']['no_extra_half']}` | preferred repo exponent convention |",
            f"| half_factor | `{p['allowed_eta_forms']['half_factor']}` | raw-variance alternative |",
            f"| double_factor | `{p['allowed_eta_forms']['double_factor']}` | sensitivity diagnostic |",
            "",
            f"Preferred eta form: `{p['preferred_eta_form']}`",
            f"eta_l=8alpha/(9pi) remains supported: `{p['does_eta_l_8alpha_9pi_remain_supported']}`",
            f"Factor two closes: `{p['does_factor_two_close']}`",
            f"Promotes full lepton 8/9: `{p['does_this_promote_full_lepton_8_9']}`",
            "",
            "## Claim-Status Table",
            "",
            "| Link | Status | Statement | Limitation |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in p["claim_status_table"]:
        link = row.link if isinstance(row, ClaimStatusRow) else row["link"]
        status = row.status if isinstance(row, ClaimStatusRow) else row["status"]
        statement = row.statement if isinstance(row, ClaimStatusRow) else row["statement"]
        limitation = row.limitation if isinstance(row, ClaimStatusRow) else row["limitation"]
        lines.append(f"| `{link}` | `{status}` | {statement} | {limitation} |")
    lines.extend(["", "## Open Blockers", ""])
    lines.extend(f"{index}. {item}" for index, item in enumerate(p["open_blockers"], start=1))
    lines.extend(
        [
            "",
            "## Claim Safety",
            "",
            "- No official frozen outputs are changed.",
            "- No retuning is performed.",
            "- No frozen lepton or quark dressing rule is changed.",
            "- No claim is made that BHSM replaces the Standard Model.",
            "- The charged-lepton dressing remains candidate-only.",
            "",
        ]
    )
    return "\n".join(lines)


def render_status_table_markdown(payload: dict[str, Any] | None = None) -> str:
    """Render just the charged-lepton claim-status table."""

    p = audit_payload() if payload is None else payload
    lines = [
        "# BHSM Charged-Lepton Claim Status Table",
        "",
        "| Link | Status | Evidence | Limitation |",
        "| --- | --- | --- | --- |",
    ]
    for row in p["claim_status_table"]:
        link = row.link if isinstance(row, ClaimStatusRow) else row["link"]
        status = row.status if isinstance(row, ClaimStatusRow) else row["status"]
        evidence = row.evidence if isinstance(row, ClaimStatusRow) else row["evidence"]
        limitation = row.limitation if isinstance(row, ClaimStatusRow) else row["limitation"]
        lines.append(f"| `{link}` | `{status}` | {evidence} | {limitation} |")
    lines.append("")
    return "\n".join(lines)


def render_factor_two_markdown(payload: dict[str, Any] | None = None) -> str:
    """Render factor-of-two normalization status for charged leptons."""

    p = audit_payload() if payload is None else payload
    return "\n".join(
        [
            "# BHSM Charged-Lepton Factor-Two Normalization Status",
            "",
            f"Status: `{p['factor_two_status']}`",
            f"Preferred eta form: `{p['preferred_eta_form']}`",
            "",
            "| Form | eta_l |",
            "| --- | ---: |",
            f"| no_extra_half | `{p['allowed_eta_forms']['no_extra_half']}` |",
            f"| half_factor | `{p['allowed_eta_forms']['half_factor']}` |",
            f"| double_factor | `{p['allowed_eta_forms']['double_factor']}` |",
            "",
            "The no-extra-half form remains supported by the repo exponent convention. The raw-variance and doubled forms remain recorded alternatives. No official prediction is changed.",
            "",
        ]
    )


def render_open_blockers_markdown(payload: dict[str, Any] | None = None) -> str:
    """Render charged-lepton open blockers."""

    p = audit_payload() if payload is None else payload
    lines = ["# BHSM Charged-Lepton Open Blockers", ""]
    lines.extend(f"{index}. {item}" for index, item in enumerate(p["open_blockers"], start=1))
    lines.extend(["", "These blockers prevent promotion to a fully derived or official lepton dressing rule.", ""])
    return "\n".join(lines)


def export_charged_lepton_consolidation_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export charged-lepton consolidation artifacts."""

    base = Path(root)
    payload = audit_payload()
    outputs = {
        "theory_main": base / "theory" / "charged_lepton_partial_derivation_consolidated.md",
        "status_table": base / "theory" / "charged_lepton_claim_status_table.md",
        "factor_two": base / "theory" / "charged_lepton_factor_two_normalization_status.md",
        "blockers": base / "theory" / "charged_lepton_open_blockers.md",
        "audit_md": base / "audits" / "charged_lepton_partial_derivation_consolidation_audit.md",
        "audit_json": base / "audits" / "charged_lepton_partial_derivation_consolidation_audit.json",
    }
    for path in outputs.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    outputs["theory_main"].write_text(render_consolidated_markdown(payload), encoding="utf-8")
    outputs["status_table"].write_text(render_status_table_markdown(payload), encoding="utf-8")
    outputs["factor_two"].write_text(render_factor_two_markdown(payload), encoding="utf-8")
    outputs["blockers"].write_text(render_open_blockers_markdown(payload), encoding="utf-8")
    outputs["audit_md"].write_text(render_consolidated_markdown(payload), encoding="utf-8")
    outputs["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_charged_lepton_consolidation_outputs()
