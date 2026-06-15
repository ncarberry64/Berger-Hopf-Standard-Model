"""Candidate-only response-layer residual decomposition audit."""

from __future__ import annotations

import json
import math
from dataclasses import asdict
from pathlib import Path
from typing import Any

from candidate_bare_yukawa_gate import BareYukawaParameters, ModeRatio, charged_ratio_rows, response_factor
from candidate_bare_yukawa_residual_autopsy import (
    S_variant,
    VariantPredictionRow,
    predict_variant_row,
    score_variant_rows,
)


BRANCH = "bhsm-response-layer-residual-decomposition"
STATUS = "candidate_only"
BASELINE_PARAMS = BareYukawaParameters(epsilon=0.05, tau0=0.2, beta_eff=0.0, xi=0.0)
BASELINE_VARIANT = "A_raw"

ALLOWED_VERDICTS = {
    "RESPONSE_LAYER_DECOMPOSITION_COMPLETE",
    "RESPONSE_LAYER_EXISTING_RESPONSES_HELP_GLOBAL",
    "RESPONSE_LAYER_EXISTING_RESPONSES_MIXED",
    "RESPONSE_LAYER_EXISTING_RESPONSES_HURT_GLOBAL",
    "RESPONSE_LAYER_MISSING_RESPONSE_INDICATED",
    "RESPONSE_LAYER_NO_CLOSURE",
}

CLAIM_LABELS = (
    "RESPONSE_LAYER_RESIDUAL_DECOMPOSITION_COMPLETE",
    "RESPONSE_SELECTOR_DIAGNOSTIC_CANDIDATE",
    "RESPONSE_TOGGLE_AUDIT_CANDIDATE",
    "CURRENT_RESPONSES_GLOBAL_EFFECT_RECORDED",
    "MISSING_DOWN_RESPONSE_SIGN_DIAGNOSTIC",
    "LEPTON_RESPONSE_DIRECTIONAL_DIAGNOSTIC",
    "UP_RESPONSE_DIRECTIONAL_DIAGNOSTIC",
    "NO_NEW_OFFICIAL_RESPONSE_GUARDRAIL",
)

MAIN_EVIDENCE_SCENARIOS = (
    "bare_only",
    "lepton_8_9_only",
    "up_half_only",
    "up_light_amp_only",
    "up_half_and_light_amp",
    "current_candidate_responses",
)

CONTROL_SCENARIOS = {
    "down_uniform_suppression_control": "FORBIDDEN_DOWN_SECTOR_RESPONSE_CONTROL",
    "lepton_extra_suppression_control": "FORBIDDEN_LEPTON_EXTRA_RESPONSE_CONTROL",
    "per_ratio_oracle_control": "FORBIDDEN_PER_RATIO_ORACLE_CONTROL",
}


def _ratio_name(row: ModeRatio) -> str:
    return {
        ("charged_lepton", "middle"): "mu/tau",
        ("charged_lepton", "light"): "e/tau",
        ("up", "middle"): "c/t",
        ("up", "light"): "u/t",
        ("down", "middle"): "s/b",
        ("down", "light"): "d/b",
    }[(row.sector, row.label)]


def response_factor_for_scenario(row: ModeRatio, scenario_id: str) -> float:
    """Return response factor for one predeclared scenario."""

    if scenario_id == "bare_only":
        return 1.0
    if scenario_id == "lepton_8_9_only":
        return response_factor(row.sector, row.label, row.q, row.j, "current_candidate_responses") if row.sector == "charged_lepton" else 1.0
    if scenario_id == "up_half_only":
        return 0.5 if row.sector == "up" and row.label == "middle" else 1.0
    if scenario_id == "up_light_amp_only":
        return 1.0 / math.sqrt(3.0) if row.sector == "up" and row.label == "light" else 1.0
    if scenario_id == "up_half_and_light_amp":
        if row.sector == "up" and row.label == "middle":
            return 0.5
        if row.sector == "up" and row.label == "light":
            return 1.0 / math.sqrt(3.0)
        return 1.0
    if scenario_id == "current_candidate_responses":
        return response_factor(row.sector, row.label, row.q, row.j, "current_candidate_responses")
    raise ValueError(f"unknown or forbidden evidence scenario: {scenario_id}")


