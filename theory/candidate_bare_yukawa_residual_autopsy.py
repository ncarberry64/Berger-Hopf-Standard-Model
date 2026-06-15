"""Candidate-only residual autopsy for the bare Yukawa numerical gate.

This file extends the candidate numerical gate without entering official BHSM
prediction logic. It compares invariant action variants under a universal
parameter policy and preserves the previous Tier C result.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from candidate_bare_yukawa_gate import (
    BRANCH as PREVIOUS_BRANCH,
    PARAMETER_POLICY,
    BareYukawaParameters,
    ModeRatio,
    charged_ratio_rows,
    fiber_fraction,
    lambda_hat,
    response_factor,
    scan_universal_parameters,
)


BRANCH = "bhsm-bare-yukawa-residual-autopsy"
STATUS = "candidate_only"
PREVIOUS_VERDICT = "BARE_YUKAWA_NUMERICAL_GATE_TIER_C_ORDERING_ONLY"

ALLOWED_VERDICTS = {
    "BARE_YUKAWA_RESIDUAL_AUTOPSY_COMPLETE",
    "BARE_YUKAWA_INVARIANT_VARIANT_TIER_A_STRONG",
    "BARE_YUKAWA_INVARIANT_VARIANT_TIER_B_PLAUSIBLE",
    "BARE_YUKAWA_INVARIANT_VARIANT_TIER_C_ORDERING_ONLY",
    "BARE_YUKAWA_INVARIANT_VARIANT_TIER_D_FAIL",
}

CLAIM_LABELS = (
    "BARE_YUKAWA_RESIDUAL_AUTOPSY_COMPLETE",
    "BARE_YUKAWA_INVARIANT_ACTION_VARIANTS_CANDIDATE",
    "RAW_BARE_ACTION_TIER_C_ORDERING_ONLY_CONFIRMED",
    "DEGREE_NORMALIZED_ACTION_CANDIDATE",
    "CHANNEL_DIMENSION_NORMALIZED_ACTION_CANDIDATE",
    "BRANCH_RELATIVE_ACTION_STRUCTURAL_CANDIDATE_CONTROL",
    "NO_SECTOR_SPECIFIC_TUNING_GUARDRAIL_REINFORCED",
)

RESPONSE_SCENARIOS = ("bare_only", "current_candidate_responses")


@dataclass(frozen=True)
class ActionVariant:
    """One invariant action variant."""

    variant_id: str
    status: str
    description: str
    control_only: bool
    primary_evidence_allowed: bool


@dataclass(frozen=True)
class VariantPredictionRow:
    """One residual row for a variant."""

    ratio_name: str
    sector: str
    mode_qj: tuple[int, int]
    reference_ratio: float
    predicted_ratio: float
    log_residual: float
    abs_log_residual: float
    multiplicative_error: float
    response_scenario: str
    action_variant: str
    sign: str
    mode_class: str
    scheme_sensitive: bool


VARIANTS = (
    ActionVariant(
        "A_raw",
        "RAW_BARE_ACTION_TIER_C_ORDERING_ONLY_CONFIRMED",
        "Raw integer-coordinate action from the previous numerical gate.",
        False,
        True,
    ),
    ActionVariant(
        "B_target_degree_normalized",
        "DEGREE_NORMALIZED_ACTION_CANDIDATE",
        "Sheet-coordinate action using q/N_f and j/N_f.",
        False,
        True,
    ),
    ActionVariant(
        "C_mixed_raw_degree",
        "MIXED_RAW_DEGREE_ACTION_CANDIDATE",
        "Raw eigenvalue divided by target degree N_f.",
        False,
        True,
    ),
    ActionVariant(
        "D_channel_dimension_normalized",
        "CHANNEL_DIMENSION_NORMALIZED_ACTION_CANDIDATE",
        "Raw eigenvalue divided by active channel count N_f^2-1.",
        False,
        True,
    ),
    ActionVariant(
        "E_branch_relative",
        "BRANCH_RELATIVE_ACTION_STRUCTURAL_CANDIDATE_CONTROL",
        "Sector-relative subtraction by the minimum selected nonzero branch.",
        True,
        False,
    ),
)

SECTOR_TARGETS = {
    "charged_lepton": 3,
    "up": 6,
    "down": 12,
}


def autopsy_parameter_grid() -> tuple[BareYukawaParameters, ...]:
    """Return broad finite grid for invariant-action audit."""

    epsilons = [0.0, 0.025, 0.05, 0.075, 0.1]
    tau0s = [0.0, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 3.0, 5.0]
    betas = [0.0, 0.01, 0.05, 0.1, 0.2]
    xis = [0.0, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0]
    return tuple(
        BareYukawaParameters(epsilon, tau0, beta_eff, xi)
        for epsilon in epsilons
        for tau0 in tau0s
        for beta_eff in betas
        for xi in xis
    )


def target_degree(sector: str) -> int:
    """Return |Omega*_f| for the sector."""

    return SECTOR_TARGETS[sector]


def dim_active(sector: str) -> int:
    """Return N_f^2-1 active operator channel count."""

    n_f = target_degree(sector)
    return n_f * n_f - 1


def lambda_raw(row: ModeRatio, params: BareYukawaParameters) -> float:
    """Return raw candidate lambda."""

    return lambda_hat(row.q, row.j, params.epsilon)


def lambda_degree(row: ModeRatio, params: BareYukawaParameters) -> float:
    """Return target-degree normalized lambda."""

    n_f = target_degree(row.sector)
    return (1.0 + params.epsilon) ** -2 * (row.q / n_f) ** 2 + (row.j / n_f) ** 2


def lambda_mixed(row: ModeRatio, params: BareYukawaParameters) -> float:
    """Return raw lambda divided by target degree."""

    return lambda_raw(row, params) / target_degree(row.sector)


def lambda_channel(row: ModeRatio, params: BareYukawaParameters) -> float:
    """Return raw lambda divided by active channel dimension."""

    return lambda_raw(row, params) / dim_active(row.sector)


def _sector_min_raw(row: ModeRatio, params: BareYukawaParameters) -> float:
    rows = [item for item in charged_ratio_rows() if item.sector == row.sector]
    return min(lambda_raw(item, params) for item in rows)


def lambda_branch(row: ModeRatio, params: BareYukawaParameters) -> float:
    """Return branch-relative lambda control."""

    return max(0.0, lambda_raw(row, params) - _sector_min_raw(row, params))


def lambda_for_variant(row: ModeRatio, params: BareYukawaParameters, variant_id: str) -> float:
    """Return lambda for one action variant."""

    functions: dict[str, Callable[[ModeRatio, BareYukawaParameters], float]] = {
        "A_raw": lambda_raw,
        "B_target_degree_normalized": lambda_degree,
        "C_mixed_raw_degree": lambda_mixed,
        "D_channel_dimension_normalized": lambda_channel,
        "E_branch_relative": lambda_branch,
    }
    return functions[variant_id](row, params)


def S_variant(row: ModeRatio, params: BareYukawaParameters, variant_id: str) -> float:
    """Return action for a row under an invariant variant."""

    lam = lambda_for_variant(row, params, variant_id)
    return params.tau0 * (lam + params.beta_eff * lam * lam) - params.xi * fiber_fraction(row.q, row.j)


def predict_variant_row(
    row: ModeRatio,
    params: BareYukawaParameters,
    variant_id: str,
    response_scenario: str,
) -> VariantPredictionRow:
    """Return residual row for one variant and scenario."""

    z = response_factor(row.sector, row.label, row.q, row.j, response_scenario)
    predicted = math.exp(max(-700.0, -S_variant(row, params, variant_id))) * z
    log_residual = math.log(predicted / row.reference)
    return VariantPredictionRow(
        ratio_name=_ratio_name(row),
        sector=row.sector,
        mode_qj=(row.q, row.j),
        reference_ratio=row.reference,
        predicted_ratio=predicted,
        log_residual=log_residual,
        abs_log_residual=abs(log_residual),
        multiplicative_error=math.exp(abs(log_residual)),
        response_scenario=response_scenario,
        action_variant=variant_id,
        sign="overpredict" if log_residual > 0 else "underpredict" if log_residual < 0 else "exact",
        mode_class=row.label,
        scheme_sensitive=row.scheme_sensitive,
    )


def _ratio_name(row: ModeRatio) -> str:
    if row.sector == "charged_lepton" and row.label == "middle":
        return "mu/tau"
    if row.sector == "charged_lepton" and row.label == "light":
        return "e/tau"
    if row.sector == "up" and row.label == "middle":
        return "c/t"
    if row.sector == "up" and row.label == "light":
        return "u/t"
    if row.sector == "down" and row.label == "middle":
        return "s/b"
    if row.sector == "down" and row.label == "light":
        return "d/b"
    raise ValueError(row)


def score_variant_rows(rows: tuple[VariantPredictionRow, ...]) -> dict[str, Any]:
    """Return score and residual signature summary."""

    errors = [row.log_residual for row in rows]
    by_ratio = {row.ratio_name: row.predicted_ratio for row in rows}
    ordering = {
        "charged_lepton_ordering_pass": by_ratio["mu/tau"] > by_ratio["e/tau"],
        "up_ordering_pass": by_ratio["c/t"] > by_ratio["u/t"],
        "down_ordering_pass": by_ratio["s/b"] > by_ratio["d/b"],
    }
    ordering["ordering_pass"] = all(ordering.values())
    return {
        "rms_log_error": math.sqrt(sum(error * error for error in errors) / len(errors)),
        "max_abs_log_error": max(abs(error) for error in errors),
        **ordering,
    }


def evaluate_variant(
    params: BareYukawaParameters,
    variant_id: str,
    response_scenario: str,
) -> dict[str, Any]:
    """Evaluate one universal parameter set."""

    rows = tuple(
        predict_variant_row(row, params, variant_id, response_scenario)
        for row in charged_ratio_rows()
    )
    return {"parameters": params, "rows": rows, **score_variant_rows(rows)}


def scan_variant(variant_id: str, response_scenario: str) -> dict[str, Any]:
    """Return best universal-parameter result for variant and response scenario."""

    best: dict[str, Any] | None = None
    for params in autopsy_parameter_grid():
        result = evaluate_variant(params, variant_id, response_scenario)
        if best is None or (result["rms_log_error"], result["max_abs_log_error"]) < (
            best["rms_log_error"],
            best["max_abs_log_error"],
        ):
            best = result
    assert best is not None
    return best


def verdict_from_variant_result(result: dict[str, Any], variant: ActionVariant) -> str:
    """Return allowed verdict for variant result."""

    if variant.control_only or not result["ordering_pass"]:
        return "BARE_YUKAWA_INVARIANT_VARIANT_TIER_D_FAIL"
    rms = float(result["rms_log_error"])
    max_abs = float(result["max_abs_log_error"])
    if rms <= 0.25 and max_abs <= 0.6:
        return "BARE_YUKAWA_INVARIANT_VARIANT_TIER_A_STRONG"
    if rms <= 1.25 and max_abs <= 2.5:
        return "BARE_YUKAWA_INVARIANT_VARIANT_TIER_B_PLAUSIBLE"
    return "BARE_YUKAWA_INVARIANT_VARIANT_TIER_C_ORDERING_ONLY"


def _rms_for(rows: tuple[VariantPredictionRow, ...], *, sector: str | None = None, mode_class: str | None = None) -> float:
    selected = [
        row.log_residual
        for row in rows
        if (sector is None or row.sector == sector) and (mode_class is None or row.mode_class == mode_class)
    ]
    return math.sqrt(sum(error * error for error in selected) / len(selected))


def residual_autopsy(rows: tuple[VariantPredictionRow, ...]) -> dict[str, Any]:
    """Return ranked residual and signature autopsy for rows."""

    worst = sorted(rows, key=lambda row: row.abs_log_residual, reverse=True)
    sign_pattern = {row.ratio_name: row.sign for row in rows}
    sector_rms = {
        "charged_lepton": _rms_for(rows, sector="charged_lepton"),
        "up": _rms_for(rows, sector="up"),
        "down": _rms_for(rows, sector="down"),
    }
    mode_rms = {
        "middle": _rms_for(rows, mode_class="middle"),
        "light": _rms_for(rows, mode_class="light"),
    }
    concentration = {
        "largest_sector": max(sector_rms.items(), key=lambda item: item[1])[0],
        "largest_mode_class": max(mode_rms.items(), key=lambda item: item[1])[0],
        "pure_fiber_rows": [asdict(row) for row in rows if row.mode_qj[1] == 0],
        "down_sector_scheme_sensitive": True,
        "quark_scheme_sensitive": True,
    }
    return {
        "worst_residuals": [asdict(row) for row in worst],
        "sector_rms": sector_rms,
        "mode_rms": mode_rms,
        "sign_pattern": sign_pattern,
        "concentration": concentration,
    }


def _jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def build_autopsy_payload() -> dict[str, Any]:
    """Return the residual autopsy payload."""

    previous = scan_universal_parameters("current_candidate_responses")
    previous_rows = tuple(
        predict_variant_row(row, previous["parameters"], "A_raw", "current_candidate_responses")
        for row in charged_ratio_rows()
    )
    previous_score = score_variant_rows(previous_rows)

    variant_results: list[dict[str, Any]] = []
    best_evidence: dict[str, Any] | None = None
    best_evidence_variant: ActionVariant | None = None
    raw_current_rms = previous_score["rms_log_error"]
    raw_bare_rms = scan_variant("A_raw", "bare_only")["rms_log_error"]

    for variant in VARIANTS:
        for scenario in RESPONSE_SCENARIOS:
            result = scan_variant(variant.variant_id, scenario)
            verdict = verdict_from_variant_result(result, variant)
            response_delta = raw_bare_rms - result["rms_log_error"]
            variant_delta = raw_current_rms - result["rms_log_error"]
            entry = {
                "variant_id": variant.variant_id,
                "variant_status": variant.status,
                "response_scenario": scenario,
                "control_only": variant.control_only,
                "primary_evidence_allowed": variant.primary_evidence_allowed,
                "verdict": verdict,
                "parameter_policy": PARAMETER_POLICY,
                "best_parameters": asdict(result["parameters"]),
                "rms_log_error": result["rms_log_error"],
                "max_abs_log_error": result["max_abs_log_error"],
                "ordering_pass": result["ordering_pass"],
                "lepton_rms_log_error": _rms_for(result["rows"], sector="charged_lepton"),
                "up_rms_log_error": _rms_for(result["rows"], sector="up"),
                "down_rms_log_error": _rms_for(result["rows"], sector="down"),
                "middle_mode_rms_log_error": _rms_for(result["rows"], mode_class="middle"),
                "light_mode_rms_log_error": _rms_for(result["rows"], mode_class="light"),
                "response_improvement_delta": response_delta,
                "variant_improvement_delta": variant_delta,
                "rows": [asdict(row) for row in result["rows"]],
            }
            variant_results.append(entry)
            if variant.primary_evidence_allowed and (
                best_evidence is None
                or (entry["rms_log_error"], entry["max_abs_log_error"]) < (
                    best_evidence["rms_log_error"],
                    best_evidence["max_abs_log_error"],
                )
            ):
                best_evidence = entry
                best_evidence_variant = variant

    assert best_evidence is not None and best_evidence_variant is not None
    best_variant = {
        key: best_evidence[key]
        for key in (
            "variant_id",
            "response_scenario",
            "verdict",
            "parameter_policy",
            "best_parameters",
            "rms_log_error",
            "max_abs_log_error",
            "ordering_pass",
        )
    }
    return {
        "status": STATUS,
        "branch": BRANCH,
        "previous_branch": PREVIOUS_BRANCH,
        "previous_gate_verdict": PREVIOUS_VERDICT,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "claim_labels": CLAIM_LABELS,
        "allowed_verdicts": sorted(ALLOWED_VERDICTS),
        "best_variant": best_variant,
        "variant_results": variant_results,
        "residual_autopsy": residual_autopsy(previous_rows),
        "previous_raw_action_result": {
            "variant_id": "A_raw",
            "response_scenario": "current_candidate_responses",
            "best_parameters": asdict(previous["parameters"]),
            "rms_log_error": previous_score["rms_log_error"],
            "max_abs_log_error": previous_score["max_abs_log_error"],
            "ordering_pass": previous_score["ordering_pass"],
        },
        "parameter_policy": {
            "main_variants_A_to_D": "single_universal_parameter_set",
            "sector_specific_parameters_used": False,
            "branch_relative_is_control_only": True,
            "forbidden_sector_fit_control_implemented": False,
        },
        "notes": [
            "candidate-only",
            "quark ratios are scheme-sensitive where applicable",
            "no frozen predictions changed",
            "no official predictions changed",
            "previous Tier C ordering-only result remains valid",
        ],
    }


def render_autopsy_markdown(payload: dict[str, Any] | None = None) -> str:
    """Render residual autopsy report."""

    p = payload or build_autopsy_payload()
    best = p["best_variant"]
    lines = [
        "# Bare Yukawa Residual Autopsy",
        "",
        "Status: `BARE_YUKAWA_RESIDUAL_AUTOPSY_COMPLETE`",
        "",
        "This candidate-only audit preserves the previous `BARE_YUKAWA_NUMERICAL_GATE_TIER_C_ORDERING_ONLY` outcome. Tier C is scientifically useful because it shows the raw candidate action preserves hierarchy ordering while failing numerical closure.",
        "",
        "## Best Evidence Variant",
        "",
        f"Variant: `{best['variant_id']}`",
        f"Response scenario: `{best['response_scenario']}`",
        f"Verdict: `{best['verdict']}`",
        f"Best parameters: `{best['best_parameters']}`",
        f"RMS log error: `{best['rms_log_error']}`",
        f"Max abs log error: `{best['max_abs_log_error']}`",
        f"Ordering pass: `{best['ordering_pass']}`",
        "",
        "## Previous Raw-Action Residuals",
        "",
        "| Ratio | Sector | q,j | predicted | reference | log residual | x-error | sign |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in p["residual_autopsy"]["worst_residuals"]:
        lines.append(
            f"| `{row['ratio_name']}` | `{row['sector']}` | `{tuple(row['mode_qj'])}` | `{row['predicted_ratio']}` | `{row['reference_ratio']}` | `{row['log_residual']}` | `{row['multiplicative_error']}` | `{row['sign']}` |"
        )
    lines.extend(
        [
            "",
            "## Residual Pattern",
            "",
            f"Sector RMS: `{p['residual_autopsy']['sector_rms']}`",
            f"Mode RMS: `{p['residual_autopsy']['mode_rms']}`",
            f"Sign pattern: `{p['residual_autopsy']['sign_pattern']}`",
            "",
            "The raw best fit has `beta_eff=0` and `xi=0`, so the current fourth-order and focusing terms are not numerically favored by this coarse universal scan. The previous epsilon value hit the upper bound, suggesting raw eigenvalue normalization may be incomplete.",
            "",
            "## Claim Boundaries",
            "",
            "- No official predictions are changed.",
            "- No frozen predictions are changed.",
            "- Quark references remain scheme-sensitive.",
            "- Branch-relative subtraction is a structural control, not primary evidence.",
            "- `BARE_YUKAWA_SPECTRAL_ACTION_CANDIDATE` is not upgraded to derived.",
            "- `FULL_BHSM_MASS_ENGINE_CANDIDATE_ARCHITECTURE` is not upgraded to derived.",
            "",
        ]
    )
    return "\n".join(lines)


def render_variants_markdown(payload: dict[str, Any] | None = None) -> str:
    """Render invariant-action alternatives note."""

    p = payload or build_autopsy_payload()
    lines = [
        "# Bare Yukawa Invariant-Action Alternatives",
        "",
        "Status: `BARE_YUKAWA_INVARIANT_ACTION_VARIANTS_CANDIDATE`",
        "",
        "The raw integer eigenvalue may be incomplete because the previous scan preferred the largest epsilon tested and zeroed the fourth-order and focusing terms. This note audits invariant alternatives without sector-specific tuning.",
        "",
        "## Variants",
        "",
        "| Variant | Status | Control only | Rationale |",
        "| --- | --- | --- | --- |",
    ]
    for variant in VARIANTS:
        lines.append(
            f"| `{variant.variant_id}` | `{variant.status}` | `{variant.control_only}` | {variant.description} |"
        )
    lines.extend(
        [
            "",
            "Degree normalization tests whether suppression should depend on normalized sheet coordinates. Channel-dimension normalization tests whether active operator channel space dilutes spectral cost. Branch-relative subtraction is dangerous because it subtracts a sector minimum; it is therefore `BRANCH_RELATIVE_ACTION_STRUCTURAL_CANDIDATE_CONTROL` only.",
            "",
            "## Variant Results",
            "",
            "| Variant | Response | Verdict | RMS log error | Max abs log error | Ordering | Evidence allowed |",
            "| --- | --- | --- | ---: | ---: | --- | --- |",
        ]
    )
    for row in p["variant_results"]:
        lines.append(
            f"| `{row['variant_id']}` | `{row['response_scenario']}` | `{row['verdict']}` | `{row['rms_log_error']}` | `{row['max_abs_log_error']}` | `{row['ordering_pass']}` | `{row['primary_evidence_allowed']}` |"
        )
    lines.extend(
        [
            "",
            "## Guardrails",
            "",
            "- `NO_SECTOR_SPECIFIC_TUNING_GUARDRAIL_REINFORCED`",
            "- `QUARK_RATIO_SCHEME_SENSITIVITY_GUARDRAIL`",
            "- No sector-specific parameters are used in variants A-D.",
            "- Variant E is not used as primary evidence.",
            "- No official frozen output is updated.",
            "",
        ]
    )
    return "\n".join(lines)


def export_autopsy_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Write autopsy Markdown and JSON files."""

    base = Path(root)
    payload = build_autopsy_payload()
    (base / "theory").mkdir(parents=True, exist_ok=True)
    (base / "theory" / "bare_yukawa_residual_autopsy.md").write_text(
        render_autopsy_markdown(payload),
        encoding="utf-8",
    )
    (base / "theory" / "bare_yukawa_residual_autopsy_results.json").write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (base / "theory" / "bare_yukawa_invariant_action_alternatives.md").write_text(
        render_variants_markdown(payload),
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_autopsy_outputs(Path(__file__).resolve().parents[1])
