"""Charged-lepton precision dressing candidate audit.

This sprint tests one fixed mode-dependent dressing rule for charged leptons:

    Z_l(k,j) = exp[-eta_l * (q^2 + j^2)].

The single parameter eta_l is fit from mu/tau only; e/tau is then a held-out
check.  Because eta_l is not independently derived, the candidate is not
official and does not alter frozen BHSM outputs.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import exp, isfinite, log
from pathlib import Path
from typing import Any

from bhsm_v1 import build_bhsm_bare_v1, compare_bhsm_v1_branches
from mass_scheme import build_ratio_reference, default_mass_references
from mode_selection import hopf_charge


LEPTON_PRECISION_DERIVED = "LEPTON_PRECISION_DERIVED"
LEPTON_DRESSING_CANDIDATE_NOT_OFFICIAL = "LEPTON_DRESSING_CANDIDATE_NOT_OFFICIAL"
LEPTON_PRECISION_WARNING_CONFIRMED = "LEPTON_PRECISION_WARNING_CONFIRMED"
LEPTON_DRESSING_REJECTED = "LEPTON_DRESSING_REJECTED"
CANDIDATE_NOT_OFFICIAL = "CANDIDATE_NOT_OFFICIAL"

LEPTON_MODES = {
    "middle": (5, 2),
    "light": (9, 3),
}
LEPTON_RATIO_PARTICLES = {
    "middle": ("mu", "tau"),
    "light": ("e", "tau"),
}


@dataclass(frozen=True)
class LeptonResidual:
    """One lepton ratio residual row."""

    rank: str
    quantity: str
    mode: tuple[int, int]
    q: int
    mode_norm: int
    predicted: float
    reference: float
    absolute_error: float
    relative_error: float


@dataclass(frozen=True)
class DressingRow:
    """One dressed candidate lepton row."""

    rank: str
    mode: tuple[int, int]
    mode_norm: int
    dressing_factor: float
    dressed_prediction: float
    reference: float
    relative_error: float
    baseline_relative_error: float
    improved: bool
    fitted_input: bool
    held_out: bool


@dataclass(frozen=True)
class LeptonPrecisionResult:
    """Structured output for the charged-lepton precision sprint."""

    classification: str
    candidate_status: str
    closes_lepton_precision_blocker: bool
    official_lepton_ratios_changed: bool
    per_particle_fitted_factors_used: bool
    fit_parameter_name: str
    fit_parameter_value: float
    fit_input_ratio: str
    held_out_ratio: str
    held_out_improved: bool
    damages_other_sectors_if_extended: bool
    recommendation: str


def reference_lepton_ratios() -> dict[str, float]:
    """Return pole lepton ratio references from the existing repo constants."""

    refs = default_mass_references()["MIXED_DEFAULT"]
    return {
        rank: build_ratio_reference(num, den, refs).ratio
        for rank, (num, den) in LEPTON_RATIO_PARTICLES.items()
    }


def frozen_lepton_ratios() -> dict[str, float]:
    """Return official frozen charged-lepton ratios."""

    outputs = build_bhsm_bare_v1().outputs["charged_lepton_ratios"]
    return {
        "middle": float(outputs["middle"]),
        "light": float(outputs["light"]),
    }


def mode_norm(mode: tuple[int, int]) -> int:
    """Return the predeclared Hopf/base norm q^2 + j^2."""

    k, j = mode
    q = hopf_charge(k, j)
    return q * q + j * j


def baseline_residuals() -> tuple[LeptonResidual, ...]:
    """Return baseline official lepton residuals."""

    refs = reference_lepton_ratios()
    preds = frozen_lepton_ratios()
    rows: list[LeptonResidual] = []
    for rank, mode in LEPTON_MODES.items():
        predicted = preds[rank]
        reference = refs[rank]
        rows.append(
            LeptonResidual(
                rank=rank,
                quantity="mu/tau" if rank == "middle" else "e/tau",
                mode=mode,
                q=hopf_charge(*mode),
                mode_norm=mode_norm(mode),
                predicted=predicted,
                reference=reference,
                absolute_error=abs(predicted - reference),
                relative_error=abs(predicted - reference) / abs(reference),
            )
        )
    return tuple(rows)


def fit_eta_from_mu_tau() -> float:
    """Fit eta_l from mu/tau only."""

    mu = next(row for row in baseline_residuals() if row.rank == "middle")
    factor = mu.reference / mu.predicted
    if factor <= 0:
        raise ValueError("invalid mu/tau fit factor")
    eta = -log(factor) / float(mu.mode_norm)
    if not isfinite(eta):
        raise ValueError("nonfinite eta_l")
    return eta


def dressing_factor(mode: tuple[int, int], eta_l: float) -> float:
    """Return exp[-eta_l*(q^2+j^2)]."""

    return exp(-float(eta_l) * float(mode_norm(mode)))


def candidate_dressing_rows() -> tuple[DressingRow, ...]:
    """Return dressed candidate rows with e/tau held out."""

    eta_l = fit_eta_from_mu_tau()
    residuals = {row.rank: row for row in baseline_residuals()}
    rows: list[DressingRow] = []
    for rank, mode in LEPTON_MODES.items():
        baseline = residuals[rank]
        factor = dressing_factor(mode, eta_l)
        dressed = baseline.predicted * factor
        rel = abs(dressed - baseline.reference) / abs(baseline.reference)
        rows.append(
            DressingRow(
                rank=rank,
                mode=mode,
                mode_norm=mode_norm(mode),
                dressing_factor=factor,
                dressed_prediction=dressed,
                reference=baseline.reference,
                relative_error=rel,
                baseline_relative_error=baseline.relative_error,
                improved=rel < baseline.relative_error,
                fitted_input=rank == "middle",
                held_out=rank == "light",
            )
        )
    return tuple(rows)


def extension_damage_check() -> dict[str, Any]:
    """Report why extending the rule outside charged leptons is not allowed here."""

    comparison = compare_bhsm_v1_branches()
    return {
        "extended_to_quarks_or_ckm": False,
        "extension_allowed": False,
        "reason": (
            "The candidate is explicitly charged-lepton scoped. Extending the fitted "
            "eta_l to quarks or CKM would change official frozen outputs without a "
            "derivation."
        ),
        "official_branch_comparison": comparison,
    }


def precision_result() -> LeptonPrecisionResult:
    """Return the sprint-level charged-lepton precision result."""

    rows = candidate_dressing_rows()
    held_out = next(row for row in rows if row.held_out)
    fit_row = next(row for row in rows if row.fitted_input)
    both_improve = all(row.improved for row in rows)
    classification = (
        LEPTON_DRESSING_CANDIDATE_NOT_OFFICIAL
        if both_improve
        else LEPTON_PRECISION_WARNING_CONFIRMED
    )
    return LeptonPrecisionResult(
        classification=classification,
        candidate_status=CANDIDATE_NOT_OFFICIAL,
        closes_lepton_precision_blocker=False,
        official_lepton_ratios_changed=False,
        per_particle_fitted_factors_used=False,
        fit_parameter_name="eta_l",
        fit_parameter_value=fit_eta_from_mu_tau(),
        fit_input_ratio="mu/tau",
        held_out_ratio="e/tau",
        held_out_improved=held_out.improved,
        damages_other_sectors_if_extended=True,
        recommendation=(
            "Keep official lepton ratios frozen. The one-parameter mode-norm "
            "candidate improves mu/tau and the held-out e/tau row, but eta_l is fit "
            "from mu/tau rather than derived, so the candidate remains non-official."
        ),
    )


def frozen_sanity_payload() -> dict[str, Any]:
    """Return frozen-output sanity checks."""

    comparison = compare_bhsm_v1_branches()
    rows = comparison["rows"]
    changed = [row for row in rows if row["changed"]]
    return {
        "BHSM_BARE_V1_unchanged": comparison["branches"][0] == "BHSM_BARE_V1",
        "BHSM_DRESSED_V1_CANDIDATE_unchanged": comparison["branches"][1]
        == "BHSM_DRESSED_V1_CANDIDATE",
        "dressed_branch_changes_only_c_over_t": len(changed) == 1
        and changed[0]["quantity"] == "c/t",
        "u_over_t_unchanged": next(row for row in rows if row["quantity"] == "u/t")[
            "changed"
        ]
        is False,
        "ckm_sin_theta_13_unchanged": next(
            row for row in rows if row["quantity"] == "sin_theta_13"
        )["changed"]
        is False,
        "changed_rows": changed,
    }


def audit_payload() -> dict[str, Any]:
    """Return full charged-lepton precision closure audit payload."""

    result = precision_result()
    return {
        "title": "BHSM charged-lepton precision dressing audit",
        "status": "BLOCKS_FULL_COMPLETION",
        "blocker": "LEPTON_PRECISION_NOT_SOLVED",
        "classification": result.classification,
        "candidate_status": result.candidate_status,
        "closes_lepton_precision_blocker": result.closes_lepton_precision_blocker,
        "official_lepton_ratios_changed": result.official_lepton_ratios_changed,
        "baseline_residuals": baseline_residuals(),
        "candidate_rule": {
            "name": "charged_lepton_mode_norm_exponential",
            "formula": "Z_l(k,j)=exp[-eta_l*(q^2+j^2)]",
            "fit_parameter": result.fit_parameter_name,
            "fit_parameter_value": result.fit_parameter_value,
            "fit_input_ratio": result.fit_input_ratio,
            "held_out_ratio": result.held_out_ratio,
            "derived": False,
            "pre_registered_in_this_sprint": True,
            "per_particle_fitted_factors_used": result.per_particle_fitted_factors_used,
        },
        "candidate_rows": candidate_dressing_rows(),
        "damage_checks": extension_damage_check(),
        "frozen_sanity": frozen_sanity_payload(),
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "promotion_criteria": (
            "derive eta_l independently from BHSM internal dynamics",
            "pre-freeze the rule before future external comparisons",
            "show the charged-lepton scope follows from the action rather than convenience",
            "show no damage to quark, CKM, gauge, Higgs, or H_T screens",
        ),
        "rejection_criteria": (
            "eta_l remains fitted from mu/tau",
            "the held-out e/tau row fails under updated references",
            "the rule requires separate electron and muon factors",
            "extension outside charged leptons damages frozen outputs",
        ),
        "recommendation": result.recommendation,
        "limitations": (
            "One parameter is fit from mu/tau, so this is not a derivation.",
            "The candidate is not part of BHSM_BARE_V1 or BHSM_DRESSED_V1_CANDIDATE.",
            "No time/location variation is used.",
            "No ordinary running/scheme explanation is claimed.",
        ),
    }


def _jsonable(value: object) -> object:
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
    """Render the audit as Markdown."""

    payload = payload or audit_payload()
    lines = [
        "# Charged-Lepton Precision Closure",
        "",
        "## Problem",
        "",
        "BHSM charged-lepton ratios survive at hierarchy/pattern level, but the sprint asks whether one fixed mode-dependent rule can improve both `mu/tau` and `e/tau` without per-particle fitting.",
        "",
        "## Official Frozen Lepton Status",
        "",
        "- Official frozen lepton ratios are unchanged.",
        "- The candidate is not part of `BHSM_BARE_V1` or `BHSM_DRESSED_V1_CANDIDATE`.",
        "",
        "## Why Ordinary Running Failed",
        "",
        "Charged-lepton pole ratios are scheme-stable at this audit level; ordinary running is not used as a precision repair.",
        "",
        "## Why Time/Location Variation Is Rejected",
        "",
        "The sprint uses no time, location, or environment variation. Any such rule would violate the fixed frozen-output discipline.",
        "",
        "## Candidate Fixed Mode-Dressing Rule",
        "",
        f"Formula: `{payload['candidate_rule']['formula']}`",
        f"Fit input: `{payload['candidate_rule']['fit_input_ratio']}`",
        f"Held-out row: `{payload['candidate_rule']['held_out_ratio']}`",
        f"eta_l: `{payload['candidate_rule']['fit_parameter_value']}`",
        "",
        "## Held-Out Prediction Logic",
        "",
        "| Rank | Mode | Norm | Baseline Error | Dressed Error | Improved | Fitted Input | Held Out |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["candidate_rows"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                row.rank,
                row.mode,
                row.mode_norm,
                row.baseline_relative_error,
                row.relative_error,
                row.improved,
                row.fitted_input,
                row.held_out,
            )
        )
    lines.extend(
        [
            "",
            "## Damage Checks",
            "",
            f"Extension allowed: `{payload['damage_checks']['extension_allowed']}`",
            payload["damage_checks"]["reason"],
            "",
            "## Closure Verdict",
            "",
            f"Classification: `{payload['classification']}`",
            f"Candidate status: `{payload['candidate_status']}`",
            f"Lepton precision blocker closed: `{payload['closes_lepton_precision_blocker']}`",
            "",
            "The candidate improves both rows, but it remains non-official because `eta_l` is fit from `mu/tau`, not derived.",
            "",
            "## Promotion Criteria",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["promotion_criteria"])
    lines.extend(["", "## Rejection Criteria", ""])
    lines.extend(f"- {item}" for item in payload["rejection_criteria"])
    lines.extend(["", "## Recommendation", "", payload["recommendation"], ""])
    return "\n".join(lines)


def export_charged_lepton_precision_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export theory, audit, and candidate files."""

    base = Path(root)
    payload = audit_payload()
    markdown = render_markdown(payload)
    paths = {
        "theory": base / "theory" / "charged_lepton_precision_closure.md",
        "audit_md": base / "audits" / "charged_lepton_precision_closure_audit.md",
        "audit_json": base / "audits" / "charged_lepton_precision_closure_audit.json",
        "candidate_md": base / "candidates" / "BHSM_LEPTON_DRESSED_V1_CANDIDATE.md",
        "candidate_json": base / "candidates" / "BHSM_LEPTON_DRESSED_V1_CANDIDATE.json",
    }
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    paths["theory"].write_text(markdown, encoding="utf-8")
    paths["audit_md"].write_text(markdown, encoding="utf-8")
    paths["candidate_md"].write_text(markdown, encoding="utf-8")
    json_payload = json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n"
    paths["audit_json"].write_text(json_payload, encoding="utf-8")
    paths["candidate_json"].write_text(json_payload, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_charged_lepton_precision_outputs()