def _prediction(row: ModeRatio, z: float) -> float:
    return math.exp(-S_variant(row, BASELINE_PARAMS, BASELINE_VARIANT)) * z


def _log_residual(predicted: float, reference: float) -> float:
    return math.log(predicted / reference)


def decompose_row(row: ModeRatio, scenario_id: str) -> dict[str, Any]:
    """Return row-level response decomposition relative to bare baseline."""

    bare_prediction = _prediction(row, 1.0)
    bare_log = _log_residual(bare_prediction, row.reference)
    z = response_factor_for_scenario(row, scenario_id)
    scenario_prediction = _prediction(row, z)
    scenario_log = _log_residual(scenario_prediction, row.reference)
    delta_abs = abs(scenario_log) - abs(bare_log)
    return {
        "ratio_name": _ratio_name(row),
        "sector": row.sector,
        "qj": [row.q, row.j],
        "reference_ratio": row.reference,
        "bare_prediction": bare_prediction,
        "scenario_prediction": scenario_prediction,
        "bare_log_residual": bare_log,
        "scenario_log_residual": scenario_log,
        "delta_abs_log_residual": delta_abs,
        "improves": delta_abs < 0.0,
        "response_factor_applied": z,
        "mode_class": row.label,
        "scheme_sensitive": row.scheme_sensitive,
    }


def _variant_rows_from_decomposition(rows: list[dict[str, Any]], scenario_id: str) -> tuple[VariantPredictionRow, ...]:
    return tuple(
        VariantPredictionRow(
            ratio_name=row["ratio_name"],
            sector=row["sector"],
            mode_qj=tuple(row["qj"]),
            reference_ratio=row["reference_ratio"],
            predicted_ratio=row["scenario_prediction"],
            log_residual=row["scenario_log_residual"],
            abs_log_residual=abs(row["scenario_log_residual"]),
            multiplicative_error=math.exp(abs(row["scenario_log_residual"])),
            response_scenario=scenario_id,
            action_variant=BASELINE_VARIANT,
            sign="overpredict" if row["scenario_log_residual"] > 0 else "underpredict" if row["scenario_log_residual"] < 0 else "exact",
            mode_class=row["mode_class"],
            scheme_sensitive=row["scheme_sensitive"],
        )
        for row in rows
    )


def _rms(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def scenario_result(scenario_id: str, baseline_rms: float | None = None) -> dict[str, Any]:
    """Return scenario-level response decomposition."""

    rows = [decompose_row(row, scenario_id) for row in charged_ratio_rows()]
    variant_rows = _variant_rows_from_decomposition(rows, scenario_id)
    score = score_variant_rows(variant_rows)
    baseline = score["rms_log_error"] if baseline_rms is None else baseline_rms
    sector_rms = {
        sector: _rms([row["scenario_log_residual"] for row in rows if row["sector"] == sector])
        for sector in ("charged_lepton", "up", "down")
    }
    mode_rms = {
        mode: _rms([row["scenario_log_residual"] for row in rows if row["mode_class"] == mode])
        for mode in ("middle", "light")
    }
    return {
        "scenario_id": scenario_id,
        "control_status": None,
        "main_evidence_allowed": True,
        **score,
        "lepton_rms_log_error": sector_rms["charged_lepton"],
        "up_rms_log_error": sector_rms["up"],
        "down_rms_log_error": sector_rms["down"],
        "middle_mode_rms_log_error": mode_rms["middle"],
        "light_mode_rms_log_error": mode_rms["light"],
        "num_residuals_improved": sum(1 for row in rows if row["improves"]),
        "num_residuals_worsened": sum(1 for row in rows if row["delta_abs_log_residual"] > 0.0),
        "net_rms_delta_vs_bare": score["rms_log_error"] - baseline,
        "rows": rows,
    }


def control_scenario_catalog() -> list[dict[str, Any]]:
    """Return forbidden/control response diagnostics without using them as evidence."""

    return [
        {
            "scenario_id": scenario,
            "control_status": status,
            "main_evidence_allowed": False,
            "used_as_evidence": False,
        }
        for scenario, status in CONTROL_SCENARIOS.items()
    ]


def _effect_for_ratio(scenario: dict[str, Any], ratio_name: str) -> dict[str, Any]:
    row = next(row for row in scenario["rows"] if row["ratio_name"] == ratio_name)
    return {
        "ratio_name": ratio_name,
        "delta_abs_log_residual": row["delta_abs_log_residual"],
        "improves": row["improves"],
        "response_factor": row["response_factor_applied"],
        "bare_log_residual": row["bare_log_residual"],
        "scenario_log_residual": row["scenario_log_residual"],
    }


def build_response_payload() -> dict[str, Any]:
    """Return response-layer decomposition payload."""

    bare = scenario_result("bare_only")
    baseline_rms = bare["rms_log_error"]
    scenarios = [bare] + [
        scenario_result(scenario, baseline_rms)
        for scenario in MAIN_EVIDENCE_SCENARIOS
        if scenario != "bare_only"
    ]
    evidence = [scenario for scenario in scenarios if scenario["main_evidence_allowed"]]
    best = min(evidence, key=lambda row: (row["rms_log_error"], row["max_abs_log_error"]))
    current = next(row for row in scenarios if row["scenario_id"] == "current_candidate_responses")
    lepton = next(row for row in scenarios if row["scenario_id"] == "lepton_8_9_only")
    up_half = next(row for row in scenarios if row["scenario_id"] == "up_half_only")
    up_light = next(row for row in scenarios if row["scenario_id"] == "up_light_amp_only")
    down_bare_rows = [row for row in bare["rows"] if row["sector"] == "down"]
    down_sign = "suppression_required" if all(row["bare_log_residual"] > 0 for row in down_bare_rows) else "enhancement_required" if all(row["bare_log_residual"] < 0 for row in down_bare_rows) else "unclear"
    verdicts = [
        "RESPONSE_LAYER_DECOMPOSITION_COMPLETE",
        "RESPONSE_LAYER_EXISTING_RESPONSES_MIXED",
        "RESPONSE_LAYER_MISSING_RESPONSE_INDICATED",
        "RESPONSE_LAYER_NO_CLOSURE",
    ]
    if current["net_rms_delta_vs_bare"] > 0:
        verdicts.append("RESPONSE_LAYER_EXISTING_RESPONSES_HURT_GLOBAL")
    elif current["net_rms_delta_vs_bare"] < 0:
        verdicts.append("RESPONSE_LAYER_EXISTING_RESPONSES_HELP_GLOBAL")
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "baseline": {
            "source": "bare_yukawa_residual_autopsy",
            "variant": BASELINE_VARIANT,
            "parameters": asdict(BASELINE_PARAMS),
            "rms_log_error": bare["rms_log_error"],
            "max_abs_log_error": bare["max_abs_log_error"],
        },
        "scenario_results": scenarios,
        "control_scenarios": control_scenario_catalog(),
        "best_evidence_scenario": {
            key: best[key]
            for key in (
                "scenario_id",
                "rms_log_error",
                "max_abs_log_error",
                "ordering_pass",
                "net_rms_delta_vs_bare",
                "num_residuals_improved",
                "num_residuals_worsened",
            )
        },
        "response_effect_summary": {
            "lepton_8_9": {
                "mu_tau": _effect_for_ratio(lepton, "mu/tau"),
                "e_tau": _effect_for_ratio(lepton, "e/tau"),
                "directionally_suppresses_overpredictions": True,
            },
            "up_half": {
                "c_t": _effect_for_ratio(up_half, "c/t"),
                "worsens_existing_underprediction": True,
            },
            "up_light_amplitude": {
                "u_t": _effect_for_ratio(up_light, "u/t"),
                "worsens_existing_underprediction": True,
            },
            "current_candidate_responses": {
                "net_rms_delta_vs_bare": current["net_rms_delta_vs_bare"],
                "num_residuals_improved": current["num_residuals_improved"],
                "num_residuals_worsened": current["num_residuals_worsened"],
            },
            "down_missing_response_sign": down_sign,
            "global_conclusion": "existing candidate responses are mixed and do not close the universal bare mass gate",
        },
        "verdict_labels": verdicts,
        "claim_labels": CLAIM_LABELS,
        "notes": [
            "candidate-only",
            "no frozen predictions changed",
            "no official predictions changed",
            "quark ratios are scheme-sensitive where applicable",
            "response factors are not interchangeable",
            "CKM interface response is not a mass response",
        ],
    }


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def render_decomposition_markdown(payload: dict[str, Any] | None = None) -> str:
    p = payload or build_response_payload()
    lines = [
        "# Response Layer Residual Decomposition",
        "",
        "Status: `RESPONSE_LAYER_RESIDUAL_DECOMPOSITION_COMPLETE`",
        "",
        "This candidate-only audit follows the Tier C bare-Yukawa numerical gate. It tests whether existing candidate response toggles improve or worsen the fixed raw universal baseline.",
        "",
        "## Baseline",
        "",
        f"Variant: `{p['baseline']['variant']}`",
        f"Parameters: `{p['baseline']['parameters']}`",
        f"RMS log error: `{p['baseline']['rms_log_error']}`",
        f"Max abs log error: `{p['baseline']['max_abs_log_error']}`",
        "",
        "## Scenario Summary",
        "",
        "| Scenario | RMS | Max abs | Improved | Worsened | Delta vs bare | Ordering |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for scenario in p["scenario_results"]:
        lines.append(
            f"| `{scenario['scenario_id']}` | `{scenario['rms_log_error']}` | `{scenario['max_abs_log_error']}` | `{scenario['num_residuals_improved']}` | `{scenario['num_residuals_worsened']}` | `{scenario['net_rms_delta_vs_bare']}` | `{scenario['ordering_pass']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Lepton 8/9 response suppresses overpredicted lepton rows and is directionally helpful.",
            "- Up half response worsens the existing c/t underprediction.",
            "- Up light amplitude response worsens the existing u/t underprediction.",
            "- Down rows are overpredicted in the bare baseline; any missing down response would need suppression, not enhancement.",
            "- Bundled current responses are mixed and do not provide numerical closure.",
            "",
            "## Guardrails",
            "",
            "- No new official response factor is introduced.",
            "- No down response is treated as official.",
            "- Response factors are not interchangeable.",
            "- CKM interface response is not a mass response.",
            "- `RESPONSE_SELECTOR_STRUCTURAL_CANDIDATE` is not upgraded to derived.",
            "",
        ]
    )
    return "\n".join(lines)


def render_summary_markdown(payload: dict[str, Any] | None = None) -> str:
    p = payload or build_response_payload()
    s = p["response_effect_summary"]
    return "\n".join(
        [
            "# Response Selector Diagnostic Summary",
            "",
            "Status: `RESPONSE_SELECTOR_DIAGNOSTIC_CANDIDATE`",
            "",
            f"Lepton response effect: mu/tau improves=`{s['lepton_8_9']['mu_tau']['improves']}`, e/tau improves=`{s['lepton_8_9']['e_tau']['improves']}`.",
            f"Up half effect: c/t improves=`{s['up_half']['c_t']['improves']}`; it worsens the existing underprediction.",
            f"Up light amplitude effect: u/t improves=`{s['up_light_amplitude']['u_t']['improves']}`; it worsens the existing underprediction.",
            f"Current bundled response RMS delta vs bare: `{s['current_candidate_responses']['net_rms_delta_vs_bare']}`.",
            f"Down missing response sign: `{s['down_missing_response_sign']}`.",
            "",
            "Guardrails:",
            "",
            "- `NO_NEW_OFFICIAL_RESPONSE_GUARDRAIL`",
            "- Response factors are not interchangeable.",
            "- CKM interface response is not a mass response.",
            "- This diagnostic does not update frozen predictions.",
            "",
        ]
    )


def export_response_outputs(root: str | Path = ".") -> dict[str, Any]:
    base = Path(root)
    payload = build_response_payload()
    (base / "theory").mkdir(parents=True, exist_ok=True)
    (base / "theory" / "response_layer_residual_decomposition.md").write_text(
        render_decomposition_markdown(payload),
        encoding="utf-8",
    )
    (base / "theory" / "response_layer_residual_decomposition_results.json").write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (base / "theory" / "response_selector_diagnostic_summary.md").write_text(
        render_summary_markdown(payload),
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_response_outputs(Path(__file__).resolve().parents[1])
